from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    """Nhật ký hoạt động để admin trace"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Null for system actions

    action = Column(String(100), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    entity_type = Column(String(100), nullable=False, index=True)  # USER, PRODUCT, ORDER, etc.
    entity_id = Column(Integer, nullable=True, index=True)

    # Changes
    old_value = Column(Text, nullable=True)  # JSON snapshot before
    new_value = Column(Text, nullable=True)  # JSON snapshot after

    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, etc.
    request_path = Column(String(500), nullable=True)

    # Additional context
    description = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON for extra data

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", foreign_keys=[user_id])
