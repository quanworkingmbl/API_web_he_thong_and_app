from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SettlementStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"


class PayoutStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class WithdrawalStatus(str, enum.Enum):
    PENDING = "PENDING"       # Seller vừa tạo, chờ admin duyệt
    APPROVED = "APPROVED"     # Admin duyệt → đang chuyển khoản
    COMPLETED = "COMPLETED"   # Chuyển khoản thành công
    REJECTED = "REJECTED"     # Admin từ chối


class SellerWallet(Base):
    """Ví người bán – theo dõi số dư"""
    __tablename__ = "seller_wallets"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Số dư
    pending_balance   = Column(Numeric(15, 2), default=0, nullable=False)  # Legacy – chờ buyer xác nhận
    available_balance = Column(Numeric(15, 2), default=0, nullable=False)  # 80% seller_amount – có thể rút
    reserve_balance   = Column(Numeric(15, 2), default=0, nullable=False)  # 20% giữ lại 7 ngày bảo lãnh
    total_withdrawn   = Column(Numeric(15, 2), default=0, nullable=False)  # Tổng đã rút ra

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])


class Settlement(Base):
    """Kỳ đối soát – tổng hợp doanh thu theo kỳ"""
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    total_orders = Column(Integer, default=0, nullable=False)
    total_amount = Column(Numeric(15, 2), default=0, nullable=False)
    total_platform_fee = Column(Numeric(15, 2), default=0, nullable=False)
    total_seller_amount = Column(Numeric(15, 2), default=0, nullable=False)

    status = Column(SQLEnum(SettlementStatus), default=SettlementStatus.PENDING)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
    approver = relationship("User", foreign_keys=[approved_by])
    payouts = relationship("Payout", back_populates="settlement")


class Payout(Base):
    """Chi trả cho seller (gắn với Settlement)"""
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    settlement_id = Column(Integer, ForeignKey("settlements.id"), nullable=True)

    amount = Column(Numeric(15, 2), nullable=False)
    bank_name = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_account_name = Column(String(255), nullable=True)

    status = Column(SQLEnum(PayoutStatus), default=PayoutStatus.PENDING)
    transaction_ref = Column(String(255), nullable=True)
    note = Column(Text, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
    processor = relationship("User", foreign_keys=[processed_by])
    settlement = relationship("Settlement", back_populates="payouts")


class WithdrawalRequest(Base):
    """Yêu cầu rút tiền — seller tự tạo, admin duyệt/từ chối"""
    __tablename__ = "withdrawal_requests"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount = Column(Numeric(15, 2), nullable=False)               # Số tiền muốn rút
    available_snapshot = Column(Numeric(15, 2), nullable=True)    # available_balance lúc tạo
    min_reserve_snapshot = Column(Numeric(15, 2), nullable=True)  # min_reserve lúc tạo

    # Snapshot thông tin ngân hàng từ seller_profile
    bank_name = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_account_name = Column(String(255), nullable=True)

    status = Column(SQLEnum(WithdrawalStatus), default=WithdrawalStatus.PENDING, nullable=False)
    note = Column(Text, nullable=True)          # Ghi chú của seller
    admin_note = Column(Text, nullable=True)    # Lý do từ chối / ghi chú admin
    transaction_ref = Column(String(255), nullable=True)

    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


# ==============================================================================
# VÍ SÀN — Ký quỹ seller (Platform Deposit Wallet)
# ==============================================================================

class DepositTransactionType(str, enum.Enum):
    TOP_UP = "TOP_UP"    # Seller nạp tiền vào
    DEDUCT = "DEDUCT"    # Admin khấu trừ (xử lý gian lận / hoàn tiền buyer)
    REFUND = "REFUND"    # Hoàn lại cho seller khi rời sàn


class DepositStatus(str, enum.Enum):
    PENDING   = "PENDING"    # Chờ admin xác nhận (chuyển khoản) hoặc chờ VNPay callback
    CONFIRMED = "CONFIRMED"  # Đã xác nhận, cộng vào deposit_balance
    REJECTED  = "REJECTED"   # Admin từ chối (chuyển khoản lỗi)


class SellerDepositWallet(Base):
    """Ký quỹ của seller — cọc bảo lãnh chống gian lận.
    
    Seller phải duy trì deposit_balance >= MIN_DEPOSIT_REQUIRED (500,000đ)
    để được phép đăng sản phẩm và nhận đơn hàng trên sàn.
    """
    __tablename__ = "seller_deposit_wallets"

    id              = Column(Integer, primary_key=True, index=True)
    seller_id       = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    deposit_balance = Column(Numeric(15, 2), default=0, nullable=False)   # Số dư ký quỹ hiện tại
    total_deposited = Column(Numeric(15, 2), default=0, nullable=False)   # Tổng đã nạp (lịch sử)
    total_deducted  = Column(Numeric(15, 2), default=0, nullable=False)   # Tổng bị khấu trừ (lịch sử)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])


class DepositTransaction(Base):
    """Lịch sử giao dịch ký quỹ — mỗi lần nạp / khấu trừ / hoàn tiền."""
    __tablename__ = "deposit_transactions"

    id        = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    amount  = Column(Numeric(15, 2), nullable=False)
    tx_type = Column(SQLEnum(DepositTransactionType), nullable=False, default=DepositTransactionType.TOP_UP)
    status  = Column(SQLEnum(DepositStatus), nullable=False, default=DepositStatus.PENDING, index=True)

    # Phương thức nạp tiền
    payment_method = Column(String(50), nullable=True)   # "BANK_TRANSFER" | "VNPAY"

    # Chuyển khoản thủ công
    bank_ref    = Column(String(255), nullable=True)   # Mã tham chiếu chuyển khoản
    receipt_url = Column(Text, nullable=True)          # URL ảnh biên lai (upload qua /medias)

    # VNPay
    vnpay_txn_ref  = Column(String(255), nullable=True, index=True)  # vnp_TxnRef = "DEP_{id}_{ts}"
    vnpay_response = Column(Text, nullable=True)                      # Raw JSON callback

    # Admin review
    note        = Column(Text, nullable=True)          # Admin ghi chú khi duyệt / từ chối
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller   = relationship("User", foreign_keys=[seller_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
