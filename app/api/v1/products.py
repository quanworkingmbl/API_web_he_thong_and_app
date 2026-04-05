from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.product import Product, ProductApproval, ProductStatus, ProductLabel, ProductPriceLog
from app.models.category import Category
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.core.permissions import check_product_label_access, check_seller_kyc_verified
from pydantic import BaseModel, Field, validator
from decimal import Decimal
import json

router = APIRouter()

# ==============================================================================
# CONSTANTS FOR VALIDATION
# ==============================================================================

MIN_DESCRIPTION_LENGTH = 50
MIN_IMAGES_COUNT = 1
MAX_PRICE = Decimal("100000000")  # 100 triệu VND
MIN_PRICE = Decimal("1000")  # 1000 VND


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
    price: Decimal = Field(..., gt=0)
    producer_id: int
    category_id: Optional[int] = None
    label: Optional[str] = None
    images: Optional[str] = None  # JSON array of image URLs
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Giá sản phẩm phải lớn hơn 0')
        if v > MAX_PRICE:
            raise ValueError(f'Giá sản phẩm không được vượt quá {MAX_PRICE:,.0f} VND')
        if v < MIN_PRICE:
            raise ValueError(f'Giá sản phẩm phải tối thiểu {MIN_PRICE:,.0f} VND')
        return v


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    label: Optional[str] = None
    images: Optional[str] = None
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Giá sản phẩm phải lớn hơn 0')
            if v > MAX_PRICE:
                raise ValueError(f'Giá sản phẩm không được vượt quá {MAX_PRICE:,.0f} VND')
            if v < MIN_PRICE:
                raise ValueError(f'Giá sản phẩm phải tối thiểu {MIN_PRICE:,.0f} VND')
        return v


class ProductApprovalRequest(BaseModel):
    status: str  # APPROVED, REJECTED
    notes: Optional[str] = None
    checked_description: bool = False
    checked_price: bool = False
    checked_images: bool = False
    # product_id lấy từ URL path, không cần trong body


# ==============================================================================
# HELPER FUNCTIONS FOR VALIDATION
# ==============================================================================

def validate_product_content(description: Optional[str], images: Optional[str], is_update: bool = False) -> List[str]:
    """
    Validate product content quality.
    Returns list of validation errors.
    """
    errors = []
    
    # Validate description length
    if description:
        if len(description.strip()) < MIN_DESCRIPTION_LENGTH:
            errors.append(f"Mô tả sản phẩm phải có ít nhất {MIN_DESCRIPTION_LENGTH} ký tự (hiện tại: {len(description.strip())} ký tự)")
    elif not is_update:
        errors.append(f"Mô tả sản phẩm là bắt buộc và phải có ít nhất {MIN_DESCRIPTION_LENGTH} ký tự")
    
    # Validate images count
    if images:
        try:
            images_list = json.loads(images)
            if isinstance(images_list, list):
                if len(images_list) < MIN_IMAGES_COUNT:
                    errors.append(f"Sản phẩm phải có ít nhất {MIN_IMAGES_COUNT} ảnh")
            else:
                errors.append("Định dạng ảnh không hợp lệ (phải là JSON array)")
        except json.JSONDecodeError:
            errors.append("Định dạng ảnh không hợp lệ (phải là JSON array)")
    elif not is_update:
        errors.append(f"Sản phẩm phải có ít nhất {MIN_IMAGES_COUNT} ảnh")
    
    return errors


def log_price_change(db: Session, product_id: int, old_price: Decimal, new_price: Decimal, changed_by: int, reason: str = None):
    """Log price change for audit purposes"""
    price_log = ProductPriceLog(
        product_id=product_id,
        old_price=old_price,
        new_price=new_price,
        changed_by=changed_by,
        reason=reason
    )
    db.add(price_log)


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
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    include_inactive: bool = Query(False, description="Include inactive products (admin/seller only)"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get list of products with pagination and filters.
    - Khách / consumer: chỉ sản phẩm APPROVED và đang bán (is_active).
    - Seller/producer: thấy sản phẩm APPROVED công khai + mọi trạng thái của chính họ.
    - Admin / content_manager: xem toàn bộ (kèm bộ lọc khác).
    """
    query = db.query(Product)

    ut = ((current_user.type if current_user else None) or "").lower()

    # Filter by is_active based on user role
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    elif not include_inactive:
        # Default: only show active products for consumers
        if not current_user or current_user.type not in ("admin", "producer", "seller", "content_manager"):
            query = query.filter(Product.is_active == True)
    elif include_inactive:
        # Admin can see all, seller can only see their own inactive
        if current_user and current_user.type in ("producer", "seller"):
            # Seller: only include their own inactive products
            query = query.filter(
                (Product.is_active == True) | (Product.producer_id == current_user.id)
            )
        elif not current_user or current_user.type not in ("admin", "content_manager"):
            # Non-admin without auth: only active
            query = query.filter(Product.is_active == True)

    # Catalog visibility: tránh lộ SP chưa duyệt ra khách / consumer
    if ut in ("admin", "content_manager"):
        pass
    elif ut in ("producer", "seller"):
        query = query.filter(
            or_(
                Product.status == ProductStatus.APPROVED,
                Product.producer_id == current_user.id,
            )
        )
    else:
        query = query.filter(
            Product.status == ProductStatus.APPROVED,
            Product.is_active == True,
        )

    if status:
        # Seller lọc theo trạng thái khác APPROVED: chỉ áp cho sản phẩm của họ (tránh xem SP người khác)
        if ut in ("producer", "seller"):
            st_upper = status.strip().upper() if isinstance(status, str) else str(status).upper()
            if st_upper != "APPROVED":
                query = query.filter(Product.producer_id == current_user.id)
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
    """Get product details by ID (chỉ SP công khai APPROVED trừ khi admin/moderator hoặc chủ sản phẩm)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ut = ((current_user.type if current_user else None) or "").lower()
    can_see_unpublished = ut in ("admin", "content_manager")
    is_owner = (
        current_user is not None
        and ut in ("producer", "seller")
        and product.producer_id == current_user.id
    )
    if not can_see_unpublished and not is_owner:
        if product.status != ProductStatus.APPROVED or not product.is_active:
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
    - **KYC Required**: Seller phải được xác minh hồ sơ kinh doanh trước khi tạo sản phẩm.
    """
    is_admin = (current_user.type == "admin")
    
    # KYC check for non-admin users
    if not is_admin:
        check_seller_kyc_verified(current_user, db)

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
    
    # Validate content quality
    content_errors = validate_product_content(product_data.description, product_data.images)
    if content_errors:
        raise HTTPException(status_code=400, detail="; ".join(content_errors))

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

    # Validate content if description or images are being updated
    update_data = product_data.dict(exclude_unset=True)
    
    desc_to_check = update_data.get('description', product.description)
    images_to_check = update_data.get('images', product.images)
    
    content_errors = validate_product_content(desc_to_check, images_to_check, is_update=True)
    if content_errors:
        raise HTTPException(status_code=400, detail="; ".join(content_errors))
    
    # Log price change if price is being updated
    if 'price' in update_data and update_data['price'] != product.price:
        log_price_change(
            db=db,
            product_id=product.id,
            old_price=product.price,
            new_price=update_data['price'],
            changed_by=current_user.id,
            reason="Cập nhật giá sản phẩm"
        )
    
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
    """
    Delete a product.
    - Nếu sản phẩm đã có đơn hàng: không cho xóa, chỉ cho ẩn (is_active=False)
    - Admin có thể xóa bất kỳ sản phẩm nào (nếu chưa có đơn)
    - Seller chỉ xóa sản phẩm của mình
    """
    is_admin = (current_user.type == "admin")
    
    query = db.query(Product).filter(Product.id == product_id)
    if not is_admin:
        query = query.filter(Product.producer_id == current_user.id)
    
    product = query.first()
    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Product not found" if is_admin else "Sản phẩm không tồn tại hoặc bạn không có quyền xóa"
        )
    
    # Check if product has any orders
    from app.models.order import Order
    has_orders = db.query(Order).filter(Order.id.in_(
        db.query(OrderItem.order_id).filter(OrderItem.product_id == product_id)
    )).first() is not None if 'OrderItem' in dir() else False
    
    # Alternative: check via a simple subquery (assuming order_items table exists)
    try:
        from sqlalchemy import text
        result = db.execute(
            text("SELECT 1 FROM order_items WHERE product_id = :pid LIMIT 1"),
            {"pid": product_id}
        ).fetchone()
        has_orders = result is not None
    except Exception:
        has_orders = False
    
    if has_orders:
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa sản phẩm đã có đơn hàng. Vui lòng ẩn sản phẩm thay vì xóa (PUT /{product_id}/toggle-active)"
        )
    
    db.delete(product)
    db.commit()
    
    return {"success": True, "message": "Product deleted successfully"}


@router.put("/{product_id}/toggle-active")
async def toggle_product_active(
    product_id: int,
    is_active: bool = Query(..., description="True = hiện, False = ẩn"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ẩn/hiện sản phẩm (soft delete).
    - Admin: toggle bất kỳ sản phẩm nào
    - Seller: chỉ toggle sản phẩm của mình
    """
    is_admin = (current_user.type == "admin")
    
    query = db.query(Product).filter(Product.id == product_id)
    if not is_admin:
        query = query.filter(Product.producer_id == current_user.id)
    
    product = query.first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found" if is_admin else "Sản phẩm không tồn tại hoặc bạn không có quyền thay đổi"
        )
    
    product.is_active = is_active
    product.updated_at = datetime.utcnow()
    db.commit()
    
    status_text = "hiển thị" if is_active else "ẩn"
    return {
        "success": True, 
        "message": f"Sản phẩm đã được {status_text}",
        "data": {
            "product_id": product.id,
            "is_active": product.is_active
        }
    }


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
    """
    Approve or reject a product.
    Kiểm tra KYC của seller trước khi duyệt.
    """
    # Permission check: chỉ admin hoặc content_manager mới được duyệt sản phẩm
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Không có quyền duyệt sản phẩm. Yêu cầu role: admin hoặc content_manager")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if seller is KYC verified before approving
    if approval_data.status == "APPROVED":
        from app.models.seller_profile import SellerProfile, VerificationStatus
        seller_profile = db.query(SellerProfile).filter(
            SellerProfile.user_id == product.producer_id
        ).first()
        
        if not seller_profile or seller_profile.verification_status != VerificationStatus.VERIFIED:
            raise HTTPException(
                status_code=400,
                detail="Không thể duyệt sản phẩm: Seller chưa được xác minh hồ sơ kinh doanh (KYC)"
            )
    
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
    check_product_label_access(current_user)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.label = label
    db.commit()

    return {"success": True, "message": "Product label updated successfully"}
