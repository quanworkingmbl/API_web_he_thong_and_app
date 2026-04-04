from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PromotionType(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"


class PromotionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    promotion_type = Column(SQLEnum(PromotionType), nullable=False, default=PromotionType.PERCENTAGE)
    discount_value = Column(Numeric(12, 2), nullable=False)  # % hoặc số tiền
    min_order_amount = Column(Numeric(12, 2), default=0)  # Đơn tối thiểu
    max_discount_amount = Column(Numeric(12, 2), nullable=True)  # Giảm tối đa (cho %)

    # Applicable scope
    applicable_to = Column(String(50), default="ALL")  # ALL, SELLER, PRODUCT, CATEGORY
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nếu riêng seller
    applicable_product_ids = Column(Text, nullable=True)  # JSON array
    applicable_category_ids = Column(Text, nullable=True)  # JSON array

    # User conditions
    user_conditions = Column(Text, nullable=True)  # JSON: first_order, min_purchases, user_level, etc.

    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # Số lần sử dụng tối đa (toàn bộ)
    usage_limit_per_user = Column(Integer, nullable=True)  # Giới hạn mỗi người dùng
    used_count = Column(Integer, default=0)

    # Time range
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Status
    status = Column(SQLEnum(PromotionStatus), default=PromotionStatus.ACTIVE, index=True)
    is_public = Column(Boolean, default=True)  # Hiển thị cho consumer

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    seller = relationship("User", foreign_keys=[seller_id])
    creator = relationship("User", foreign_keys=[created_by])
