from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.product import Product, ProductApproval, ProductStatus, ProductLabel
from app.models.category import Category
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel, Field
from decimal import Decimal

router = APIRouter()


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    producer_id: int
    producer_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    status: str
    label: Optional[str]
    images: Optional[str]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    data: List[ProductResponse]
    meta: dict


class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    producer_id: int
    category_id: Optional[int] = None
    label: Optional[str] = None
    images: Optional[str] = None  # JSON array of image URLs


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    category_id: Optional[int] = None
    label: Optional[str] = None
    images: Optional[str] = None


class ProductApprovalRequest(BaseModel):
    product_id: int
    status: str  # APPROVED, REJECTED
    notes: Optional[str] = None
    checked_description: bool = False
    checked_price: bool = False
    checked_images: bool = False


# ==============================================================================
# LIST & GET ENDPOINTS
# ==============================================================================

@router.get("", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    producer_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    label: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get list of products with pagination and filters
    """
    query = db.query(Product)

    if status:
        query = query.filter(Product.status == status)
    if producer_id:
        query = query.filter(Product.producer_id == producer_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if label:
        query = query.filter(Product.label == label)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    total = query.count()
    skip = (page - 1) * limit
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    # Get producer names and category names
    product_list = []
    for p in products:
        producer = db.query(User).filter(User.id == p.producer_id).first()
        category = db.query(Category).filter(Category.id == p.category_id).first() if p.category_id else None
        product_list.append(ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            producer_id=p.producer_id,
            producer_name=producer.name if producer else None,
            category_id=p.category_id,
            category_name=category.name if category else None,
            status=p.status.value if hasattr(p.status, 'value') else str(p.status),
            label=p.label,
            images=p.images,
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else None
        ))
    
    return ProductListResponse(
        data=product_list,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get product details by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    producer = db.query(User).filter(User.id == product.producer_id).first()
    category = db.query(Category).filter(Category.id == product.category_id).first() if product.category_id else None

    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        producer_id=product.producer_id,
        producer_name=producer.name if producer else None,
        category_id=product.category_id,
        category_name=category.name if category else None,
        status=product.status.value if hasattr(product.status, 'value') else str(product.status),
        label=product.label,
        images=product.images,
        created_at=product.created_at.isoformat() if product.created_at else "",
        updated_at=product.updated_at.isoformat() if product.updated_at else None
    )


# ==============================================================================
# CREATE, UPDATE, DELETE ENDPOINTS
# ==============================================================================

@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: CreateProductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo sản phẩm mới.
    - **Admin**: có thể tạo cho bất kỳ producer nào (truyền `producer_id` trong body).
    - **Seller/Producer**: `producer_id` tự động gán = `current_user.id`, bỏ qua giá trị body.
    """
    is_admin = (current_user.type == "admin")

    if is_admin:
        # Admin chỉ định producer tùy ý
        actual_producer_id = product_data.producer_id
    else:
        # Seller/Producer chỉ tạo sản phẩm cho chính mình
        actual_producer_id = current_user.id

    producer = db.query(User).filter(User.id == actual_producer_id).first()
    if not producer:
        raise HTTPException(status_code=400, detail="Producer not found")

    # Validate category if provided
    if product_data.category_id:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        producer_id=actual_producer_id,
        category_id=product_data.category_id,
        status=ProductStatus.PENDING,
        label=product_data.label,
        images=product_data.images,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    category = db.query(Category).filter(Category.id == new_product.category_id).first() if new_product.category_id else None

    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        description=new_product.description,
        price=new_product.price,
        producer_id=new_product.producer_id,
        producer_name=producer.name,
        category_id=new_product.category_id,
        category_name=category.name if category else None,
        status=new_product.status.value if hasattr(new_product.status, 'value') else str(new_product.status),
        label=new_product.label,
        images=new_product.images,
        created_at=new_product.created_at.isoformat() if new_product.created_at else "",
        updated_at=None
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: UpdateProductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật sản phẩm.
    - **Admin**: cập nhật bất kỳ sản phẩm nào.
    - **Seller/Producer**: chỉ được cập nhật sản phẩm của **chính mình** (ownership check).
    """
    is_admin = (current_user.type == "admin")

    query = db.query(Product).filter(Product.id == product_id)
    if not is_admin:
        # Seller chỉ sửa sản phẩm của mình
        query = query.filter(Product.producer_id == current_user.id)

    product = query.first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found" if is_admin else "Sản phẩm không tồn tại hoặc bạn không có quyền chỉnh sửa"
        )

    # Validate category if provided in update
    if product_data.category_id is not None:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    update_data = product_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    producer = db.query(User).filter(User.id == product.producer_id).first()
    category = db.query(Category).filter(Category.id == product.category_id).first() if product.category_id else None

    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        producer_id=product.producer_id,
        producer_name=producer.name if producer else None,
        category_id=product.category_id,
        category_name=category.name if category else None,
        status=product.status.value if hasattr(product.status, 'value') else str(product.status),
        label=product.label,
        images=product.images,
        created_at=product.created_at.isoformat() if product.created_at else "",
        updated_at=product.updated_at.isoformat() if product.updated_at else None
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    return {"success": True, "message": "Product deleted successfully"}


# ==============================================================================
# APPROVAL & LABEL ENDPOINTS
# ==============================================================================

@router.post("/{product_id}/approve")
async def approve_product(
    product_id: int,
    approval_data: ProductApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject a product"""
    # Permission check: chỉ admin hoặc content_manager mới được duyệt sản phẩm
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Không có quyền duyệt sản phẩm. Yêu cầu role: admin hoặc content_manager")
    
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
    
    return {"success": True, "message": f"Product {approval_data.status.lower()} successfully"}


@router.put("/{product_id}/label")
async def update_product_label(
    product_id: int,
    label: str = Query(..., pattern="^(CLEAN_AGRICULTURE|TRADITIONAL_CRAFT|OCOP)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update product label
    Labels: CLEAN_AGRICULTURE, TRADITIONAL_CRAFT, OCOP
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.label = label
    db.commit()
    
    return {"success": True, "message": "Product label updated successfully"}
