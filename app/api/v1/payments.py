"""
Payment Management API
======================
Bao gồm:
  VNPAY Gateway:
    POST /payments/vnpay/create    – Tạo URL thanh toán (ràng buộc method + trạng thái đơn)
    GET  /payments/vnpay/return    – Return URL (với kiểm tra số tiền + idempotency)
    POST /payments/vnpay/ipn       – IPN webhook (idempotent, lưu đầy đủ gateway data)

  Payment CRUD:
    GET  /payments/                – Danh sách (phân quyền buyer/seller/admin)
    GET  /payments/{id}/status     – Chi tiết (ownership check)
    GET  /payments/reconciliation  – Đối soát (admin + date filter)

  Refund:
    POST /payments/refund          – Hoàn tiền an toàn (kiểm tra điều kiện, audit log)

  Config (admin):
    PUT  /payments/config/fee      – Cập nhật phí nền tảng (audit log)
    PUT  /payments/config/cycle    – Cập nhật chu kỳ thanh toán (audit log)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
import json

from app.core.database import get_db
from app.models.payment import Payment, PaymentTransaction, PaymentAuditLog, PaymentStatus, PaymentCycle
from app.models.order import Order, OrderStatus
from app.models.settlement import DepositTransaction, DepositStatus
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.vnpay import vnpay_service
from app.api.v1.deposit import _confirm_deposit_tx
from app.core.permissions import check_payment_config_access
from pydantic import BaseModel, Field

router = APIRouter()

# Tolerance khớp số tiền gateway vs order (VND, do VNPAY trả về đơn vị *100)
AMOUNT_TOLERANCE = Decimal("1")   # 1 VND tolerance


# ==============================================================================
# HELPERS
# ==============================================================================

def _resolve_role(user: User) -> str:
    t = (user.type or "").lower()
    if t in ("admin", "superadmin"):
        return "admin"
    if t in ("producer", "seller"):
        return "seller"
    return "buyer"


def _get_client_info(request: Request) -> tuple[str, str]:
    # FIX: Lấy IP thực khi chạy sau nginx/Cloud Run (X-Forwarded-For)
    xff = request.headers.get("X-Forwarded-For", "")
    real_ip = request.headers.get("X-Real-IP", "")
    if xff:
        ip = xff.split(",")[0].strip()   # IP đầu tiên = client thực
    elif real_ip:
        ip = real_ip.strip()
    elif request.client:
        ip = request.client.host
    else:
        ip = "127.0.0.1"
    ua = request.headers.get("User-Agent", "")[:490]
    return ip, ua


def _check_payment_ownership(payment: Payment, current_user: User):
    """Chặn truy cập trái phép vào payment của người khác."""
    role = _resolve_role(current_user)
    if role == "admin":
        return
    if role == "buyer" and payment.customer_id != current_user.id:
        raise HTTPException(403, "Bạn không có quyền xem payment này")
    if role == "seller" and payment.seller_id != current_user.id:
        raise HTTPException(403, "Bạn không có quyền xem payment này")


def _audit(db: Session, action: str, payment_id: Optional[int] = None,
           actor_id: Optional[int] = None, amount: Optional[Decimal] = None,
           note: Optional[str] = None, ip: Optional[str] = None, ua: Optional[str] = None):
    log = PaymentAuditLog(
        payment_id=payment_id,
        action=action,
        actor_id=actor_id,
        amount=amount,
        note=note,
        ip_address=ip,
        user_agent=ua,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.flush()


def _create_payment_record(db: Session, order: Order, gateway_txn_no: str,
                            response_code: str, bank_code: str,
                            amount_from_gw: Decimal,
                            gateway_response_raw: dict) -> Payment:
    """Tạo Payment record và transaction sau khi IPN/return thành công."""
    amount_mismatch = abs(order.total_amount - amount_from_gw) > AMOUNT_TOLERANCE

    payment = Payment(
        order_id=order.id,
        customer_id=order.customer_id,
        seller_id=order.seller_id,
        amount=order.total_amount,
        amount_from_gateway=amount_from_gw,
        amount_mismatch=amount_mismatch,
        platform_fee_percentage=order.platform_fee_percentage,
        platform_fee_amount=order.platform_fee_amount,
        seller_amount=order.seller_amount,
        vnpay_transaction_no=gateway_txn_no,
        vnpay_response_code=response_code,
        vnpay_bank_code=bank_code,
        gateway_transaction_id=gateway_txn_no,
        gateway_response=json.dumps(gateway_response_raw, ensure_ascii=False),
        status=PaymentStatus.FAILED if amount_mismatch else PaymentStatus.COMPLETED,
        failure_code="AMOUNT_MISMATCH" if amount_mismatch else None,
        failure_message=(
            f"Số tiền gateway ({amount_from_gw}) lệch order ({order.total_amount})"
            if amount_mismatch else None
        ),
        payment_cycle=PaymentCycle.WEEKLY,
    )
    db.add(payment)
    db.flush()

    # Ghi transaction
    txn = PaymentTransaction(
        payment_id=payment.id,
        transaction_type="PAYMENT",
        amount=amount_from_gw,
        status=payment.status,
        gateway_ref=gateway_txn_no,
        notes="VNPAY IPN/Return" + (" – AMOUNT MISMATCH" if amount_mismatch else ""),
    )
    db.add(txn)

    return payment


# ==============================================================================
# VNPAY ENDPOINTS
# ==============================================================================

class VNPayCreateRequest(BaseModel):
    order_id: int


@router.post("/vnpay/create", summary="Tạo URL thanh toán VNPAY")
async def create_vnpay_payment(
    payment_data: VNPayCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo URL thanh toán VNPAY.
    Ràng buộc:
    - Phải là đơn của chính user.
    - Order.payment_method phải là VNPAY.
    - Trạng thái đơn phải là PENDING hoặc CONFIRMED.
    - Chưa được thanh toán (payment_status != PAID).
    """
    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    if not order:
        raise HTTPException(404, "Đơn hàng không tồn tại")

    # Ownership
    if order.customer_id != current_user.id:
        raise HTTPException(403, "Không có quyền thanh toán đơn hàng này")

    # Ràng buộc phương thức
    payment_method_val = (
        order.payment_method.value
        if hasattr(order.payment_method, "value")
        else str(order.payment_method)
    )
    if payment_method_val != "VNPAY":
        raise HTTPException(400, f"Đơn hàng dùng phương thức '{payment_method_val}', không phải VNPAY")

    # Ràng buộc trạng thái
    ALLOWED_STATUSES = {OrderStatus.PENDING, OrderStatus.CONFIRMED}
    if order.status not in ALLOWED_STATUSES:
        raise HTTPException(
            400,
            f"Không thể thanh toán đơn hàng đang ở trạng thái {order.status.value}. "
            "Chỉ thanh toán được khi đơn PENDING hoặc CONFIRMED."
        )

    if order.payment_status == "PAID":
        raise HTTPException(400, "Đơn hàng đã được thanh toán")

    client_ip, _ = _get_client_info(request)
    payment_url = vnpay_service.create_payment_url(
        order_id=order.id,
        amount=float(order.total_amount),
        order_info=f"Thanh toan don hang {order.order_number}",
        client_ip=client_ip
    )

    return {
        "success": True,
        "data": {
            "order_id": order.id,
            "order_number": order.order_number,
            "amount": str(order.total_amount),
            "payment_url": payment_url
        }
    }


# ==============================================================================
# MOCK PAYMENT (Sandbox/Test only)
# ==============================================================================

class MockPaymentRequest(BaseModel):
    order_id: int

@router.post("/mock/success", summary="[SANDBOX] Giả lập thanh toán thành công")
async def mock_payment_success(
    body: MockPaymentRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint chỉ dùng trong môi trường sandbox/test.
    Giả lập kết quả thanh toán thành công từ VNPAY mà không cần
    qua cổng thanh toán thực (bypass 'Sai chữ ký' sandbox issue).

    Yêu cầu biến môi trường: VNPAY_MOCK_MODE=true
    """
    import os
    if os.getenv("VNPAY_MOCK_MODE", "false").lower() != "true":
        raise HTTPException(403, "Mock payment chỉ hoạt động khi VNPAY_MOCK_MODE=true")

    order = db.query(Order).filter(Order.id == body.order_id).first()
    if not order:
        raise HTTPException(404, "Đơn hàng không tồn tại")

    if order.customer_id != current_user.id:
        raise HTTPException(403, "Không có quyền thanh toán đơn hàng này")

    if order.payment_status == "PAID":
        raise HTTPException(400, "Đơn hàng đã được thanh toán")

    # Tạo mock transaction number
    from datetime import datetime
    mock_txn_no = f"MOCK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{order.id}"

    payment = _create_payment_record(
        db=db,
        order=order,
        gateway_txn_no=mock_txn_no,
        response_code="00",
        bank_code="NCB",
        amount_from_gw=order.total_amount,
        gateway_response_raw={"mock": True, "order_id": order.id},
    )

    order.payment_status = "PAID"
    order.status = OrderStatus.CONFIRMED

    _audit(db, "MOCK_PAYMENT_SUCCESS", payment.id,
           actor_id=current_user.id,
           note=f"Mock payment for sandbox testing. txn={mock_txn_no}")
    db.commit()

    logger.info("[MOCK] Payment success for order_id=%s, txn=%s", order.id, mock_txn_no)

    return {
        "success": True,
        "message": "Mock payment thành công (sandbox only)",
        "data": {
            "order_id": order.id,
            "order_number": order.order_number,
            "payment_id": payment.id,
            "amount": str(order.total_amount),
            "transaction_no": mock_txn_no,
            "status": "PAID",
        }
    }


@router.get("/vnpay/return", summary="VNPAY return URL")
async def vnpay_return(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint VNPAY redirect về sau khi thanh toán.
    - Xác minh chữ ký.
    - Kiểm tra idempotency (đã PAID → không ghi trùng).
    - So sánh amount gateway vs order.
    - Lưu đầy đủ gateway data.
    """
    params = dict(request.query_params)
    result = vnpay_service.verify_return_url(params)

    if not result["is_valid"]:
        return {"success": False, "message": "Chữ ký không hợp lệ", "code": "INVALID_SIGNATURE"}

    order_id     = result["order_id"]
    transaction_no = result.get("transaction_no", "")
    response_code  = result.get("response_code", "")
    bank_code      = result.get("bank_code", "")
    is_success     = vnpay_service.is_payment_success(response_code, result.get("transaction_status", ""))

    # verify_return_url đã chia 100 rồi → dùng trực tiếp (không chia thêm)
    try:
        amount_from_gw = Decimal(str(result.get("amount", "0")))
    except Exception:
        amount_from_gw = Decimal("0")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"success": False, "message": "Đơn hàng không tồn tại"}

    # [IDEMPOTENCY] Kiểm tra xem transaction_no đã được xử lý chưa
    existing = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.vnpay_transaction_no == transaction_no,
    ).first()
    if existing:
        return {
            "success": True,
            "message": "Giao dịch đã được xử lý trước đó (idempotent)",
            "data": {"order_id": order_id, "payment_id": existing.id, "status": existing.status.value}
        }

    # Khởi tạo payment = None – đảm bảo biến luôn được định nghĩa
    # dù thanh toán thành công hay thất bại, tránh NameError ở bước build deep link
    payment = None

    if is_success and order.payment_status != "PAID":
        payment = _create_payment_record(db, order, transaction_no, response_code,
                                         bank_code, amount_from_gw, params)
        if not payment.amount_mismatch:
            order.payment_status = "PAID"
            order.status = OrderStatus.CONFIRMED
        else:
            order.payment_status = "FAILED"

        _audit(db, "VNPAY_RETURN", payment.id, note=f"return url. code={response_code}, mismatch={payment.amount_mismatch}")
        db.commit()
    elif not is_success:
        # Lưu bản ghi FAILED nếu chưa có
        if not existing:
            p = Payment(
                order_id=order.id,
                customer_id=order.customer_id,
                seller_id=order.seller_id,
                amount=order.total_amount,
                amount_from_gateway=amount_from_gw,
                platform_fee_percentage=order.platform_fee_percentage,
                platform_fee_amount=order.platform_fee_amount,
                seller_amount=order.seller_amount,
                vnpay_transaction_no=transaction_no,
                vnpay_response_code=response_code,
                vnpay_bank_code=bank_code,
                gateway_response=json.dumps(params, ensure_ascii=False),
                status=PaymentStatus.FAILED,
                failure_code=response_code,
                failure_message=f"VNPAY response code: {response_code}",
                payment_cycle=PaymentCycle.WEEKLY,
            )
            db.add(p)
            _audit(db, "VNPAY_RETURN_FAILED", None, note=f"code={response_code}")
        db.commit()

    # ── Build deep link để redirect về Flutter App (Option B) ──────────────────
    deep_link = vnpay_service.build_deep_link(
        success=is_success,
        order_id=order_id,
        payment_id=payment.id if payment is not None else None,
        response_code=response_code,
    )

    # Trả HTML tự redirect sang deep link agrarian://...
    # Nếu WebView detect URL change bắt đầu bằng "agrarian://" → đóng WebView
    _inline_msg = "\u2705 Thanh to\u00e1n th\u00e0nh c\u00f4ng!" if is_success else "\u274c Thanh to\u00e1n th\u1ea5t b\u1ea1i."
    _body_msg   = "\u2705 Thanh to\u00e1n th\u00e0nh c\u00f4ng! \u0110ang quay l\u1ea1i \u1ee9ng d\u1ee5ng..." if is_success else "\u274c Thanh to\u00e1n th\u1ea5t b\u1ea1i. \u0110ang quay l\u1ea1i \u1ee9ng d\u1ee5ng..."
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Agrarian Payment</title></head>
<body>
<script>
  window.location.href = "{deep_link}";
  setTimeout(function() {{
    document.body.innerHTML = '<p style="font-family:sans-serif;text-align:center;margin-top:60px">' +
      '{_inline_msg}' +
      '</p>';
  }}, 2000);
</script>
<p style="font-family:sans-serif;text-align:center;margin-top:60px">
  {_body_msg}
</p>
</body>
</html>"""
    return HTMLResponse(content=html)


@router.api_route("/vnpay/ipn", methods=["GET", "POST"], summary="VNPAY IPN Webhook")
async def vnpay_ipn(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    IPN server-to-server từ VNPAY.
    - Idempotent: nếu đã xử lý transaction_no này → trả 00 ngay.
    - Kiểm tra amount khớp order.
    - Lưu đầy đủ gateway_response, transaction_no, bank_code.
    """
    params = dict(request.query_params)
    result = vnpay_service.verify_return_url(params)

    if not result["is_valid"]:
        return {"RspCode": "97", "Message": "Invalid Signature"}

    txn_ref        = params.get("vnp_TxnRef", "")
    transaction_no = result.get("transaction_no", "")
    response_code  = result.get("response_code", "")
    bank_code      = result.get("bank_code", "")
    is_success     = vnpay_service.is_payment_success(
        response_code, result.get("transaction_status", "")
    )

    try:
        amount_from_gw = Decimal(str(result.get("amount", "0")))
    except Exception:
        amount_from_gw = Decimal("0")

    # Nạp ký quỹ: IPN đăng ký trên portal trỏ /payments/vnpay/ipn — xử lý deposit tại đây
    deposit_tx = (
        db.query(DepositTransaction)
        .filter(DepositTransaction.vnpay_txn_ref == txn_ref)
        .with_for_update()
        .first()
    )
    if deposit_tx:
        if deposit_tx.status == DepositStatus.CONFIRMED:
            return {"RspCode": "00", "Message": "Confirm Success"}
        deposit_tx.vnpay_response = json.dumps(params, ensure_ascii=False)
        if is_success and abs(amount_from_gw - Decimal(str(deposit_tx.amount))) <= AMOUNT_TOLERANCE:
            _confirm_deposit_tx(deposit_tx, db)
        elif is_success:
            deposit_tx.note = f"IPN amount mismatch: expected {deposit_tx.amount}, got {amount_from_gw}"
        else:
            deposit_tx.status = DepositStatus.REJECTED
            deposit_tx.note = f"IPN fail code={response_code}"
        db.commit()
        return {"RspCode": "00", "Message": "Confirm Success"}

    order_id = result["order_id"]
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"RspCode": "01", "Message": "Order Not Found"}

    # [IDEMPOTENCY] Kiểm tra xem đã xử lý transaction_no này chưa
    existing = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.vnpay_transaction_no == transaction_no,
    ).first()
    if existing:
        # Đã xử lý → trả 00 ngay (VNPAY yêu cầu)
        return {"RspCode": "00", "Message": "Confirm Success (idempotent)"}

    if order.payment_status == "PAID" and is_success:
        return {"RspCode": "02", "Message": "Order Already Confirmed"}

    if is_success:
        payment = _create_payment_record(db, order, transaction_no, response_code,
                                         bank_code, amount_from_gw, params)
        if payment.amount_mismatch:
            # Amount lệch → KHÔNG confirm, log để điều tra
            _audit(db, "IPN_AMOUNT_MISMATCH", payment.id,
                   note=f"Expected {order.total_amount}, got {amount_from_gw}")
            db.commit()
            return {"RspCode": "04", "Message": "Invalid Amount"}

        order.payment_status = "PAID"
        order.status = OrderStatus.CONFIRMED
        _audit(db, "IPN_RECEIVED", payment.id,
               note=f"txn={transaction_no}, code={response_code}, bank={bank_code}")
        db.commit()

    return {"RspCode": "00", "Message": "Confirm Success"}


# ==============================================================================
# VNPAY PAYMENT STATUS (for App polling)
# ==============================================================================

@router.get("/vnpay/status/{order_id}", summary="Trạng thái thanh toán VNPAY theo order_id")
async def get_vnpay_payment_status(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    App dùng endpoint này để polling kết quả sau khi WebView đóng.
    Ownership: chỉ customer hoặc admin mới xem được.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Đơn hàng không tồn tại")

    # Ownership check
    role = _resolve_role(current_user)
    if role == "buyer" and order.customer_id != current_user.id:
        raise HTTPException(403, "Không có quyền xem trạng thái đơn hàng này")

    # Lấy payment mới nhất của đơn
    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order_id)
        .order_by(Payment.created_at.desc())
        .first()
    )

    return {
        "success": True,
        "data": {
            "order_id":         order_id,
            "order_status":     order.status.value if hasattr(order.status, 'value') else str(order.status),
            "payment_status":   order.payment_status,
            "payment_id":       payment.id if payment else None,
            "payment_method":   order.payment_method.value if hasattr(order.payment_method, 'value') else str(order.payment_method),
            "transaction_no":   payment.vnpay_transaction_no if payment else None,
            "amount":           str(payment.amount) if payment else None,
            "bank_code":        payment.vnpay_bank_code if payment else None,
            "response_code":    payment.vnpay_response_code if payment else None,
            "is_paid":          order.payment_status == "PAID",
            "payment_record":   PaymentResponse.from_orm(payment).dict() if payment else None,
        }
    }




# ==============================================================================
# PAYMENT LIST / DETAIL
# ==============================================================================

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    seller_id: int
    amount: Decimal
    amount_from_gateway: Optional[Decimal]
    amount_mismatch: Optional[bool]
    platform_fee_percentage: Decimal
    platform_fee_amount: Decimal
    seller_amount: Decimal
    status: str
    vnpay_transaction_no: Optional[str]
    vnpay_response_code: Optional[str]
    vnpay_bank_code: Optional[str]
    refunded_amount: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", summary="Danh sách payment (phân quyền)")
async def get_payments(
    page:        int           = Query(1, ge=1),
    limit:       int           = Query(20, ge=1, le=100),
    status:      Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None, description="[Admin only]"),
    seller_id:   Optional[int] = Query(None, description="[Admin only]"),
    search:      Optional[str] = Query(None, description="Tìm theo order_id"),
    current_user: User = Depends(get_current_user),   # bắt buộc đăng nhập
    db: Session = Depends(get_db)
):
    """
    Danh sách payment có phân quyền:
    - buyer  → chỉ xem payment của mình (customer_id)
    - seller → chỉ xem payment của shop mình (seller_id)
    - admin  → xem tất cả + đầy đủ filter
    """
    role  = _resolve_role(current_user)
    query = db.query(Payment)

    if role == "buyer":
        query = query.filter(Payment.customer_id == current_user.id)
    elif role == "seller":
        query = query.filter(Payment.seller_id == current_user.id)
    else:  # admin
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        if seller_id:
            query = query.filter(Payment.seller_id == seller_id)

    if status:
        query = query.filter(Payment.status == status)
    if search:
        try:
            oid = int(search)
            query = query.filter(Payment.order_id == oid)
        except ValueError:
            pass

    total    = query.count()
    skip     = (page - 1) * limit
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [PaymentResponse.from_orm(p) for p in payments],
        "meta": {"total": total, "page": page, "limit": limit,
                 "total_pages": (total + limit - 1) // limit}
    }


@router.get("/{payment_id}/status", summary="Chi tiết payment")
async def get_payment_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chi tiết payment. Ownership check: chỉ xem payment của mình (buyer/seller/admin)."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment không tồn tại")

    _check_payment_ownership(payment, current_user)

    transactions = [
        {
            "id": t.id,
            "type": t.transaction_type,
            "amount": str(t.amount),
            "status": t.status.value,
            "gateway_ref": t.gateway_ref,
            "notes": t.notes,
            "created_at": t.created_at.isoformat(),
        }
        for t in payment.transactions
    ]

    return {
        "success": True,
        "data": {
            **PaymentResponse.from_orm(payment).dict(),
            "transactions": transactions,
        }
    }


@router.get("/reconciliation", summary="Đối soát thanh toán [Admin]")
async def get_payment_reconciliation(
    start_date:   Optional[str] = Query(None, description="ISO format: 2024-01-01"),
    end_date:     Optional[str] = Query(None, description="ISO format: 2024-01-31"),
    seller_id:    Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Đối soát doanh thu theo khoảng thời gian."""
    if (current_user.type or "").lower() not in ("admin", "superadmin"):
        raise HTTPException(403, "Chỉ admin mới có quyền đối soát")

    query = db.query(Payment).filter(Payment.status == PaymentStatus.COMPLETED)

    if start_date:
        try:
            sd = datetime.fromisoformat(start_date)
            query = query.filter(Payment.created_at >= sd)
        except ValueError:
            raise HTTPException(400, "start_date không đúng định dạng ISO (YYYY-MM-DD)")

    if end_date:
        try:
            ed = datetime.fromisoformat(end_date)
            query = query.filter(Payment.created_at <= ed)
        except ValueError:
            raise HTTPException(400, "end_date không đúng định dạng ISO (YYYY-MM-DD)")

    if seller_id:
        query = query.filter(Payment.seller_id == seller_id)

    payments = query.order_by(Payment.created_at.desc()).all()

    total_paid       = sum(p.amount for p in payments)
    total_platform   = sum(p.platform_fee_amount for p in payments)
    total_seller     = sum(p.seller_amount for p in payments)
    mismatch_count   = sum(1 for p in payments if p.amount_mismatch)

    return {
        "success": True,
        "data": {
            "period": {"start": start_date, "end": end_date},
            "total_orders": len(payments),
            "total_customer_paid": str(total_paid),
            "total_platform_commission": str(total_platform),
            "total_seller_amount": str(total_seller),
            "amount_mismatch_count": mismatch_count,
            "payments": [PaymentResponse.from_orm(p) for p in payments],
        }
    }


# ==============================================================================
# REFUND
# ==============================================================================

class RefundRequest(BaseModel):
    payment_id: int
    amount:     Decimal     = Field(..., gt=0, description="Số tiền hoàn (VND)")
    reason:     str         = Field(..., min_length=10, max_length=500)


@router.post("/refund", summary="Hoàn tiền an toàn [Admin]")
async def process_refund(
    refund_data: RefundRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hoàn tiền.
    Điều kiện:
    - Chỉ admin mới thực hiện được.
    - Payment phải ở trạng thái COMPLETED.
    - Số tiền hoàn ≤ số đã thu.
    - Không hoàn quá số tiền đã hoàn trước đó.
    Khi hoàn:
    - Cập nhật order.payment_status.
    - Ghi PaymentTransaction loại REFUND.
    - Ghi PaymentAuditLog.
    - Mock gateway call (TODO: tích hợp thực với VNPAY Refund API khi có).
    """
    check_payment_config_access(current_user)

    payment = db.query(Payment).filter(Payment.id == refund_data.payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment không tồn tại")

    # Chỉ hoàn tiền khi payment đã COMPLETED
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            400,
            f"Chỉ hoàn tiền được khi payment ở trạng thái COMPLETED. Hiện tại: {payment.status.value}"
        )

    # Tính tổng đã hoàn trước đó
    already_refunded = payment.refunded_amount or Decimal("0")
    max_refundable   = payment.amount - already_refunded

    if refund_data.amount > max_refundable:
        raise HTTPException(
            400,
            f"Số tiền hoàn ({refund_data.amount}) vượt quá số có thể hoàn "
            f"({max_refundable} = {payment.amount} đã thu - {already_refunded} đã hoàn trước)"
        )

    # === Mock gateway refund (thay bằng api call thực tế) ===
    # vnpay_service.refund(payment.vnpay_transaction_no, float(refund_data.amount))
    # =========================================================

    now = datetime.utcnow()
    new_refunded_total = already_refunded + refund_data.amount
    is_full_refund     = new_refunded_total >= payment.amount

    # Cập nhật Payment
    payment.refunded_amount = new_refunded_total
    payment.refund_note     = refund_data.reason
    payment.refunded_at     = now
    payment.status          = PaymentStatus.REFUNDED if is_full_refund else PaymentStatus.PARTIAL_REFUNDED

    # Tạo transaction REFUND
    txn = PaymentTransaction(
        payment_id=payment.id,
        transaction_type="REFUND" if is_full_refund else "PARTIAL_REFUND",
        amount=refund_data.amount,
        status=PaymentStatus.REFUNDED,
        notes=f"[REFUND] {refund_data.reason} (mock gateway - chưa gọi API thực)",
    )
    db.add(txn)

    # Cập nhật Order.payment_status
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order:
        order.payment_status = "REFUNDED" if is_full_refund else "PARTIAL_REFUNDED"

    ip, ua = _get_client_info(request)
    _audit(db, "REFUND", payment.id, current_user.id,
           amount=refund_data.amount,
           note=f"Hoàn {refund_data.amount} VND. Lý do: {refund_data.reason}. Full={is_full_refund}",
           ip=ip, ua=ua)

    db.commit()

    return {
        "success": True,
        "message": f"Đã hoàn {'toàn bộ' if is_full_refund else 'một phần'} {refund_data.amount} VND",
        "data": {
            "payment_id": payment.id,
            "refunded_amount": str(refund_data.amount),
            "total_refunded": str(payment.refunded_amount),
            "remaining": str(payment.amount - payment.refunded_amount),
            "payment_status": payment.status.value,
            "note": "[MOCK] Chưa gọi VNPAY Refund API thực. Cần tích hợp khi có credential."
        }
    }


# ==============================================================================
# CONFIG (Admin only + audit log)
# ==============================================================================

@router.put("/config/fee", summary="Cập nhật phí nền tảng [Admin]")
async def update_platform_fee(
    fee_percentage: Decimal = Query(..., ge=0, le=100),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Cập nhật phí nền tảng (audit log). Lưu ý: cần bảng config riêng để persist thực sự."""
    check_payment_config_access(current_user)

    ip, ua = _get_client_info(request) if request else ("", "")
    _audit(db, "CONFIG_FEE", None, current_user.id,
           note=f"Set platform fee = {fee_percentage}%", ip=ip, ua=ua)
    db.commit()

    return {
        "success": True,
        "message": f"Platform fee đã được cập nhật thành {fee_percentage}%",
        "note": "Cần persist vào bảng platform_config để áp dụng toàn hệ thống"
    }


@router.put("/config/cycle", summary="Cập nhật chu kỳ thanh toán [Admin]")
async def update_payment_cycle(
    cycle:   str     = Query(..., pattern="^(WEEKLY|MONTHLY)$"),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Cập nhật chu kỳ thanh toán (audit log)."""
    check_payment_config_access(current_user)

    ip, ua = _get_client_info(request) if request else ("", "")
    _audit(db, "CONFIG_CYCLE", None, current_user.id,
           note=f"Set payment cycle = {cycle}", ip=ip, ua=ua)
    db.commit()

    return {
        "success": True,
        "message": f"Payment cycle đã được cập nhật thành {cycle}",
        "note": "Cần persist vào bảng platform_config để áp dụng toàn hệ thống"
    }
