from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Permission(Base):
    """Quyền hạn chi tiết trong hệ thống"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)

    # Permission info
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False, index=True)  # VD: product.create, order.view
    module = Column(String(100), nullable=False, index=True)  # VD: product, order, user
    description = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RolePermission(Base):
    """Liên kết giữa Role và Permission"""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("Role", foreign_keys=[role_id])
    permission = relationship("Permission", foreign_keys=[permission_id])
