from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SettlementItem(Base):
    """Chi tiết các đơn hàng/thanh toán trong một settlement - để audit"""
    __tablename__ = "settlement_items"

    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(Integer, ForeignKey("settlements.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, index=True)

    # Amounts
    order_amount = Column(Numeric(15, 2), nullable=False)  # Tổng đơn hàng
    platform_fee = Column(Numeric(10, 2), nullable=False)  # Phí platform
    seller_amount = Column(Numeric(15, 2), nullable=False)  # Số tiền seller nhận

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    settlement = relationship("Settlement", foreign_keys=[settlement_id])
    order = relationship("Order", foreign_keys=[order_id])
    payment = relationship("Payment", foreign_keys=[payment_id])
