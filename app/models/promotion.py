from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PromotionType(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"


class PromotionStatus(str, enum.Enum):
    PENDING = "PENDING"    # Chờ Admin duyệt (mặc định khi Seller tạo)
    ACTIVE = "ACTIVE"      # Đã duyệt, đang hoạt động
    INACTIVE = "INACTIVE"  # Tạm dừng / bị từ chối
    EXPIRED = "EXPIRED"    # Hết hạn


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    promotion_type = Column(SQLEnum(PromotionType), nullable=False, default=PromotionType.PERCENTAGE)
    discount_value = Column(Numeric(12, 2), nullable=False)  # % hoặc số tiền
    min_order_amount = Column(Numeric(12, 2), default=0)     # Đơn tối thiểu
    max_discount_amount = Column(Numeric(12, 2), nullable=True)  # Giảm tối đa (cho %)

    # Applicable scope
    applicable_to = Column(String(50), default="ALL")  # ALL, SELLER, PRODUCT, CATEGORY
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    applicable_product_ids = Column(Text, nullable=True)   # JSON array
    applicable_category_ids = Column(Text, nullable=True)  # JSON array

    # User conditions
    user_conditions = Column(Text, nullable=True)  # JSON: first_order, min_purchases, user_level, etc.

    # Usage limits
    usage_limit = Column(Integer, nullable=True)          # Tổng số lần dùng tối đa
    usage_limit_per_user = Column(Integer, nullable=True) # Giới hạn mỗi người dùng
    used_count = Column(Integer, default=0)

    # Time range
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Status & visibility
    status = Column(SQLEnum(PromotionStatus), default=PromotionStatus.PENDING, index=True)
    is_public = Column(Boolean, default=True)       # Hiển thị cho consumer
    is_flash_sale = Column(Boolean, default=False)  # ⚡ Flash Sale — hiển thị countdown

    # Admin approval fields
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin đã duyệt
    approved_at = Column(DateTime(timezone=True), nullable=True)           # Thời điểm duyệt
    rejection_reason = Column(Text, nullable=True)                         # Lý do từ chối

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    seller = relationship("User", foreign_keys=[seller_id])
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
