from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.category import Category
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.permissions import check_category_manage_access
from pydantic import BaseModel, Field
import re

router = APIRouter()


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[int] = None
    order: Optional[int] = 0        # Có thể NULL trong DB với data cũ
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    data: List[CategoryResponse]
    meta: dict


class CreateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[int] = None
    order: int = 0
    is_active: bool = True


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name"""
    # Simple slug generation - lowercase, replace spaces with hyphens
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


# ==============================================================================
# CRUD ENDPOINTS
# ==============================================================================

@router.get("", response_model=CategoryListResponse)
async def get_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of categories"""
    query = db.query(Category)
    
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    elif parent_id is None and Query(None):
        # Get root categories by default
        pass
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))
    
    total = query.count()
    skip = (page - 1) * limit
    categories = query.order_by(Category.order, Category.name).offset(skip).limit(limit).all()
    
    return CategoryListResponse(
        data=[CategoryResponse.from_orm(c) for c in categories],
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get category by ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return CategoryResponse.from_orm(category)


@router.post("", response_model=CategoryResponse)
async def create_category(
    category_data: CreateCategoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category"""
    check_category_manage_access(current_user)

    # Check if name already exists
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    # Generate slug
    slug = generate_slug(category_data.name)
    
    # Ensure slug is unique
    existing_slug = db.query(Category).filter(Category.slug == slug).first()
    if existing_slug:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    # Validate parent_id if provided
    if category_data.parent_id:
        parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    new_category = Category(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        icon=category_data.icon,
        image=category_data.image,
        parent_id=category_data.parent_id,
        order=category_data.order,
        is_active=category_data.is_active
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return CategoryResponse.from_orm(new_category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: UpdateCategoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a category"""
    check_category_manage_access(current_user)

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_data.dict(exclude_unset=True)
    
    # If name is being updated, update slug too
    if "name" in update_data:
        new_slug = generate_slug(update_data["name"])
        existing_slug = db.query(Category).filter(
            Category.slug == new_slug,
            Category.id != category_id
        ).first()
        if existing_slug:
            new_slug = f"{new_slug}-{int(datetime.utcnow().timestamp())}"
        update_data["slug"] = new_slug
    
    # Validate parent_id if provided
    if "parent_id" in update_data and update_data["parent_id"]:
        if update_data["parent_id"] == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")
        parent = db.query(Category).filter(Category.id == update_data["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    
    return CategoryResponse.from_orm(category)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a category"""
    check_category_manage_access(current_user)

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has children
    children = db.query(Category).filter(Category.parent_id == category_id).count()
    if children > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category with {children} subcategories. Delete subcategories first."
        )
    
    db.delete(category)
    db.commit()
    
    return {"success": True, "message": "Category deleted successfully"}
