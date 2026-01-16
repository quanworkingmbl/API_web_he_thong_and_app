from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class PermissionType(str, enum.Enum):
    CATALOGUE = "CATALOGUE"
    MENU = "MENU"

class PermissionStatus(str, enum.Enum):
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("permissions.id"), nullable=True)
    name = Column(String(255), unique=True, nullable=False)
    label = Column(String(255), nullable=False)
    type = Column(SQLEnum(PermissionType), nullable=False)
    route = Column(String(255), nullable=True)
    status = Column(String(50), default="ENABLE")
    order = Column(Integer, default=0)
    icon = Column(String(255), nullable=True)
    component = Column(String(255), nullable=True)
    hide = Column(Boolean, default=False)
    hide_tab = Column(Boolean, default=False)
    frame_src = Column(String(500), nullable=True)
    new_feature = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Self-referential relationship for parent-child
    parent = relationship("Permission", remote_side=[id], backref="children")
    roles = relationship("RolePermission", back_populates="permission")

