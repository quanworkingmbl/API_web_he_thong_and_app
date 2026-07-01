"""
Notification Model – Bảng thông báo hệ thống

Lưu trữ tất cả thông báo cho mọi loại người dùng:
- Buyer: thông báo đơn hàng, khuyến mãi
- Seller: đơn hàng mới, duyệt sản phẩm, bài viết, KYC
- Admin: hồ sơ seller, sản phẩm/bài viết chờ duyệt, khiếu nại
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Người nhận thông báo
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Phân loại thông báo
    # ORDER | SYSTEM | PROMOTION | PAYMENT
    category = Column(String(20), nullable=False, default="SYSTEM")

    # Nội dung
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Deep link – URL điều hướng khi tap vào thông báo
    # Ví dụ: /orders/123, /products/45, /complaints/7
    action_url = Column(String(500), nullable=True)

    # Object liên quan (polymorphic reference)
    # ref_type: order | product | complaint | return | content | seller_profile
    ref_type = Column(String(50), nullable=True)
    ref_id = Column(Integer, nullable=True)

    # Trạng thái đọc
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates=None, lazy="select", foreign_keys=[user_id])

    # Indexes để truy vấn nhanh
    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_user_unread", "user_id", "is_read"),
        Index("idx_notifications_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Notification id={self.id} user_id={self.user_id} category={self.category} is_read={self.is_read}>"
