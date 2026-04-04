from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ShippingRate(Base):
    """Bảng giá vận chuyển theo provider, service, tuyến đường"""
    __tablename__ = "shipping_rates"

    id = Column(Integer, primary_key=True, index=True)

    # Provider and service
    provider = Column(String(50), nullable=False, index=True)  # GHN, GHTK, VNPOST
    service_code = Column(String(50), nullable=False, index=True)  # EXPRESS, STANDARD

    # Route
    origin_province = Column(String(20), nullable=True, index=True)
    destination_province = Column(String(20), nullable=True, index=True)

    # Pricing
    base_rate = Column(Numeric(10, 2), nullable=False)  # Giá cơ bản
    per_kg_rate = Column(Numeric(10, 2), nullable=False, default=0)  # Giá mỗi kg
    sla_days = Column(Integer, nullable=True)  # Thời gian giao hàng (ngày)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ShippingServiceType(Base):
    """Các dịch vụ vận chuyển có sẵn"""
    __tablename__ = "shipping_services"

    id = Column(Integer, primary_key=True, index=True)

    # Provider and service
    provider = Column(String(50), nullable=False, index=True)
    service_code = Column(String(50), nullable=False, index=True)
    service_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
