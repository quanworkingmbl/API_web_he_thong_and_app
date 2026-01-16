from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.permission import Permission
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class PermissionResponse(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    label: str
    type: str
    route: Optional[str]
    status: Optional[str]
    order: Optional[int]
    icon: Optional[str]
    component: Optional[str]
    hide: Optional[bool]
    hideTab: Optional[bool]
    frameSrc: Optional[str]
    newFeature: Optional[bool]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True

class PermissionsListResponse(BaseModel):
    data: List[PermissionResponse]
    meta: dict

class CreatePermissionRequest(BaseModel):
    parent_id: Optional[int] = None
    name: str
    label: str
    type: str
    route: Optional[str] = None
    status: Optional[str] = "ENABLE"
    order: Optional[int] = 0
    icon: Optional[str] = None
    component: Optional[str] = None
    hide: Optional[bool] = False
    hide_tab: Optional[bool] = False
    frame_src: Optional[str] = None
    new_feature: Optional[bool] = False

class UpdatePermissionRequest(BaseModel):
    parent_id: Optional[int] = None
    name: Optional[str] = None
    label: Optional[str] = None
    type: Optional[str] = None
    route: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None
    icon: Optional[str] = None
    component: Optional[str] = None
    hide: Optional[bool] = None
    hide_tab: Optional[bool] = None
    frame_src: Optional[str] = None
    new_feature: Optional[bool] = None

@router.get("", response_model=PermissionsListResponse)
async def get_permissions(
    limit: int = Query(50, ge=1, le=500),
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of permissions"""
    query = db.query(Permission)
    
    if search:
        query = query.filter(
            Permission.name.ilike(f"%{search}%") |
            Permission.label.ilike(f"%{search}%")
        )
    
    total = query.count()
    offset = (page - 1) * limit
    permissions = query.offset(offset).limit(limit).all()
    
    return PermissionsListResponse(
        data=[PermissionResponse(
            id=p.id,
            parent_id=p.parent_id,
            name=p.name,
            label=p.label,
            type=p.type.value if hasattr(p.type, 'value') else str(p.type),
            route=p.route,
            status=p.status,
            order=p.order,
            icon=p.icon,
            component=p.component,
            hide=p.hide,
            hideTab=p.hide_tab,
            frameSrc=p.frame_src,
            newFeature=p.new_feature,
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else None
        ) for p in permissions],
        meta={
            "total": total,
            "limit": limit,
            "current_page": page,
            "total_pages": (total + limit - 1) // limit
        }
    )

@router.post("", response_model=PermissionResponse)
async def create_permission(
    permission_data: CreatePermissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new permission"""
    existing_permission = db.query(Permission).filter(Permission.name == permission_data.name).first()
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission name already exists")
    
    new_permission = Permission(
        parent_id=permission_data.parent_id,
        name=permission_data.name,
        label=permission_data.label,
        type=permission_data.type,
        route=permission_data.route,
        status=permission_data.status,
        order=permission_data.order,
        icon=permission_data.icon,
        component=permission_data.component,
        hide=permission_data.hide,
        hide_tab=permission_data.hide_tab,
        frame_src=permission_data.frame_src,
        new_feature=permission_data.new_feature
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return PermissionResponse(
        id=new_permission.id,
        parent_id=new_permission.parent_id,
        name=new_permission.name,
        label=new_permission.label,
        type=new_permission.type.value if hasattr(new_permission.type, 'value') else str(new_permission.type),
        route=new_permission.route,
        status=new_permission.status,
        order=new_permission.order,
        icon=new_permission.icon,
        component=new_permission.component,
        hide=new_permission.hide,
        hideTab=new_permission.hide_tab,
        frameSrc=new_permission.frame_src,
        newFeature=new_permission.new_feature,
        created_at=new_permission.created_at.isoformat() if new_permission.created_at else "",
        updated_at=new_permission.updated_at.isoformat() if new_permission.updated_at else None
    )

@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: UpdatePermissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a permission"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    update_data = permission_data.dict(exclude_unset=True)
    # Convert hide_tab to hideTab for database
    if "hide_tab" in update_data:
        update_data["hide_tab"] = update_data.pop("hide_tab")
    
    for key, value in update_data.items():
        setattr(permission, key, value)
    
    db.commit()
    db.refresh(permission)
    
    return PermissionResponse(
        id=permission.id,
        parent_id=permission.parent_id,
        name=permission.name,
        label=permission.label,
        type=permission.type.value if hasattr(permission.type, 'value') else str(permission.type),
        route=permission.route,
        status=permission.status,
        order=permission.order,
        icon=permission.icon,
        component=permission.component,
        hide=permission.hide,
        hideTab=permission.hide_tab,
        frameSrc=permission.frame_src,
        newFeature=permission.new_feature,
        created_at=permission.created_at.isoformat() if permission.created_at else "",
        updated_at=permission.updated_at.isoformat() if permission.updated_at else None
    )

@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a permission"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db.delete(permission)
    db.commit()
    
    return {"message": "Permission deleted successfully"}

