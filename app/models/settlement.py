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
    reserve_balance   = Column(Numeric(15, 2), default=0, nullable=False)  # 20% giữ lại 30 ngày bảo lãnh
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
