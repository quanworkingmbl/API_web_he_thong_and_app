from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Boolean, Enum as SQLEnum
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
    usage_limit = Column(Integer, nullable=True)  # Số lần sử dụng tối đa
    used_count = Column(Integer, default=0)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(PromotionStatus), default=PromotionStatus.ACTIVE)
    is_public = Column(Boolean, default=True)  # Hiển thị cho consumer
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
