from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PaymentProvider(Base):
    """Nhà cung cấp cổng thanh toán - VNPAY, MOMO, ZALOPAY, etc."""
    __tablename__ = "payment_providers"

    id = Column(Integer, primary_key=True, index=True)

    # Provider info
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)  # VNPAY, MOMO, ZALOPAY

    # API configuration
    api_endpoint = Column(Text, nullable=True)
    config = Column(Text, nullable=True)  # JSON: api_key, merchant_id, etc. (encrypted)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PaymentMethodType(Base):
    """Loại phương thức thanh toán"""
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("payment_providers.id"), nullable=True, index=True)

    # Method info
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)  # COD, BANK_TRANSFER, MOMO, etc.
    description = Column(Text, nullable=True)

    # Configuration
    config = Column(Text, nullable=True)  # JSON: fees, limits, etc.

    # Display
    icon_url = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    provider = relationship("PaymentProvider", foreign_keys=[provider_id])


class OrderAdjustment(Base):
    """Điều chỉnh đơn hàng - thuế, phí, giảm giá, hoàn tiền chi tiết"""
    __tablename__ = "order_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # Loại điều chỉnh
    adjustment_type = Column(String(50), nullable=False, index=True)  # TAX, FEE, DISCOUNT, REFUND, SHIPPING

    # Amount
    amount = Column(String(20), nullable=False)  # Sử dụng String để tránh precision issues
    description = Column(Text, nullable=True)

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", foreign_keys=[order_id])
    creator = relationship("User", foreign_keys=[created_by])
