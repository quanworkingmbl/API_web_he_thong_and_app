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
# CONSTANTS
# ==============================================================================
MIN_DESCRIPTION_LENGTH = 50
MIN_IMAGES_COUNT = 1
MAX_PRICE = Decimal("100000000")
MIN_PRICE = Decimal("1000")
VAT_DEFAULT = Decimal("10.00")  # Seller khong duoc thay doi VAT


# ==============================================================================
# RESPONSE / REQUEST SCHEMAS
# ==============================================================================

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    is_active: bool
    seller_id: int
    seller_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    status: str
    label: Optional[str]
    product_type: Optional[str] = None    # AGRICULTURAL | HANDICRAFT
    packaging_type: Optional[str] = None  # thung, lon, hop, bo...
    images: Optional[str]
    sku: Optional[str] = None
    unit: Optional[str] = None
    weight: Optional[int] = None
    stock_quantity: Optional[int] = None
    vat_rate: Optional[Decimal] = None
    approved_at: Optional[str] = None
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    data: List[ProductResponse]
    meta: dict


class CreateProductRequest(BaseModel):
    """Admin tao san pham – co the chi dinh seller_id va set label"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    seller_id: int
    category_id: Optional[int] = None
    label: Optional[str] = None
    product_type: Optional[str] = Field(None, pattern="^(AGRICULTURAL|HANDICRAFT)$")
    packaging_type: Optional[str] = Field(None, max_length=50)
    images: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=20)
    weight: Optional[int] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    vat_rate: Optional[Decimal] = Field(None, ge=0, le=100)

    @validator("price")
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Gia san pham phai lon hon 0")
        if v > MAX_PRICE:
            raise ValueError(f"Gia toi da {MAX_PRICE:,.0f} VND")
        if v < MIN_PRICE:
            raise ValueError(f"Gia toi thieu {MIN_PRICE:,.0f} VND")
        return v


class UpdateProductRequest(BaseModel):
    """Admin cap nhat san pham"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    label: Optional[str] = None
    product_type: Optional[str] = Field(None, pattern="^(AGRICULTURAL|HANDICRAFT)$")
    packaging_type: Optional[str] = Field(None, max_length=50)
    images: Optional[str] = None
    is_active: Optional[bool] = None
    sku: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=20)
    weight: Optional[int] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    vat_rate: Optional[Decimal] = Field(None, ge=0, le=100)

    @validator("price")
    def validate_price(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("Gia san pham phai lon hon 0")
            if v > MAX_PRICE:
                raise ValueError(f"Gia toi da {MAX_PRICE:,.0f} VND")
            if v < MIN_PRICE:
                raise ValueError(f"Gia toi thieu {MIN_PRICE:,.0f} VND")
        return v


class ProductApprovalRequest(BaseModel):
    status: str
    notes: Optional[str] = None
    checked_description: bool = False
    checked_price: bool = False
    checked_images: bool = False
    checked_traceability: bool = False


# ==============================================================================
# HELPERS
# ==============================================================================

def validate_product_content(description, images, is_update=False):
    errors = []
    if description:
        if len(description.strip()) < MIN_DESCRIPTION_LENGTH:
            errors.append(f"Mo ta phai co it nhat {MIN_DESCRIPTION_LENGTH} ky tu")
    elif not is_update:
        errors.append("Mo ta san pham la bat buoc")
    if images:
        try:
            lst = json.loads(images)
            if not isinstance(lst, list):
                errors.append("Dinh dang anh khong hop le (phai la JSON array)")
            elif len(lst) < MIN_IMAGES_COUNT:
                errors.append(f"Phai co it nhat {MIN_IMAGES_COUNT} anh")
        except json.JSONDecodeError:
            errors.append("Dinh dang anh khong hop le")
    elif not is_update:
        errors.append(f"Phai co it nhat {MIN_IMAGES_COUNT} anh")
    return errors


def log_price_change(db, product_id, old_price, new_price, changed_by, reason=None):
    db.add(ProductPriceLog(
        product_id=product_id, old_price=old_price,
        new_price=new_price, changed_by=changed_by, reason=reason,
    ))


def _build_product_response(p, db):
    """Build ProductResponse tu model – tai su dung o moi endpoint."""
    seller = db.query(User).filter(User.id == p.seller_id).first()
    category = db.query(Category).filter(Category.id == p.category_id).first() if p.category_id else None
    return ProductResponse(
        id=p.id, name=p.name, description=p.description, price=p.price,
        is_active=bool(p.is_active), seller_id=p.seller_id,
        seller_name=seller.name if seller else None,
        category_id=p.category_id,
        category_name=category.name if category else None,
        status=p.status.value if hasattr(p.status, "value") else str(p.status),
        label=p.label.value if hasattr(p.label, "value") else p.label,
        product_type=p.product_type if p.product_type else None,
        packaging_type=p.packaging_type,
        images=p.images, sku=p.sku, unit=p.unit, weight=p.weight,
        stock_quantity=p.stock_quantity, vat_rate=p.vat_rate,
        approved_at=p.approved_at.isoformat() if p.approved_at else None,
        created_at=p.created_at.isoformat() if p.created_at else "",
        updated_at=p.updated_at.isoformat() if p.updated_at else None,
    )


# ==============================================================================
# LIST & GET ENDPOINTS
# ==============================================================================

@router.get("", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    seller_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    label: Optional[str] = Query(None),
    product_type: Optional[str] = Query(None, description="AGRICULTURAL | HANDICRAFT"),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Lay danh sach san pham. Consumer: chi APPROVED+active. Seller: them SP cua minh. Admin: tat ca."""
    query = db.query(Product)
    ut = ((current_user.type if current_user else None) or "").lower()

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    elif not include_inactive:
        if not current_user or ut not in ("admin", "producer", "seller", "content_manager"):
            query = query.filter(Product.is_active == True)
    else:
        if current_user and ut in ("producer", "seller"):
            query = query.filter(
                (Product.is_active == True) | (Product.seller_id == current_user.id)
            )
        elif not current_user or ut not in ("admin", "content_manager"):
            query = query.filter(Product.is_active == True)

    if ut in ("admin", "content_manager"):
        pass
    elif ut in ("producer", "seller"):
        query = query.filter(
            or_(Product.status == ProductStatus.APPROVED,
                Product.seller_id == current_user.id)
        )
    else:
        query = query.filter(Product.status == ProductStatus.APPROVED, Product.is_active == True)

    if status:
        if ut in ("producer", "seller") and status.upper() != "APPROVED":
            query = query.filter(Product.seller_id == current_user.id)
        query = query.filter(Product.status == status)
    if seller_id:
        query = query.filter(Product.seller_id == seller_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if label:
        query = query.filter(Product.label == label)
    if product_type:
        query = query.filter(Product.product_type == product_type)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return ProductListResponse(
        data=[_build_product_response(p, db) for p in products],
        meta={"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit},
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    ut = ((current_user.type if current_user else None) or "").lower()
    is_owner = current_user and ut in ("producer", "seller") and product.seller_id == current_user.id
    if ut not in ("admin", "content_manager") and not is_owner:
        if product.status != ProductStatus.APPROVED or not product.is_active:
            raise HTTPException(status_code=404, detail="Product not found")
    return _build_product_response(product, db)


# ==============================================================================
# CREATE / UPDATE / DELETE
# ==============================================================================

@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: CreateProductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tao san pham. Admin: chi dinh seller_id va label. Seller: tu dong seller_id, label=None, vat=10%."""
    is_admin = current_user.type == "admin"
    if not is_admin:
        check_seller_kyc_verified(current_user, db)
    actual_id = product_data.seller_id if is_admin else current_user.id
    if not db.query(User).filter(User.id == actual_id).first():
        raise HTTPException(status_code=400, detail="Seller not found")
    if product_data.category_id:
        if not db.query(Category).filter(Category.id == product_data.category_id).first():
            raise HTTPException(status_code=400, detail="Category not found")
    errs = validate_product_content(product_data.description, product_data.images)
    if errs:
        raise HTTPException(status_code=400, detail="; ".join(errs))
    p = Product(
        name=product_data.name, description=product_data.description,
        price=product_data.price, seller_id=actual_id,
        category_id=product_data.category_id, status=ProductStatus.PENDING,
        label=product_data.label if is_admin else None,
        product_type=product_data.product_type,
        packaging_type=product_data.packaging_type,
        images=product_data.images, sku=product_data.sku,
        unit=product_data.unit, weight=product_data.weight,
        stock_quantity=product_data.stock_quantity or 0,
        vat_rate=product_data.vat_rate if is_admin else VAT_DEFAULT,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _build_product_response(p, db)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: UpdateProductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_admin = current_user.type == "admin"
    q = db.query(Product).filter(Product.id == product_id)
    if not is_admin:
        q = q.filter(Product.seller_id == current_user.id)
    product = q.first()
    if not product:
        raise HTTPException(status_code=404,
            detail="Product not found" if is_admin else "San pham khong ton tai hoac khong co quyen")
    if product_data.category_id:
        if not db.query(Category).filter(Category.id == product_data.category_id).first():
            raise HTTPException(status_code=400, detail="Category not found")
    update_data = product_data.dict(exclude_unset=True)
    if not is_admin:
        update_data.pop("label", None)
        update_data.pop("vat_rate", None)
    errs = validate_product_content(
        update_data.get("description", product.description),
        update_data.get("images", product.images), is_update=True)
    if errs:
        raise HTTPException(status_code=400, detail="; ".join(errs))
    if "price" in update_data and update_data["price"] != product.price:
        log_price_change(db, product.id, product.price, update_data["price"], current_user.id)
    for k, v in update_data.items():
        setattr(product, k, v)
    db.commit()
    db.refresh(product)
    return _build_product_response(product, db)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete SP (is_active=False). Chi hard-delete neu chua co don hang."""
    is_admin = current_user.type == "admin"
    q = db.query(Product).filter(Product.id == product_id)
    if not is_admin:
        q = q.filter(Product.seller_id == current_user.id)
    product = q.first()
    if not product:
        raise HTTPException(status_code=404,
            detail="Product not found" if is_admin else "San pham khong ton tai hoac khong co quyen")
    try:
        from sqlalchemy import text
        has_orders = db.execute(
            text("SELECT 1 FROM order_items WHERE product_id = :pid LIMIT 1"),
            {"pid": product_id}).fetchone() is not None
    except Exception:
        has_orders = False
    if has_orders:
        product.is_active = False
        product.updated_at = datetime.utcnow()
        db.commit()
        return {"success": True, "message": "San pham da duoc an (co don hang lien quan)",
                "data": {"product_id": product_id, "is_active": False}}
    db.delete(product)
    db.commit()
    return {"success": True, "message": "Da xoa san pham"}


@router.put("/{product_id}/toggle-active")
async def toggle_product_active(
    product_id: int,
    is_active: bool = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_admin = current_user.type == "admin"
    q = db.query(Product).filter(Product.id == product_id)
    if not is_admin:
        q = q.filter(Product.seller_id == current_user.id)
    product = q.first()
    if not product:
        raise HTTPException(status_code=404,
            detail="Product not found" if is_admin else "San pham khong ton tai hoac khong co quyen")
    product.is_active = is_active
    product.updated_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": f"San pham da {'hien' if is_active else 'an'}",
            "data": {"product_id": product.id, "is_active": product.is_active}}


# ==============================================================================
# APPROVAL & LABEL  (Admin / content_manager only)
# ==============================================================================

@router.post("/{product_id}/approve")
async def approve_product(
    product_id: int,
    approval_data: ProductApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Yeu cau role admin hoac content_manager")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if approval_data.status == "APPROVED":
        from app.models.seller_profile import SellerProfile, VerificationStatus
        sp = db.query(SellerProfile).filter(SellerProfile.user_id == product.seller_id).first()
        if not sp or sp.verification_status != VerificationStatus.VERIFIED:
            raise HTTPException(status_code=400, detail="Seller chua KYC – khong the duyet")
        product.approved_at = datetime.utcnow()
    product.status = approval_data.status
    db.add(ProductApproval(
        product_id=product_id, approver_id=current_user.id,
        status=approval_data.status, notes=approval_data.notes,
        checked_description=approval_data.checked_description,
        checked_price=approval_data.checked_price,
        checked_images=approval_data.checked_images,
        checked_traceability=approval_data.checked_traceability,
    ))
    db.commit()
    return {"success": True, "message": f"Product {approval_data.status.lower()} successfully"}


@router.put("/{product_id}/label")
async def update_product_label(
    product_id: int,
    label: str = Query(..., pattern="^(CLEAN_AGRICULTURE|TRADITIONAL_CRAFT|OCOP)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gan nhan san pham – Admin only, sau khi da xac minh chung nhan."""
    check_product_label_access(current_user)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.label = label
    db.commit()
    return {"success": True, "message": "Product label updated"}
