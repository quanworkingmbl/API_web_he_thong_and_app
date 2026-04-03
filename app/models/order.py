from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chờ xác nhận
    CONFIRMED = "CONFIRMED"       # Đã xác nhận
    PROCESSING = "PROCESSING"     # Đang xử lý
    SHIPPING = "SHIPPING"         # Đang giao hàng
    DELIVERED = "DELIVERED"       # Đã giao hàng
    CANCELLED = "CANCELLED"       # Đã hủy
    REFUNDED = "REFUNDED"         # Đã hoàn tiền


class PaymentMethod(str, enum.Enum):
    COD = "COD"                   # Thanh toán khi nhận hàng
    BANK_TRANSFER = "BANK_TRANSFER"  # Chuyển khoản ngân hàng
    MOMO = "MOMO"                 # Ví MoMo
    VNPAY = "VNPAY"               # VNPay
    ZALOPAY = "ZALOPAY"           # ZaloPay


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)

    # Customer info
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255), nullable=True)

    # Shipping address (snapshot)
    shipping_address = Column(Text, nullable=False)
    shipping_province = Column(String(100), nullable=True)
    shipping_district = Column(String(100), nullable=True)
    shipping_ward = Column(String(100), nullable=True)

    # Seller info
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Order amounts
    currency = Column(String(3), default="VND", nullable=False)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    shipping_fee = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    tip_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)

    # Platform commission
    platform_fee_percentage = Column(Numeric(5, 2), nullable=False, default=5.0)
    platform_fee_amount = Column(Numeric(10, 2), nullable=False, default=0)
    seller_amount = Column(Numeric(15, 2), nullable=False, default=0)

    # Status and payment
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.COD)
    payment_status = Column(String(20), default="UNPAID", index=True)  # UNPAID, PAID, REFUNDED
    is_cod = Column(Boolean, default=False)  # COD flag

    # Promotion
    voucher_code = Column(String(50), nullable=True)

    # Risk management
    fraud_score = Column(Integer, nullable=True)  # 0-100, higher = more risky

    # Notes
    customer_note = Column(Text, nullable=True)
    seller_note = Column(Text, nullable=True)
    admin_note = Column(Text, nullable=True)
    cancel_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], backref="orders_as_customer")
    seller = relationship("User", foreign_keys=[seller_id], backref="orders_as_seller")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, nullable=True)  # For product variants (future)

    # Product snapshot (giữ thông tin tại thời điểm đặt hàng)
    product_name = Column(String(255), nullable=False)
    product_image = Column(Text, nullable=True)
    sku_snapshot = Column(String(100), nullable=True)  # SKU at time of order

    # Pricing & quantity
    unit_price = Column(Numeric(15, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)  # Tax per line
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)  # Discount per line
    total_price = Column(Numeric(15, 2), nullable=False)

    # Physical attributes
    weight = Column(Numeric(10, 3), nullable=True)  # For shipping calculation

    # Fulfillment
    fulfill_status = Column(String(50), nullable=True)  # PENDING, FULFILLED, CANCELLED

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
