from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.config import settings
from app.models.user import User, UserRole, UserStatus
from app.models.role import Role
from pydantic import BaseModel, EmailStr, Field
import httpx
import re

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
security = HTTPBearer()

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

class TokenResponse(BaseModel):
    api_token: str
    expires_at: str
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


async def verify_recaptcha_v3(token: Optional[str], request: Request) -> None:
    """Validate reCAPTCHA v3 token with Google siteverify API."""
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

    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
    }
    if request.client and request.client.host:
        payload["remoteip"] = request.client.host

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.RECAPTCHA_VERIFY_URL, data=payload)
            response.raise_for_status()
            verify_result = response.json()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify reCAPTCHA right now",
        )

    if not verify_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA verification failed",
        )

    action = verify_result.get("action")
    if action != settings.RECAPTCHA_EXPECTED_ACTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reCAPTCHA action",
        )

    score = float(verify_result.get("score", 0.0) or 0.0)
    if score < settings.RECAPTCHA_MIN_SCORE:
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
            if datetime.utcnow() < user.status_expire_at:
                # Still suspended
                expire_str = user.status_expire_at.strftime("%Y-%m-%d %H:%M:%S UTC")
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
    
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=expires_delta
    )
    
    # Use UTC time and add Z suffix for proper timezone
    expires_at = datetime.utcnow() + expires_delta
    
    return StandardResponse(
        success=True,
        message="Login successful",
        data={
            "api_token": access_token,
            "token_type": "Bearer",
            "expires_at": expires_at.isoformat() + "Z",  # Add Z for UTC timezone
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
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint
    Note: Client should remove token from storage
    JWT tokens cannot be invalidated server-side without a token blacklist
    """
    return StandardResponse(
        success=True,
        message="Logged out successfully. Please remove token from client storage."
    )

@router.post("/refresh", response_model=StandardResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    Requires valid Bearer token in Authorization header
    Returns new token with extended expiration
    """
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email},
        expires_delta=expires_delta
    )
    
    expires_at = datetime.utcnow() + expires_delta
    
    return StandardResponse(
        success=True,
        message="Token refreshed successfully",
        data={
            "api_token": access_token,
            "token_type": "Bearer",
            "expires_at": expires_at.isoformat()
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

    current_user.updated_at = datetime.utcnow()
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

