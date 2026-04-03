from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Warehouse(Base):
    """Kho hàng / Địa điểm fulfillment"""
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Null for platform warehouses

    warehouse_name = Column(String(255), nullable=False)
    warehouse_code = Column(String(50), unique=True, nullable=False, index=True)

    # Address
    address = Column(Text, nullable=False)
    province_id = Column(Integer, nullable=True)
    province_name = Column(String(100), nullable=True)
    district_id = Column(Integer, nullable=True)
    district_name = Column(String(100), nullable=True)
    ward_id = Column(Integer, nullable=True)
    ward_name = Column(String(100), nullable=True)

    # Contact
    contact_person = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)

    # Flags
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
