from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ProductMedia(Base):
    """Ảnh và video sản phẩm với metadata"""
    __tablename__ = "product_media"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)

    media_type = Column(String(20), nullable=False)  # IMAGE, VIDEO
    media_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)

    # Metadata
    alt_text = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # For videos, in seconds

    # Display
    sort_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)  # Main product image

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", foreign_keys=[product_id])
