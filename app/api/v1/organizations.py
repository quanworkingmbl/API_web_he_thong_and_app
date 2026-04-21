from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.organization import Organization
from app.models.user import User, UserOrganization
from app.api.v1.auth import get_current_user
from app.core.permissions import check_organization_manage_access
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================

class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: str
    updated_at: Optional[str]
    member_count: int = 0

    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    data: List[OrganizationResponse]
    meta: dict


class CreateOrganizationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None


class MemberResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    user_type: Optional[str]
    joined_at: datetime


# ==============================================================================
# CRUD ENDPOINTS
# ==============================================================================

@router.get("", response_model=OrganizationListResponse)
async def get_organizations(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of organizations (Hợp tác xã, Làng nghề thủ công)"""
    query = db.query(Organization)
    
    if search:
        query = query.filter(Organization.name.ilike(f"%{search}%"))
    
    total = query.count()
    skip = (page - 1) * limit
    organizations = query.order_by(Organization.name).offset(skip).limit(limit).all()
    
    org_list = []
    for org in organizations:
        # Count members
        member_count = db.query(UserOrganization).filter(
            UserOrganization.organization_id == org.id
        ).count()
        
        org_list.append(OrganizationResponse(
            id=org.id,
            name=org.name,
            description=org.description,
            created_at=org.created_at.isoformat() if org.created_at else "",
            updated_at=org.updated_at.isoformat() if org.updated_at else None,
            member_count=member_count
        ))
    
    return OrganizationListResponse(
        data=org_list,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization_by_id(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization by ID"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    member_count = db.query(UserOrganization).filter(
        UserOrganization.organization_id == org_id
    ).count()
    
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        description=org.description,
        created_at=org.created_at.isoformat() if org.created_at else "",
        updated_at=org.updated_at.isoformat() if org.updated_at else None,
        member_count=member_count
    )


@router.post("", response_model=OrganizationResponse)
async def create_organization(
    org_data: CreateOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization"""
    check_organization_manage_access(current_user)

    # Check if name already exists
    existing = db.query(Organization).filter(Organization.name == org_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization name already exists")
    
    new_org = Organization(
        name=org_data.name,
        description=org_data.description
    )
    
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    return OrganizationResponse(
        id=new_org.id,
        name=new_org.name,
        description=new_org.description,
        created_at=new_org.created_at.isoformat() if new_org.created_at else "",
        updated_at=None,
        member_count=0
    )


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: int,
    org_data: UpdateOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an organization"""
    check_organization_manage_access(current_user)

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    update_data = org_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)
    
    db.commit()
    db.refresh(org)
    
    member_count = db.query(UserOrganization).filter(
        UserOrganization.organization_id == org_id
    ).count()
    
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        description=org.description,
        created_at=org.created_at.isoformat() if org.created_at else "",
        updated_at=org.updated_at.isoformat() if org.updated_at else None,
        member_count=member_count
    )


@router.delete("/{org_id}")
async def delete_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an organization"""
    check_organization_manage_access(current_user)

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if organization has members
    member_count = db.query(UserOrganization).filter(
        UserOrganization.organization_id == org_id
    ).count()
    
    if member_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete organization with {member_count} members. Remove members first."
        )
    
    db.delete(org)
    db.commit()
    
    return {"success": True, "message": "Organization deleted successfully"}


# ==============================================================================
# MEMBER MANAGEMENT ENDPOINTS
# ==============================================================================

@router.get("/{org_id}/members")
async def get_organization_members(
    org_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get members of an organization"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    query = db.query(UserOrganization).filter(UserOrganization.organization_id == org_id)
    total = query.count()
    skip = (page - 1) * limit
    memberships = query.offset(skip).limit(limit).all()
    
    members = []
    for m in memberships:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            members.append(MemberResponse(
                id=m.id,
                user_id=user.id,
                user_name=user.name,
                user_email=user.email,
                user_type=user.type,
                joined_at=m.created_at
            ))
    
    return {
        "success": True,
        "data": [m.dict() for m in members],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.post("/{org_id}/members")
async def add_member_to_organization(
    org_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to an organization"""
    check_organization_manage_access(current_user)

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Check if user is already a member
    existing = db.query(UserOrganization).filter(
        UserOrganization.organization_id == org_id,
        UserOrganization.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this organization")
    
    membership = UserOrganization(
        organization_id=org_id,
        user_id=user_id
    )
    
    db.add(membership)
    db.commit()
    
    return {"success": True, "message": f"User {user.name} added to organization"}


@router.delete("/{org_id}/members/{user_id}")
async def remove_member_from_organization(
    org_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from an organization"""
    check_organization_manage_access(current_user)

    membership = db.query(UserOrganization).filter(
        UserOrganization.organization_id == org_id,
        UserOrganization.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    db.delete(membership)
    db.commit()
    
    return {"success": True, "message": "Member removed from organization"}
