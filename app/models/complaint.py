from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ComplaintStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class ModerationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Purchase verification
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True, index=True)

    # Ratings
    rating = Column(Integer, nullable=False)  # 1-5 (product)
    seller_rating = Column(Integer, nullable=True)  # 1-5 (seller rating riêng)

    # Review content
    comment = Column(Text, nullable=True)

    # Moderation
    moderation_status = Column(SQLEnum(ModerationStatus), default=ModerationStatus.PENDING, index=True)
    moderated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime(timezone=True), nullable=True)
    moderation_note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    user = relationship("User", foreign_keys=[user_id])
    order_item = relationship("OrderItem", foreign_keys=[order_item_id])
    moderator = relationship("User", foreign_keys=[moderated_by])
    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")

    # Unique constraint: một user chỉ review một product một lần
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_user_product_review'),
    )

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)  # Added FK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    complaint_type = Column(String(50), nullable=False, index=True)  # PRODUCT, PAYMENT, SERVICE
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(ComplaintStatus), default=ComplaintStatus.PENDING, index=True)
    handled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id])
    handler = relationship("User", foreign_keys=[handled_by])
    product = relationship("Product", foreign_keys=[product_id])
    order = relationship("Order", foreign_keys=[order_id])

