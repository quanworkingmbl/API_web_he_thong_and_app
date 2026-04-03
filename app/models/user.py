from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    gender = Column(String(50), nullable=True)
    locale = Column(String(10), default="vi", nullable=True)  # vi, en
    activated = Column(Integer, default=1)  # 1 = active, 0 = inactive
    type = Column(String(50), nullable=True)  # consumer, producer, admin, etc.

    # Authentication & Security
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(String(255), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    roles = relationship("UserRole", back_populates="user")
    organizations = relationship("UserOrganization", back_populates="user")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

class UserOrganization(Base):
    __tablename__ = "user_organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="organizations")
    organization = relationship("Organization", back_populates="users")

