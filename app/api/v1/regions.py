from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.region import Region
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field
import re

router = APIRouter()


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================

class RegionResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    image: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RegionListResponse(BaseModel):
    data: List[RegionResponse]
    meta: dict


class CreateRegionRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    image: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    order: int = 0
    is_active: bool = True


class UpdateRegionRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    image: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name"""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


# ==============================================================================
# CRUD ENDPOINTS
# ==============================================================================

@router.get("", response_model=RegionListResponse)
async def get_regions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of regions"""
    query = db.query(Region)
    
    if is_active is not None:
        query = query.filter(Region.is_active == is_active)
    if search:
        query = query.filter(Region.name.ilike(f"%{search}%"))
    
    total = query.count()
    skip = (page - 1) * limit
    regions = query.order_by(Region.order, Region.name).offset(skip).limit(limit).all()
    
    return RegionListResponse(
        data=[RegionResponse.from_orm(r) for r in regions],
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    )


@router.get("/{region_id}", response_model=RegionResponse)
async def get_region_by_id(
    region_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get region by ID"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    return RegionResponse.from_orm(region)


@router.post("", response_model=RegionResponse)
async def create_region(
    region_data: CreateRegionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new region"""
    # Check if name already exists
    existing = db.query(Region).filter(Region.name == region_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Region name already exists")
    
    # Generate slug
    slug = generate_slug(region_data.name)
    
    # Ensure slug is unique
    existing_slug = db.query(Region).filter(Region.slug == slug).first()
    if existing_slug:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    new_region = Region(
        name=region_data.name,
        slug=slug,
        description=region_data.description,
        image=region_data.image,
        latitude=region_data.latitude,
        longitude=region_data.longitude,
        order=region_data.order,
        is_active=region_data.is_active
    )
    
    db.add(new_region)
    db.commit()
    db.refresh(new_region)
    
    return RegionResponse.from_orm(new_region)


@router.put("/{region_id}", response_model=RegionResponse)
async def update_region(
    region_id: int,
    region_data: UpdateRegionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a region"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    update_data = region_data.dict(exclude_unset=True)
    
    # If name is being updated, update slug too
    if "name" in update_data:
        new_slug = generate_slug(update_data["name"])
        existing_slug = db.query(Region).filter(
            Region.slug == new_slug,
            Region.id != region_id
        ).first()
        if existing_slug:
            new_slug = f"{new_slug}-{int(datetime.utcnow().timestamp())}"
        update_data["slug"] = new_slug
    
    for key, value in update_data.items():
        setattr(region, key, value)
    
    db.commit()
    db.refresh(region)
    
    return RegionResponse.from_orm(region)


@router.delete("/{region_id}")
async def delete_region(
    region_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a region"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    db.delete(region)
    db.commit()
    
    return {"success": True, "message": "Region deleted successfully"}
