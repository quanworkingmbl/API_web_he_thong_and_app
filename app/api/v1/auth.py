from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.role import Role
from app.models.permission import Permission, RolePermission
from pydantic import BaseModel, EmailStr

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    recaptcha: Optional[str] = None

class TokenResponse(BaseModel):
    api_token: str
    expires_at: str

class UserInfoResponse(BaseModel):
    id: int
    email: str
    name: str
    gender: Optional[str]
    activated: int
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: str
    updated_at: Optional[str]
    deleted_by: Optional[str]
    deleted_at: Optional[str]
    type: Optional[str]
    roles: list
    permissions: list
    source_providers: list

    class Config:
        from_attributes = True

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from token"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

@router.post("/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint"""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if user.activated != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not activated",
        )
    
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=expires_delta
    )
    
    from datetime import datetime
    expires_at = datetime.utcnow() + expires_delta
    
    return {
        "api_token": access_token,
        "expires_at": expires_at.isoformat()
    }

@router.post("/info")
async def get_user_info(
    email: str,
    api_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get user info with roles and permissions"""
    # Try to get user from token first, then from email
    user = None
    
    # If api_token provided, decode it to get user_id
    if api_token:
        payload = decode_access_token(api_token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id)).first()
    
    # If no user from token, try email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    roles_data = []
    permission_ids = set()
    
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles_data.append({
                "id": role.id,
                "role_name": role.role_name,
                "description": role.description
            })
            # Get permissions for this role
            role_permissions = db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).all()
            for rp in role_permissions:
                permission_ids.add(rp.permission_id)
    
    # Get all permissions
    permissions_data = []
    for perm_id in permission_ids:
        perm = db.query(Permission).filter(Permission.id == perm_id).first()
        if perm:
            permissions_data.append({
                "id": perm.id,
                "parent_id": perm.parent_id,
                "name": perm.name,
                "label": perm.label,
                "type": perm.type,
                "route": perm.route,
                "status": perm.status,
                "order": perm.order,
                "icon": perm.icon,
                "component": perm.component,
                "hide": perm.hide,
                "hideTab": perm.hide_tab,
                "frameSrc": perm.frame_src,
                "newFeature": perm.new_feature
            })
    
    return {
        "status": 200,
        "data": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "gender": user.gender,
            "activated": user.activated,
            "created_by": user.created_by,
            "updated_by": user.updated_by,
            "created_at": user.created_at.isoformat() if user.created_at else "",
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "deleted_by": user.deleted_by,
            "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None,
            "type": user.type,
            "roles": roles_data,
            "permissions": permissions_data,
            "source_providers": []
        }
    }

@router.get("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (client should remove token)"""
    return {"message": "Logged out successfully"}

@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Refresh access token"""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email},
        expires_delta=expires_delta
    )
    
    from datetime import datetime
    expires_at = datetime.utcnow() + expires_delta
    
    return {
        "api_token": access_token,
        "expires_at": expires_at.isoformat()
    }

