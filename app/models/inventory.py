from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ProductInventory(Base):
    """Quản lý tồn kho theo kho/địa điểm"""
    __tablename__ = "product_inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)

    # Stock levels
    available_quantity = Column(Integer, default=0, nullable=False)  # Có thể bán
    reserved_quantity = Column(Integer, default=0, nullable=False)   # Đã đặt chưa ship
    allocated_quantity = Column(Integer, default=0, nullable=False)  # Đang được xử lý
    damaged_quantity = Column(Integer, default=0, nullable=False)    # Hỏng

    # Location within warehouse
    bin_location = Column(String(50), nullable=True)  # Vị trí trong kho

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    warehouse = relationship("Warehouse", foreign_keys=[warehouse_id])


class StockLog(Base):
    """Nhật ký giao dịch tồn kho"""
    __tablename__ = "stock_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    transaction_type = Column(String(50), nullable=False)  # PURCHASE, SALE, RETURN, ADJUSTMENT, DAMAGE
    quantity_change = Column(Integer, nullable=False)  # +/- number
    quantity_after = Column(Integer, nullable=False)  # Tồn kho sau giao dịch

    # Reference
    reference_type = Column(String(50), nullable=True)  # ORDER, RETURN, MANUAL
    reference_id = Column(Integer, nullable=True)

    note = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    warehouse = relationship("Warehouse", foreign_keys=[warehouse_id])
    creator = relationship("User", foreign_keys=[created_by])
