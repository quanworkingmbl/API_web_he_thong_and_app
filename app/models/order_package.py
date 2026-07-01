from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class OrderPackageStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chờ xác nhận
    CONFIRMED = "CONFIRMED"       # Đã xác nhận
    PROCESSING = "PROCESSING"     # Đang xử lý
    SHIPPING = "SHIPPING"         # Đang giao hàng
    DELIVERED = "DELIVERED"       # Đã giao hàng
    CANCELLED = "CANCELLED"       # Đã hủy
    REFUNDED = "REFUNDED"         # Đã hoàn tiền


class OrderPackage(Base):
    """
    Package/Sub-order theo seller - cho phép một đơn hàng có nhiều seller
    Mỗi package thuộc một seller và chứa các items của seller đó
    """
    __tablename__ = "order_packages"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True, index=True)

    # Package amounts
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    shipping_fee = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)

    # Platform commission
    platform_fee_percentage = Column(Numeric(5, 2), nullable=False, default=5.0)
    platform_fee_amount = Column(Numeric(10, 2), nullable=False, default=0)
    seller_amount = Column(Numeric(15, 2), nullable=False, default=0)

    # Status
    status = Column(SQLEnum(OrderPackageStatus), default=OrderPackageStatus.PENDING)

    # Tracking
    tracking_code = Column(String(100), nullable=True, index=True)

    # Notes
    seller_note = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    order = relationship("Order", foreign_keys=[order_id], backref="packages")
    seller = relationship("User", foreign_keys=[seller_id])
    store = relationship("Store", foreign_keys=[store_id])
