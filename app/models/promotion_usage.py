from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PromotionUsage(Base):
    """Theo dõi việc sử dụng mã khuyến mãi - kiểm soát quota"""
    __tablename__ = "promotion_usages"

    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # Discount applied
    discount_amount = Column(Numeric(12, 2), nullable=False)

    # Timestamp
    used_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    promotion = relationship("Promotion", foreign_keys=[promotion_id])
    user = relationship("User", foreign_keys=[user_id])
    order = relationship("Order", foreign_keys=[order_id])


class OrderPromotion(Base):
    """Liên kết đơn hàng với các mã khuyến mãi (cho multi-promotion per order)"""
    __tablename__ = "order_promotions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Discount amount
    discount_amount = Column(Numeric(12, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", foreign_keys=[order_id])
    promotion = relationship("Promotion", foreign_keys=[promotion_id])
    seller = relationship("User", foreign_keys=[seller_id])
