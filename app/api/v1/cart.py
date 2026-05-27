from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import Product, ProductStatus
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.inventory import (
    get_available_stock,
    get_unit_price,
    get_variant_for_product,
    validate_line_for_sale,
)
from pydantic import BaseModel, Field

_SHIPPING_FEE = Decimal("30000")

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, le=999)
    variant_id: Optional[int] = None


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., ge=1, le=999)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    seller_id: int
    seller_name: str = ""
    variant_id: Optional[int] = None
    product_name: str
    product_image: Optional[str]
    unit_label: str = "1 sản phẩm"
    location_label: str = ""
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    stock_quantity: int
    is_active: bool = True

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    subtotal: Decimal
    shipping_fee: str
    discount_amount: str
    total_amount: Decimal
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==============================================================================
# HELPER
# ==============================================================================

def _get_or_create_cart(user_id: int, db: Session) -> Cart:
    """Lấy giỏ hàng của user, tạo mới nếu chưa có."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _cart_line_filter(db: Session, cart_id: int, product_id: int, variant_id: Optional[int]):
    q = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    if variant_id is not None:
        q = q.filter(CartItem.variant_id == variant_id)
    else:
        q = q.filter(CartItem.variant_id.is_(None))
    return q


def _build_cart_response(cart: Cart, db: Session) -> CartResponse:
    """Build CartResponse với đầy đủ thông tin sản phẩm."""
    items_data = []
    subtotal_total = Decimal("0")

    # Sắp xếp theo item.id để đảm bảo thứ tự ổn định, không đổi vị trí sau mỗi update
    sorted_items = sorted(cart.items, key=lambda x: x.id)

    for item in sorted_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        variant = (
            get_variant_for_product(db, product.id, item.variant_id)
            if item.variant_id
            else None
        )
        avail = get_available_stock(db, product, item.variant_id)
        line_subtotal = item.unit_price * item.quantity
        subtotal_total += line_subtotal

        # Lấy seller name từ relationship (tránh N+1 query)
        seller_name = ""
        if product.seller and product.seller.full_name:
            seller_name = product.seller.full_name

        # Lấy category name làm location_label
        location_label = ""
        if product.category_id:
            from app.models.category import Category
            cat = db.query(Category).filter(Category.id == product.category_id).first()
            if cat:
                location_label = cat.name

        # unit_label từ variant hoặc product unit
        unit_label = "1 sản phẩm"
        if variant and hasattr(variant, "unit") and variant.unit:
            unit_label = str(variant.unit)
        elif hasattr(product, "unit") and product.unit:
            unit_label = str(product.unit)

        items_data.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                seller_id=product.seller_id,
                seller_name=seller_name,
                variant_id=item.variant_id,
                product_name=product.name,
                product_image=product.images,
                unit_label=unit_label,
                location_label=location_label,
                unit_price=item.unit_price,
                quantity=item.quantity,
                subtotal=line_subtotal,
                stock_quantity=avail,
                is_active=product.is_active,
            )
        )

    total_amount = subtotal_total + _SHIPPING_FEE

    return CartResponse(
        items=items_data,
        total_items=len(items_data),
        subtotal=subtotal_total,
        shipping_fee=str(_SHIPPING_FEE),
        discount_amount="0",
        total_amount=total_amount,
        updated_at=cart.updated_at,
    )


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("", summary="Xem giỏ hàng hiện tại")
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy giỏ hàng của người dùng đang đăng nhập."""
    cart = _get_or_create_cart(current_user.id, db)
    return {
        "success": True,
        "data": _build_cart_response(cart, db),
    }


@router.post("/items", summary="Thêm sản phẩm vào giỏ hàng")
async def add_cart_item(
    item_data: CartItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Thêm sản phẩm vào giỏ hàng. Nếu cùng product+variant đã có, cộng dồn số lượng."""
    product = db.query(Product).filter(
        Product.id == item_data.product_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại hoặc chưa được duyệt")

    _, unit_price = validate_line_for_sale(db, product, item_data.quantity, item_data.variant_id)

    cart = _get_or_create_cart(current_user.id, db)

    # Multi-seller: giỏ hàng hỗ trợ sản phẩm của nhiều seller cùng lúc.
    existing_item = _cart_line_filter(
        db, cart.id, item_data.product_id, item_data.variant_id
    ).first()

    if existing_item:
        new_qty = existing_item.quantity + item_data.quantity
        validate_line_for_sale(db, product, new_qty, item_data.variant_id)
        existing_item.quantity = new_qty
        existing_item.unit_price = unit_price
        if item_data.variant_id is not None:
            existing_item.variant_id = item_data.variant_id
        db.commit()
        db.refresh(existing_item)
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            variant_id=item_data.variant_id,
            quantity=item_data.quantity,
            unit_price=unit_price,
        )
        db.add(item)
        db.commit()
        db.refresh(item)

    db.refresh(cart)
    return {
        "success": True,
        "message": "Đã thêm vào giỏ hàng",
        "data": _build_cart_response(cart, db),
    }


@router.put("/items/{item_id}", summary="Cập nhật số lượng sản phẩm")
async def update_cart_item(
    item_id: int,
    item_data: UpdateCartItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cập nhật số lượng một item trong giỏ hàng."""
    cart = _get_or_create_cart(current_user.id, db)

    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item không tồn tại trong giỏ hàng")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    validate_line_for_sale(db, product, item_data.quantity, item.variant_id)
    variant = (
        get_variant_for_product(db, product.id, item.variant_id) if item.variant_id else None
    )
    item.quantity = item_data.quantity
    item.unit_price = get_unit_price(product, variant)
    db.commit()
    db.refresh(cart)

    return {
        "success": True,
        "message": "Đã cập nhật giỏ hàng",
        "data": _build_cart_response(cart, db),
    }


@router.delete("/items/{item_id}", summary="Xóa sản phẩm khỏi giỏ hàng")
async def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa một item khỏi giỏ hàng."""
    cart = _get_or_create_cart(current_user.id, db)

    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item không tồn tại trong giỏ hàng")

    db.delete(item)
    db.commit()
    db.refresh(cart)

    return {
        "success": True,
        "message": "Đã xóa sản phẩm khỏi giỏ hàng",
        "data": _build_cart_response(cart, db),
    }


@router.delete("", summary="Xóa toàn bộ giỏ hàng")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa toàn bộ giỏ hàng."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()

    return {
        "success": True,
        "message": "Đã xóa toàn bộ giỏ hàng",
    }
