from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentCycle(str, enum.Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Payment details
    provider = Column(String(50), nullable=True)  # MOMO, VNPAY, ZALOPAY, BANK_TRANSFER
    transaction_id = Column(String(255), unique=True, index=True, nullable=True)
    currency = Column(String(3), default="VND", nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    # Platform fee
    platform_fee_percentage = Column(Numeric(5, 2), default=5.0)
    platform_fee_amount = Column(Numeric(10, 2), nullable=False)
    seller_amount = Column(Numeric(10, 2), nullable=False)

    # Status and timestamps
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Gateway response
    failure_reason = Column(Text, nullable=True)
    raw_response = Column(Text, nullable=True)  # JSON response from gateway
    capture_id = Column(String(255), nullable=True)  # For capture transactions
    refund_id = Column(String(255), nullable=True)  # For refund transactions

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("User", foreign_keys=[customer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    transactions = relationship("PaymentTransaction", back_populates="payment")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # PAYMENT, REFUND, TRANSFER

    # Transaction details
    provider_ref = Column(String(255), nullable=True)  # Provider's transaction reference
    request_id = Column(String(255), nullable=True)  # Internal request ID for idempotency
    currency = Column(String(3), default="VND", nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    exchange_rate = Column(Numeric(15, 6), nullable=True)  # For multi-currency
    provider_fee = Column(Numeric(10, 2), nullable=True)  # Fee charged by payment provider

    status = Column(SQLEnum(PaymentStatus), nullable=False, index=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)  # When funds were settled
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    payment = relationship("Payment", back_populates="transactions")

