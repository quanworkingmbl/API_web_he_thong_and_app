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
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Payment gateway integration
    payment_method_id = Column(Integer, nullable=True, index=True)  # FK to payment_methods
    gateway_transaction_id = Column(String(255), nullable=True, index=True)  # Mã giao dịch từ cổng
    payment_channel = Column(String(50), nullable=True)  # card, bank, wallet, cod

    # Amount and currency
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="VND", nullable=False)

    # Platform fee
    platform_fee_percentage = Column(Numeric(5, 2), default=5.0)
    platform_fee_amount = Column(Numeric(10, 2), nullable=False)
    seller_amount = Column(Numeric(10, 2), nullable=False)

    # Card/Bank details (if applicable)
    card_brand = Column(String(50), nullable=True)  # Visa, Mastercard, JCB
    bank_code = Column(String(50), nullable=True)  # Bank code nếu chuyển khoản

    # Status and error handling
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    failure_code = Column(String(50), nullable=True)
    failure_message = Column(Text, nullable=True)

    # Gateway response (for debugging)
    gateway_response = Column(Text, nullable=True)  # JSON full response từ gateway

    # Legacy field
    payment_cycle = Column(SQLEnum(PaymentCycle), default=PaymentCycle.WEEKLY)

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
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(PaymentStatus), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    payment = relationship("Payment", back_populates="transactions")

