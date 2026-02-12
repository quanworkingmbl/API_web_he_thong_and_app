# 📚 HƯỚNG DẪN XÂY DỰNG LẠI DỰ ÁN CMS API TỪ ĐẦU

## 📋 Tổng quan dự án

**Tên dự án:** CMS API - FastAPI Backend  
**Công nghệ:** FastAPI + SQLAlchemy + PostgreSQL (Supabase) + JWT Auth  
**Phiên bản Python:** 3.11+

### Các tính năng chính:
- Authentication & Authorization với JWT
- Role-Based Access Control (RBAC)
- Quản lý Users, Roles, Permissions
- Quản lý Products, Orders, Payments
- Quản lý Content, Complaints, Contracts
- Dashboard & Statistics APIs
- Mobile App APIs

---

## 📁 CẤU TRÚC DỰ ÁN

```
Du_an_cms_API/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py     # API Router
│   │       ├── auth.py         # Authentication
│   │       ├── users.py        # User management
│   │       ├── roles.py        # Role management
│   │       ├── permissions.py  # Permission management
│   │       ├── organizations.py
│   │       ├── products.py
│   │       ├── payments.py
│   │       ├── orders.py
│   │       ├── content.py
│   │       ├── complaints.py
│   │       ├── contracts.py
│   │       ├── categories.py
│   │       ├── regions.py
│   │       ├── media.py
│   │       ├── dashboard.py
│   │       ├── stats.py
│   │       └── mobile_app.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings/Configuration
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── security.py         # JWT & Password utils
│   │   ├── permissions.py      # RBAC utilities
│   │   ├── exceptions.py       # Exception handlers
│   │   ├── logging_config.py   # Logging setup
│   │   └── middleware.py       # Custom middleware
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       ├── role.py
│       ├── permission.py
│       ├── organization.py
│       ├── product.py
│       ├── payment.py
│       ├── order.py
│       ├── content.py
│       ├── complaint.py
│       ├── partner_contract.py
│       ├── category.py
│       ├── region.py
│       └── media.py
├── alembic/                     # Database migrations
├── requirements.txt
├── run.py
├── .env
├── Procfile
├── railway.json
└── README.md
```

---

# 🚀 PHASE 1: KHỞI TẠO DỰ ÁN

## Bước 1.1: Tạo thư mục dự án và Virtual Environment

```bash
# Tạo thư mục dự án
mkdir Du_an_cms_API
cd Du_an_cms_API

# Tạo virtual environment
python -m venv venv

# Kích hoạt venv (Windows)
venv\Scripts\activate

# Kích hoạt venv (Linux/Mac)
source venv/bin/activate
```

## Bước 1.2: Tạo file `requirements.txt`

```txt
fastapi==0.109.0  
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
argon2-cffi==23.1.0
python-multipart==0.0.6
email-validator==2.1.0
httpx==0.26.0
gunicorn==21.2.0
```
Giải thích 
pydantic đây là xương sống của FastAPi
pydantic-settings đây là nơi quản lý thông tin nhảy cảm 
Cài đặt:
```bash
pip install -r requirements.txt
```

## Bước 1.3: Tạo file `.env`

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-xxx.pooler.supabase.com:5432/postgres

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=True
```

## Bước 1.4: Tạo file `run.py`

```python
#!/usr/bin/env python3
"""
Development server runner
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

---

# 🏗️ PHASE 2: TẠO CORE MODULES

## Bước 2.1: Tạo cấu trúc thư mục app

```bash
mkdir app
mkdir app\core
mkdir app\models
mkdir app\api
mkdir app\api\v1
```

## Bước 2.2: Tạo `app/__init__.py`

```python
# app/__init__.py
# Package init file
```

## Bước 2.3: Tạo `app/core/__init__.py`

```python
# app/core/__init__.py
# Core package init
```

## Bước 2.4: Tạo `app/core/config.py` - Configuration

```python
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DIRECT_URL: str = ""
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # App
    APP_NAME: str = "CMS API"
    APP_VERSION: str = "1.0.0"
    DEBUG: Union[bool, str] = True
    
    @field_validator('DEBUG', mode='before') -> Kiểm tra và đưa về kiểu dữ liệu chuẩn 
    @classmethod  -> cần tác động lên cái khuôn
    def parse_debug(cls, v: Union[bool, str, int]) -> bool:
        """Parse DEBUG from various formats"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        if isinstance(v, int):
            return bool(v)
        return True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Bước 2.5: Tạo `app/core/database.py` - Database Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from app.core.config import settings

def clean_database_url(url: str) -> str:
    """Remove pgbouncer parameter from connection string"""
    if not url:
        return url
    # Remove ?pgbouncer=true if present
    if '?pgbouncer=true' in url:
        url = url.replace('?pgbouncer=true', '')
    elif '&pgbouncer=true' in url:
        url = url.replace('&pgbouncer=true', '')
    # Parse and clean query parameters
    parsed = urlparse(url)
    if parsed.query:
        params = parse_qs(parsed.query)
        params.pop('pgbouncer', None)
        new_query = urlencode(params, doseq=True) if params else ''
        parsed = parsed._replace(query=new_query)
        url = urlunparse(parsed)
    return url

# Clean DATABASE_URL
clean_url = clean_database_url(settings.DATABASE_URL)

# Create engine
engine = create_engine(
    clean_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Bước 2.6: Tạo `app/core/security.py` - Security Utilities

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

## Bước 2.7: Tạo `app/core/exceptions.py` - Exception Handlers

```python
"""
Custom exception handlers
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation error",
            "errors": jsonable_encoder(exc.errors()),
        },
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
        },
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if request.app.debug else None,
        },
    )
```

## Bước 2.8: Tạo `app/core/logging_config.py` - Logging

```python
"""
Logging configuration
"""
import logging
import sys
from app.core.config import settings

def setup_logging():
    """Setup logging configuration"""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

---

# 🗄️ PHASE 3: TẠO MODELS (DATABASE TABLES)

## Bước 3.1: Tạo `app/models/__init__.py`

```python
from app.models.user import User, UserRole, UserOrganization
from app.models.role import Role, RolePermission
from app.models.permission import Permission
from app.models.organization import Organization
from app.models.media import Media
from app.models.product import Product, ProductApproval
from app.models.payment import Payment, PaymentTransaction
from app.models.content import Content
from app.models.complaint import Complaint, Review
from app.models.partner_contract import PartnerContract
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod
from app.models.category import Category
from app.models.region import Region

__all__ = [
    "User",
    "UserRole",
    "UserOrganization",
    "Role",
    "RolePermission",
    "Permission",
    "Organization",
    "Media",
    "Product",
    "ProductApproval",
    "Payment",
    "PaymentTransaction",
    "Content",
    "Complaint",
    "Review",
    "PartnerContract",
    "Order",
    "OrderItem",
    "OrderStatus",
    "PaymentMethod",
    "Category",
    "Region",
]
```

## Bước 3.2: Tạo `app/models/user.py` - User Model

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    gender = Column(String(50), nullable=True)
    activated = Column(Integer, default=1)  # 1 = active, 0 = inactive
    type = Column(String(50), nullable=True)  # consumer, producer, admin, etc.
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(String(255), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roles = relationship("UserRole", back_populates="user")
    organizations = relationship("UserOrganization", back_populates="user")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

class UserOrganization(Base):
    __tablename__ = "user_organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="organizations")
    organization = relationship("Organization", back_populates="users")
```

## Bước 3.3: Tạo `app/models/role.py` - Role Model

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("UserRole", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
```

## Bước 3.4: Tạo `app/models/permission.py` - Permission Model

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class PermissionType(str, enum.Enum):
    CATALOGUE = "CATALOGUE"
    MENU = "MENU"

class PermissionStatus(str, enum.Enum):
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("permissions.id"), nullable=True)
    name = Column(String(255), unique=True, nullable=False)
    label = Column(String(255), nullable=False)
    type = Column(SQLEnum(PermissionType), nullable=False)
    route = Column(String(255), nullable=True)
    status = Column(String(50), default="ENABLE")
    order = Column(Integer, default=0)
    icon = Column(String(255), nullable=True)
    component = Column(String(255), nullable=True)
    hide = Column(Boolean, default=False)
    hide_tab = Column(Boolean, default=False)
    frame_src = Column(String(500), nullable=True)
    new_feature = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Self-referential relationship
    parent = relationship("Permission", remote_side=[id], backref="children")
    roles = relationship("RolePermission", back_populates="permission")
```

## Bước 3.5: Tạo `app/models/organization.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("UserOrganization", back_populates="organization")
```

## Bước 3.6: Tạo `app/models/product.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ProductStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ProductLabel(str, enum.Enum):
    CLEAN_AGRICULTURE = "CLEAN_AGRICULTURE"
    TRADITIONAL_CRAFT = "TRADITIONAL_CRAFT"
    OCOP = "OCOP"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    producer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.PENDING)
    label = Column(String(50), nullable=True)
    images = Column(Text, nullable=True)  # JSON array of image URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    producer = relationship("User", foreign_keys=[producer_id])

class ProductApproval(Base):
    __tablename__ = "product_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(ProductStatus), nullable=False)
    notes = Column(Text, nullable=True)
    checked_description = Column(Boolean, default=False)
    checked_price = Column(Boolean, default=False)
    checked_images = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", foreign_keys=[product_id])
    approver = relationship("User", foreign_keys=[approver_id])
```

## Bước 3.7: Tạo các models còn lại

Tạo các file sau với nội dung tương tự:
- `app/models/payment.py` - Payment, PaymentTransaction
- `app/models/order.py` - Order, OrderItem, OrderStatus, PaymentMethod
- `app/models/content.py` - Content
- `app/models/complaint.py` - Complaint, Review
- `app/models/partner_contract.py` - PartnerContract
- `app/models/category.py` - Category
- `app/models/region.py` - Region
- `app/models/media.py` - Media

---

# 🔌 PHASE 4: TẠO API ENDPOINTS

## Bước 4.1: Tạo `app/api/__init__.py`

```python
# API package init
```

## Bước 4.2: Tạo `app/api/v1/__init__.py` - API Router

```python
from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    roles,
    permissions,
    organizations,
    dashboard,
    media,
    products,
    payments,
    content,
    complaints,
    contracts,
    stats,
    orders,
    categories,
    regions,
    mobile_app,
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# API routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/admin/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/admin/permissions", tags=["Permissions"])
api_router.include_router(organizations.router, prefix="/org", tags=["Organizations"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(media.router, prefix="/medias", tags=["Media"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])
api_router.include_router(stats.router, tags=["Stats"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(regions.router, prefix="/regions", tags=["Regions"])
api_router.include_router(mobile_app.router, prefix="/mobile", tags=["Mobile App"])
```

## Bước 4.3: Tạo `app/api/v1/auth.py` - Authentication API

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.role import Role, RolePermission
from app.models.permission import Permission
from pydantic import BaseModel, EmailStr, Field
import re

router = APIRouter()
security = HTTPBearer()

# ========== SCHEMAS ==========
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=255)
    gender: Optional[str] = None
    type: Optional[str] = "consumer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    recaptcha: Optional[str] = None

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[list] = None

# ========== DEPENDENCIES ==========
def get_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract Bearer token from Authorization header"""
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

def get_current_user(token: str = Depends(get_bearer_token), db: Session = Depends(get_db)):
    """Get current authenticated user from Bearer token"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = db.query(User).filter(User.id == int(user_id), User.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted",
        )
    
    if user.activated != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not activated",
        )
    
    return user

# ========== ENDPOINTS ==========
@router.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account"""
    # Check if email exists
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = User(
        email=register_data.email,
        password_hash=get_password_hash(register_data.password),
        name=register_data.name,
        gender=register_data.gender,
        type=register_data.type or "consumer",
        activated=1
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return StandardResponse(
        success=True,
        message="User registered successfully",
        data={"id": new_user.id, "email": new_user.email, "name": new_user.name}
    )

@router.post("/login", response_model=StandardResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - returns Bearer token"""
    user = db.query(User).filter(
        User.email == login_data.email,
        User.deleted_at.is_(None)
    ).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if user.activated != 1:
        raise HTTPException(status_code=403, detail="Account not activated")
    
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=expires_delta
    )
    
    expires_at = datetime.utcnow() + expires_delta
    
    return StandardResponse(
        success=True,
        message="Login successful",
        data={
            "api_token": access_token,
            "token_type": "Bearer",
            "expires_at": expires_at.isoformat() + "Z",
            "user": {"id": user.id, "email": user.email, "name": user.name, "type": user.type}
        }
    )

@router.get("/me", response_model=StandardResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user info with roles and permissions"""
    # Get roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    roles_data = []
    permission_ids = set()
    
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles_data.append({"id": role.id, "role_name": role.role_name})
            # Get permissions
            role_perms = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
            for rp in role_perms:
                permission_ids.add(rp.permission_id)
    
    # Get permissions
    permissions_data = []
    for perm_id in permission_ids:
        perm = db.query(Permission).filter(Permission.id == perm_id).first()
        if perm:
            permissions_data.append({
                "id": perm.id, "name": perm.name, "label": perm.label,
                "type": perm.type, "route": perm.route, "icon": perm.icon
            })
    
    return StandardResponse(
        success=True,
        message="User information retrieved successfully",
        data={
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "type": current_user.type,
            "roles": roles_data,
            "permissions": permissions_data
        }
    )

@router.post("/logout", response_model=StandardResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout - client should remove token"""
    return StandardResponse(success=True, message="Logged out successfully")

@router.post("/refresh", response_model=StandardResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token"""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email},
        expires_delta=expires_delta
    )
    
    return StandardResponse(
        success=True,
        message="Token refreshed",
        data={"api_token": access_token, "token_type": "Bearer"}
    )
```

## Bước 4.4: Tạo các API endpoints khác

Tạo các file endpoint tương tự cho:
- `app/api/v1/users.py` - CRUD Users
- `app/api/v1/roles.py` - CRUD Roles
- `app/api/v1/permissions.py` - CRUD Permissions
- `app/api/v1/organizations.py` - CRUD Organizations
- `app/api/v1/products.py` - Products management
- `app/api/v1/payments.py` - Payments
- `app/api/v1/orders.py` - Orders
- `app/api/v1/content.py` - Content management
- `app/api/v1/complaints.py` - Complaints & Reviews
- `app/api/v1/contracts.py` - Partner contracts
- `app/api/v1/categories.py` - Categories
- `app/api/v1/regions.py` - Regions
- `app/api/v1/media.py` - Media upload
- `app/api/v1/dashboard.py` - Dashboard APIs
- `app/api/v1/stats.py` - Statistics
- `app/api/v1/mobile_app.py` - Mobile App APIs

---

# 🎯 PHASE 5: TẠO MAIN.PY VÀ CHẠY ỨNG DỤNG

## Bước 5.1: Tạo `app/main.py` - Entry Point

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1 import api_router
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "CMS API", "version": settings.APP_VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Bước 5.2: Chạy ứng dụng

```bash
# Chạy development server
python run.py

# Hoặc sử dụng uvicorn trực tiếp
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Truy cập:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

# 🗃️ PHASE 6: DATABASE MIGRATIONS VỚI ALEMBIC

## Bước 6.1: Khởi tạo Alembic

```bash
alembic init alembic
```

## Bước 6.2: Cấu hình `alembic.ini`

Sửa dòng `sqlalchemy.url`:
```ini
sqlalchemy.url = postgresql://...
```

## Bước 6.3: Cập nhật `alembic/env.py`

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.database import Base
from app.models import *  # Import all models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Bước 6.4: Tạo và chạy migrations

```bash
# Tạo migration
alembic revision --autogenerate -m "Initial migration"

# Chạy migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

# 🚀 PHASE 7: DEPLOYMENT

## Bước 7.1: Tạo `Procfile` cho Railway/Heroku

```
web: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## Bước 7.2: Tạo `runtime.txt`

```
python-3.11.7
```

## Bước 7.3: Tạo `railway.json`

```json
{
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
        "builder": "NIXPACKS"
    },
    "deploy": {
        "numReplicas": 1,
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 10
    }
}
```

---

# ✅ CHECKLIST HOÀN THÀNH

- [ ] Phase 1: Khởi tạo dự án
  - [ ] Tạo thư mục và venv
  - [ ] Cài đặt requirements.txt
  - [ ] Tạo .env
  - [ ] Tạo run.py

- [ ] Phase 2: Core Modules
  - [ ] config.py
  - [ ] database.py
  - [ ] security.py
  - [ ] exceptions.py
  - [ ] logging_config.py

- [ ] Phase 3: Models
  - [ ] user.py
  - [ ] role.py
  - [ ] permission.py
  - [ ] organization.py
  - [ ] product.py
  - [ ] Các models còn lại

- [ ] Phase 4: API Endpoints
  - [ ] auth.py
  - [ ] users.py
  - [ ] roles.py
  - [ ] permissions.py
  - [ ] Các endpoints còn lại

- [ ] Phase 5: Main.py và chạy thử

- [ ] Phase 6: Alembic migrations

- [ ] Phase 7: Deployment configs

---

**Lưu ý:** Tài liệu này cung cấp code mẫu cơ bản. Để xem code đầy đủ của từng file, hãy tham khảo trực tiếp trong thư mục dự án hiện tại.
