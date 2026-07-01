"""
Promotions API – Quản lý mã khuyến mãi / Coupon

Admin:
- GET    /promotions              – Xem danh sách
- POST   /promotions              – Tạo mã khuyến mãi (mặc định ACTIVE)
- GET    /promotions/{id}         – Xem chi tiết
- PUT    /promotions/{id}         – Cập nhật
- DELETE /promotions/{id}         – Xóa
- POST   /promotions/{id}/approve – Admin duyệt mã (PENDING → ACTIVE)
- POST   /promotions/{id}/reject  – Admin từ chối mã (PENDING → INACTIVE)

Seller:
- Tạo mã → mặc định PENDING, chờ Admin duyệt

Public/Consumer:
- GET    /promotions/public        – Xem mã KM công khai (ACTIVE)
- GET    /promotions/flash-sales   – Xem Flash Sale đang diễn ra
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import json
from app.core.database import get_db
from app.models.promotion import Promotion, PromotionType, PromotionStatus
from app.models.promotion_usage import PromotionUsage, OrderPromotion
from app.models.product import Product
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class PromotionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    promotion_type: str
    discount_value: Decimal
    min_order_amount: Decimal
    max_discount_amount: Optional[Decimal]
    usage_limit: Optional[int]
    usage_limit_per_user: Optional[int]
    applicable_to: str
    seller_id: Optional[int]
    seller_name: Optional[str] = None
    creator_username: Optional[str] = None
    applicable_product_ids: List[int]
    applicable_category_ids: List[int]
    used_count: int
    start_date: datetime
    end_date: datetime
    status: str
    is_public: bool
    is_flash_sale: bool = False
    # Approval info
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedPromotionResponse(BaseModel):
    success: bool = True
    data: List[PromotionResponse]
    meta: dict


class CreatePromotionRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    promotion_type: str = Field(default="PERCENTAGE", pattern="^(PERCENTAGE|FIXED_AMOUNT)$")
    discount_value: Decimal = Field(..., gt=0)
    min_order_amount: Decimal = Field(default=0, ge=0)
    max_discount_amount: Optional[Decimal] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_user: Optional[int] = Field(None, ge=1)
    applicable_to: str = Field(default="ALL", pattern="^(ALL|SELLER|PRODUCT|CATEGORY)$")
    seller_id: Optional[int] = None
    applicable_product_ids: Optional[List[int]] = None
    applicable_category_ids: Optional[List[int]] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|EXPIRED|PENDING)$")
    start_date: datetime
    end_date: datetime
    is_public: bool = True
    is_flash_sale: bool = False


class UpdatePromotionRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    promotion_type: Optional[str] = Field(None, pattern="^(PERCENTAGE|FIXED_AMOUNT)$")
    discount_value: Optional[Decimal] = Field(None, gt=0)
    min_order_amount: Optional[Decimal] = Field(None, ge=0)
    max_discount_amount: Optional[Decimal] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_user: Optional[int] = Field(None, ge=1)
    applicable_to: Optional[str] = Field(None, pattern="^(ALL|SELLER|PRODUCT|CATEGORY)$")
    seller_id: Optional[int] = None
    applicable_product_ids: Optional[List[int]] = None
    applicable_category_ids: Optional[List[int]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|EXPIRED|PENDING)$")
    is_public: Optional[bool] = None
    is_flash_sale: Optional[bool] = None


class RejectPromotionRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)


def _parse_json_id_list(raw: Optional[str]) -> List[int]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return []

    if not isinstance(parsed, list):
        return []

    values: List[int] = []
    for item in parsed:
        try:
            values.append(int(item))
        except (TypeError, ValueError):
            continue
    return values


def _serialize_id_list(values: Optional[List[int]]) -> Optional[str]:
    if values is None:
        return None
    cleaned = sorted({int(v) for v in values if v is not None})
    return json.dumps(cleaned)


def _is_admin_user(current_user: User) -> bool:
    return ((current_user.type or "").lower() == "admin")


def _is_seller_user(current_user: User) -> bool:
    return ((current_user.type or "").lower() in {"seller", "producer"})


def _ensure_manage_permission(current_user: User):
    if not (_is_admin_user(current_user) or _is_seller_user(current_user)):
        raise HTTPException(status_code=403, detail="Bạn không có quyền quản lý khuyến mãi")


def _validate_scope_payload(
    db: Session,
    current_user: User,
    is_admin: bool,
    applicable_to: str,
    seller_id: Optional[int],
    product_ids: List[int],
    category_ids: List[int],
):
    scope = (applicable_to or "ALL").upper()

    if scope in {"SELLER", "PRODUCT", "CATEGORY"} and not seller_id:
        raise HTTPException(status_code=400, detail="Thiếu seller_id cho phạm vi khuyến mãi")

    if scope == "PRODUCT" and not product_ids:
        raise HTTPException(status_code=400, detail="Phạm vi PRODUCT phải có applicable_product_ids")

    if scope == "CATEGORY" and not category_ids:
        raise HTTPException(status_code=400, detail="Phạm vi CATEGORY phải có applicable_category_ids")

    if not is_admin:
        if seller_id != current_user.id:
            raise HTTPException(status_code=403, detail="Seller chỉ được tạo khuyến mãi cho cửa hàng của mình")

        if product_ids:
            owned_count = db.query(Product.id).filter(
                Product.id.in_(product_ids),
                Product.seller_id == current_user.id,
            ).count()
            if owned_count != len(set(product_ids)):
                raise HTTPException(status_code=400, detail="Có sản phẩm không thuộc quyền sở hữu của seller")


def _build_promotion_response(p: Promotion, db: Session) -> dict:
    seller_name: Optional[str] = None
    if p.seller_id:
        seller = db.query(User).filter(User.id == p.seller_id).first()
        if seller:
            seller_name = seller.name or seller.email

    creator_username: Optional[str] = None
    if p.created_by:
        creator = db.query(User).filter(User.id == p.created_by).first()
        if creator:
            creator_username = creator.email or creator.name

    return PromotionResponse(
        id=p.id,
        code=p.code,
        name=p.name,
        description=p.description,
        promotion_type=p.promotion_type.value if hasattr(p.promotion_type, 'value') else str(p.promotion_type),
        discount_value=p.discount_value,
        min_order_amount=p.min_order_amount,
        max_discount_amount=p.max_discount_amount,
        usage_limit=p.usage_limit,
        usage_limit_per_user=p.usage_limit_per_user,
        applicable_to=(p.applicable_to or "ALL"),
        seller_id=p.seller_id,
        seller_name=seller_name,
        creator_username=creator_username,
        applicable_product_ids=_parse_json_id_list(p.applicable_product_ids),
        applicable_category_ids=_parse_json_id_list(p.applicable_category_ids),
        used_count=p.used_count,
        start_date=p.start_date,
        end_date=p.end_date,
        status=p.status.value if hasattr(p.status, 'value') else str(p.status),
        is_public=p.is_public,
        is_flash_sale=bool(p.is_flash_sale),
        approved_by=p.approved_by,
        approved_at=p.approved_at,
        rejection_reason=p.rejection_reason,
        created_by=p.created_by,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


# ==============================================================================
# ADMIN / SELLER ENDPOINTS
# ==============================================================================

@router.get("", response_model=PaginatedPromotionResponse)
async def get_promotions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo code hoặc tên"),
    seller_id: Optional[int] = Query(None, description="Admin lọc theo seller (seller_id)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin hoặc seller xem danh sách mã khuyến mãi."""
    _ensure_manage_permission(current_user)
    is_admin = _is_admin_user(current_user)

    query = db.query(Promotion)

    if not is_admin:
        query = query.filter(
            or_(
                Promotion.seller_id == current_user.id,
                Promotion.created_by == current_user.id,
            )
        )
    else:
        if seller_id is not None:
            query = query.filter(
                or_(
                    Promotion.seller_id == seller_id,
                    Promotion.created_by == seller_id,
                )
            )

    if status:
        query = query.filter(Promotion.status == status)
    if search:
        query = query.filter(
            (Promotion.code.ilike(f"%{search}%")) | (Promotion.name.ilike(f"%{search}%"))
        )

    total = query.count()
    skip = (page - 1) * limit
    items = query.order_by(Promotion.created_at.desc()).offset(skip).limit(limit).all()

    return PaginatedPromotionResponse(
        success=True,
        data=[_build_promotion_response(p, db) for p in items],
        meta={"total": total, "page": page, "limit": limit}
    )


@router.get("/public")
async def get_public_promotions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """[Public] Xem mã khuyến mãi công khai đang hoạt động"""
    now = datetime.utcnow()
    query = db.query(Promotion).filter(
        Promotion.is_public == True,
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
    )
    if search:
        query = query.filter(
            (Promotion.code.ilike(f"%{search}%")) | (Promotion.name.ilike(f"%{search}%"))
        )

    total = query.count()
    skip = (page - 1) * limit
    items = query.order_by(Promotion.end_date.asc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "description": p.description,
                "promotion_type": p.promotion_type.value if hasattr(p.promotion_type, 'value') else str(p.promotion_type),
                "discount_value": str(p.discount_value),
                "min_order_amount": str(p.min_order_amount),
                "max_discount_amount": str(p.max_discount_amount) if p.max_discount_amount else None,
                "is_flash_sale": bool(p.is_flash_sale),
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat(),
                # Countdown: số giây còn lại đến khi kết thúc
                "ends_in_seconds": max(0, int((p.end_date.replace(tzinfo=None) - now).total_seconds())),
            }
            for p in items
        ],
        "meta": {"total": total, "page": page, "limit": limit}
    }


@router.get("/flash-sales")
async def get_flash_sales(
    db: Session = Depends(get_db)
):
    """[Public] Lấy danh sách Flash Sale đang diễn ra (để hiển thị countdown trong App)"""
    now = datetime.utcnow()
    items = db.query(Promotion).filter(
        Promotion.is_flash_sale == True,
        Promotion.is_public == True,
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
    ).order_by(Promotion.end_date.asc()).limit(20).all()

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "promotion_type": p.promotion_type.value if hasattr(p.promotion_type, 'value') else str(p.promotion_type),
                "discount_value": str(p.discount_value),
                "max_discount_amount": str(p.max_discount_amount) if p.max_discount_amount else None,
                "applicable_to": p.applicable_to or "ALL",
                "seller_id": p.seller_id,
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat(),
                # Countdown quan trọng nhất
                "ends_in_seconds": max(0, int((p.end_date.replace(tzinfo=None) - now).total_seconds())),
            }
            for p in items
        ]
    }


@router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_promotion_by_id(
    promotion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin hoặc seller xem chi tiết mã khuyến mãi."""
    _ensure_manage_permission(current_user)

    promo = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")

    if not _is_admin_user(current_user):
        if promo.seller_id != current_user.id and promo.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Bạn không có quyền xem khuyến mãi này")

    return _build_promotion_response(promo, db)


@router.post("", response_model=PromotionResponse)
async def create_promotion(
    promo_data: CreatePromotionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin hoặc seller tạo mã khuyến mãi.
    - Admin: mặc định ACTIVE (không cần tự duyệt).
    - Seller: mặc định PENDING, cần Admin duyệt trước khi dùng.
    """
    _ensure_manage_permission(current_user)
    is_admin = _is_admin_user(current_user)

    existing = db.query(Promotion).filter(Promotion.code == promo_data.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mã khuyến mãi đã tồn tại")

    if promo_data.end_date <= promo_data.start_date:
        raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    scope = (promo_data.applicable_to or "ALL").upper()
    seller_id_value = promo_data.seller_id if is_admin else current_user.id
    if not is_admin and scope == "ALL":
        scope = "SELLER"

    product_ids = list(promo_data.applicable_product_ids or [])
    category_ids = list(promo_data.applicable_category_ids or [])

    _validate_scope_payload(
        db=db,
        current_user=current_user,
        is_admin=is_admin,
        applicable_to=scope,
        seller_id=seller_id_value,
        product_ids=product_ids,
        category_ids=category_ids,
    )

    # Admin tạo → ACTIVE ngay; Seller tạo → PENDING chờ duyệt
    if promo_data.status:
        if is_admin:
            status_value = promo_data.status.upper()
        else:
            # Seller không được tự set ACTIVE
            status_value = "PENDING"
    else:
        status_value = "ACTIVE" if is_admin else "PENDING"

    new_promo = Promotion(
        code=promo_data.code.upper(),
        name=promo_data.name,
        description=promo_data.description,
        promotion_type=promo_data.promotion_type,
        discount_value=promo_data.discount_value,
        min_order_amount=promo_data.min_order_amount,
        max_discount_amount=promo_data.max_discount_amount,
        usage_limit=promo_data.usage_limit,
        usage_limit_per_user=promo_data.usage_limit_per_user,
        applicable_to=scope,
        seller_id=seller_id_value,
        applicable_product_ids=_serialize_id_list(product_ids),
        applicable_category_ids=_serialize_id_list(category_ids),
        start_date=promo_data.start_date,
        end_date=promo_data.end_date,
        status=PromotionStatus(status_value),
        is_public=promo_data.is_public,
        is_flash_sale=promo_data.is_flash_sale,
        created_by=current_user.id,
    )
    db.add(new_promo)
    db.commit()
    db.refresh(new_promo)

    return _build_promotion_response(new_promo, db)


@router.post("/{promotion_id}/approve", response_model=PromotionResponse)
async def approve_promotion(
    promotion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    [Admin only] Duyệt mã khuyến mãi PENDING → ACTIVE.
    Sau khi duyệt, mã sẽ hoạt động theo start_date/end_date.
    """
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có thể duyệt mã khuyến mãi")

    promo = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")

    if promo.status != PromotionStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ duyệt được mã đang PENDING. Trạng thái hiện tại: {promo.status.value}"
        )

    promo.status = PromotionStatus.ACTIVE
    promo.approved_by = current_user.id
    promo.approved_at = datetime.utcnow()
    promo.rejection_reason = None  # Xóa lý do từ chối cũ nếu có
    db.commit()
    db.refresh(promo)

    return _build_promotion_response(promo, db)


@router.post("/{promotion_id}/reject", response_model=PromotionResponse)
async def reject_promotion(
    promotion_id: int,
    body: RejectPromotionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    [Admin only] Từ chối mã khuyến mãi PENDING → INACTIVE.
    Seller sẽ thấy lý do từ chối và có thể chỉnh sửa rồi gửi lại.
    """
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có thể từ chối mã khuyến mãi")

    promo = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")

    if promo.status != PromotionStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ từ chối được mã đang PENDING. Trạng thái hiện tại: {promo.status.value}"
        )

    promo.status = PromotionStatus.INACTIVE
    promo.rejection_reason = body.reason
    promo.approved_by = None
    promo.approved_at = None
    db.commit()
    db.refresh(promo)

    return _build_promotion_response(promo, db)


@router.put("/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    promotion_id: int,
    promo_data: UpdatePromotionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin hoặc seller cập nhật mã khuyến mãi.
    Nếu Seller sửa mã đã bị từ chối (INACTIVE) → tự động reset về PENDING để Admin duyệt lại.
    """
    _ensure_manage_permission(current_user)
    is_admin = _is_admin_user(current_user)

    promo_query = db.query(Promotion).filter(Promotion.id == promotion_id)
    if not is_admin:
        promo_query = promo_query.filter(
            or_(
                Promotion.seller_id == current_user.id,
                Promotion.created_by == current_user.id,
            )
        )

    promo = promo_query.first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")

    update_data = promo_data.dict(exclude_unset=True)

    if not is_admin:
        update_data.pop("seller_id", None)
        if update_data.get("applicable_to") == "ALL":
            update_data["applicable_to"] = "SELLER"
        # Seller không được tự set ACTIVE
        if update_data.get("status") == "ACTIVE":
            update_data["status"] = "PENDING"
        # Nếu Seller sửa mã INACTIVE (bị từ chối) → reset về PENDING để duyệt lại
        if promo.status == PromotionStatus.INACTIVE and "status" not in update_data:
            update_data["status"] = "PENDING"

    new_scope = (update_data.get("applicable_to") or promo.applicable_to or "ALL").upper()
    new_seller_id = update_data.get("seller_id", promo.seller_id)
    if not is_admin:
        new_seller_id = current_user.id

    new_product_ids = (
        list(update_data["applicable_product_ids"])
        if "applicable_product_ids" in update_data
        else _parse_json_id_list(promo.applicable_product_ids)
    )
    new_category_ids = (
        list(update_data["applicable_category_ids"])
        if "applicable_category_ids" in update_data
        else _parse_json_id_list(promo.applicable_category_ids)
    )

    _validate_scope_payload(
        db=db,
        current_user=current_user,
        is_admin=is_admin,
        applicable_to=new_scope,
        seller_id=new_seller_id,
        product_ids=new_product_ids,
        category_ids=new_category_ids,
    )

    if "start_date" in update_data or "end_date" in update_data:
        start_date = update_data.get("start_date", promo.start_date)
        end_date = update_data.get("end_date", promo.end_date)
        if end_date <= start_date:
            raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    for key, value in update_data.items():
        if key in {"applicable_product_ids", "applicable_category_ids", "applicable_to", "seller_id"}:
            continue
        if key == "status":
            setattr(promo, key, PromotionStatus(value.upper()))
            # Nếu reset về PENDING → xóa approval info
            if value.upper() == "PENDING":
                promo.approved_by = None
                promo.approved_at = None
                promo.rejection_reason = None
        else:
            setattr(promo, key, value)

    promo.applicable_to = new_scope
    promo.seller_id = new_seller_id
    if "applicable_product_ids" in update_data:
        promo.applicable_product_ids = _serialize_id_list(new_product_ids)
    if "applicable_category_ids" in update_data:
        promo.applicable_category_ids = _serialize_id_list(new_category_ids)

    db.commit()
    db.refresh(promo)

    return _build_promotion_response(promo, db)


@router.delete("/{promotion_id}")
async def delete_promotion(
    promotion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin hoặc seller xóa khuyến mãi thuộc quyền của mình."""
    _ensure_manage_permission(current_user)
    is_admin = _is_admin_user(current_user)

    promo_query = db.query(Promotion).filter(Promotion.id == promotion_id)
    if not is_admin:
        promo_query = promo_query.filter(
            or_(
                Promotion.seller_id == current_user.id,
                Promotion.created_by == current_user.id,
            )
        )

    promo = promo_query.first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")

    # Xóa các bản ghi liên quan trước (tránh ForeignKeyViolation)
    db.query(PromotionUsage).filter(PromotionUsage.promotion_id == promotion_id).delete(synchronize_session=False)
    db.query(OrderPromotion).filter(OrderPromotion.promotion_id == promotion_id).delete(synchronize_session=False)

    db.delete(promo)
    db.commit()

    return {"success": True, "message": "Đã xóa mã khuyến mãi"}
