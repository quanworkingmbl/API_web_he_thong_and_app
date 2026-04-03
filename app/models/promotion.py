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


class PromotionScope(str, enum.Enum):
    ALL = "ALL"  # Applies to all products
    PRODUCT = "PRODUCT"  # Specific products
    CATEGORY = "CATEGORY"  # Specific categories
    SELLER = "SELLER"  # Specific sellers
    USER = "USER"  # Specific users


class PromotionChannel(str, enum.Enum):
    APP = "APP"
    WEB = "WEB"
    ALL = "ALL"


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Promotion type & value
    promotion_type = Column(SQLEnum(PromotionType), nullable=False, default=PromotionType.PERCENTAGE)
    discount_value = Column(Numeric(12, 2), nullable=False)  # % hoặc số tiền
    min_order_amount = Column(Numeric(12, 2), default=0)  # Đơn tối thiểu
    max_discount_amount = Column(Numeric(12, 2), nullable=True)  # Giảm tối đa (cho %)

    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # Số lần sử dụng tối đa (toàn hệ thống)
    max_usage_per_user = Column(Integer, nullable=True)  # Số lần mỗi user được dùng
    used_count = Column(Integer, default=0)

    # Scope & targeting
    scope = Column(SQLEnum(PromotionScope), default=PromotionScope.ALL)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # If seller-created
    channel = Column(SQLEnum(PromotionChannel), default=PromotionChannel.ALL)
    audience_segment = Column(String(100), nullable=True)  # VIP, NEW_USER, etc.

    # Stacking rules
    stacking_allowed = Column(Boolean, default=False)  # Can combine with other promos

    # Time validity
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Status
    status = Column(SQLEnum(PromotionStatus), default=PromotionStatus.ACTIVE, index=True)
    is_public = Column(Boolean, default=True)  # Hiển thị cho consumer

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    seller = relationship("User", foreign_keys=[seller_id])
    creator = relationship("User", foreign_keys=[created_by])
