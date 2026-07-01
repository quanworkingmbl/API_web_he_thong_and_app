from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class MediaType(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class ProductMedia(Base):
    """Media (ảnh/video) của sản phẩm - thay thế JSON text trong products.images"""
    __tablename__ = "product_media"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)

    # Media info
    media_type = Column(SQLEnum(MediaType), default=MediaType.IMAGE, nullable=False)
    url = Column(Text, nullable=False)
    alt_text = Column(String(255), nullable=True)

    # Display order
    sort_order = Column(Integer, default=0, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)  # Ảnh chính của sản phẩm

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id], backref="media")
