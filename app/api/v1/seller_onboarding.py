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
from sqlalchemy import func as sql_func
from typing import Optional
from datetime import datetime
import logging
from app.core.database import get_db
from app.models.seller_profile import SellerProfile, VerificationStatus
from app.models.user import User, UserRole
from app.models.role import Role
from app.api.v1.auth import get_current_user, get_current_user_allow_inactive
from pydantic import BaseModel, Field
from app.services.notification import (
    notify_kyc_pending_to_admin,
    notify_kyc_verified_to_seller,
    notify_kyc_rejected_to_seller,
)

router = APIRouter()
logger = logging.getLogger(__name__)


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


class AdminUpdateSellerProfileRequest(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2, max_length=255)
    business_type: Optional[str] = Field(
        default=None,
        pattern="^(INDIVIDUAL|HOUSEHOLD|COOPERATIVE|COMPANY)$"
    )
    description: Optional[str] = None
    address: Optional[str] = None

    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)

    id_card_number: Optional[str] = Field(None, max_length=20)
    id_card_front_url: Optional[str] = None
    id_card_back_url: Optional[str] = None

    business_license_url: Optional[str] = None
    business_registration_cert_url: Optional[str] = None
    food_safety_cert_url: Optional[str] = None

    tax_code: Optional[str] = Field(None, max_length=50)
    business_registration_number: Optional[str] = Field(None, max_length=50)

    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_name: Optional[str] = None


# ==============================================================================
# HELPERS
# ==============================================================================

# Ánh xạ tên field từ request schema → column trong SellerProfile
_FIELD_MAP: dict = {
    "phone": "shop_phone",
    "email": "shop_email",
    "tax_code": "tax_id",
}


def _apply_request_to_profile(profile: SellerProfile, data: BaseModel) -> None:
    """Map các field từ request sang đúng column của SellerProfile model."""
    for key, value in data.model_dump(exclude_unset=True).items():
        model_key = _FIELD_MAP.get(key, key)
        if hasattr(profile, model_key):
            setattr(profile, model_key, value)


def _enum_value(value):
    if value is None:
        return None
    return value.value if hasattr(value, "value") else str(value)


def _profile_to_response_data(profile: SellerProfile, user: Optional[User] = None) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "user_name": user.name if user else None,
        "user_email": user.email if user else None,
        "business_name": profile.business_name,
        "business_type": _enum_value(profile.business_type),
        "description": profile.description,
        "address": profile.address,
        "shop_phone": profile.shop_phone,
        "shop_email": profile.shop_email,
        "phone": profile.shop_phone,
        "email": profile.shop_email,
        "id_card_number": profile.id_card_number,
        "id_card_front_url": profile.id_card_front_url,
        "id_card_back_url": profile.id_card_back_url,
        "business_license_url": profile.business_license_url,
        "business_registration_cert_url": profile.business_registration_cert_url,
        "food_safety_cert_url": profile.food_safety_cert_url,
        "tax_id": profile.tax_id,
        "tax_code": profile.tax_id,
        "business_registration_number": profile.business_registration_number,
        "bank_name": profile.bank_name,
        "bank_account_number": profile.bank_account_number,
        "bank_account_name": profile.bank_account_name,
        "verification_status": _enum_value(profile.verification_status),
        "rejection_reason": profile.rejection_reason,
        "verified_by": profile.verified_by,
        "verified_at": profile.verified_at.isoformat() if profile.verified_at else None,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


def _sync_verified_seller_role(db: Session, user_id: int) -> None:
    """Ensure verified seller has seller role and no legacy customer-like role."""
    candidate_roles = db.query(Role).filter(
        sql_func.lower(Role.role_name).in_(["seller", "producer"])
    ).all()
    if not candidate_roles:
        return

    seller_role = next(
        (role for role in candidate_roles if (role.role_name or "").strip().lower() == "seller"),
        candidate_roles[0],
    )

    customer_links = db.query(UserRole).join(
        Role, UserRole.role_id == Role.id
    ).filter(
        UserRole.user_id == user_id,
        sql_func.lower(Role.role_name).in_(["customer", "consumer", "buyer"])
    ).all()
    for link in customer_links:
        db.delete(link)

    seller_link = db.query(UserRole.id).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == seller_role.id,
    ).first()
    if seller_link is None:
        db.add(UserRole(user_id=user_id, role_id=seller_role.id))


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
    Người dùng nộp hồ sơ kinh doanh để được xác minh trở thành người bán.
    - Tài khoản consumer: type được nâng lên 'seller' khi nộp hồ sơ.
    - Nếu đã có hồ sơ, sẽ cập nhật lại (reset về PENDING).
    - Admin không được phép dùng endpoint này.
    Loại hình kinh doanh: HOUSEHOLD | COOPERATIVE | COMPANY.
    """
    if current_user.type == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin không thể đăng ký hồ sơ người bán"
        )

    # Nâng quyền user mua hàng -> seller khi nộp hồ sơ.
    # Hỗ trợ dữ liệu cũ dùng type='customer'.
    current_type = (current_user.type or "").strip().lower()
    if current_type in {"", "consumer", "customer", "buyer"}:
        current_user.type = "seller"

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

    # Sau mỗi lần nộp/cập nhật hồ sơ, tài khoản về trạng thái chờ duyệt
    current_user.activated = 0
    db.commit()
    db.refresh(profile)

    # [NOTIFICATION K1] Thông báo Admin: có hồ sơ seller mới chờ duyệt
    try:
        admin_ids = [
            u.id for u in db.query(User).filter(User.type == "admin").all()
        ]
        if admin_ids:
            notify_kyc_pending_to_admin(
                db=db,
                admin_user_ids=admin_ids,
                seller_user_id=current_user.id,
                seller_name=current_user.name or "Tài khoản",
                business_name=profile.business_name or "Chưa có tên",
            )
            db.commit()
    except Exception as _e:
        logger.warning("[KYC] Không gửi được notification KYC pending cho admin: %s", _e)

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
    """Xem trạng thái hồ sơ kinh doanh của mình. Admin không được phép."""
    if current_user.type == "admin":
        raise HTTPException(status_code=403, detail="Admin không thể xem hồ sơ này")

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
            seller_type = (seller_user.type or "").strip().lower()
            if seller_type not in {"seller", "producer"}:
                seller_user.type = "seller"
            _sync_verified_seller_role(db, user_id)
    elif data.status == "REJECTED":
        profile.rejection_reason = data.rejection_reason
        if seller_user:
            seller_user.activated = 0

    db.commit()

    # [NOTIFICATION K2/K3] Thông báo cho Seller kết quả duyệt hồ sơ
    try:
        if data.status == "VERIFIED":
            notify_kyc_verified_to_seller(db=db, seller_id=user_id)
        else:
            notify_kyc_rejected_to_seller(
                db=db,
                seller_id=user_id,
                rejection_reason=data.rejection_reason or "Không đáp ứng yêu cầu",
            )
        db.commit()
    except Exception as _e:
        logger.warning("[KYC] Không gửi được notification KYC verify/reject cho seller: %s", _e)

    return {
        "success": True,
        "message": f"Hồ sơ đã được {'xác minh' if data.status == 'VERIFIED' else 'từ chối'}",
        "data": {
            "user_id": user_id,
            "status": data.status,
            "rejection_reason": data.rejection_reason if data.status == "REJECTED" else None
        }
    }


@router.get("/applications/{user_id}", summary="Admin xem chi tiết hồ sơ seller")
async def get_seller_application_detail(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền")

    profile = db.query(SellerProfile).filter(
        SellerProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Hồ sơ seller không tồn tại")

    user = db.query(User).filter(User.id == user_id).first()
    return {
        "success": True,
        "data": _profile_to_response_data(profile, user),
    }


@router.put("/applications/{user_id}", summary="Admin cập nhật hồ sơ seller")
async def update_seller_application_detail(
    user_id: int,
    data: AdminUpdateSellerProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền")

    profile = db.query(SellerProfile).filter(
        SellerProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Hồ sơ seller không tồn tại")

    _apply_request_to_profile(profile, data)
    db.commit()
    db.refresh(profile)

    user = db.query(User).filter(User.id == user_id).first()
    return {
        "success": True,
        "message": "Đã cập nhật hồ sơ seller",
        "data": _profile_to_response_data(profile, user),
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
        data_list.append(_profile_to_response_data(p, user))

    return {
        "success": True,
        "data": data_list,
        "meta": {"total": total, "page": page, "limit": limit}
    }
