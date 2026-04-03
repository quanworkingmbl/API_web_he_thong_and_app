from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Store(Base):
    """Cửa hàng/Shop settings cho người bán"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Store branding
    store_name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    logo_url = Column(Text, nullable=True)
    banner_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # Store policies
    return_policy = Column(Text, nullable=True)
    shipping_policy = Column(Text, nullable=True)
    terms_of_service = Column(Text, nullable=True)

    # Operating hours (JSON)
    business_hours = Column(Text, nullable=True)  # JSON: {"monday": "9:00-18:00", ...}

    # Pickup address
    pickup_address = Column(Text, nullable=True)
    pickup_province_id = Column(Integer, nullable=True)
    pickup_district_id = Column(Integer, nullable=True)
    pickup_ward_id = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
