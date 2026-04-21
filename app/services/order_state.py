"""
app/services/order_state.py
===========================
Tập trung toàn bộ logic nghiệp vụ liên quan đến trạng thái đơn hàng:

1. VALID_TRANSITIONS  – Bảng chuyển trạng thái hợp lệ theo vai trò
2. check_order_ownership     – Kiểm tra quyền đọc / ghi đơn hàng
3. validate_status_transition – Từ chối nhảy trạng thái không hợp lệ
4. log_status_change          – Ghi audit log
5. resolve_payment_status     – Quy tắc payment_status theo phương thức thanh toán
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Set, Dict
from datetime import datetime

from app.models.order import Order, OrderStatus, OrderStatusLog


# ==============================================================================
# 1. BẢNG CHUYỂN TRẠNG THÁI HỢP LỆ THEO VAI TRÒ
# ==============================================================================

# Định nghĩa: VALID_TRANSITIONS[role][old_status] = {allowed_new_statuses}
VALID_TRANSITIONS: Dict[str, Dict[OrderStatus, Set[OrderStatus]]] = {
    # Consumer: chỉ được hủy đơn của mình khi còn PENDING hoặc CONFIRMED
    "consumer": {
        OrderStatus.PENDING:   {OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.CANCELLED},
    },

    # Seller: điều phối toàn bộ vòng đời đơn hàng phía bán
    "seller": {
        OrderStatus.PENDING:    {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED:  {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
        OrderStatus.PROCESSING: {OrderStatus.SHIPPING},
        OrderStatus.SHIPPING:   {OrderStatus.DELIVERED},
    },

    # Producer = alias của seller (cùng quyền)
    "producer": {
        OrderStatus.PENDING:    {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED:  {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
        OrderStatus.PROCESSING: {OrderStatus.SHIPPING},
        OrderStatus.SHIPPING:   {OrderStatus.DELIVERED},
    },
}

# Admin được phép chuyển sang bất kỳ trạng thái nào (không hạn chế)
ADMIN_ROLES = {"admin"}

# Tất cả trạng thái hợp lệ để validate enum
ALL_STATUSES: Set[OrderStatus] = set(OrderStatus)


# ==============================================================================
# 2. KIỂM TRA QUYỀN ĐỌC / SỞ HỮU ĐƠN HÀNG
# ==============================================================================

def check_order_ownership(order: Order, current_user) -> None:
    """
    Kiểm tra user hiện tại có quyền xem/thao tác đơn hàng không.

    Quy tắc:
    - consumer  → phải là customer_id của đơn
    - seller / producer → phải là seller_id của đơn
    - admin     → không hạn chế

    Raise HTTPException 403 nếu vi phạm.
    """
    role = (current_user.type or "").lower()

    if role in ADMIN_ROLES:
        return  # Admin unrestricted

    if role == "consumer":
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền xem đơn hàng này"
            )

    elif role in ("seller", "producer"):
        if order.seller_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền xem đơn hàng này"
            )

    else:
        # Vai trò không xác định → từ chối
        raise HTTPException(
            status_code=403,
            detail="Vai trò của bạn không có quyền truy cập đơn hàng"
        )


# ==============================================================================
# 3. VALIDATE CHUYỂN TRẠNG THÁI (STATE MACHINE)
# ==============================================================================

def validate_status_transition(
    old_status: OrderStatus,
    new_status: OrderStatus,
    role: str,
) -> None:
    """
    Kiểm tra xem việc chuyển từ old_status → new_status có hợp lệ với role không.

    Raise HTTPException 400 nếu chuyển trạng thái không hợp lệ.
    Raise HTTPException 403 nếu role không có quyền thực hiện bước đó.
    """
    role = role.lower()

    # Admin được phép mọi chuyển đổi
    if role in ADMIN_ROLES:
        return

    # Không cho phép chuyển sang cùng trạng thái
    if old_status == new_status:
        raise HTTPException(
            status_code=400,
            detail=f"Đơn hàng đã ở trạng thái {old_status.value}"
        )

    # Kiểm tra role có trong bảng chuyển đổi không
    role_transitions = VALID_TRANSITIONS.get(role)
    if role_transitions is None:
        raise HTTPException(
            status_code=403,
            detail="Vai trò của bạn không có quyền cập nhật trạng thái đơn hàng"
        )

    # Kiểm tra old_status có trong bảng không
    allowed_next = role_transitions.get(old_status)
    if allowed_next is None:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Vai trò '{role}' không được phép cập nhật đơn hàng "
                f"đang ở trạng thái {old_status.value}"
            )
        )

    # Kiểm tra new_status có trong tập hợp được phép không
    if new_status not in allowed_next:
        allowed_names = ", ".join(s.value for s in sorted(allowed_next, key=lambda x: x.value))
        raise HTTPException(
            status_code=400,
            detail=(
                f"Không thể chuyển trạng thái từ {old_status.value} → {new_status.value}. "
                f"Vai trò '{role}' chỉ được phép chuyển sang: [{allowed_names}]"
            )
        )


# ==============================================================================
# 4. GHI AUDIT LOG
# ==============================================================================

def log_status_change(
    db: Session,
    order_id: int,
    old_status: Optional[str],
    new_status: str,
    actor_id: Optional[int],
    role: str,
    note: Optional[str] = None,
    auto_flush: bool = True,
) -> OrderStatusLog:
    """
    Tạo bản ghi audit log cho mỗi lần trạng thái đơn hàng thay đổi.

    Args:
        db          : SQLAlchemy Session
        order_id    : ID đơn hàng
        old_status  : Trạng thái cũ (None nếu tạo mới)
        new_status  : Trạng thái mới
        actor_id    : ID user thực hiện (None nếu là system/webhook)
        role        : consumer | seller | admin | system
        note        : Ghi chú thêm
        auto_flush  : flush() ngay sau khi add (default True)
    """
    log = OrderStatusLog(
        order_id=order_id,
        old_status=old_status,
        new_status=new_status,
        actor_id=actor_id,
        role=role,
        note=note,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    if auto_flush:
        db.flush()
    return log


# ==============================================================================
# 5. QUY TẮC PAYMENT STATUS
# ==============================================================================

def resolve_payment_status(
    order: Order,
    new_order_status: OrderStatus,
) -> Optional[str]:
    """
    Trả về giá trị payment_status mới cần set, hoặc None nếu không cần thay đổi.

    Quy tắc:
    - DELIVERED + COD → PAID  (thanh toán khi nhận hàng)
    - DELIVERED + online (VNPAY/MOMO/ZALOPAY/BANK_TRANSFER) → không thay đổi
      (payment_status được set bởi payment webhook riêng)
    - REFUNDED → REFUNDED
    - Mọi trường hợp khác → không thay đổi
    """
    COD_METHOD = "COD"

    if new_order_status == OrderStatus.DELIVERED:
        payment_method_val = (
            order.payment_method.value
            if hasattr(order.payment_method, "value")
            else str(order.payment_method)
        )
        if payment_method_val == COD_METHOD:
            return "PAID"
        # Online payment – chờ webhook, không tự động set PAID
        return None

    if new_order_status == OrderStatus.REFUNDED:
        return "REFUNDED"

    return None
