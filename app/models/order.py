from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, Enum as SQLEnum
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
    PLATFORM_CREDITS = "PLATFORM_CREDITS"  # Tiền sàn (credits)



class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer info
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255), nullable=True)
    
    # Shipping address
    shipping_address = Column(Text, nullable=False)
    shipping_province = Column(String(100), nullable=True)
    shipping_district = Column(String(100), nullable=True)
    shipping_ward = Column(String(100), nullable=True)
    
    # Seller info
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order amounts
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    shipping_fee = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    # VAT – tính từ vat_rate của từng sản phẩm (VAT included trong giá niêm yết)
    # Platform giữ để nộp thuế thay seller. Đơn cũ = 0 (grandfathered).
    vat_amount = Column(Numeric(10, 2), nullable=False, default=0)

    # Platform commission
    platform_fee_percentage = Column(Numeric(5, 2), nullable=False, default=10.0)
    platform_fee_amount = Column(Numeric(10, 2), nullable=False, default=0)
    seller_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Status and payment
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.COD)
    payment_status = Column(String(20), default="UNPAID")  # UNPAID, PAID, REFUNDED

    # Multi-seller & payment gateway fields
    currency = Column(String(3), default="VND", nullable=False)  # VND, USD, etc.
    channel = Column(String(50), nullable=True)  # WEB, MOBILE_APP, THIRD_PARTY
    coupon_code = Column(String(50), nullable=True)  # Mã coupon đã sử dụng
    tax_breakdown = Column(Text, nullable=True)  # JSON breakdown của thuế
    fee_breakdown = Column(Text, nullable=True)  # JSON breakdown của phí

    # Notes
    customer_note = Column(Text, nullable=True)
    seller_note = Column(Text, nullable=True)
    admin_note = Column(Text, nullable=True)
    cancel_reason = Column(Text, nullable=True)
    
    # Soft-delete
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Đã cộng tiền vào ví seller chưa (chống double-credit)
    wallet_credited = Column(Boolean, default=False, nullable=False, index=True)


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
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # Multi-seller support
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Seller của item này
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    package_id = Column(Integer, ForeignKey("order_packages.id", ondelete="SET NULL"), nullable=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True)

    # Product snapshot (giữ thông tin tại thời điểm đặt hàng)
    product_name = Column(String(255), nullable=False)
    product_image = Column(Text, nullable=True)
    unit_price = Column(Numeric(15, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Numeric(15, 2), nullable=False)

    # Item-level pricing breakdown
    tax_amount = Column(Numeric(10, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)

    # Item-level tracking
    tracking_code = Column(String(100), nullable=True)  # Nếu item giao riêng

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    seller = relationship("User", foreign_keys=[seller_id])
    variant = relationship("ProductVariant", foreign_keys=[variant_id])
    store = relationship("Store", foreign_keys=[store_id])
    package = relationship("OrderPackage", foreign_keys=[package_id])


# ==============================================================================
# ORDER STATUS AUDIT LOG
# ==============================================================================

class OrderStatusLog(Base):
    """
    Audit log mỗi lần trạng thái đơn hàng thay đổi.
    Ghi lại: ai thay đổi, từ trạng thái nào sang trạng thái nào, khi nào.
    """
    __tablename__ = "order_status_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    old_status = Column(String(30), nullable=True)   # None khi tạo mới
    new_status = Column(String(30), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # None = system/webhook
    role = Column(String(30), nullable=True)          # consumer / seller / admin / system
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    order = relationship("Order", foreign_keys=[order_id])
    actor = relationship("User", foreign_keys=[actor_id])
