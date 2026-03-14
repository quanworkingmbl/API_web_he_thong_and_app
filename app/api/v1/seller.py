"""
Seller API – Dành riêng cho người bán (producer/seller)

Endpoints:
- GET  /seller/dashboard     – Thống kê tổng quan (đơn, doanh thu, sản phẩm)
- GET  /seller/orders        – Danh sách đơn hàng của seller
- PUT  /seller/orders/{id}/confirm – Xác nhận đơn → CONFIRMED
- PUT  /seller/orders/{id}/reject  – Từ chối đơn   → CANCELLED
- GET  /seller/products      – Sản phẩm của seller
- PUT  /seller/products/{id}/stock – Cập nhật tồn kho
- GET  /seller/profile       – Thông tin shop / profile
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product, ProductStatus
from app.models.user import User
from app.api.v1.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# PERMISSION HELPER
# ==============================================================================

def _require_seller(current_user: User):
    """Chặn truy cập nếu không phải seller / producer / admin."""
    allowed_types = {"producer", "seller", "admin"}
    if current_user.type not in allowed_types:
        raise HTTPException(status_code=403, detail="Chỉ người bán mới có quyền truy cập")
    return current_user


# ==============================================================================
# SCHEMAS
# ==============================================================================

class StockUpdateRequest(BaseModel):
    stock_quantity: int = Field(..., ge=0)


class RejectOrderRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("/dashboard", summary="Thống kê tổng quan của seller")
async def get_seller_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard dành cho người bán:
    - Tổng đơn hàng
    - Đơn theo trạng thái
    - Doanh thu (đơn đã giao)
    - Tổng sản phẩm
    """
    _require_seller(current_user)
    seller_id = current_user.id

    # Thống kê đơn hàng
    total_orders = db.query(Order).filter(Order.seller_id == seller_id).count()

    orders_by_status = {}
    for status in OrderStatus:
        cnt = db.query(Order).filter(
            Order.seller_id == seller_id,
            Order.status == status
        ).count()
        orders_by_status[status.value.lower()] = cnt

    # Doanh thu (đơn DELIVERED)
    delivered_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.status == OrderStatus.DELIVERED
    ).all()
    total_revenue = sum(o.seller_amount for o in delivered_orders)
    total_platform_fee = sum(o.platform_fee_amount for o in delivered_orders)

    # Thống kê 30 ngày gần nhất
    last_30_days = datetime.utcnow() - timedelta(days=30)
    recent_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.created_at >= last_30_days
    ).count()
    recent_revenue_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.status == OrderStatus.DELIVERED,
        Order.created_at >= last_30_days
    ).all()
    recent_revenue = sum(o.seller_amount for o in recent_revenue_orders)

    # Sản phẩm
    total_products = db.query(Product).filter(Product.producer_id == seller_id).count()
    approved_products = db.query(Product).filter(
        Product.producer_id == seller_id,
        Product.status == ProductStatus.APPROVED
    ).count()
    low_stock_products = db.query(Product).filter(
        Product.producer_id == seller_id,
        Product.stock_quantity < 5
    ).count()

    return {
        "success": True,
        "data": {
            "seller": {
                "id": current_user.id,
                "name": current_user.name,
                "type": current_user.type
            },
            "orders": {
                "total": total_orders,
                "last_30_days": recent_orders,
                "by_status": orders_by_status
            },
            "revenue": {
                "total_seller_amount": str(total_revenue),
                "total_platform_fee": str(total_platform_fee),
                "last_30_days": str(recent_revenue)
            },
            "products": {
                "total": total_products,
                "approved": approved_products,
                "low_stock": low_stock_products
            }
        }
    }


@router.get("/orders", summary="Danh sách đơn hàng của seller")
async def get_seller_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter theo trạng thái"),
    search: Optional[str] = Query(None, description="Tìm theo mã đơn hàng"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách đơn hàng của seller đang đăng nhập."""
    _require_seller(current_user)

    query = db.query(Order).filter(Order.seller_id == current_user.id)

    if status:
        query = query.filter(Order.status == status)
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))

    total = query.count()
    skip = (page - 1) * limit
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    order_list = []
    for o in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        order_list.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "shipping_address": o.shipping_address,
            "total_amount": str(o.total_amount),
            "seller_amount": str(o.seller_amount),
            "platform_fee_amount": str(o.platform_fee_amount),
            "status": o.status.value if hasattr(o.status, "value") else str(o.status),
            "payment_method": o.payment_method.value if hasattr(o.payment_method, "value") else str(o.payment_method),
            "payment_status": o.payment_status,
            "item_count": len(items),
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "total_price": str(item.total_price)
                }
                for item in items
            ],
            "created_at": o.created_at.isoformat()
        })

    return {
        "success": True,
        "data": order_list,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.put("/orders/{order_id}/confirm", summary="Xác nhận đơn hàng")
async def confirm_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller xác nhận đơn hàng → chuyển sang CONFIRMED.
    Chỉ được xác nhận khi đơn đang ở trạng thái PENDING.
    """
    _require_seller(current_user)

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.seller_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể xác nhận đơn hàng đang ở trạng thái {order.status.value}"
        )

    # Kiểm tra và trừ tồn kho
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm '{product.name}' không đủ hàng (còn {product.stock_quantity}, cần {item.quantity})"
                )
            product.stock_quantity -= item.quantity

    order.status = OrderStatus.CONFIRMED
    order.confirmed_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Đã xác nhận đơn hàng",
        "order_id": order_id,
        "status": "CONFIRMED"
    }


@router.put("/orders/{order_id}/reject", summary="Từ chối / hủy đơn hàng")
async def reject_order(
    order_id: int,
    reject_data: RejectOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller từ chối đơn hàng → chuyển sang CANCELLED.
    Chỉ được từ chối khi đơn đang ở PENDING hoặc CONFIRMED.
    """
    _require_seller(current_user)

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.seller_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    cancellable_statuses = {OrderStatus.PENDING, OrderStatus.CONFIRMED}
    if order.status not in cancellable_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể hủy đơn hàng đang ở trạng thái {order.status.value}"
        )

    # Hoàn lại tồn kho nếu đã trừ (CONFIRMED)
    if order.status == OrderStatus.CONFIRMED:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity

    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()
    order.cancel_reason = reject_data.reason
    db.commit()

    return {
        "success": True,
        "message": "Đã hủy đơn hàng",
        "order_id": order_id,
        "reason": reject_data.reason
    }


@router.put("/orders/{order_id}/ship", summary="Chuyển đơn sang Đang giao hàng")
async def mark_order_shipping(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller đánh dấu đơn hàng đã giao cho đơn vị vận chuyển."""
    _require_seller(current_user)

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.seller_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    if order.status not in {OrderStatus.CONFIRMED, OrderStatus.PROCESSING}:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển sang giao hàng từ trạng thái {order.status.value}"
        )

    order.status = OrderStatus.SHIPPING
    order.shipped_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Đã chuyển đơn sang trạng thái Đang giao hàng",
        "order_id": order_id,
        "status": "SHIPPING"
    }


@router.get("/products", summary="Sản phẩm của seller")
async def get_seller_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách sản phẩm của seller đang đăng nhập."""
    _require_seller(current_user)

    query = db.query(Product).filter(Product.producer_id == current_user.id)
    if status:
        query = query.filter(Product.status == status)

    total = query.count()
    skip = (page - 1) * limit
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "stock_quantity": p.stock_quantity,
                "is_active": p.is_active,
                "label": p.label,
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                "images": p.images,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in products
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.put("/products/{product_id}/stock", summary="Cập nhật tồn kho sản phẩm")
async def update_product_stock(
    product_id: int,
    stock_data: StockUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller cập nhật số lượng tồn kho của sản phẩm."""
    _require_seller(current_user)

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại hoặc không có quyền")

    old_qty = product.stock_quantity
    product.stock_quantity = stock_data.stock_quantity
    db.commit()

    return {
        "success": True,
        "message": f"Đã cập nhật tồn kho từ {old_qty} → {stock_data.stock_quantity}",
        "product_id": product_id,
        "stock_quantity": stock_data.stock_quantity
    }


@router.get("/profile", summary="Thông tin shop/profile của seller")
async def get_seller_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Thông tin profile của seller."""
    _require_seller(current_user)

    total_products = db.query(Product).filter(Product.producer_id == current_user.id).count()
    approved_products = db.query(Product).filter(
        Product.producer_id == current_user.id,
        Product.status == ProductStatus.APPROVED
    ).count()
    total_orders = db.query(Order).filter(Order.seller_id == current_user.id).count()

    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "type": current_user.type,
            "gender": current_user.gender,
            "activated": current_user.activated,
            "stats": {
                "total_products": total_products,
                "approved_products": approved_products,
                "total_orders": total_orders
            },
            "member_since": current_user.created_at.isoformat() if current_user.created_at else None
        }
    }
