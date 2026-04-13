from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Optional
from uuid import uuid4
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_refresh_token,
)
from app.core.config import settings
from app.models.user import User, UserRole, UserStatus
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from pydantic import BaseModel, EmailStr, Field
import httpx
import re
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
security = HTTPBearer()
logger = logging.getLogger(__name__)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=2, max_length=255)
    gender: Optional[str] = None
    type: Optional[str] = "consumer"  # consumer, producer, etc.
# ... nghĩa là không được thiếu
# Tham số ge: ≥ (greater or equal), gt: >, le: ≤, lt: <
# Khai báo	Có bắt buộc không?
# str	✅ Bắt buộc
# Optional[str]	✅ Bắt buộc (nhưng cho null)
# Optional[str] = None	❌ Không bắt buộc
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    recaptcha: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None

class TokenResponse(BaseModel):
    api_token: str
    access_token: Optional[str] = None
    expires_at: str
    refresh_token: Optional[str] = None
    refresh_expires_at: Optional[str] = None
    token_type: str = "Bearer"

class UserInfoResponse(BaseModel):
    id: int
    email: str
    name: str
    gender: Optional[str]
    activated: int
    status: str
    status_reason: Optional[str]
    status_expire_at: Optional[str]
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: str
    updated_at: Optional[str]
    deleted_by: Optional[str]
    deleted_at: Optional[str]
    type: Optional[str]
    roles: list
    source_providers: list

    class Config:
        from_attributes = True

class StandardResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[list] = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_utc_iso(dt: datetime) -> str:
    return _to_utc_aware(dt).isoformat().replace("+00:00", "Z")


def _get_client_ip(request: Request) -> Optional[str]:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _extract_refresh_token(refresh_data: Optional[RefreshTokenRequest], request: Request) -> Optional[str]:
    if refresh_data and refresh_data.refresh_token:
        return refresh_data.refresh_token

    cookie_token = request.cookies.get("refresh_token")
    if cookie_token:
        return cookie_token

    header_token = request.headers.get("X-Refresh-Token")
    if header_token:
        return header_token

    return None


def _create_token_pair(
    user: User,
    request: Request,
    db: Session,
    family_id: Optional[str] = None,
) -> dict:
    now = _utcnow()
    access_expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_expires_at = now + access_expires_delta
    refresh_expires_at = now + refresh_expires_delta

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_expires_delta,
    )

    refresh_jti = str(uuid4())
    refresh_family_id = family_id or str(uuid4())
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "jti": refresh_jti,
            "family_id": refresh_family_id,
        },
        expires_delta=refresh_expires_delta,
    )

    refresh_token_row = RefreshToken(
        user_id=user.id,
        jti=refresh_jti,
        family_id=refresh_family_id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=refresh_expires_at,
        created_by_ip=_get_client_ip(request),
        created_by_user_agent=request.headers.get("User-Agent"),
    )
    db.add(refresh_token_row)

    return {
        "api_token": access_token,
        "access_token": access_token,
        "expires_at": _to_utc_iso(access_expires_at),
        "refresh_token": refresh_token,
        "refresh_expires_at": _to_utc_iso(refresh_expires_at),
        "token_type": "Bearer",
        "refresh_jti": refresh_jti,
        "refresh_family_id": refresh_family_id,
    }


def _revoke_token_family(db: Session, user_id: int, family_id: str, reason: str) -> int:
    now = _utcnow()
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.family_id == family_id,
        RefreshToken.revoked_at.is_(None),
    ).all()

    for token in tokens:
        token.revoked_at = now
        token.revoked_reason = reason

    return len(tokens)


def _revoke_all_active_user_tokens(db: Session, user_id: int, reason: str) -> int:
    now = _utcnow()
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    ).all()

    for token in tokens:
        token.revoked_at = now
        token.revoked_reason = reason

    return len(tokens)


def _is_recaptcha_bypass_allowed(request: Request) -> bool:
    """Allow bypass only for trusted clients with a dedicated bypass secret."""
    if not settings.RECAPTCHA_BYPASS_ENABLED:
        return False

    bypass_secret = settings.RECAPTCHA_BYPASS_SECRET_KEY
    if not bypass_secret:
        return False

    header_secret = request.headers.get("X-Recaptcha-Bypass-Token")
    if not header_secret or header_secret != bypass_secret:
        return False

    client_type = (request.headers.get("X-Client-Type") or "").strip().lower()
    allowed_clients = {
        c.strip().lower()
        for c in settings.RECAPTCHA_BYPASS_CLIENTS.split(",")
        if c.strip()
    }
    if not allowed_clients:
        return True

    return client_type in allowed_clients


async def verify_recaptcha_v3(token: Optional[str], request: Request) -> None:
    """Validate reCAPTCHA v3 token with Google siteverify API."""
    if _is_recaptcha_bypass_allowed(request):
        return

    if not settings.RECAPTCHA_ENABLED:
        return

    if not settings.RECAPTCHA_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="reCAPTCHA is not configured on server",
        )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA token is required",
        )

    client_ip = _get_client_ip(request)
    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
    }
    if client_ip:
        payload["remoteip"] = client_ip

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.RECAPTCHA_VERIFY_URL, data=payload)
            response.raise_for_status()
            verify_result = response.json()
    except httpx.HTTPError as exc:
        logger.warning("reCAPTCHA verify HTTP error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify reCAPTCHA right now",
        )

    if not verify_result.get("success"):
        error_codes = verify_result.get("error-codes") or []
        logger.warning(
            "reCAPTCHA verify failed: error_codes=%s hostname=%s action=%s score=%s client_ip=%s",
            error_codes,
            verify_result.get("hostname"),
            verify_result.get("action"),
            verify_result.get("score"),
            client_ip,
        )

        detail = "reCAPTCHA verification failed"
        if settings.DEBUG and error_codes:
            detail = f"reCAPTCHA verification failed: {', '.join(error_codes)}"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    action = verify_result.get("action")
    if action != settings.RECAPTCHA_EXPECTED_ACTION:
        logger.warning(
            "reCAPTCHA action mismatch: got=%s expected=%s hostname=%s client_ip=%s",
            action,
            settings.RECAPTCHA_EXPECTED_ACTION,
            verify_result.get("hostname"),
            client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reCAPTCHA action",
        )

    score = float(verify_result.get("score", 0.0) or 0.0)
    if score < settings.RECAPTCHA_MIN_SCORE:
        logger.warning(
            "reCAPTCHA score too low: score=%.3f min=%.3f action=%s hostname=%s client_ip=%s",
            score,
            settings.RECAPTCHA_MIN_SCORE,
            action,
            verify_result.get("hostname"),
            client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA score too low",
        )

def get_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract Bearer token from Authorization header"""
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

def check_user_status(user: User) -> None:
    """
    Check user account status and raise appropriate exception if suspended or banned
    
    Raises:
        HTTPException 403: If user is SUSPENDED (and not expired) or BANNED
    """
    if user.status == UserStatus.BANNED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account has been permanently banned. Reason: {user.status_reason or 'No reason provided'}"
        )
    
    if user.status == UserStatus.SUSPENDED:
        # Check if suspension has expired
        if user.status_expire_at:
            status_expire_at = _to_utc_aware(user.status_expire_at)
            if _utcnow() < status_expire_at:
                # Still suspended
                expire_str = status_expire_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account is suspended until {expire_str}. Reason: {user.status_reason or 'No reason provided'}"
                )
            # Suspension expired - should auto-reactivate but we'll just allow login
            # Admin should have a cron job to auto-reactivate expired suspensions
        else:
            # Suspended indefinitely
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is suspended indefinitely. Reason: {user.status_reason or 'No reason provided'}"
            )


def _get_user_from_token(token: str, db: Session) -> User:
    """Resolve user from JWT token and ensure account is not deleted."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id_int, User.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user(token: str = Depends(get_bearer_token), db: Session = Depends(get_db)):
    """Get current authenticated user from Bearer token in header"""
    user = _get_user_from_token(token, db)
    
    if user.activated != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not activated",
        )
    
    # Check user status (BANNED/SUSPENDED)
    check_user_status(user)
    
    return user


def get_current_user_allow_inactive(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get authenticated user from Bearer token without checking `activated` flag.
    Used for onboarding flows where seller accounts may still be inactive.
    """
    user = _get_user_from_token(token, db)

    # BANNED/SUSPENDED accounts are still blocked.
    check_user_status(user)

    return user

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    """
    Optional authentication - returns User if authenticated, None otherwise
    Useful for development/testing without strict authentication
    """
    if not credentials:
        # In DEBUG mode, create a mock user for testing
        if settings.DEBUG:
            # Return first admin user or create a mock one
            mock_user = db.query(User).filter(User.activated == 1).first()
            if mock_user:
                return mock_user
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload is None:
            return None
            
        user_id = payload.get("sub")
        if user_id is None:
            return None
            
        user_id_int = int(user_id)
        user = db.query(User).filter(User.id == user_id_int, User.deleted_at.is_(None)).first()
        return user
    except Exception:
        return None

@router.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account
    Public endpoint - no authentication required
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if len(register_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Validate email format (pydantic EmailStr already does this, but extra check)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, register_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Create new user
    # Producer/seller phải qua xét duyệt hồ sơ (activated=0) trước khi bán hàng
    # Consumer được kích hoạt ngay (activated=1)
    user_type = register_data.type or "consumer"
    is_seller = user_type in ("producer", "seller")
    new_user = User(
        email=register_data.email,
        password_hash=get_password_hash(register_data.password),
        name=register_data.name,
        gender=register_data.gender,
        type=user_type,
        activated=0 if is_seller else 1
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return StandardResponse(
        success=True,
        message="User registered successfully",
        data={
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "type": new_user.type
        }
    )

@router.post("/login", response_model=StandardResponse)
async def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Login endpoint
    Returns Bearer token in response
    Use token in Authorization header: Authorization: Bearer <token>
    """
    await verify_recaptcha_v3(login_data.recaptcha, request)

    user = db.query(User).filter(
        User.email == login_data.email,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    allow_inactive_for_onboarding = user.type in ("producer", "seller")
    if user.activated != 1 and not allow_inactive_for_onboarding:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not activated. Please contact administrator."
        )
    
    # Check user status (BANNED/SUSPENDED)
    check_user_status(user)
    
    token_pair = _create_token_pair(user=user, request=request, db=db)
    db.commit()
    
    return StandardResponse(
        success=True,
        message="Login successful",
        data={
            "api_token": token_pair["api_token"],
            "access_token": token_pair["access_token"],
            "refresh_token": token_pair["refresh_token"],
            "token_type": token_pair["token_type"],
            "expires_at": token_pair["expires_at"],
            "refresh_expires_at": token_pair["refresh_expires_at"],
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "type": user.type,
                "activated": user.activated
            }
        }
    )

@router.get("/me", response_model=StandardResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user info with roles and permissions
    Requires Bearer token in Authorization header
    """
    user = current_user
    
    # Get user roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    roles_data = []
    
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles_data.append({
                "id": role.id,
                "role_name": role.role_name,
                "description": role.description
            })
    
    return StandardResponse(
        success=True,
        message="User information retrieved successfully",
        data={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "gender": user.gender,
            "activated": user.activated,
            "status": user.status.value,
            "status_reason": user.status_reason,
            "status_expire_at": user.status_expire_at.isoformat() if user.status_expire_at else None,
            "created_by": user.created_by,
            "updated_by": user.updated_by,
            "created_at": user.created_at.isoformat() if user.created_at else "",
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "deleted_by": user.deleted_by,
            "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
            "type": user.type,
            "roles": roles_data,
            "source_providers": []
        }
    )

@router.post("/logout", response_model=StandardResponse)
async def logout(
    request: Request,
    refresh_data: Optional[RefreshTokenRequest] = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout endpoint
    Revokes refresh token for current device when provided.
    If no refresh token is provided, revokes all active refresh tokens of current user.
    """
    revoked_count = 0
    raw_refresh_token = _extract_refresh_token(refresh_data, request)

    if raw_refresh_token:
        payload = decode_refresh_token(raw_refresh_token)
        if payload and str(payload.get("sub")) == str(current_user.id):
            token_jti = payload.get("jti")
            if token_jti:
                token_row = db.query(RefreshToken).filter(
                    RefreshToken.user_id == current_user.id,
                    RefreshToken.jti == token_jti,
                    RefreshToken.revoked_at.is_(None),
                ).first()
                if token_row:
                    token_row.revoked_at = _utcnow()
                    token_row.revoked_reason = "logout"
                    revoked_count = 1

    if revoked_count == 0:
        revoked_count = _revoke_all_active_user_tokens(
            db,
            user_id=current_user.id,
            reason="logout_all_sessions",
        )

    db.commit()

    return StandardResponse(
        success=True,
        message="Logged out successfully. Please remove token from client storage.",
        data={"revoked_refresh_tokens": revoked_count},
    )

@router.post("/refresh", response_model=StandardResponse)
async def refresh_token(
    request: Request,
    refresh_data: Optional[RefreshTokenRequest] = Body(default=None),
    db: Session = Depends(get_db),
):
    """
    Refresh token endpoint using refresh-token rotation.
    Accepts refresh token from JSON body, cookie (`refresh_token`) or header (`X-Refresh-Token`).
    """
    raw_refresh_token = _extract_refresh_token(refresh_data, request)
    if not raw_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required",
        )

    payload = decode_refresh_token(raw_refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")
    token_jti = payload.get("jti")
    family_id = payload.get("family_id")
    if not user_id or not token_jti or not family_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in refresh token",
        )

    user = db.query(User).filter(
        User.id == user_id_int,
        User.deleted_at.is_(None),
    ).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted",
        )

    allow_inactive_for_onboarding = user.type in ("producer", "seller")
    if user.activated != 1 and not allow_inactive_for_onboarding:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not activated. Please contact administrator.",
        )

    check_user_status(user)

    refresh_row = db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.jti == token_jti,
    ).first()

    token_hash = hash_refresh_token(raw_refresh_token)
    if (
        refresh_row is None
        or refresh_row.family_id != family_id
        or refresh_row.token_hash != token_hash
    ):
        _revoke_token_family(
            db,
            user_id=user.id,
            family_id=family_id,
            reason="refresh_token_reuse_detected",
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid",
        )

    if refresh_row.revoked_at is not None:
        _revoke_token_family(
            db,
            user_id=user.id,
            family_id=family_id,
            reason="refresh_token_reuse_detected",
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    if _to_utc_aware(refresh_row.expires_at) <= _utcnow():
        refresh_row.revoked_at = _utcnow()
        refresh_row.revoked_reason = "expired"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    token_pair = _create_token_pair(
        user=user,
        request=request,
        db=db,
        family_id=family_id,
    )

    refresh_row.revoked_at = _utcnow()
    refresh_row.revoked_reason = "rotated"
    refresh_row.replaced_by_jti = token_pair["refresh_jti"]

    db.commit()
    
    return StandardResponse(
        success=True,
        message="Token refreshed successfully",
        data={
            "api_token": token_pair["api_token"],
            "access_token": token_pair["access_token"],
            "refresh_token": token_pair["refresh_token"],
            "token_type": token_pair["token_type"],
            "expires_at": token_pair["expires_at"],
            "refresh_expires_at": token_pair["refresh_expires_at"],
        }
    )


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None


@router.put("/profile", response_model=StandardResponse)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin cá nhân (dùng chung cho Admin, Seller, Consumer)
    """
    update_data = profile_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")

    for key, value in update_data.items():
        setattr(current_user, key, value)

    current_user.updated_at = _utcnow()
    db.commit()
    db.refresh(current_user)

    return StandardResponse(
        success=True,
        message="Cập nhật thông tin cá nhân thành công",
        data={
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "gender": current_user.gender,
            "type": current_user.type,
        }
    )

