from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Address(Base):
    """Địa chỉ khách hàng và người bán"""
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Address type
    address_type = Column(String(20), nullable=False)  # BILLING, SHIPPING, PICKUP

    # Address details
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address_line1 = Column(Text, nullable=False)
    address_line2 = Column(Text, nullable=True)

    # Administrative divisions
    province_id = Column(Integer, nullable=True)
    province_name = Column(String(100), nullable=True)
    district_id = Column(Integer, nullable=True)
    district_name = Column(String(100), nullable=True)
    ward_id = Column(Integer, nullable=True)
    ward_name = Column(String(100), nullable=True)

    postal_code = Column(String(20), nullable=True)

    # Flags
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id])
