from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ReturnType(str, enum.Enum):
    RETURN = "RETURN"         # Trả hàng hoàn tiền
    EXCHANGE = "EXCHANGE"     # Đổi hàng


class ReturnStatus(str, enum.Enum):
    PENDING = "PENDING"                   # Chờ seller xét duyệt
    SELLER_APPROVED = "SELLER_APPROVED"   # Seller đồng ý → chờ admin xác nhận nhận hàng
    SELLER_REJECTED = "SELLER_REJECTED"   # Seller từ chối → escalate lên admin
    APPROVED = "APPROVED"                 # Admin duyệt (override seller từ chối)
    REJECTED = "REJECTED"                 # Admin từ chối (cuối cùng)
    CANCELLED = "CANCELLED"               # Khách hàng đã hủy
    RECEIVED = "RECEIVED"                 # Đã nhận hàng trả về
    REFUNDED = "REFUNDED"                 # Đã hoàn tiền (cho RETURN)
    EXCHANGED = "EXCHANGED"               # Đã gửi hàng đổi (cho EXCHANGE)



class ReturnRequest(Base):
    """Yêu cầu đổi/trả hàng của khách hàng"""
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Item-level return support
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True, index=True)

    return_type = Column(SQLEnum(ReturnType), nullable=False, default=ReturnType.RETURN)
    reason = Column(Text, nullable=False)
    images = Column(Text, nullable=True)  # JSON array of image URLs làm chứng cứ

    # Refund info
    refund_amount = Column(String(20), nullable=True)  # Số tiền hoàn
    refund_method = Column(String(50), nullable=True)  # ORIGINAL, BANK_TRANSFER, WALLET

    # Seller return address
    seller_return_address_id = Column(Integer, nullable=True)  # FK to addresses
    return_shipping_code = Column(String(100), nullable=True)  # Mã vận đơn trả hàng

    status = Column(SQLEnum(ReturnStatus), default=ReturnStatus.PENDING, index=True)
    admin_note = Column(Text, nullable=True)

    # Seller handling (bước 1: seller xử lý trước)
    seller_note = Column(Text, nullable=True)
    seller_handled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    seller_handled_at = Column(DateTime(timezone=True), nullable=True)

    # Admin handling (bước 2: admin xác nhận hoặc override)
    handled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    handled_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order = relationship("Order", foreign_keys=[order_id])
    user = relationship("User", foreign_keys=[user_id])
    order_item = relationship("OrderItem", foreign_keys=[order_item_id])
    handler = relationship("User", foreign_keys=[handled_by])
    approver = relationship("User", foreign_keys=[approved_by])
