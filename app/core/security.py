from datetime import datetime, timedelta
from typing import Optional
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def _decode_token(token: str, secret_key: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    to_encode.setdefault("token_type", "access")
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.refresh_token_secret_key,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    payload = _decode_token(token, settings.SECRET_KEY)
    if payload is None:
        return None
    token_type = payload.get("token_type")
    # Accept legacy tokens that don't include token_type.
    if token_type and token_type != "access":
        return None
    return payload


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT refresh token"""
    payload = _decode_token(token, settings.refresh_token_secret_key)
    if payload is None:
        return None
    if payload.get("token_type") != "refresh":
        return None
    return payload


def hash_refresh_token(token: str) -> str:
    """Create a deterministic hash for refresh token persistence."""
    raw = f"{settings.refresh_token_secret_key}:{token}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

