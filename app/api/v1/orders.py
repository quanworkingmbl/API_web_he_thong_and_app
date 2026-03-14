from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel, Field
from decimal import Decimal
import uuid

router = APIRouter()


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    total_price: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    shipping_address: str
    seller_id: int
    seller_name: Optional[str] = None
    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    platform_fee_percentage: Decimal
    platform_fee_amount: Decimal
    seller_amount: Decimal
    status: str
    payment_method: str
    payment_status: str
    customer_note: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    data: List[OrderResponse]
    meta: dict


class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(PENDING|CONFIRMED|PROCESSING|SHIPPING|DELIVERED|CANCELLED|REFUNDED)$")
    note: Optional[str] = None
    cancel_reason: Optional[str] = None


# ==============================================================================
# LIST & GET ENDPOINTS
# ==============================================================================

@router.get("", response_model=OrderListResponse)
async def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    seller_id: Optional[int] = Query(None),
    payment_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by order number"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of orders with pagination and filters.
    [FIX 2] Phân quyền theo role:
    - consumer  → chỉ xem đơn của chính mình
    - producer  → chỉ xem đơn thuộc shop mình
    - admin     → xem tất cả (có thể lọc thêm)
    """
    user_type = (current_user.type or "").lower()
    query = db.query(Order)

    # Giới hạn theo role
    if user_type == "consumer":
        query = query.filter(Order.customer_id == current_user.id)
    elif user_type in ("producer", "seller"):
        query = query.filter(Order.seller_id == current_user.id)
    # admin: không lọc, xem tất cả

    if status:
        query = query.filter(Order.status == status)
    if customer_id and user_type == "admin":
        query = query.filter(Order.customer_id == customer_id)
    if seller_id and user_type == "admin":
        query = query.filter(Order.seller_id == seller_id)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))
    
    total = query.count()
    skip = (page - 1) * limit
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    order_list = []
    for o in orders:
        seller = db.query(User).filter(User.id == o.seller_id).first()
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        
        order_list.append(OrderResponse(
            id=o.id,
            order_number=o.order_number,
            customer_id=o.customer_id,
            customer_name=o.customer_name,
            customer_phone=o.customer_phone,
            customer_email=o.customer_email,
            shipping_address=o.shipping_address,
            seller_id=o.seller_id,
            seller_name=seller.name if seller else None,
            subtotal=o.subtotal,
            shipping_fee=o.shipping_fee,
            discount_amount=o.discount_amount,
            total_amount=o.total_amount,
            platform_fee_percentage=o.platform_fee_percentage,
            platform_fee_amount=o.platform_fee_amount,
            seller_amount=o.seller_amount,
            status=o.status.value if hasattr(o.status, 'value') else str(o.status),
            payment_method=o.payment_method.value if hasattr(o.payment_method, 'value') else str(o.payment_method),
            payment_status=o.payment_status,
            customer_note=o.customer_note,
            created_at=o.created_at,
            items=[OrderItemResponse.from_orm(item) for item in items]
        ))
    
    return OrderListResponse(
        data=order_list,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    seller = db.query(User).filter(User.id == order.seller_id).first()
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_email=order.customer_email,
        shipping_address=order.shipping_address,
        seller_id=order.seller_id,
        seller_name=seller.name if seller else None,
        subtotal=order.subtotal,
        shipping_fee=order.shipping_fee,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount,
        platform_fee_percentage=order.platform_fee_percentage,
        platform_fee_amount=order.platform_fee_amount,
        seller_amount=order.seller_amount,
        status=order.status.value if hasattr(order.status, 'value') else str(order.status),
        payment_method=order.payment_method.value if hasattr(order.payment_method, 'value') else str(order.payment_method),
        payment_status=order.payment_status,
        customer_note=order.customer_note,
        created_at=order.created_at,
        items=[OrderItemResponse.from_orm(item) for item in items]
    )


# ==============================================================================
# UPDATE STATUS ENDPOINT
# ==============================================================================

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_data: UpdateOrderStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update order status.
    [FIX 2] Phân quyền:
    - consumer  → CHỈ được huỷ đơn của chính mình (CANCELLED)
    - producer  → chỉ được cập nhật đơn thuộc shop mình
    - admin     → cập nhật bất kỳ đơn nào
    """
    user_type = (current_user.type or "").lower()

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Kiểm tra quyền sở hữu
    if user_type == "consumer":
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Không có quyền chỉnh sửa đơn hàng này")
        # Consumer chỉ được huỷ đơn
        if status_data.status != "CANCELLED":
            raise HTTPException(status_code=403, detail="Người mua chỉ được phép huỷ đơn")
    elif user_type in ("producer", "seller"):
        if order.seller_id != current_user.id:
            raise HTTPException(status_code=403, detail="Không có quyền chỉnh sửa đơn hàng này")
    # admin: không giới hạn
    
    old_status = order.status
    order.status = status_data.status
    
    # Update timestamps based on status
    now = datetime.utcnow()
    if status_data.status == "CONFIRMED":
        order.confirmed_at = now
    elif status_data.status == "SHIPPING":
        order.shipped_at = now
    elif status_data.status == "DELIVERED":
        order.delivered_at = now
        order.payment_status = "PAID"  # Mark as paid when delivered (for COD)
    elif status_data.status == "CANCELLED":
        order.cancelled_at = now
        if status_data.cancel_reason:
            order.cancel_reason = status_data.cancel_reason
    
    if status_data.note:
        order.admin_note = status_data.note
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Order status updated from {old_status} to {status_data.status}",
        "order_id": order_id
    }


# ==============================================================================
# STATISTICS ENDPOINT
# ==============================================================================

@router.get("/stats/overview")
async def get_order_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order statistics overview"""
    from sqlalchemy import func as sql_func
    
    total = db.query(Order).count()
    
    # Count by status
    by_status = {}
    for status in OrderStatus:
        count = db.query(Order).filter(Order.status == status).count()
        by_status[status.value.lower()] = count
    
    # Revenue stats
    completed_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).all()
    total_revenue = sum(o.total_amount for o in completed_orders)
    total_platform_fee = sum(o.platform_fee_amount for o in completed_orders)
    total_seller_amount = sum(o.seller_amount for o in completed_orders)
    
    return {
        "success": True,
        "data": {
            "total_orders": total,
            "by_status": by_status,
            "revenue": {
                "total": str(total_revenue),
                "platform_fee": str(total_platform_fee),
                "seller_amount": str(total_seller_amount)
            }
        }
    }
