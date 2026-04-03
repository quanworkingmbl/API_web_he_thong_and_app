from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ReturnType(str, enum.Enum):
    RETURN = "RETURN"         # Trả hàng hoàn tiền
    EXCHANGE = "EXCHANGE"     # Đổi hàng


class ReturnStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chờ xét duyệt
    APPROVED = "APPROVED"         # Đã duyệt – cần gửi hàng về
    REJECTED = "REJECTED"         # Từ chối
    CANCELLED = "CANCELLED"       # Khách hàng đã hủy
    RECEIVED = "RECEIVED"         # Đã nhận hàng trả về
    REFUNDED = "REFUNDED"         # Đã hoàn tiền (cho RETURN)
    EXCHANGED = "EXCHANGED"       # Đã gửi hàng đổi (cho EXCHANGE)



class ReturnRequest(Base):
    """Yêu cầu đổi/trả hàng của khách hàng"""
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True)  # Specific item
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    return_type = Column(SQLEnum(ReturnType), nullable=False, default=ReturnType.RETURN)
    reason = Column(Text, nullable=False)
    images = Column(Text, nullable=True)  # JSON array of image URLs làm chứng cứ

    # Item details
    quantity = Column(Integer, nullable=True)  # Số lượng đổi/trả
    refund_amount = Column(Numeric(15, 2), nullable=True)  # Số tiền hoàn
    resolution_option = Column(String(50), nullable=True)  # REFUND, EXCHANGE, STORE_CREDIT

    # Pickup information
    pickup_address = Column(Text, nullable=True)  # Địa chỉ lấy hàng trả

    status = Column(SQLEnum(ReturnStatus), default=ReturnStatus.PENDING, index=True)
    admin_note = Column(Text, nullable=True)
    handled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    handled_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order = relationship("Order", foreign_keys=[order_id])
    user = relationship("User", foreign_keys=[user_id])
    handler = relationship("User", foreign_keys=[handled_by])
