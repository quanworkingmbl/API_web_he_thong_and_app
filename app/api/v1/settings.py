"""
System Settings API — Cấu hình hệ thống
Admin có thể cấu hình:
- VAT mặc định
- Platform fee (hoa hồng sàn)
- Phí vận chuyển mặc định
- Đơn hàng tối thiểu
- Phương thức thanh toán được phép
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field
from decimal import Decimal
import json

router = APIRouter()

# ==============================================================================
# DEFAULT SETTINGS
# ==============================================================================

DEFAULT_SETTINGS = {
    "default_vat_rate": "10.00",               # VAT mặc định 10%
    "platform_fee_percentage": "5.00",          # Hoa hồng sàn 5%
    "shipping_fee_default": "30000",            # Phí ship mặc định 30k
    "min_order_amount": "10000",               # Đơn tối thiểu 10k
    "allowed_payment_methods": json.dumps([    # Phương thức thanh toán
        "COD", "PLATFORM_CREDITS", "BANK_TRANSFER"
    ]),
    "platform_name": "AgriMart",
    "support_email": "support@agrimart.vn",
    "support_phone": "1900-xxxx",
    "maintenance_mode": "false",
    "max_product_images": "10",
    "free_shipping_threshold": "500000",        # Miễn phí ship trên 500k
}


# ==============================================================================
# SCHEMAS
# ==============================================================================

class SystemSettingsResponse(BaseModel):
    default_vat_rate: float = 10.0
    platform_fee_percentage: float = 5.0
    shipping_fee_default: float = 30000.0
    min_order_amount: float = 10000.0
    allowed_payment_methods: List[str] = ["COD", "PLATFORM_CREDITS", "BANK_TRANSFER"]
    platform_name: str = "AgriMart"
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    maintenance_mode: bool = False
    max_product_images: int = 10
    free_shipping_threshold: float = 500000.0


class UpdateSettingsRequest(BaseModel):
    default_vat_rate: Optional[float] = Field(None, ge=0, le=100)
    platform_fee_percentage: Optional[float] = Field(None, ge=0, le=100)
    shipping_fee_default: Optional[float] = Field(None, ge=0)
    min_order_amount: Optional[float] = Field(None, ge=0)
    allowed_payment_methods: Optional[List[str]] = None
    platform_name: Optional[str] = Field(None, max_length=100)
    support_email: Optional[str] = Field(None, max_length=255)
    support_phone: Optional[str] = Field(None, max_length=20)
    maintenance_mode: Optional[bool] = None
    max_product_images: Optional[int] = Field(None, ge=1, le=20)
    free_shipping_threshold: Optional[float] = Field(None, ge=0)


# ==============================================================================
# HELPERS
# ==============================================================================

def _ensure_settings_table(db: Session):
    """Tạo bảng system_settings nếu chưa có"""
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    db.commit()


def _get_setting(db: Session, key: str) -> Optional[str]:
    """Lấy một setting theo key"""
    try:
        result = db.execute(
            text("SELECT value FROM system_settings WHERE key = :key"),
            {"key": key}
        ).fetchone()
        return result[0] if result else None
    except Exception:
        return None


def _get_all_settings(db: Session) -> dict:
    """Lấy toàn bộ settings, merge với defaults"""
    _ensure_settings_table(db)
    settings = dict(DEFAULT_SETTINGS)
    try:
        rows = db.execute(text("SELECT key, value FROM system_settings")).fetchall()
        for row in rows:
            settings[row[0]] = row[1]
    except Exception:
        pass
    return settings


def _set_setting(db: Session, key: str, value: str):
    """Upsert một setting"""
    db.execute(
        text("""
            INSERT INTO system_settings (key, value, updated_at)
            VALUES (:key, :value, NOW())
            ON CONFLICT (key) DO UPDATE
            SET value = :value, updated_at = NOW()
        """),
        {"key": key, "value": value}
    )


def _parse_settings_to_response(raw: dict) -> SystemSettingsResponse:
    """Convert raw dict to typed response"""
    try:
        payment_methods = json.loads(raw.get("allowed_payment_methods", "[]"))
    except Exception:
        payment_methods = ["COD", "PLATFORM_CREDITS", "BANK_TRANSFER"]

    return SystemSettingsResponse(
        default_vat_rate=float(raw.get("default_vat_rate", 10)),
        platform_fee_percentage=float(raw.get("platform_fee_percentage", 5)),
        shipping_fee_default=float(raw.get("shipping_fee_default", 30000)),
        min_order_amount=float(raw.get("min_order_amount", 10000)),
        allowed_payment_methods=payment_methods,
        platform_name=raw.get("platform_name", "AgriMart"),
        support_email=raw.get("support_email"),
        support_phone=raw.get("support_phone"),
        maintenance_mode=raw.get("maintenance_mode", "false").lower() == "true",
        max_product_images=int(raw.get("max_product_images", 10)),
        free_shipping_threshold=float(raw.get("free_shipping_threshold", 500000)),
    )


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("", response_model=SystemSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy cấu hình hệ thống.
    - Admin: xem toàn bộ
    - Seller/Consumer: chỉ xem các thông tin công khai (VAT, phí ship)
    """
    raw = _get_all_settings(db)
    return _parse_settings_to_response(raw)


@router.get("/public")
async def get_public_settings(db: Session = Depends(get_db)):
    """
    Lấy cấu hình công khai — không cần auth.
    Dùng cho mobile app lấy VAT, phí ship, phương thức thanh toán.
    """
    raw = _get_all_settings(db)
    parsed = _parse_settings_to_response(raw)
    return {
        "success": True,
        "data": {
            "default_vat_rate": parsed.default_vat_rate,
            "shipping_fee_default": parsed.shipping_fee_default,
            "min_order_amount": parsed.min_order_amount,
            "allowed_payment_methods": parsed.allowed_payment_methods,
            "platform_name": parsed.platform_name,
            "free_shipping_threshold": parsed.free_shipping_threshold,
            "support_phone": parsed.support_phone,
        }
    }


@router.put("", response_model=SystemSettingsResponse)
async def update_settings(
    data: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật cấu hình hệ thống. Chỉ Admin mới được cập nhật.
    """
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có thể thay đổi cấu hình hệ thống")

    _ensure_settings_table(db)

    fields = data.dict(exclude_none=True)

    for key, value in fields.items():
        if key == "allowed_payment_methods":
            _set_setting(db, key, json.dumps(value))
        elif key == "maintenance_mode":
            _set_setting(db, key, str(value).lower())
        else:
            _set_setting(db, key, str(value))

    db.commit()

    raw = _get_all_settings(db)
    return _parse_settings_to_response(raw)


@router.post("/reset")
async def reset_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset toàn bộ cấu hình về mặc định. Chỉ Admin."""
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có thể reset cấu hình")

    _ensure_settings_table(db)
    db.execute(text("DELETE FROM system_settings"))
    db.commit()

    return {"success": True, "message": "Đã reset cấu hình về mặc định"}
