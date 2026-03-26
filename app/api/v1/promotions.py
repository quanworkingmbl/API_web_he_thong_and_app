"""
Promotions API – Quản lý mã khuyến mãi / Coupon

Admin:
- GET    /promotions              – Xem danh sách
- POST   /promotions              – Tạo mã khuyến mãi
- GET    /promotions/{id}         – Xem chi tiết
- PUT    /promotions/{id}         – Cập nhật
- DELETE /promotions/{id}         – Xóa

Public/Consumer:
- GET    /promotions/public       – Xem mã KM công khai (is_public=True, ACTIVE)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.models.promotion import Promotion, PromotionType, PromotionStatus
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
    used_count: int
    start_date: datetime
    end_date: datetime
    status: str
    is_public: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedPromotionResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[PromotionResponse]


class CreatePromotionRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    promotion_type: str = Field(default="PERCENTAGE", pattern="^(PERCENTAGE|FIXED_AMOUNT)$")
    discount_value: Decimal = Field(..., gt=0)
    min_order_amount: Decimal = Field(default=0, ge=0)
    max_discount_amount: Optional[Decimal] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    start_date: datetime
    end_date: datetime
    is_public: bool = True


class UpdatePromotionRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    promotion_type: Optional[str] = Field(None, pattern="^(PERCENTAGE|FIXED_AMOUNT)$")
    discount_value: Optional[Decimal] = Field(None, gt=0)
    min_order_amount: Optional[Decimal] = Field(None, ge=0)
    max_discount_amount: Optional[Decimal] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|EXPIRED)$")
    is_public: Optional[bool] = None


def _build_promotion_response(p: Promotion) -> dict:
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
        used_count=p.used_count,
        start_date=p.start_date,
        end_date=p.end_date,
        status=p.status.value if hasattr(p.status, 'value') else str(p.status),
        is_public=p.is_public,
        created_by=p.created_by,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


# ==============================================================================
# ADMIN ENDPOINTS
# ==============================================================================

@router.get("", response_model=PaginatedPromotionResponse)
async def get_promotions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo code hoặc tên"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Xem danh sách mã khuyến mãi"""
    query = db.query(Promotion)

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
        total=total,
        page=page,
        limit=limit,
        data=[_build_promotion_response(p) for p in items]
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
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat(),
            }
            for p in items
        ],
        "meta": {"total": total, "page": page, "limit": limit}
    }


@router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_promotion_by_id(
    promotion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Xem chi tiết mã khuyến mãi"""
    promo = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")
    return _build_promotion_response(promo)


@router.post("", response_model=PromotionResponse)
async def create_promotion(
    promo_data: CreatePromotionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Tạo mã khuyến mãi"""
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền tạo mã khuyến mãi")

    existing = db.query(Promotion).filter(Promotion.code == promo_data.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mã khuyến mãi đã tồn tại")

    if promo_data.end_date <= promo_data.start_date:
        raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    new_promo = Promotion(
        code=promo_data.code.upper(),
        name=promo_data.name,
        description=promo_data.description,
        promotion_type=promo_data.promotion_type,
        discount_value=promo_data.discount_value,
        min_order_amount=promo_data.min_order_amount,
        max_discount_amount=promo_data.max_discount_amount,
        usage_limit=promo_data.usage_limit,
        start_date=promo_data.start_date,
        end_date=promo_data.end_date,
        status=PromotionStatus.ACTIVE,
        is_public=promo_data.is_public,
        created_by=current_user.id,
    )
    db.add(new_promo)
    db.commit()
    db.refresh(new_promo)

    return _build_promotion_response(new_promo)


@router.put("/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    promotion_id: int,
    promo_data: UpdatePromotionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Cập nhật mã khuyến mãi"""
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền cập nhật")

    promo = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")

    update_data = promo_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(promo, key, value)

    db.commit()
    db.refresh(promo)

    return _build_promotion_response(promo)


@router.delete("/{promotion_id}")
async def delete_promotion(
    promotion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Xóa mã khuyến mãi"""
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa")

    promo = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Mã khuyến mãi không tồn tại")

    db.delete(promo)
    db.commit()

    return {"success": True, "message": "Đã xóa mã khuyến mãi"}
