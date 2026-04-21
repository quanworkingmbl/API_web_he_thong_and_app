from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.core.database import get_db
from app.models.user import User, UserStatus
from app.api.v1.auth import get_current_user
from app.core.permissions import check_user_manage_access
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    gender: Optional[str]
    activated: int
    status: str
    status_reason: Optional[str]
    status_expire_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_by: Optional[str]
    deleted_at: Optional[datetime]
    type: Optional[str]

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    data: List[UserResponse]
    meta: dict

class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    gender: Optional[str] = None
    type: Optional[str] = None
    activated: int = 1

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    type: Optional[str] = None
    activated: Optional[int] = None

class UpdateUserStatusRequest(BaseModel):
    status: str = Field(..., description="User status: ACTIVE, SUSPENDED, BANNED")
    status_reason: Optional[str] = Field(None, description="Reason for status change")
    status_expire_at: Optional[datetime] = Field(None, description="Expiration time for SUSPENDED status")


@router.get("", response_model=UserListResponse)
async def get_users(
    model: Optional[str] = Query(None),
    activated: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of users"""
    check_user_manage_access(current_user)

    query = db.query(User).filter(User.deleted_at.is_(None))
    
    if model:
        query = query.filter(User.type == model)
    if activated is not None:
        query = query.filter(User.activated == activated)
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()
    
    return UserListResponse(
        data=[UserResponse.from_orm(user) for user in users],
        meta={
            "total": total,
            "limit": limit,
            "current_page": page,
            "total_pages": (total + limit - 1) // limit
        }
    )

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: CreateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    check_user_manage_access(current_user)

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    from app.core.security import get_password_hash
    
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        gender=user_data.gender,
        type=user_data.type,
        activated=user_data.activated,
        created_by=current_user.email
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user"""
    check_user_manage_access(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_by = current_user.email
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


# ==============================================================================
# NEW ENDPOINTS
# ==============================================================================

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    check_user_manage_access(current_user)

    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a user
    Không xóa vĩnh viễn, chỉ đánh dấu deleted_at
    """
    check_user_manage_access(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user.deleted_at = datetime.utcnow()
    user.deleted_by = current_user.email
    
    db.commit()
    
    return {"success": True, "message": "User deleted successfully"}


@router.put("/{user_id}/activate")
async def activate_user(
    user_id: int,
    activated: int = Query(..., ge=0, le=1, description="1 = active, 0 = inactive"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate a user
    activated = 1: Kích hoạt
    activated = 0: Vô hiệu hóa
    """
    check_user_manage_access(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.activated = activated
    user.updated_by = current_user.email
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    status_text = "activated" if activated == 1 else "deactivated"
    return {"success": True, "message": f"User {status_text} successfully"}


@router.post("/{user_id}/roles")
async def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign roles to a user
    Xóa tất cả roles cũ và gán roles mới
    """
    check_user_manage_access(current_user)

    from app.models.user import UserRole
    from app.models.role import Role
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate role_ids exist
    existing_roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    existing_role_ids = [r.id for r in existing_roles]
    
    invalid_ids = set(role_ids) - set(existing_role_ids)
    if invalid_ids:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role IDs: {list(invalid_ids)}"
        )
    
    # Remove existing roles
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    
    # Assign new roles
    for role_id in role_ids:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
    
    db.commit()
    
    return {
        "success": True, 
        "message": f"Assigned {len(role_ids)} roles to user",
        "role_ids": role_ids
    }


@router.get("/{user_id}/roles")
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all roles assigned to a user"""
    check_user_manage_access(current_user)

    from app.models.user import UserRole
    from app.models.role import Role
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    
    return {
        "success": True,
        "data": [
            {"id": role.id, "role_name": role.role_name, "description": role.description}
            for role in roles
        ]
    }


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: UpdateUserStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user account status (ACTIVE, SUSPENDED, BANNED)
    Admin only endpoint
    Prevents self-ban/self-suspend
    """
    check_user_manage_access(current_user)

    # Validate status value
    try:
        new_status = UserStatus[status_data.status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: ACTIVE, SUSPENDED, BANNED"
        )
    
    # Find target user
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-ban/self-suspend
    if user.id == current_user.id and new_status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=400, 
            detail="You cannot suspend or ban yourself"
        )
    
    # Validate SUSPENDED requires expire time
    if new_status == UserStatus.SUSPENDED and not status_data.status_expire_at:
        raise HTTPException(
            status_code=400,
            detail="status_expire_at is required for SUSPENDED status (or use BANNED for permanent)"
        )
    
    # Update status
    user.status = new_status
    user.status_reason = status_data.status_reason
    user.status_expire_at = status_data.status_expire_at if new_status == UserStatus.SUSPENDED else None
    user.updated_by = current_user.email
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "message": f"User status updated to {new_status.value}",
        "data": {
            "user_id": user.id,
            "status": user.status.value,
            "status_reason": user.status_reason,
            "status_expire_at": user.status_expire_at.isoformat() if user.status_expire_at else None
        }
    }

