from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ContentStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ContentAuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DELETE = "DELETE"
    RESTORE = "RESTORE"

class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False)  # POST, PRODUCT_DESCRIPTION, etc.
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    images = Column(Text, nullable=True)  # JSON array
    videos = Column(Text, nullable=True)  # JSON array
    
    # Soft delete fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Approval fields
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    author = relationship("User", foreign_keys=[author_id])
    approver = relationship("User", foreign_keys=[approved_by])
    deleter = relationship("User", foreign_keys=[deleted_by])
    product = relationship("Product", foreign_keys=[product_id])


class ContentAuditLog(Base):
    """Log tất cả hành động trên content để audit"""
    __tablename__ = "content_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    action = Column(SQLEnum(ContentAuditAction), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    content = relationship("Content", foreign_keys=[content_id])
    user = relationship("User", foreign_keys=[user_id])

