from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ContentStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

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
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    author = relationship("User", foreign_keys=[author_id])
    approver = relationship("User", foreign_keys=[approved_by])
    product = relationship("Product", foreign_keys=[product_id])

