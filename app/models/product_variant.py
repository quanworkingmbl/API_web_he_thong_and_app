from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ProductVariant(Base):
    """Biến thể sản phẩm (ví dụ: size, màu sắc)"""
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # Variant identifiers
    sku = Column(String(100), unique=True, nullable=False, index=True)
    barcode = Column(String(100), nullable=True)

    # Variant attributes (JSON: {"size": "L", "color": "Red"})
    attributes = Column(Text, nullable=False)  # JSON

    # Pricing
    price = Column(Numeric(10, 2), nullable=True)  # Override product price
    compare_at_price = Column(Numeric(10, 2), nullable=True)

    # Inventory
    stock_quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)

    # Physical attributes
    weight = Column(Numeric(10, 3), nullable=True)
    length = Column(Numeric(10, 2), nullable=True)
    width = Column(Numeric(10, 2), nullable=True)
    height = Column(Numeric(10, 2), nullable=True)

    # Images
    image_url = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", foreign_keys=[product_id])


class ProductOption(Base):
    """Tùy chọn sản phẩm (ví dụ: Size, Color)"""
    __tablename__ = "product_options"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    option_name = Column(String(100), nullable=False)  # Size, Color, Material
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    values = relationship("ProductOptionValue", back_populates="option", cascade="all, delete-orphan")


class ProductOptionValue(Base):
    """Giá trị của tùy chọn sản phẩm (ví dụ: S, M, L)"""
    __tablename__ = "product_option_values"

    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("product_options.id"), nullable=False)

    value = Column(String(100), nullable=False)  # S, M, L or Red, Blue, Green
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    option = relationship("ProductOption", back_populates="values")
