"""
Thống nhất tồn kho giữa Product (SP đơn) và ProductVariant (SKU).

Quy ước:
- Sản phẩm **không** có biến thể active nào: nguồn tồn = `Product.stock_quantity`.
- Sản phẩm **có** ít nhất một biến thể active: tồn chỉ nằm trên từng `ProductVariant`;
  khi đó bắt buộc chỉ định `variant_id` khi thêm giỏ / đặt hàng.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_variant import ProductVariant


def count_active_variants(db: Session, product_id: int) -> int:
    n = (
        db.query(func.count(ProductVariant.id))
        .filter(
            ProductVariant.product_id == product_id,
            ProductVariant.is_active.is_(True),
        )
        .scalar()
    )
    return int(n or 0)


def requires_variant(db: Session, product_id: int) -> bool:
    return count_active_variants(db, product_id) > 0


def get_variant_for_product(
    db: Session, product_id: int, variant_id: int
) -> Optional[ProductVariant]:
    return (
        db.query(ProductVariant)
        .filter(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id,
            ProductVariant.is_active.is_(True),
        )
        .first()
    )


def get_available_stock(db: Session, product: Product, variant_id: Optional[int]) -> int:
    if not requires_variant(db, product.id):
        return int(product.stock_quantity or 0)
    if variant_id is None:
        return 0
    v = get_variant_for_product(db, product.id, variant_id)
    return int(v.stock_quantity) if v else 0


def get_unit_price(product: Product, variant: Optional[ProductVariant]) -> Decimal:
    if variant is not None:
        return Decimal(str(variant.price))
    return Decimal(str(product.price))


def validate_line_for_sale(
    db: Session, product: Product, quantity: int, variant_id: Optional[int]
) -> Tuple[Optional[ProductVariant], Decimal]:
    """
    Kiểm tra đủ tồn và trả về (variant hoặc None, đơn giá).
    Raises HTTPException 400 nếu không hợp lệ.
    """
    if variant_id is not None and not get_variant_for_product(db, product.id, variant_id):
        raise HTTPException(status_code=400, detail="Biến thể không tồn tại hoặc không khả dụng")

    if requires_variant(db, product.id):
        if variant_id is None:
            raise HTTPException(
                status_code=400,
                detail="Sản phẩm có nhiều biến thể (SKU). Vui lòng chọn biến thể trước khi đặt hàng.",
            )
        v = get_variant_for_product(db, product.id, variant_id)
        assert v is not None
        avail = int(v.stock_quantity)
        price = get_unit_price(product, v)
    else:
        if variant_id is not None:
            raise HTTPException(
                status_code=400,
                detail="Sản phẩm này không có biến thể; không cần variant_id.",
            )
        v = None
        avail = int(product.stock_quantity or 0)
        price = get_unit_price(product, None)

    if quantity > avail:
        raise HTTPException(
            status_code=400,
            detail=f"Không đủ hàng trong kho. Còn lại: {avail}, yêu cầu: {quantity}",
        )
    return v, price


def decrement_stock(
    db: Session, product: Product, quantity: int, variant_id: Optional[int]
) -> None:
    """Trừ tồn (đã kiểm tra trước đó)."""
    if requires_variant(db, product.id):
        if variant_id is None:
            raise ValueError("variant_id required when product has variants")
        v = (
            db.query(ProductVariant)
            .filter(
                ProductVariant.id == variant_id,
                ProductVariant.product_id == product.id,
            )
            .with_for_update()
            .first()
        )
        if not v:
            raise ValueError("Variant not found")
        v.stock_quantity = int(v.stock_quantity) - quantity
    else:
        product.stock_quantity = int(product.stock_quantity or 0) - quantity


def increment_stock(
    db: Session, product: Product, quantity: int, variant_id: Optional[int]
) -> None:
    """Hoàn tồn (hủy đơn / trả hàng)."""
    if requires_variant(db, product.id):
        if variant_id is None:
            # Đơn cũ không có variant_id: cộng vào tồn cấp sản phẩm (legacy)
            product.stock_quantity = int(product.stock_quantity or 0) + quantity
            return
        v = (
            db.query(ProductVariant)
            .filter(
                ProductVariant.id == variant_id,
                ProductVariant.product_id == product.id,
            )
            .first()
        )
        if v:
            v.stock_quantity = int(v.stock_quantity) + quantity
        else:
            product.stock_quantity = int(product.stock_quantity or 0) + quantity
    else:
        product.stock_quantity = int(product.stock_quantity or 0) + quantity
