from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    READ = "READ"


class NotificationType(str, enum.Enum):
    ORDER = "ORDER"
    PAYMENT = "PAYMENT"
    SHIPMENT = "SHIPMENT"
    PROMOTION = "PROMOTION"
    SYSTEM = "SYSTEM"
    REVIEW = "REVIEW"


class Notification(Base):
    """Thông báo cho người dùng"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Related entity
    reference_type = Column(String(50), nullable=True)  # ORDER, PAYMENT, etc.
    reference_id = Column(Integer, nullable=True)

    # Channel
    channel = Column(String(50), nullable=False)  # APP, EMAIL, SMS

    # Status
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata (JSON)
    metadata = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
