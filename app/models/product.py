from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ProductStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ProductLabel(str, enum.Enum):
    CLEAN_AGRICULTURE = "CLEAN_AGRICULTURE"  # Nông sản sạch
    TRADITIONAL_CRAFT = "TRADITIONAL_CRAFT"  # Làng nghề truyền thống
    OCOP = "OCOP"  # One Commune One Product

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    producer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.PENDING)
    label = Column(String(50), nullable=True)  # CLEAN_AGRICULTURE, TRADITIONAL_CRAFT, OCOP
    images = Column(Text, nullable=True)  # JSON array of image URLs
    # Inventory management
    stock_quantity = Column(Integer, default=0, nullable=False) # Số lượng tồn kho
    is_active = Column(Boolean, default=True, nullable=False)# Sản phẩm có đang được bán hay không 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    producer = relationship("User", foreign_keys=[producer_id])
    category = relationship("Category", foreign_keys=[category_id], back_populates="products")

class ProductApproval(Base):
    __tablename__ = "product_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(ProductStatus), nullable=False)
    notes = Column(Text, nullable=True)
    checked_description = Column(Boolean, default=False)
    checked_price = Column(Boolean, default=False)
    checked_images = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", foreign_keys=[product_id])
    approver = relationship("User", foreign_keys=[approver_id])

