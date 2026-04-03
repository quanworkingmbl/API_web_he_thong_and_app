from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SubOrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPING = "SHIPPING"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class SubOrder(Base):
    """Đơn hàng con cho từng người bán (multi-seller support)"""
    __tablename__ = "sub_orders"

    id = Column(Integer, primary_key=True, index=True)
    master_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    sub_order_number = Column(String(50), unique=True, nullable=False, index=True)

    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Amounts for this sub-order
    currency = Column(String(3), default="VND", nullable=False)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    shipping_fee = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)

    # Platform commission
    platform_fee_percentage = Column(Numeric(5, 2), nullable=False, default=5.0)
    platform_fee_amount = Column(Numeric(10, 2), nullable=False, default=0)
    seller_amount = Column(Numeric(15, 2), nullable=False, default=0)

    # Status
    status = Column(SQLEnum(SubOrderStatus), default=SubOrderStatus.PENDING, index=True)
    payment_status = Column(String(20), default="UNPAID", index=True)

    # Notes
    seller_note = Column(Text, nullable=True)
    admin_note = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    master_order = relationship("Order", foreign_keys=[master_order_id])
    seller = relationship("User", foreign_keys=[seller_id])
    items = relationship("SubOrderItem", back_populates="sub_order", cascade="all, delete-orphan")


class SubOrderItem(Base):
    """Chi tiết sản phẩm trong đơn hàng con"""
    __tablename__ = "sub_order_items"

    id = Column(Integer, primary_key=True, index=True)
    sub_order_id = Column(Integer, ForeignKey("sub_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)

    # Product snapshot
    product_name = Column(String(255), nullable=False)
    product_image = Column(Text, nullable=True)
    sku_snapshot = Column(String(100), nullable=True)

    # Pricing & quantity
    unit_price = Column(Numeric(15, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_price = Column(Numeric(15, 2), nullable=False)

    # Fulfillment
    fulfill_status = Column(String(50), nullable=True)  # PENDING, FULFILLED, CANCELLED

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sub_order = relationship("SubOrder", back_populates="items")
    product = relationship("Product", foreign_keys=[product_id])
