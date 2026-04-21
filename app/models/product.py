from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ProductStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ProductLabel(str, enum.Enum):
    CLEAN_AGRICULTURE = "CLEAN_AGRICULTURE"  # Nông sản sạch
    TRADITIONAL_CRAFT = "TRADITIONAL_CRAFT"  # Làng nghề truyền thống
    OCOP = "OCOP"  # One Commune One Product


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)

    # Multi-seller support
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)

    # Seller relationship
    seller = relationship("User", foreign_keys=[seller_id])

    # Product identification
    sku = Column(String(100), unique=True, nullable=True, index=True)  # Nullable vì có thể dùng variants
    slug = Column(String(255), unique=True, nullable=True, index=True)  # For SEO-friendly URLs

    # Physical properties for shipping
    weight = Column(Integer, nullable=True)  # Trọng lượng (gram)
    dimensions = Column(Text, nullable=True)  # JSON: {length, width, height} in cm
    unit = Column(String(20), nullable=True)  # Đơn vị tính: kg, piece, box, etc.

    # Loại sản phẩm – điều khiển form UI khác nhau giữa Nông sản và Thủ công mỹ nghệ
    product_type = Column(
        SQLEnum("AGRICULTURAL", "HANDICRAFT", name="product_type_enum"),
        nullable=True,
        index=True,
    )

    # Bao bì / đóng gói
    packaging_type = Column(String(50), nullable=True)  # thùng, lon, hộp, bó, cái...

    # Tax
    vat_rate = Column(Numeric(5, 2), nullable=True)  # VAT rate (%)

    # Status and visibility
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.PENDING, index=True)
    label = Column(SQLEnum(ProductLabel), nullable=True, index=True)  # Admin-only – gán sau khi có chứng nhận
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Đang bán hay không
    published_at = Column(DateTime(timezone=True), nullable=True)   # Lên lịch hiển thị
    unpublished_at = Column(DateTime(timezone=True), nullable=True)  # Tự động ẩn
    approved_at = Column(DateTime(timezone=True), nullable=True)     # Thời điểm Admin duyệt

    # Legacy image field (sẽ migrate sang product_media)
    images = Column(Text, nullable=True)  # JSON array of image URLs (deprecated)
    videos = Column(Text, nullable=True)  # URL hoặc JSON array URL video sản phẩm

    # Inventory management
    stock_quantity = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("User", foreign_keys=[seller_id])
    category = relationship("Category", foreign_keys=[category_id], back_populates="products")
    store = relationship("Store", foreign_keys=[store_id])


class ProductApproval(Base):
    __tablename__ = "product_approvals"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(ProductStatus), nullable=False)
    notes = Column(Text, nullable=True)
    checked_description = Column(Boolean, default=False)
    checked_price = Column(Boolean, default=False)
    checked_images = Column(Boolean, default=False)
    checked_traceability = Column(Boolean, default=False)  # Đã kiểm tra nguồn gốc
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    approver = relationship("User", foreign_keys=[approver_id])


class ProductPriceLog(Base):
    """Log thay đổi giá sản phẩm - dùng để audit và phát hiện gian lận"""
    __tablename__ = "product_price_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    old_price = Column(Numeric(15, 2), nullable=False)
    new_price = Column(Numeric(15, 2), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    changer = relationship("User", foreign_keys=[changed_by])
