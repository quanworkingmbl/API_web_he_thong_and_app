from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Category(Base):
    """
    Danh mục sản phẩm
    Ví dụ: Rau củ quả, Trái cây, Thủ công mỹ nghệ, Nông sản khô, Gia vị...
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)  # Icon class or URL
    image = Column(Text, nullable=True)  # Category image URL
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)  # For subcategories - with FK
    order = Column(Integer, default=0)  # Display order
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with products
    products = relationship("Product", back_populates="category")
    # Self-referential relationship for parent category
    parent = relationship("Category", remote_side=[id], backref="subcategories")
