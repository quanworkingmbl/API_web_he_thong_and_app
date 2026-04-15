"""
Seller Onboarding API – Đăng ký & Xác minh người bán

Endpoints:
- POST /seller/register                 – Seller nộp hồ sơ kinh doanh
- GET  /seller/verification-status      – Xem trạng thái duyệt
- PUT  /seller/verify/{user_id}         – Admin duyệt / từ chối
- GET  /seller/applications             – Admin xem danh sách hồ sơ chờ
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.models.seller_profile import SellerProfile, VerificationStatus
from app.models.user import User
from app.api.v1.auth import get_current_user, get_current_user_allow_inactive
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class SellerRegisterRequest(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=255)
    business_type: str = Field(
        default="HOUSEHOLD",
        pattern="^(HOUSEHOLD|COOPERATIVE|COMPANY)$"
    )
    description: Optional[str] = None
    address: Optional[str] = None

    # Thông tin liên hệ cửa hàng (map → shop_phone / shop_email trong DB)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)

    # Giấy tờ định danh
    id_card_number: Optional[str] = Field(None, max_length=20)
    id_card_front_url: Optional[str] = None
    id_card_back_url: Optional[str] = None

    # Giấy phép & chứng chỉ
    business_license_url: Optional[str] = None                          # Hình ảnh giấy phép KD
    business_registration_cert_url: Optional[str] = None               # Giấy CN Đăng ký KD
    food_safety_cert_url: Optional[str] = None                         # Giấy CN ATTP (nếu có)

    # Thông tin thuế (map → tax_id trong DB)
    tax_code: Optional[str] = Field(None, max_length=50)               # Mã số thuế
    business_registration_number: Optional[str] = Field(None, max_length=50)  # Số ĐKKD

    # Tài khoản ngân hàng
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_name: Optional[str] = None


class VerifySellerRequest(BaseModel):
    status: str = Field(..., pattern="^(VERIFIED|REJECTED)$")
    rejection_reason: Optional[str] = None


# ==============================================================================
# HELPERS
# ==============================================================================

# Ánh xạ tên field từ request schema → column trong SellerProfile
_FIELD_MAP: dict = {
    "phone": "shop_phone",
    "email": "shop_email",
    "tax_code": "tax_id",
}


def _apply_request_to_profile(profile: SellerProfile, data: SellerRegisterRequest) -> None:
    """Map các field từ request sang đúng column của SellerProfile model."""
    for key, value in data.model_dump(exclude_unset=True).items():
        model_key = _FIELD_MAP.get(key, key)
        if hasattr(profile, model_key):
            setattr(profile, model_key, value)


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.post("/register", summary="Seller nộp hồ sơ kinh doanh")
async def register_seller_profile(
    data: SellerRegisterRequest,
    current_user: User = Depends(get_current_user_allow_inactive),
    db: Session = Depends(get_db)
):
    """
    Người bán nộp hồ sơ kinh doanh để được xác minh.
    Nếu đã có hồ sơ, sẽ cập nhật lại (reset về PENDING).
    Loại hình kinh doanh: HOUSEHOLD | COOPERATIVE | COMPANY.
    """
    if current_user.type not in {"producer", "seller"}:
        raise HTTPException(
            status_code=400,
            detail="Chỉ tài khoản loại 'producer' hoặc 'seller' mới cần nộp hồ sơ"
        )

    existing = db.query(SellerProfile).filter(
        SellerProfile.user_id == current_user.id
    ).first()

    if existing:
        # Cập nhật hồ sơ
        _apply_request_to_profile(existing, data)
        existing.verification_status = VerificationStatus.PENDING
        existing.rejection_reason = None
        existing.verified_by = None
        existing.verified_at = None
        profile = existing
        msg = "Hồ sơ đã được cập nhật, chờ xét duyệt lại"
    else:
        profile = SellerProfile(user_id=current_user.id)
        _apply_request_to_profile(profile, data)
        db.add(profile)
        msg = "Hồ sơ đã được nộp thành công, chờ admin xét duyệt"

    # Sau mỗi lần nộp/cập nhật hồ sơ, tài khoản seller về PENDING
    current_user.activated = 0
    db.commit()
    db.refresh(profile)

    return {
        "success": True,
        "message": msg,
        "data": {
            "id": profile.id,
            "business_name": profile.business_name,
            "business_type": profile.business_type.value if hasattr(profile.business_type, "value") else str(profile.business_type),
            "verification_status": profile.verification_status.value if hasattr(profile.verification_status, "value") else str(profile.verification_status)
        }
    }


@router.get("/verification-status", summary="Xem trạng thái xác minh")
async def get_verification_status(
    current_user: User = Depends(get_current_user_allow_inactive),
    db: Session = Depends(get_db)
):
    """Seller xem trạng thái hồ sơ của mình."""
    if current_user.type not in {"producer", "seller"}:
        raise HTTPException(status_code=403, detail="Chỉ tài khoản seller/producer mới có thể xem trạng thái KYC")

    profile = db.query(SellerProfile).filter(
        SellerProfile.user_id == current_user.id
    ).first()

    if not profile:
        return {
            "success": True,
            "data": None,
            "message": "Chưa nộp hồ sơ kinh doanh. Hãy dùng POST /api/seller/register."
        }

    return {
        "success": True,
        "data": {
            "id": profile.id,
            "business_name": profile.business_name,
            "business_type": profile.business_type.value if hasattr(profile.business_type, "value") else str(profile.business_type),
            "verification_status": profile.verification_status.value if hasattr(profile.verification_status, "value") else str(profile.verification_status),
            "rejection_reason": profile.rejection_reason,
            "verified_at": profile.verified_at.isoformat() if profile.verified_at else None,
            "bank_name": profile.bank_name,
            "bank_account_number": profile.bank_account_number,
            "shop_phone": profile.shop_phone,
            "shop_email": profile.shop_email,
            "tax_id": profile.tax_id,
            "business_registration_number": profile.business_registration_number,
            "created_at": profile.created_at.isoformat() if profile.created_at else None
        }
    }


@router.put("/verify/{user_id}", summary="Admin duyệt / từ chối hồ sơ seller")
async def verify_seller(
    user_id: int,
    data: VerifySellerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin xác minh hoặc từ chối hồ sơ kinh doanh của seller.
    Nếu VERIFIED → activated = 1 (cho phép bán hàng).
    Nếu REJECTED → giữ activated = 0.
    """
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền")

    profile = db.query(SellerProfile).filter(
        SellerProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Hồ sơ seller không tồn tại")

    if data.status == "REJECTED" and not data.rejection_reason:
        raise HTTPException(
            status_code=400,
            detail="rejection_reason là bắt buộc khi từ chối hồ sơ"
        )

    profile.verification_status = VerificationStatus(data.status)
    profile.verified_by = current_user.id
    profile.verified_at = datetime.utcnow()

    # Cập nhật trạng thái activated của user
    seller_user = db.query(User).filter(User.id == user_id).first()
    if data.status == "VERIFIED":
        profile.rejection_reason = None
        if seller_user:
            seller_user.activated = 1
    elif data.status == "REJECTED":
        profile.rejection_reason = data.rejection_reason
        if seller_user:
            seller_user.activated = 0

    db.commit()

    return {
        "success": True,
        "message": f"Hồ sơ đã được {'xác minh' if data.status == 'VERIFIED' else 'từ chối'}",
        "data": {
            "user_id": user_id,
            "status": data.status,
            "rejection_reason": data.rejection_reason if data.status == "REJECTED" else None
        }
    }


@router.get("/applications", summary="Admin xem danh sách hồ sơ chờ duyệt")
async def get_seller_applications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="PENDING / VERIFIED / REJECTED"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin xem danh sách hồ sơ kinh doanh của seller."""
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền")

    query = db.query(SellerProfile)
    if status:
        try:
            status_enum = VerificationStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="status phải là PENDING | VERIFIED | REJECTED")
        query = query.filter(SellerProfile.verification_status == status_enum)

    total = query.count()
    skip = (page - 1) * limit
    items = query.order_by(SellerProfile.created_at.desc()).offset(skip).limit(limit).all()

    data_list = []
    for p in items:
        user = db.query(User).filter(User.id == p.user_id).first()
        data_list.append({
            "id": p.id,
            "user_id": p.user_id,
            "user_name": user.name if user else None,
            "user_email": user.email if user else None,
            "business_name": p.business_name,
            "business_type": p.business_type.value if hasattr(p.business_type, "value") else str(p.business_type),
            "id_card_number": p.id_card_number,
            "shop_phone": p.shop_phone,
            "shop_email": p.shop_email,
            "tax_id": p.tax_id,
            "verification_status": p.verification_status.value if hasattr(p.verification_status, "value") else str(p.verification_status),
            "created_at": p.created_at.isoformat() if p.created_at else None
        })

    return {
        "success": True,
        "data": data_list,
        "meta": {"total": total, "page": page, "limit": limit}
    }
