from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ProductChangeLog(Base):
    """
    Ghi lại lịch sử mọi thay đổi của sản phẩm (giá, tên, mô tả, tồn kho,
    trạng thái, ảnh, v.v.) để audit và minh bạch với cả Seller và Admin.

    Mỗi lần cập nhật sản phẩm sẽ tạo N bản ghi – một bản ghi cho mỗi field
    thay đổi. Điều này giúp dễ filter và hiển thị timeline chi tiết.
    """
    __tablename__ = "product_change_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Loại thay đổi: UPDATE | STATUS_CHANGE | TOGGLE_ACTIVE | CREATE
    change_type = Column(String(50), nullable=False, default="UPDATE")

    # Tên field bị thay đổi: price, name, description, stock_quantity, ...
    field_name = Column(String(100), nullable=False)

    # Giá trị cũ và mới lưu dạng text (dễ lưu mọi kiểu dữ liệu)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    # Ghi chú tùy chọn (lý do thay đổi giá, v.v.)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    changer = relationship("User", foreign_keys=[changed_by])
