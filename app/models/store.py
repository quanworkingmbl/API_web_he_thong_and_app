from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Store(Base):
    """Cửa hàng/chi nhánh của seller - hỗ trợ multi-store per seller"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Thông tin cửa hàng
    store_name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    logo_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # Địa chỉ lấy hàng
    pickup_address = Column(Text, nullable=True)
    pickup_province_code = Column(String(20), nullable=True)
    pickup_district_code = Column(String(20), nullable=True)
    pickup_ward_code = Column(String(20), nullable=True)

    # Liên hệ
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)

    # Cấu hình vận chuyển (JSON)
    shipping_config = Column(Text, nullable=True)  # JSON: free_ship_threshold, shipping_rates, etc.

    # Trạng thái
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    seller = relationship("User", foreign_keys=[seller_id], backref="stores")
