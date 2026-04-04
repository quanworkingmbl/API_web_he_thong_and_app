from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ProductVariant(Base):
    """Biến thể sản phẩm - size, màu, trọng lượng khác nhau"""
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # Thông tin biến thể
    sku = Column(String(100), unique=True, nullable=False, index=True)
    variant_name = Column(String(255), nullable=False)  # VD: "Đỏ - XL", "500g"

    # Giá và tồn kho riêng
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)

    # Thông tin vật lý
    weight = Column(Integer, nullable=True)  # gram
    dimensions = Column(Text, nullable=True)  # JSON: {length, width, height} in cm

    # Hình ảnh riêng (nếu có)
    image_url = Column(Text, nullable=True)

    # Trạng thái
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id], backref="variants")


class ProductOption(Base):
    """Tùy chọn sản phẩm - VD: Màu sắc, Kích thước, Trọng lượng"""
    __tablename__ = "product_options"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # Tên tùy chọn
    option_name = Column(String(100), nullable=False)  # VD: "Màu sắc", "Kích thước"

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id], backref="options")


class ProductOptionValue(Base):
    """Giá trị của tùy chọn - VD: Đỏ, Xanh, XL, L"""
    __tablename__ = "product_option_values"

    id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, ForeignKey("product_options.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)

    # Giá trị
    value = Column(String(100), nullable=False)  # VD: "Đỏ", "XL", "500g"

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    option = relationship("ProductOption", foreign_keys=[option_id], backref="values")
    variant = relationship("ProductVariant", foreign_keys=[variant_id])


class MovementType(str, enum.Enum):
    IN = "IN"              # Nhập kho
    OUT = "OUT"            # Xuất kho
    ADJUSTMENT = "ADJUSTMENT"  # Điều chỉnh


class InventoryMovement(Base):
    """Lịch sử xuất nhập kho"""
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)

    # Loại chuyển động
    movement_type = Column(SQLEnum(MovementType), nullable=False)

    # Số lượng
    quantity = Column(Integer, nullable=False)  # Số dương cho IN, số âm cho OUT

    # Tham chiếu (order_id, purchase_id, etc.)
    reference_type = Column(String(50), nullable=True)  # ORDER, PURCHASE, ADJUSTMENT
    reference_id = Column(Integer, nullable=True)

    # Ghi chú
    notes = Column(Text, nullable=True)

    # Người thực hiện
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    variant = relationship("ProductVariant", foreign_keys=[variant_id])
    creator = relationship("User", foreign_keys=[created_by])


class ReservationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"      # Đang giữ
    RELEASED = "RELEASED"  # Đã giải phóng
    FULFILLED = "FULFILLED"  # Đã xuất hàng


class StockReservation(Base):
    """Giữ hàng tạm thời khi đặt hàng - tránh oversell"""
    __tablename__ = "stock_reservations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # Số lượng giữ
    quantity = Column(Integer, nullable=False)

    # Trạng thái
    status = Column(SQLEnum(ReservationStatus), default=ReservationStatus.ACTIVE, nullable=False)

    # Thời gian
    reserved_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Tự động giải phóng sau thời gian này
    released_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    variant = relationship("ProductVariant", foreign_keys=[variant_id])
    order = relationship("Order", foreign_keys=[order_id])
