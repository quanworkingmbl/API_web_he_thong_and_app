from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Cart(Base):
    """Giỏ hàng của người dùng (server-side)"""
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for guest carts
    session_key = Column(String(255), nullable=True, index=True)  # For guest cart identification

    # Multi-currency support
    currency = Column(String(3), default="VND", nullable=False)

    # Promotion tracking
    applied_promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id])
    applied_promotion = relationship("Promotion", foreign_keys=[applied_promotion_id])
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    """Chi tiết từng sản phẩm trong giỏ hàng"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For seller grouping
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)  # Snapshot giá tại thời điểm thêm
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", foreign_keys=[product_id])
    seller = relationship("User", foreign_keys=[seller_id])
