from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    gender: Optional[str]
    activated: int
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

