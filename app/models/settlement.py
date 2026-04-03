from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SettlementStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chờ đối soát
    APPROVED = "APPROVED"         # Đã duyệt đối soát
    COMPLETED = "COMPLETED"       # Đã chi trả


class PayoutStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chờ xử lý
    PROCESSING = "PROCESSING"     # Đang chuyển tiền
    SUCCESS = "SUCCESS"           # Thành công
    FAILED = "FAILED"             # Thất bại


class SellerWallet(Base):
    """Ví người bán – theo dõi số dư"""
    __tablename__ = "seller_wallets"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Số dư
    pending_balance = Column(Numeric(15, 2), default=0, nullable=False)     # Tiền chờ đối soát
    available_balance = Column(Numeric(15, 2), default=0, nullable=False)   # Tiền khả dụng
    frozen_balance = Column(Numeric(15, 2), default=0, nullable=False)      # Tiền bị phong tỏa
    total_withdrawn = Column(Numeric(15, 2), default=0, nullable=False)     # Tổng đã rút

    last_settled_at = Column(DateTime(timezone=True), nullable=True)        # Lần đối soát gần nhất

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])


class Settlement(Base):
    """Kỳ đối soát – tổng hợp doanh thu theo kỳ"""
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Kỳ đối soát
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Currency
    currency = Column(String(3), default="VND", nullable=False)

    # Thống kê
    total_orders = Column(Integer, default=0, nullable=False)
    total_amount = Column(Numeric(15, 2), default=0, nullable=False)        # Tổng giá trị đơn hàng
    total_platform_fee = Column(Numeric(15, 2), default=0, nullable=False)  # Phí nền tảng
    withholding_tax = Column(Numeric(15, 2), default=0, nullable=False)     # Thuế khấu trừ
    total_seller_amount = Column(Numeric(15, 2), default=0, nullable=False) # Seller nhận

    # References
    statement_ref = Column(String(100), nullable=True)  # Mã sao kê
    reconciliation_status = Column(String(50), nullable=True)  # MATCHED, DISCREPANCY

    status = Column(SQLEnum(SettlementStatus), default=SettlementStatus.PENDING, index=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
    approver = relationship("User", foreign_keys=[approved_by])
    payouts = relationship("Payout", back_populates="settlement")


class Payout(Base):
    """Chi trả cho seller"""
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    settlement_id = Column(Integer, ForeignKey("settlements.id"), nullable=True)

    # Amount & currency
    currency = Column(String(3), default="VND", nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)

    # Thông tin ngân hàng (snapshot)
    bank_name = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_account_name = Column(String(255), nullable=True)

    status = Column(SQLEnum(PayoutStatus), default=PayoutStatus.PENDING, index=True)
    transaction_ref = Column(String(255), nullable=True)  # Mã giao dịch chuyển khoản
    note = Column(Text, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
    processor = relationship("User", foreign_keys=[processed_by])
    settlement = relationship("Settlement", back_populates="payouts")
