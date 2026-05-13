from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


# ==============================================================================
# ENUMS
# ==============================================================================

class ComplaintStatus(str, enum.Enum):
    PENDING     = "PENDING"       # Mới gửi, chờ tiếp nhận
    ASSIGNED    = "ASSIGNED"      # Đã giao cho CS xử lý
    IN_PROGRESS = "IN_PROGRESS"   # Đang xử lý / đang trao đổi
    RESOLVED    = "RESOLVED"      # Đã giải quyết
    CLOSED      = "CLOSED"        # Đóng (hết thời hạn phản hồi / thoả thuận)
    REJECTED    = "REJECTED"      # Từ chối (khiếu nại không hợp lệ)


class ComplaintCategory(str, enum.Enum):
    """Phân loại khiếu nại theo chủ đề."""
    DELIVERY    = "DELIVERY"      # Giao hàng chậm / sai địa chỉ
    QUALITY     = "QUALITY"       # Chất lượng sản phẩm không đúng mô tả
    REFUND      = "REFUND"        # Hoàn tiền / thanh toán
    FRAUD       = "FRAUD"         # Hàng giả / lừa đảo
    SERVICE     = "SERVICE"       # Dịch vụ khách hàng
    OTHER       = "OTHER"         # Khác


class ComplaintPriority(str, enum.Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"
    URGENT = "URGENT"


class ModerationStatus(str, enum.Enum):
    PENDING  = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CommentRole(str, enum.Enum):
    """Vai trò của người viết comment trong thread."""
    BUYER  = "buyer"
    SELLER = "seller"
    ADMIN  = "admin"
    SYSTEM = "system"


# ==============================================================================
# COMPLAINT
# ==============================================================================

class Complaint(Base):
    __tablename__ = "complaints"

    id         = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    order_id   = Column(Integer, ForeignKey("orders.id"),   nullable=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"),    nullable=False, index=True)

    # Phân loại & ưu tiên (MỚI)
    category    = Column(SQLEnum(ComplaintCategory), default=ComplaintCategory.OTHER, nullable=False, index=True)
    priority    = Column(SQLEnum(ComplaintPriority), default=ComplaintPriority.MEDIUM, nullable=False, index=True)

    # Giữ lại complaint_type cũ để backward-compat nhưng dùng category chính
    complaint_type = Column(String(50), nullable=True, index=True)  # PRODUCT, PAYMENT, SERVICE

    title       = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    images      = Column(Text, nullable=True)    # JSON array of image URLs (bằng chứng)

    status      = Column(SQLEnum(ComplaintStatus), default=ComplaintStatus.PENDING, nullable=False, index=True)
    handled_by  = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution  = Column(Text, nullable=True)

    # Kết quả xử lý – liên kết refund/return (MỚI)
    resolution_type = Column(String(30), nullable=True)   # REFUND / RETURN / REPLACEMENT / NONE
    return_request_id = Column(Integer, ForeignKey("return_requests.id"), nullable=True)

    # SLA timestamps (MỚI)
    assigned_at       = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at       = Column(DateTime(timezone=True), nullable=True)
    closed_at         = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user           = relationship("User", foreign_keys=[user_id])
    handler        = relationship("User", foreign_keys=[handled_by])
    product        = relationship("Product", foreign_keys=[product_id])
    order          = relationship("Order", foreign_keys=[order_id])
    comments       = relationship("ComplaintComment",  back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintComment.created_at")
    status_logs    = relationship("ComplaintStatusLog", back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintStatusLog.timestamp")
    return_request = relationship("ReturnRequest", foreign_keys=[return_request_id])


# ==============================================================================
# COMPLAINT COMMENT THREAD (MỚI)
# ==============================================================================

class ComplaintComment(Base):
    """
    Thread trao đổi hai chiều: buyer ↔ seller ↔ admin/CS.
    Mỗi comment gắn với một complaint, ghi rõ vai trò người viết.
    """
    __tablename__ = "complaint_comments"

    id           = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    author_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role         = Column(String(20), nullable=False)   # buyer/seller/admin/system
    message      = Column(Text, nullable=False)
    attachments  = Column(Text, nullable=True)   # JSON array of image/file URLs
    is_internal  = Column(Boolean, default=False, nullable=False)  # True = chỉ admin/CS thấy
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    complaint = relationship("Complaint", back_populates="comments")
    author    = relationship("User", foreign_keys=[author_id])


# ==============================================================================
# COMPLAINT STATUS AUDIT LOG (MỚI)
# ==============================================================================

class ComplaintStatusLog(Base):
    """
    Audit trail: ai thay đổi trạng thái complaint, khi nào, lý do gì.
    """
    __tablename__ = "complaint_status_logs"

    id           = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    old_status   = Column(String(30), nullable=True)
    new_status   = Column(String(30), nullable=False)
    actor_id     = Column(Integer, ForeignKey("users.id"), nullable=True)
    note         = Column(Text, nullable=True)
    timestamp    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    complaint = relationship("Complaint", back_populates="status_logs")
    actor     = relationship("User", foreign_keys=[actor_id])


# ==============================================================================
# REVIEW
# ==============================================================================

class Review(Base):
    __tablename__ = "reviews"

    id         = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"),    nullable=False, index=True)

    # Purchase verification
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True, index=True)

    # Ratings
    rating        = Column(Integer, nullable=False)   # 1-5 (product)
    seller_rating = Column(Integer, nullable=True)    # 1-5 (seller rating riêng)

    # Review content
    comment = Column(Text, nullable=True)

    # Moderation
    moderation_status = Column(SQLEnum(ModerationStatus), default=ModerationStatus.PENDING, index=True)
    moderated_by      = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderated_at      = Column(DateTime(timezone=True), nullable=True)
    moderation_note   = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product    = relationship("Product",     foreign_keys=[product_id])
    user       = relationship("User",        foreign_keys=[user_id])
    order_item = relationship("OrderItem",   foreign_keys=[order_item_id])
    moderator  = relationship("User",        foreign_keys=[moderated_by])
    images     = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")

    __table_args__ = (
        # Cho phép user review cùng sản phẩm ở các đơn hàng khác nhau
        # → unique theo order_item_id (mỗi item chỉ được review 1 lần)
        UniqueConstraint('user_id', 'order_item_id', name='uq_user_orderitem_review'),
    )
