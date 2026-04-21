from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.role import Role
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.permissions import check_role_manage_access
from pydantic import BaseModel

router = APIRouter()

class RoleResponse(BaseModel):
    id: int
    role_name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class RolesListResponse(BaseModel):
    data: List[RoleResponse]
    meta: dict

class CreateRoleRequest(BaseModel):
    role_name: str
    description: Optional[str] = None

class UpdateRoleRequest(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None

@router.get("", response_model=RolesListResponse)
async def get_roles(
    limit: int = Query(50, ge=1, le=500),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of roles"""
    query = db.query(Role)
    
    if search:
        query = query.filter(Role.role_name.ilike(f"%{search}%"))
    
    total = query.count()
    offset = (page - 1) * limit
    roles = query.offset(offset).limit(limit).all()
    
    return RolesListResponse(
        data=[RoleResponse.from_orm(role) for role in roles],
        meta={
            "total": total,
            "limit": limit,
            "current_page": page,
            "total_pages": (total + limit - 1) // limit
        }
    )

@router.post("", response_model=RoleResponse)
async def create_role(
    role_data: CreateRoleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new role"""
    check_role_manage_access(current_user)

    existing_role = db.query(Role).filter(Role.role_name == role_data.role_name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    new_role = Role(
        role_name=role_data.role_name,
        description=role_data.description
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return RoleResponse.from_orm(new_role)

@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: UpdateRoleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a role"""
    check_role_manage_access(current_user)

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    update_data = role_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(role, key, value)
    
    db.commit()
    db.refresh(role)
    
    return RoleResponse.from_orm(role)

@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a role"""
    check_role_manage_access(current_user)

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db.delete(role)
    db.commit()
    
    return {"message": "Role deleted successfully"}

