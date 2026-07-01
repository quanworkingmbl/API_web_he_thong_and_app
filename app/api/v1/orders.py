from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.order_state import (
    check_order_ownership,
    validate_status_transition,
    log_status_change,
    resolve_payment_status,
)
from pydantic import BaseModel, Field
from decimal import Decimal
import uuid
from app.services.notification import (
    notify_order_cancelled_to_seller,
    notify_order_cancelled_by_admin,
)

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
# HELPER – build OrderResponse
# ==============================================================================

def _build_order_response(o: Order, db: Session) -> OrderResponse:
    seller = db.query(User).filter(User.id == o.seller_id).first()
    items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
    return OrderResponse(
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
    )


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
    include_inactive: bool = Query(False, description="[Admin only] Bao gồm đơn đã bị ẩn"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of orders with pagination and filters.
    Phân quyền theo role:
    - consumer  → chỉ xem đơn của chính mình (customer_id)
    - seller/producer → chỉ xem đơn thuộc shop mình (seller_id)
    - admin     → xem tất cả
    """
    user_type = (current_user.type or "").lower()
    query = db.query(Order)

    # Giới hạn theo role — chỉ admin xem toàn bộ; role khác (vd. content_manager) không được mặc định thấy hết
    if user_type == "admin":
        pass
    elif user_type == "consumer":
        query = query.filter(Order.customer_id == current_user.id)
    elif user_type in ("producer", "seller"):
        query = query.filter(Order.seller_id == current_user.id)
    else:
        raise HTTPException(
            status_code=403,
            detail="Không có quyền xem danh sách đơn hàng",
        )

    # Chỉ admin mới xem được đơn đã soft-delete
    if include_inactive and user_type == "admin":
        pass  # không filter is_active
    else:
        query = query.filter(Order.is_active == True)

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

    order_list = [_build_order_response(o, db) for o in orders]

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
    """
    Get order details by ID.
    Ownership check:
    - consumer  → chỉ xem đơn của chính mình (customer_id)
    - seller    → chỉ xem đơn thuộc shop mình (seller_id)
    - admin     → xem tất cả
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.is_active == True
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # [SECURITY] Kiểm tra ownership
    check_order_ownership(order, current_user)

    return _build_order_response(order, db)


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
    Update order status với state machine theo vai trò:
    - consumer  → CHỈ được huỷ đơn của mình (PENDING/CONFIRMED → CANCELLED)
    - seller    → PENDING→CONFIRMED/CANCELLED, CONFIRMED→PROCESSING/CANCELLED,
                  PROCESSING→SHIPPING, SHIPPING→DELIVERED
    - admin     → mọi bước, không hạn chế
    """
    user_type = (current_user.type or "").lower()

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.is_active == True
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Kiểm tra quyền sở hữu
    check_order_ownership(order, current_user)

    old_status = order.status
    try:
        new_status_enum = OrderStatus(status_data.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Trạng thái không hợp lệ: {status_data.status}")

    # [STATE MACHINE] Validate chuyển trạng thái
    validate_status_transition(old_status, new_status_enum, user_type)

    # Cập nhật trạng thái
    order.status = new_status_enum

    # Cập nhật timestamps
    now = datetime.utcnow()
    if new_status_enum == OrderStatus.CONFIRMED:
        order.confirmed_at = now
    elif new_status_enum == OrderStatus.SHIPPING:
        order.shipped_at = now
    elif new_status_enum == OrderStatus.DELIVERED:
        order.delivered_at = now
    elif new_status_enum == OrderStatus.CANCELLED:
        order.cancelled_at = now
        if status_data.cancel_reason:
            order.cancel_reason = status_data.cancel_reason

    # [PAYMENT] Cập nhật payment_status theo quy tắc
    new_payment_status = resolve_payment_status(order, new_status_enum)
    if new_payment_status is not None:
        order.payment_status = new_payment_status

    # [NOTE] Ghi note vào đúng field theo role
    if status_data.note:
        if user_type == "consumer":
            order.customer_note = status_data.note
        elif user_type in ("seller", "producer"):
            order.seller_note = status_data.note
        else:
            order.admin_note = status_data.note

    # [AUDIT] Ghi log thay đổi trạng thái
    log_status_change(
        db=db,
        order_id=order_id,
        old_status=old_status.value if hasattr(old_status, "value") else str(old_status),
        new_status=new_status_enum.value,
        actor_id=current_user.id,
        role=user_type,
        note=status_data.note or status_data.cancel_reason,
        auto_flush=True,
    )

    # [NOTIFICATION] Gửi thông báo khi hủy đơn
    if new_status_enum == OrderStatus.CANCELLED:
        cancel_reason = status_data.cancel_reason or status_data.note or None
        if user_type == "consumer":
            # [O8] Buyer hủy đơn → thông báo cho Seller
            notify_order_cancelled_to_seller(
                db=db,
                seller_id=order.seller_id,
                order_id=order_id,
                order_number=order.order_number,
                reason=cancel_reason,
            )
        elif user_type == "admin":
            # [O9] Admin hủy đơn → thông báo cho cả Buyer và Seller
            notify_order_cancelled_by_admin(
                db=db,
                target_user_id=order.customer_id,
                order_id=order_id,
                order_number=order.order_number,
                reason=cancel_reason,
            )
            notify_order_cancelled_by_admin(
                db=db,
                target_user_id=order.seller_id,
                order_id=order_id,
                order_number=order.order_number,
                reason=cancel_reason,
            )

    db.commit()

    return {
        "success": True,
        "message": f"Đã cập nhật trạng thái đơn hàng: {old_status.value} → {new_status_enum.value}",
        "order_id": order_id,
        "old_status": old_status.value if hasattr(old_status, "value") else str(old_status),
        "new_status": new_status_enum.value,
        "payment_status": order.payment_status,
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

    total = db.query(Order).filter(Order.is_active == True).count()

    # Count by status
    by_status = {}
    for status in OrderStatus:
        count = db.query(Order).filter(
            Order.status == status,
            Order.is_active == True
        ).count()
        by_status[status.value.lower()] = count

    # Revenue stats
    completed_orders = db.query(Order).filter(
        Order.status == OrderStatus.DELIVERED,
        Order.is_active == True
    ).all()
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


# ==============================================================================
# CREATE & DELETE ORDERS
# ==============================================================================

class CreateOrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class CreateOrderRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    shipping_address: str
    seller_id: int
    payment_method: str = Field(default="COD", pattern="^(COD|VNPAY|BANK_TRANSFER)$")
    customer_note: Optional[str] = None
    items: List[CreateOrderItemRequest]


@router.post("")
async def create_order(
    order_data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    [Admin] Tạo đơn hàng thủ công (ví dụ: đơn offline).
    """
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền tạo đơn hàng thủ công")

    from app.models.product import Product

    # Validate seller
    seller = db.query(User).filter(User.id == order_data.seller_id).first()
    if not seller:
        raise HTTPException(status_code=400, detail="Seller không tồn tại")

    # Calculate totals
    subtotal = Decimal("0")
    order_items = []
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Sản phẩm ID {item_data.product_id} không tồn tại")
        item_total = product.price * item_data.quantity
        subtotal += item_total
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_image": product.images,
            "unit_price": product.price,
            "quantity": item_data.quantity,
            "total_price": item_total,
        })

    platform_fee_pct = Decimal("10")
    platform_fee_amount = subtotal * platform_fee_pct / 100
    seller_amount = subtotal - platform_fee_amount

    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    new_order = Order(
        order_number=order_number,
        customer_id=current_user.id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        customer_email=order_data.customer_email,
        shipping_address=order_data.shipping_address,
        seller_id=order_data.seller_id,
        subtotal=subtotal,
        shipping_fee=Decimal("0"),
        discount_amount=Decimal("0"),
        total_amount=subtotal,
        platform_fee_percentage=platform_fee_pct,
        platform_fee_amount=platform_fee_amount,
        seller_amount=seller_amount,
        status=OrderStatus.PENDING,
        payment_method=order_data.payment_method,
        payment_status="UNPAID",
        customer_note=order_data.customer_note,
        is_active=True,
    )
    db.add(new_order)
    db.flush()  # lấy new_order.id

    for item in order_items:
        oi = OrderItem(order_id=new_order.id, **item)
        db.add(oi)

    # [AUDIT] Ghi log tạo đơn mới
    log_status_change(
        db=db,
        order_id=new_order.id,
        old_status=None,
        new_status=OrderStatus.PENDING.value,
        actor_id=current_user.id,
        role="admin",
        note="Tạo đơn hàng thủ công bởi admin",
        auto_flush=True,
    )

    db.commit()

    return {
        "success": True,
        "message": "Đã tạo đơn hàng",
        "data": {
            "id": new_order.id,
            "order_number": new_order.order_number,
            "total_amount": str(new_order.total_amount),
            "status": "PENDING",
        }
    }


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    reason: Optional[str] = Query(None, description="Lý do ẩn đơn hàng"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    [Admin] Soft-delete đơn hàng (ẩn khỏi hệ thống, giữ lịch sử).
    Chỉ admin mới thực hiện được. Đơn sẽ được đặt is_active=False.
    """
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa đơn hàng")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    if not order.is_active:
        raise HTTPException(status_code=400, detail="Đơn hàng này đã được ẩn trước đó")

    # [SOFT DELETE] Ẩn đơn thay vì xóa – giữ toàn bộ lịch sử
    order.is_active = False
    if reason:
        note = f"[SOFT DELETE] {reason}"
        order.admin_note = (order.admin_note or "") + f"\n{note}" if order.admin_note else note

    # [AUDIT] Ghi log ẩn đơn
    old_status_val = order.status.value if hasattr(order.status, "value") else str(order.status)
    log_status_change(
        db=db,
        order_id=order_id,
        old_status=old_status_val,
        new_status=old_status_val,  # trạng thái không thay đổi, chỉ is_active=False
        actor_id=current_user.id,
        role="admin",
        note=f"Soft-delete: {reason or 'Không có lý do'}",
        auto_flush=True,
    )

    db.commit()

    return {
        "success": True,
        "message": "Đơn hàng đã được ẩn (soft-delete). Dữ liệu vẫn được lưu giữ.",
        "order_id": order_id,
    }
