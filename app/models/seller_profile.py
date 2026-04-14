from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class BusinessType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"       # Cá nhân kinh doanh
    HOUSEHOLD = "HOUSEHOLD"         # Hộ kinh doanh gia đình
    COOPERATIVE = "COOPERATIVE"     # Hợp tác xã
    COMPANY = "COMPANY"             # Doanh nghiệp / Công ty


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"             # Chờ xét duyệt
    VERIFIED = "VERIFIED"           # Đã xác minh
    REJECTED = "REJECTED"           # Từ chối


class SellerProfile(Base):
    """Hồ sơ kinh doanh của người bán – dùng cho onboarding & xác minh danh tính"""
    __tablename__ = "seller_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Thông tin kinh doanh
    business_name = Column(String(255), nullable=False)         # Tên cơ sở / shop
    business_type = Column(SQLEnum(BusinessType), default=BusinessType.HOUSEHOLD)
    description = Column(Text, nullable=True)                   # Mô tả cơ sở
    address = Column(Text, nullable=True)                       # Địa chỉ cơ sở

    # Store slug and contact
    slug = Column(String(255), unique=True, nullable=True, index=True)  # URL cửa hàng
    shop_phone = Column(String(20), nullable=True)
    shop_email = Column(String(255), nullable=True)

    # Địa chỉ lấy hàng chuẩn hóa
    pickup_address_id = Column(Integer, ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)

    # Giấy tờ xác minh
    id_card_number = Column(String(20), nullable=True)          # CCCD / CMND
    id_card_front_url = Column(Text, nullable=True)             # Ảnh mặt trước CCCD
    id_card_back_url = Column(Text, nullable=True)              # Ảnh mặt sau CCCD
    business_license_url = Column(Text, nullable=True)          # Giấy phép kinh doanh

    # Tax and business registration
    tax_id = Column(String(50), nullable=True, index=True)      # Mã số thuế (MST)
    business_registration_number = Column(String(50), nullable=True)  # Số đăng ký kinh doanh

    # Tài khoản ngân hàng
    bank_name = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_account_name = Column(String(255), nullable=True)

    # Trạng thái xác minh
    verification_status = Column(
        SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, index=True
    )
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])
