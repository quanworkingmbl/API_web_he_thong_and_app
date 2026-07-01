from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ShipmentStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chưa tạo vận đơn
    CREATED = "CREATED"           # Đã tạo vận đơn tại đơn vị vận chuyển
    PICKED_UP = "PICKED_UP"       # Đã lấy hàng
    IN_TRANSIT = "IN_TRANSIT"     # Đang vận chuyển
    DELIVERED = "DELIVERED"       # Đã giao hàng thành công
    FAILED = "FAILED"             # Giao hàng thất bại
    RETURNED = "RETURNED"         # Hoàn hàng


class ShippingProvider(str, enum.Enum):
    GHN = "GHN"
    GHTK = "GHTK"
    VNPOST = "VNPOST"
    MANUAL = "MANUAL"  # Seller tự giao


class Shipment(Base):
    """Thông tin vận chuyển cho đơn hàng"""
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)

    # Shipping provider
    provider = Column(SQLEnum(ShippingProvider), default=ShippingProvider.GHN)
    service_code = Column(String(50), nullable=True)  # EXPRESS, STANDARD, etc.

    # Mã vận đơn từ đơn vị vận chuyển
    tracking_code = Column(String(100), nullable=True, index=True)
    provider_order_code = Column(String(100), nullable=True)  # Mã của GHN/GHTK

    # Trạng thái vận chuyển
    status = Column(SQLEnum(ShipmentStatus), default=ShipmentStatus.PENDING, index=True)

    # Shipper info
    shipper_name = Column(String(255), nullable=True)
    shipper_phone = Column(String(20), nullable=True)

    # COD (Cash On Delivery)
    cod_amount = Column(Numeric(10, 2), default=0)

    # Chi phí và thời gian
    fee = Column(Numeric(10, 2), default=0)
    weight = Column(Integer, default=500)  # gram
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)
    actual_delivery = Column(DateTime(timezone=True), nullable=True)

    # Package dimensions
    width = Column(Integer, nullable=True)  # cm
    height = Column(Integer, nullable=True)  # cm
    length = Column(Integer, nullable=True)  # cm
    insurance_value = Column(Numeric(10, 2), nullable=True)

    # Địa chỉ (với FK nếu dùng chuẩn hóa)
    from_address_id = Column(Integer, nullable=True)  # FK to addresses hoặc store pickup
    to_address_id = Column(Integer, nullable=True)  # FK to addresses

    # Địa chỉ text (legacy/snapshot)
    from_address = Column(Text, nullable=True)
    to_address = Column(Text, nullable=True)

    # Webhook signature để validate callbacks từ shipping provider
    webhook_signature = Column(String(255), nullable=True)

    # Note & tracking detail
    note = Column(Text, nullable=True)
    tracking_detail = Column(Text, nullable=True)  # JSON string log tracking

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order = relationship("Order", foreign_keys=[order_id])
