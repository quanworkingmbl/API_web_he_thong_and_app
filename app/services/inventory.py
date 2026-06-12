"""
Thống nhất tồn kho giữa Product (SP đơn) và ProductVariant (SKU).

Quy ước:
- Sản phẩm **không** có biến thể active nào: nguồn tồn = `Product.stock_quantity`.
- Sản phẩm **có** ít nhất một biến thể active: tồn chỉ nằm trên từng `ProductVariant`;
  khi đó bắt buộc chỉ định `variant_id` khi thêm giỏ / đặt hàng.
"""

from __future__ import annotations

from decimal import Decimal
from datetime import datetime, timezone as dt_timezone
from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_variant import ProductVariant


def _maybe_notify_out_of_stock(
    db: Session,
    product: Product,
    variant=None,
) -> None:
    """Gửi notification cho seller khi tồn kho = 0. Không raise exception."""
    qty = int(variant.stock_quantity) if variant else int(product.stock_quantity or 0)
    if qty > 0:
        return
    try:
        from app.models.notification import Notification  # noqa: PLC0415
        name = product.name or f"Sản phẩm #{product.id}"
        variant_note = f" (phiên bản: {variant.variant_name or variant.id})" if variant else ""
        notif = Notification(
            user_id=product.seller_id,
            category="SYSTEM",
            title="⚠️ Sản phẩm đã hết hàng",
            message=(
                f'Sản phẩm "{name}"{variant_note} đã hết hàng. '
                "Vui lòng cập nhật tồn kho để tiếp tục bán hàng."
            ),
            action_url=f"/seller/products/{product.id}",
            ref_type="product",
            ref_id=product.id,
        )
        db.add(notif)
        db.flush()  # flush, không commit – caller quản lý transaction
    except Exception:  # noqa: BLE001
        pass  # Không để lỗi notification phá luồng chính


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


def get_unit_price(
    product: Product,
    variant: Optional[ProductVariant],
    db: Optional[Session] = None,
) -> Decimal:
    """Trả về đơn giá áp dụng thực tế.

    Nếu `db` được truyền vào, hàm sẽ tra cứu Flash Sale promotion đang active
    cho sản phẩm và trả về giá sau giảm nếu có.
    Đối với sản phẩm có biến thể, giá variant được dùng làm base price.
    """
    if variant is not None:
        base = Decimal(str(variant.price))
    else:
        base = Decimal(str(product.price))

    if db is None:
        return base

    # Tra cứu Flash Sale promotion đang active áp dụng cho sản phẩm này
    try:
        from app.models.promotion import Promotion  # noqa: PLC0415
        import json as _json  # noqa: PLC0415

        now_utc = datetime.now(dt_timezone.utc)
        active_flash_promos = (
            db.query(Promotion)
            .filter(
                Promotion.is_flash_sale.is_(True),
                Promotion.status == "ACTIVE",
                Promotion.start_date <= now_utc,
                Promotion.end_date >= now_utc,
            )
            .all()
        )

        best_discount = Decimal("0")
        for promo in active_flash_promos:
            # Kiểm tra phạm vi áp dụng (seller / product / category / ALL)
            if promo.seller_id and promo.seller_id != product.seller_id:
                continue

            scope = str(getattr(promo, "applicable_to", "ALL") or "ALL").upper()

            if scope == "PRODUCT":
                try:
                    scoped_ids = {int(x) for x in _json.loads(promo.applicable_product_ids or "[]")}
                except Exception:
                    scoped_ids = set()
                if product.id not in scoped_ids:
                    continue
            elif scope == "CATEGORY":
                try:
                    scoped_ids = {int(x) for x in _json.loads(promo.applicable_category_ids or "[]")}
                except Exception:
                    scoped_ids = set()
                if product.category_id is None or product.category_id not in scoped_ids:
                    continue
            elif scope == "SELLER":
                if not (promo.seller_id and promo.seller_id == product.seller_id):
                    continue
            # scope == "ALL": tiếp tục

            # Kiểm tra min_order_amount
            if base < (promo.min_order_amount or Decimal("0")):
                continue

            # Tính discount
            promo_type = promo.promotion_type.value if hasattr(promo.promotion_type, "value") else str(promo.promotion_type)
            if promo_type == "PERCENTAGE":
                discount = base * promo.discount_value / Decimal("100")
            else:
                discount = Decimal(str(promo.discount_value))

            if promo.max_discount_amount and discount > promo.max_discount_amount:
                discount = promo.max_discount_amount

            if discount > best_discount:
                best_discount = discount

        final_price = base - best_discount
        return max(final_price, Decimal("0"))
    except Exception:  # noqa: BLE001
        # Fallback an toàn: không để lỗi promotion phá luồng giỏ hàng
        return base


def validate_line_for_sale(
    db: Session, product: Product, quantity: int, variant_id: Optional[int]
) -> Tuple[Optional[ProductVariant], Decimal]:
    """
    Kiểm tra đủ tồn và trả về (variant hoặc None, đơn giá sau flash sale/khuyến mãi).
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
        # Truyền db để hàm tự tra cứu flash sale promotion
        price = get_unit_price(product, v, db=db)
    else:
        if variant_id is not None:
            raise HTTPException(
                status_code=400,
                detail="Sản phẩm này không có biến thể; không cần variant_id.",
            )
        v = None
        avail = int(product.stock_quantity or 0)
        # Truyền db để hàm tự tra cứu flash sale promotion
        price = get_unit_price(product, None, db=db)

    if quantity > avail:
        raise HTTPException(
            status_code=400,
            detail=f"Không đủ hàng trong kho. Còn lại: {avail}, yêu cầu: {quantity}",
        )
    return v, price


def decrement_stock(
    db: Session, product: Product, quantity: int, variant_id: Optional[int]
) -> None:
    """Trừ tồn (cần validate_line_for_sale trước). Tự gửi notification khi hết hàng."""
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
        _maybe_notify_out_of_stock(db, product, v)
    else:
        product.stock_quantity = int(product.stock_quantity or 0) - quantity
        _maybe_notify_out_of_stock(db, product)


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
