from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AddressType(str, enum.Enum):
    SHIPPING = "SHIPPING"  # Địa chỉ giao hàng
    BILLING = "BILLING"    # Địa chỉ thanh toán


class Province(Base):
    """Tỉnh/Thành phố"""
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class District(Base):
    """Quận/Huyện"""
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    province_code = Column(String(20), ForeignKey("provinces.code"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    province = relationship("Province", foreign_keys=[province_code])


class Ward(Base):
    """Phường/Xã"""
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    district_code = Column(String(20), ForeignKey("districts.code"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    district = relationship("District", foreign_keys=[district_code])


class Address(Base):
    """Sổ địa chỉ của người dùng"""
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Loại địa chỉ
    address_type = Column(SQLEnum(AddressType), default=AddressType.SHIPPING, nullable=False)

    # Thông tin người nhận
    recipient_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    # Địa chỉ chuẩn hóa
    province_code = Column(String(20), ForeignKey("provinces.code"), nullable=True, index=True)
    district_code = Column(String(20), ForeignKey("districts.code"), nullable=True, index=True)
    ward_code = Column(String(20), ForeignKey("wards.code"), nullable=True, index=True)
    address_line = Column(Text, nullable=False)  # Số nhà, tên đường

    # Địa chỉ mặc định
    is_default = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="addresses")
    province = relationship("Province", foreign_keys=[province_code])
    district = relationship("District", foreign_keys=[district_code])
    ward = relationship("Ward", foreign_keys=[ward_code])
