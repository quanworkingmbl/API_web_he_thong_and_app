from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


# ==============================================================================
# ENUMS
# ==============================================================================

class PaymentStatus(str, enum.Enum):
    PENDING   = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED    = "FAILED"
    REFUNDED  = "REFUNDED"
    PARTIAL_REFUNDED = "PARTIAL_REFUNDED"


class PaymentCycle(str, enum.Enum):
    WEEKLY  = "WEEKLY"
    MONTHLY = "MONTHLY"


# ==============================================================================
# PAYMENT
# ==============================================================================

class Payment(Base):
    __tablename__ = "payments"

    id          = Column(Integer, primary_key=True, index=True)
    order_id    = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    seller_id   = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Payment gateway
    payment_method_id      = Column(Integer, nullable=True, index=True)
    gateway_transaction_id = Column(String(255), nullable=True, index=True)   # Mã GD cổng thanh toán
    payment_channel        = Column(String(50),  nullable=True)               # card/bank/wallet/cod

    # ── VNPAY fields (MỚI) ─────────────────────────────────────────────────
    vnpay_transaction_no = Column(String(100), nullable=True, index=True)   # vnp_TransactionNo
    vnpay_response_code  = Column(String(10),  nullable=True)               # vnp_ResponseCode
    vnpay_bank_code      = Column(String(20),  nullable=True)               # vnp_BankCode
    # Idempotency: ngăn xử lý IPN/return trùng
    # Unique constraint trên (order_id, vnpay_transaction_no) – đặt ở table_args

    # Amount
    amount                   = Column(Numeric(15, 2), nullable=False)
    currency                 = Column(String(3), default="VND", nullable=False)
    amount_from_gateway      = Column(Numeric(15, 2), nullable=True)  # Số tiền thực tế gateway trả về
    amount_mismatch          = Column(Boolean, default=False)          # True nếu lệch amount

    # Platform fee
    platform_fee_percentage  = Column(Numeric(5, 2), default=5.0)
    platform_fee_amount      = Column(Numeric(15, 2), nullable=False)
    seller_amount            = Column(Numeric(15, 2), nullable=False)

    # Card/Bank details
    card_brand  = Column(String(50), nullable=True)
    bank_code   = Column(String(50), nullable=True)

    # Status
    status          = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    failure_code    = Column(String(50),  nullable=True)
    failure_message = Column(Text,        nullable=True)

    # Gateway raw response (debug/audit)
    gateway_response = Column(Text, nullable=True)    # JSON full response

    # Refund tracking (MỚI)
    refunded_amount = Column(Numeric(15, 2), nullable=True, default=None)
    refund_note     = Column(Text, nullable=True)
    refunded_at     = Column(DateTime(timezone=True), nullable=True)

    # Legacy
    payment_cycle = Column(SQLEnum(PaymentCycle), default=PaymentCycle.WEEKLY)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer     = relationship("User", foreign_keys=[customer_id])
    seller       = relationship("User", foreign_keys=[seller_id])
    transactions = relationship("PaymentTransaction", back_populates="payment", order_by="PaymentTransaction.created_at")
    audit_logs   = relationship("PaymentAuditLog",   back_populates="payment",  order_by="PaymentAuditLog.timestamp")


# ==============================================================================
# PAYMENT TRANSACTION
# ==============================================================================

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id               = Column(Integer, primary_key=True, index=True)
    payment_id       = Column(Integer, ForeignKey("payments.id"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)    # PAYMENT / REFUND / PARTIAL_REFUND
    amount           = Column(Numeric(15, 2), nullable=False)
    status           = Column(SQLEnum(PaymentStatus), nullable=False)
    gateway_ref      = Column(String(255), nullable=True)    # Mã tham chiếu từ gateway (nếu có)
    notes            = Column(Text, nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())

    payment = relationship("Payment", back_populates="transactions")


# ==============================================================================
# PAYMENT AUDIT LOG (MỚI)
# ==============================================================================

class PaymentAuditLog(Base):
    """
    Audit trail: ghi lại mọi hành động nhạy cảm trên payment
    (refund, update config, force-complete v.v.)
    """
    __tablename__ = "payment_audit_logs"

    id         = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, index=True)
    action     = Column(String(50),  nullable=False)    # REFUND / CONFIG_FEE / CONFIG_CYCLE / IPN_RECEIVED / ...
    actor_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    amount     = Column(Numeric(15, 2), nullable=True)
    note       = Column(Text, nullable=True)
    ip_address = Column(String(50),  nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    payment = relationship("Payment", foreign_keys=[payment_id], back_populates="audit_logs")
    actor   = relationship("User",    foreign_keys=[actor_id])
