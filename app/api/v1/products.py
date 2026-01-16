from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.product import Product, ProductApproval, ProductStatus, ProductLabel
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter()

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    producer_id: int
    status: str
    label: Optional[str]
    images: Optional[str]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True

class ProductApprovalRequest(BaseModel):
    product_id: int
    status: str  # APPROVED, REJECTED
    notes: Optional[str] = None
    checked_description: bool = False
    checked_price: bool = False
    checked_images: bool = False

@router.get("", response_model=List[ProductResponse])
async def get_products(
    status: Optional[str] = Query(None),
    producer_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of products"""
    query = db.query(Product)
    
    if status:
        query = query.filter(Product.status == status)
    if producer_id:
        query = query.filter(Product.producer_id == producer_id)
    
    products = query.all()
    return [ProductResponse.from_orm(p) for p in products]

@router.post("/{product_id}/approve")
async def approve_product(
    product_id: int,
    approval_data: ProductApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update product status
    product.status = approval_data.status
    
    # Create approval record
    approval = ProductApproval(
        product_id=product_id,
        approver_id=current_user.id,
        status=approval_data.status,
        notes=approval_data.notes,
        checked_description=approval_data.checked_description,
        checked_price=approval_data.checked_price,
        checked_images=approval_data.checked_images
    )
    
    db.add(approval)
    db.commit()
    
    return {"message": f"Product {approval_data.status.lower()} successfully"}

@router.put("/{product_id}/label")
async def update_product_label(
    product_id: int,
    label: str,  # CLEAN_AGRICULTURE, TRADITIONAL_CRAFT, OCOP
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update product label"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.label = label
    db.commit()
    
    return {"message": "Product label updated successfully"}

