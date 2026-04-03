from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
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

    # Tree structure with proper ForeignKey
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    path = Column(String(500), nullable=True)  # e.g., "1/5/12" for hierarchy traversal
    level = Column(Integer, default=0)  # 0 = root, 1 = first level child, etc.
    is_leaf = Column(Boolean, default=True)  # True if no children

    order = Column(Integer, default=0)  # Display order
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")
