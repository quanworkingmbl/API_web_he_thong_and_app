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
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, le=999)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., ge=1, le=999)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    stock_quantity: int

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total_items: int
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


def _build_cart_response(cart: Cart, db: Session) -> CartResponse:
    """Build CartResponse với đầy đủ thông tin sản phẩm."""
    items_data = []
    total_amount = Decimal("0")

    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        # Lấy snapshot giá tại thời điểm thêm cart (unit_price trong CartItem)
        subtotal = item.unit_price * item.quantity
        total_amount += subtotal
        items_data.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=product.name,
            product_image=product.images,
            unit_price=item.unit_price,
            quantity=item.quantity,
            subtotal=subtotal,
            stock_quantity=product.stock_quantity
        ))

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items_data,
        total_items=len(items_data),
        total_amount=total_amount,
        updated_at=cart.updated_at
    )


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("", summary="Xem giỏ hàng hiện tại")
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy giỏ hàng của người dùng đang đăng nhập."""
    cart = _get_or_create_cart(current_user.id, db)
    return {
        "success": True,
        "data": _build_cart_response(cart, db)
    }


@router.post("/items", summary="Thêm sản phẩm vào giỏ hàng")
async def add_cart_item(
    item_data: CartItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Thêm sản phẩm vào giỏ hàng. Nếu sản phẩm đã có, cộng dồn số lượng."""
    # Kiểm tra sản phẩm
    product = db.query(Product).filter(
        Product.id == item_data.product_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại hoặc chưa được duyệt")

    # Kiểm tra tồn kho
    if product.stock_quantity < item_data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Không đủ hàng trong kho. Còn lại: {product.stock_quantity}"
        )

    cart = _get_or_create_cart(current_user.id, db)

    # Kiểm tra sản phẩm đã có trong giỏ chưa
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_data.product_id
    ).first()

    if existing_item:
        new_qty = existing_item.quantity + item_data.quantity
        if new_qty > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Tổng số lượng vượt quá tồn kho. Còn lại: {product.stock_quantity}"
            )
        existing_item.quantity = new_qty
        existing_item.unit_price = product.price  # Cập nhật giá mới nhất
        db.commit()
        db.refresh(existing_item)
        item = existing_item
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=product.price
        )
        db.add(item)
        db.commit()
        db.refresh(item)

    db.refresh(cart)
    return {
        "success": True,
        "message": "Đã thêm vào giỏ hàng",
        "data": _build_cart_response(cart, db)
    }


@router.put("/items/{item_id}", summary="Cập nhật số lượng sản phẩm")
async def update_cart_item(
    item_id: int,
    item_data: UpdateCartItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật số lượng một item trong giỏ hàng."""
    cart = _get_or_create_cart(current_user.id, db)

    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item không tồn tại trong giỏ hàng")

    # Kiểm tra tồn kho
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product and item_data.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Vượt quá tồn kho. Còn lại: {product.stock_quantity}"
        )

    item.quantity = item_data.quantity
    if product:
        item.unit_price = product.price  # Cập nhật giá
    db.commit()
    db.refresh(cart)

    return {
        "success": True,
        "message": "Đã cập nhật giỏ hàng",
        "data": _build_cart_response(cart, db)
    }


@router.delete("/items/{item_id}", summary="Xóa sản phẩm khỏi giỏ hàng")
async def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa một item khỏi giỏ hàng."""
    cart = _get_or_create_cart(current_user.id, db)

    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item không tồn tại trong giỏ hàng")

    db.delete(item)
    db.commit()
    db.refresh(cart)

    return {
        "success": True,
        "message": "Đã xóa sản phẩm khỏi giỏ hàng",
        "data": _build_cart_response(cart, db)
    }


@router.delete("", summary="Xóa toàn bộ giỏ hàng")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa toàn bộ giỏ hàng."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()

    return {
        "success": True,
        "message": "Đã xóa toàn bộ giỏ hàng"
    }
