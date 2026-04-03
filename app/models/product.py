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
    slug = Column(String(255), unique=True, index=True, nullable=True)
    description = Column(Text, nullable=True)
    meta_description = Column(String(500), nullable=True)  # SEO meta description

    # Pricing
    price = Column(Numeric(10, 2), nullable=False)

    # Product identifiers
    sku = Column(String(100), unique=True, index=True, nullable=True)
    barcode = Column(String(100), nullable=True)

    # Physical attributes
    weight = Column(Numeric(10, 3), nullable=True)  # kg
    length = Column(Numeric(10, 2), nullable=True)  # cm
    width = Column(Numeric(10, 2), nullable=True)   # cm
    height = Column(Numeric(10, 2), nullable=True)  # cm
    unit_of_measure = Column(String(20), nullable=True)  # kg, gói, hộp, cái

    # Order constraints
    min_order_qty = Column(Integer, default=1)
    max_order_qty = Column(Integer, nullable=True)
    lead_time = Column(Integer, nullable=True)  # Thời gian chuẩn bị (ngày)

    # Flags
    is_preorder = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    allow_cod = Column(Boolean, default=True)

    # Return policy
    return_window_days = Column(Integer, default=7)  # Số ngày được đổi/trả

    producer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.PENDING)
    label = Column(SQLEnum(ProductLabel), nullable=True)  # Use enum instead of string
    images = Column(Text, nullable=True)  # JSON array of image URLs

    # Inventory management
    stock_quantity = Column(Integer, default=0, nullable=False)  # Số lượng tồn kho
    is_active = Column(Boolean, default=True, nullable=False)  # Sản phẩm có đang được bán hay không

    # Display & SEO
    sort_order = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), nullable=True)

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

