from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PromotionUsage(Base):
    """Theo dõi việc sử dụng mã khuyến mãi"""
    __tablename__ = "promotion_usages"

    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # Usage tracking
    discount_applied = Column(Integer, nullable=False)  # Actual discount amount
    used_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    promotion = relationship("Promotion", foreign_keys=[promotion_id])
    user = relationship("User", foreign_keys=[user_id])
    order = relationship("Order", foreign_keys=[order_id])
