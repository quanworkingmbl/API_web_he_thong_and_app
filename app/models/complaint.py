from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ComplaintStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True)  # Verify purchase
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=True)  # Review title
    comment = Column(Text, nullable=True)
    images = Column(Text, nullable=True)  # JSON array of review images

    # Moderation
    moderation_status = Column(String(50), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    user = relationship("User", foreign_keys=[user_id])

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True)  # Specific item
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    complaint_type = Column(String(50), nullable=False, index=True)  # PRODUCT, PAYMENT, SERVICE, SELLER, DELIVERY
    category_type = Column(String(100), nullable=True)  # More specific: WRONG_ITEM, DAMAGED, LATE_DELIVERY
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # SLA tracking
    sla_due_at = Column(DateTime(timezone=True), nullable=True)  # Deadline for resolution

    status = Column(SQLEnum(ComplaintStatus), default=ComplaintStatus.PENDING, index=True)
    handled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id])
    handler = relationship("User", foreign_keys=[handled_by])
    product = relationship("Product", foreign_keys=[product_id])

