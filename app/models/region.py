from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Region(Base):
    """
    Vùng miền - để phân loại sản phẩm theo địa lý
    Ví dụ: Miền Bắc, Miền Trung, Miền Nam, Tây Nguyên, Đồng bằng sông Cửu Long...
    """
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    image = Column(Text, nullable=True)  # Region representative image
    
    # Geographic info
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    
    order = Column(Integer, default=0)  # Display order
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # products = relationship("Product", back_populates="region")
