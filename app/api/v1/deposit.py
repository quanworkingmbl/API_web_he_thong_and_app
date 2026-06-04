"""
app/api/v1/deposit.py
=====================
Ví Sàn — Platform Deposit Wallet

Seller phải nạp ký quỹ >= MIN_DEPOSIT_REQUIRED (500,000đ) trước khi
bán hàng. Hỗ trợ 2 hình thức:
  1. Chuyển khoản ngân hàng thủ công → upload biên lai → Admin duyệt
  2. VNPay Sandbox (test) → tự động CONFIRMED khi callback thành công

Endpoints:
  Seller:
    GET  /deposit/my/balance       — Xem số dư & trạng thái ký quỹ
    GET  /deposit/my/history       — Lịch sử giao dịch (phân trang)
    POST /deposit/topup/bank       — Tạo yêu cầu nạp chuyển khoản
    POST /deposit/topup/vnpay      — Tạo URL thanh toán VNPay
    GET  /deposit/vnpay/return     — VNPay redirect callback (browser)
    GET  /deposit/vnpay/ipn        — VNPay IPN (server-to-server)

  Admin:
    GET  /deposit/admin/list       — Danh sách tất cả yêu cầu nạp
    POST /deposit/admin/{id}/confirm — Xác nhận đã nhận tiền
    POST /deposit/admin/{id}/reject  — Từ chối yêu cầu
    POST /deposit/admin/deduct     — Khấu trừ thủ công (xử lý gian lận)
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.settlement import (
    DepositStatus,
    DepositTransaction,
    DepositTransactionType,
    SellerDepositWallet,
)
from app.models.user import User
from app.services.vnpay import get_client_ip, vnpay_service

_TZ_VN = timezone(timedelta(hours=7))

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Hằng số ──────────────────────────────────────────────────────────────────
MIN_DEPOSIT_REQUIRED = Decimal("500000")
PLATFORM_BANK_NAME    = "MB Bank"
PLATFORM_BANK_ACCOUNT = "0123456789"
PLATFORM_BANK_OWNER   = "CONG TY SAN NONG SAN"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_seller(user: User):
    """Chỉ seller mới được gọi endpoint này."""
    if user.type not in ("producer", "seller"):
        raise HTTPException(status_code=403, detail="Chi danh cho Seller.")


def _require_admin(user: User):
    """Chỉ admin mới được gọi endpoint này."""
    if user.type not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Chi danh cho Admin.")


def _get_or_create_deposit_wallet(seller_id: int, db: Session) -> SellerDepositWallet:
    wallet = db.query(SellerDepositWallet).filter(
        SellerDepositWallet.seller_id == seller_id
    ).first()
    if not wallet:
        wallet = SellerDepositWallet(
            seller_id=seller_id,
            deposit_balance=Decimal("0"),
            total_deposited=Decimal("0"),
            total_deducted=Decimal("0"),
        )
        db.add(wallet)
        db.flush()
    return wallet


def _confirm_deposit_tx(tx: DepositTransaction, db: Session):
    """Xác nhận giao dịch nạp tiền → cộng vào deposit_balance."""
    wallet = _get_or_create_deposit_wallet(tx.seller_id, db)
    amount = Decimal(str(tx.amount))
    wallet.deposit_balance = Decimal(str(wallet.deposit_balance)) + amount
    wallet.total_deposited = Decimal(str(wallet.total_deposited)) + amount
    tx.status = DepositStatus.CONFIRMED
    tx.reviewed_at = datetime.now(timezone.utc)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class BankTopupRequest(BaseModel):
    amount: float
    bank_ref: str
    receipt_url: Optional[str] = None


class VNPayTopupRequest(BaseModel):
    amount: float


class AdminConfirmRequest(BaseModel):
    note: Optional[str] = None


class AdminRejectRequest(BaseModel):
    note: str


class AdminDeductRequest(BaseModel):
    seller_id: int
    amount: float
    note: str


# ==============================================================================
# SELLER ENDPOINTS
# ==============================================================================

@router.get("/my/balance", summary="Seller: Xem số dư ký quỹ")
async def get_my_deposit_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trả về số dư ký quỹ hiện tại và trạng thái (đủ / thiếu)."""
    _require_seller(current_user)
    wallet = _get_or_create_deposit_wallet(current_user.id, db)
    balance = Decimal(str(wallet.deposit_balance))
    return {
        "success": True,
        "data": {
            "deposit_balance":   str(balance),
            "total_deposited":   str(wallet.total_deposited),
            "total_deducted":    str(wallet.total_deducted),
            "min_required":      str(MIN_DEPOSIT_REQUIRED),
            "is_sufficient":     balance >= MIN_DEPOSIT_REQUIRED,
            "platform_bank": {
                "bank_name":    PLATFORM_BANK_NAME,
                "account_number": PLATFORM_BANK_ACCOUNT,
                "account_owner":  PLATFORM_BANK_OWNER,
            },
        },
    }


@router.get("/my/history", summary="Seller: Lịch sử giao dịch ký quỹ")
async def get_my_deposit_history(
    page:     int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status:   Optional[str] = Query(None, description="PENDING | CONFIRMED | REJECTED"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_seller(current_user)
    q = db.query(DepositTransaction).filter(
        DepositTransaction.seller_id == current_user.id
    )
    if status:
        try:
            q = q.filter(DepositTransaction.status == DepositStatus(status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Status khong hop le: {status}")

    total = q.count()
    items = q.order_by(DepositTransaction.created_at.desc()) \
             .offset((page - 1) * per_page).limit(per_page).all()

    return {
        "success": True,
        "data": [
            {
                "id":             t.id,
                "amount":         str(t.amount),
                "tx_type":        t.tx_type,
                "status":         t.status,
                "payment_method": t.payment_method,
                "bank_ref":       t.bank_ref,
                "receipt_url":    t.receipt_url,
                "note":           t.note,
                "created_at":     t.created_at.isoformat() if t.created_at else None,
                "reviewed_at":    t.reviewed_at.isoformat() if t.reviewed_at else None,
            }
            for t in items
        ],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/topup/bank", summary="Seller: Nạp tiền qua chuyển khoản ngân hàng")
async def topup_bank_transfer(
    body: BankTopupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Seller tạo yêu cầu nạp tiền bằng chuyển khoản:
      - Điền số tiền, mã tham chiếu GD
      - Upload ảnh biên lai (qua /medias trước, rồi truyền URL vào đây)
      - Admin sẽ xem và duyệt thủ công
    """
    _require_seller(current_user)
    if body.amount < float(MIN_DEPOSIT_REQUIRED):
        raise HTTPException(
            status_code=400,
            detail=f"So tien nap toi thieu la {int(MIN_DEPOSIT_REQUIRED):,}d."
        )

    tx = DepositTransaction(
        seller_id=current_user.id,
        amount=Decimal(str(body.amount)),
        tx_type=DepositTransactionType.TOP_UP,
        status=DepositStatus.PENDING,
        payment_method="BANK_TRANSFER",
        bank_ref=body.bank_ref,
        receipt_url=body.receipt_url,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    logger.info("[Deposit] Seller #%s tao yeu cau nap CK %s VND (tx #%s)", current_user.id, body.amount, tx.id)
    return {
        "success": True,
        "message": "Yeu cau nap tien da duoc gui. Vui long cho Admin xac nhan.",
        "data": {"transaction_id": tx.id, "status": tx.status},
    }


@router.post("/topup/vnpay", summary="Seller: Nạp tiền qua VNPay (test sandbox)")
async def topup_vnpay(
    body: VNPayTopupRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tạo URL thanh toán VNPay để nạp ký quỹ.
    Sau khi thanh toán thành công, VNPay gọi callback → tự động CONFIRMED.
    """
    _require_seller(current_user)
    if body.amount < float(MIN_DEPOSIT_REQUIRED):
        raise HTTPException(
            status_code=400,
            detail=f"So tien nap toi thieu la {int(MIN_DEPOSIT_REQUIRED):,}d."
        )

    # Tạo giao dịch PENDING trước để có ID
    tx = DepositTransaction(
        seller_id=current_user.id,
        amount=Decimal(str(body.amount)),
        tx_type=DepositTransactionType.TOP_UP,
        status=DepositStatus.PENDING,
        payment_method="VNPAY",
    )
    db.add(tx)
    db.flush()  # lấy tx.id

    # TxnRef: chỉ số — id (6 chữ số) + timestamp (14), ví dụ 00000220260601165343
    now_str = datetime.now(_TZ_VN).strftime("%Y%m%d%H%M%S")
    txn_ref = f"{tx.id:06d}{now_str}"
    tx.vnpay_txn_ref = txn_ref

    deposit_return_url = os.getenv("VNPAY_DEPOSIT_RETURN_URL") or (
        vnpay_service.return_url.replace(
            "/payments/vnpay/return", "/deposit/vnpay/return"
        )
    )
    order_info = f"Nap ky quy vi san seller #{current_user.id}"

    payment_url = vnpay_service.create_payment_url(
        order_id=tx.id,
        amount=float(body.amount),
        order_info=order_info,
        client_ip=get_client_ip(request),
        return_url=deposit_return_url,
        txn_ref=txn_ref,
    )

    db.commit()
    logger.info("[Deposit] Seller #%s tao VNPay deposit %s VND (txn_ref=%s)", current_user.id, body.amount, txn_ref)
    return {
        "success": True,
        "data": {
            "transaction_id": tx.id,
            "payment_url":    payment_url,
            "txn_ref":        txn_ref,
        },
    }


def _build_result_html(success: bool, amount: int = 0, tx_id: int = 0,
                        title: str = "", subtitle: str = "",
                        redirect_url: str = "/seller/wallet?tab=topup") -> str:
    """Tạo trang kết quả thanh toán đẹp với animation."""
    if success:
        icon_color  = "#22c55e"
        bg_color    = "#f0fdf4"
        border_color = "#bbf7d0"
        circle_anim = "circle-success"
        path_d = "M6 12 L10 16 L18 8"
        status_label = "THÀNH CÔNG"
        amount_fmt = f"{amount:,}đ".replace(",", ".")
        detail_html = f"""
            <div class="amount">+{amount_fmt}</div>
            <p class="detail-text">Ký quỹ Ví Sàn đã được cộng vào tài khoản của bạn</p>
        """
    else:
        icon_color   = "#ef4444"
        bg_color     = "#fef2f2"
        border_color = "#fecaca"
        circle_anim  = "circle-fail"
        path_d = "M8 8 L16 16 M16 8 L8 16"
        status_label = "THẤT BẠI"
        amount_fmt = f"{amount:,}đ".replace(",", ".") if amount else ""
        detail_html = f"""
            <p class="detail-text" style="color:#ef4444">
                Giao dịch không thành công.<br>Vui lòng thử lại hoặc liên hệ hỗ trợ.
            </p>
        """

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{'Nạp ký quỹ thành công' if success else 'Thanh toán thất bại'} — Agrarian</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: {bg_color};
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .card {{
      background: #fff;
      border-radius: 20px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.10);
      padding: 48px 40px 40px;
      text-align: center;
      max-width: 420px;
      width: 100%;
      border: 1px solid {border_color};
      animation: slide-up 0.5s cubic-bezier(.22,.68,0,1.2) both;
    }}
    @keyframes slide-up {{
      from {{ opacity: 0; transform: translateY(32px) scale(0.97); }}
      to   {{ opacity: 1; transform: translateY(0)   scale(1); }}
    }}

    /* ── Animated circle ── */
    .icon-wrap {{
      width: 88px; height: 88px;
      margin: 0 auto 24px;
    }}
    .icon-wrap svg {{
      width: 88px; height: 88px;
      overflow: visible;
    }}
    .circle {{
      fill: none;
      stroke: {icon_color};
      stroke-width: 3;
      stroke-dasharray: 264;
      stroke-dashoffset: 264;
      stroke-linecap: round;
      transform-origin: center;
      transform: rotate(-90deg);
      animation: draw-circle 0.65s ease forwards 0.1s;
    }}
    @keyframes draw-circle {{
      to {{ stroke-dashoffset: 0; }}
    }}
    .checkmark {{
      fill: none;
      stroke: {icon_color};
      stroke-width: 3.5;
      stroke-linecap: round;
      stroke-linejoin: round;
      stroke-dasharray: 40;
      stroke-dashoffset: 40;
      animation: draw-check 0.4s ease forwards 0.75s;
    }}
    @keyframes draw-check {{
      to {{ stroke-dashoffset: 0; }}
    }}
    .icon-bg {{
      fill: {'#dcfce7' if success else '#fee2e2'};
      stroke: none;
    }}

    /* ── Badge ── */
    .badge {{
      display: inline-block;
      background: {icon_color};
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      padding: 4px 14px;
      border-radius: 99px;
      margin-bottom: 14px;
    }}

    h1 {{
      font-size: 22px;
      font-weight: 700;
      color: #111;
      margin-bottom: 6px;
    }}
    .amount {{
      font-size: 36px;
      font-weight: 800;
      color: {icon_color};
      margin: 16px 0 8px;
      letter-spacing: -1px;
    }}
    .detail-text {{
      color: #6b7280;
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 28px;
    }}

    /* ── Info box ── */
    .info-box {{
      background: #f9fafb;
      border: 1px solid #f0f0f0;
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 28px;
      text-align: left;
    }}
    .info-row {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      padding: 6px 0;
      border-bottom: 1px solid #f3f4f6;
    }}
    .info-row:last-child {{ border-bottom: none; }}
    .info-label {{ color: #9ca3af; }}
    .info-value {{ color: #111; font-weight: 600; }}

    /* ── Buttons ── */
    .btn-primary {{
      display: block;
      width: 100%;
      padding: 14px;
      background: {'#16a34a' if success else '#6b7280'};
      color: #fff;
      font-size: 15px;
      font-weight: 600;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      text-decoration: none;
      transition: opacity 0.15s;
    }}
    .btn-primary:hover {{ opacity: 0.88; }}

    /* ── Countdown ── */
    .countdown {{
      font-size: 12px;
      color: #9ca3af;
      margin-top: 14px;
    }}
    #cnt {{ font-weight: 700; color: #374151; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon-wrap">
      <svg viewBox="0 0 88 88">
        <circle class="icon-bg" cx="44" cy="44" r="40"/>
        <circle class="circle" cx="44" cy="44" r="40"/>
        <path class="checkmark" d="{path_d.replace('6 12','18 44').replace('10 16','38 60').replace('18 8','70 28').replace('8 8','28 28').replace('16 16','60 60').replace('16 8','60 28').replace('8 16','28 60')}"/>
      </svg>
    </div>

    <div class="badge">{status_label}</div>
    <h1>{'Nạp ký quỹ thành công!' if success else 'Thanh toán không thành công'}</h1>

    {detail_html}

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Mã giao dịch</span>
        <span class="info-value">#{tx_id}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Phương thức</span>
        <span class="info-value">VNPay</span>
      </div>
      <div class="info-row">
        <span class="info-label">Trạng thái</span>
        <span class="info-value" style="color:{icon_color}">{status_label}</span>
      </div>
    </div>

    <a href="{redirect_url}" class="btn-primary" id="back-btn">
      {'↩ Quay lại Ví Sàn' if success else '↩ Thử lại'}
    </a>
    <p class="countdown">Tự động chuyển sau <span id="cnt">5</span> giây</p>
  </div>

  <script>
    var n = 5;
    var el = document.getElementById('cnt');
    var timer = setInterval(function() {{
      n--;
      el.textContent = n;
      if (n <= 0) {{
        clearInterval(timer);
        window.location.href = '{redirect_url}';
      }}
    }}, 1000);
  </script>
</body>
</html>"""


@router.get("/vnpay/return", summary="VNPay: Redirect callback sau khi thanh toán")
async def vnpay_return(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    VNPay redirect người dùng về đây sau khi thanh toán.
    Xác minh chữ ký → cập nhật trạng thái → trả về HTML thông báo đẹp.
    """
    params  = dict(request.query_params)
    result  = vnpay_service.verify_return_url(params)
    txn_ref = params.get("vnp_TxnRef", "")

    # Lấy VNPAY_WEB_URL để build redirect link về UI
    web_url = os.getenv("VNPAY_WEB_URL", "").rstrip("/")
    wallet_url = f"{web_url}/seller/wallet?tab=history" if web_url else "/seller/wallet?tab=history"

    tx = db.query(DepositTransaction).filter(
        DepositTransaction.vnpay_txn_ref == txn_ref
    ).first()

    if not tx:
        return HTMLResponse(
            _build_result_html(
                success=False, tx_id=0,
                redirect_url=wallet_url,
            ),
            status_code=404,
        )

    # Đã xử lý rồi → vẫn hiện trang success đẹp
    if tx.status == DepositStatus.CONFIRMED:
        return HTMLResponse(
            _build_result_html(
                success=True,
                amount=int(tx.amount),
                tx_id=tx.id,
                redirect_url=wallet_url,
            )
        )

    tx.vnpay_response = json.dumps(params)

    if result["is_valid"] and vnpay_service.is_payment_success(
        result["response_code"], result["transaction_status"]
    ):
        _confirm_deposit_tx(tx, db)
        db.commit()
        logger.info("[Deposit] VNPay return OK — tx #%s CONFIRMED", tx.id)
        return HTMLResponse(
            _build_result_html(
                success=True,
                amount=int(tx.amount),
                tx_id=tx.id,
                redirect_url=wallet_url,
            )
        )
    else:
        tx.status = DepositStatus.REJECTED
        tx.note   = f"VNPay response_code={result.get('response_code')}"
        db.commit()
        logger.warning("[Deposit] VNPay return FAIL — tx #%s, code=%s", tx.id, result.get("response_code"))
        return HTMLResponse(
            _build_result_html(
                success=False,
                amount=int(tx.amount) if tx.amount else 0,
                tx_id=tx.id,
                redirect_url=wallet_url,
            )
        )



@router.get("/vnpay/ipn", summary="VNPay: IPN server-to-server callback")
async def vnpay_ipn(
    request: Request,
    db: Session = Depends(get_db),
):
    """VNPay gọi IPN để xác nhận giao dịch phía server."""
    params = dict(request.query_params)
    result = vnpay_service.verify_return_url(params)

    if not result["is_valid"]:
        return JSONResponse({"RspCode": "97", "Message": "Invalid Checksum"})

    txn_ref = params.get("vnp_TxnRef", "")
    tx = (
        db.query(DepositTransaction)
        .filter(DepositTransaction.vnpay_txn_ref == txn_ref)
        .with_for_update()
        .first()
    )

    if not tx:
        return JSONResponse({"RspCode": "01", "Message": "Order not found"})

    if tx.status == DepositStatus.CONFIRMED:
        return JSONResponse({"RspCode": "02", "Message": "Order already confirmed"})

    tx.vnpay_response = json.dumps(params)

    if vnpay_service.is_payment_success(result["response_code"], result["transaction_status"]):
        _confirm_deposit_tx(tx, db)
        db.commit()
        logger.info("[Deposit] VNPay IPN OK — tx #%s CONFIRMED", tx.id)
        return JSONResponse({"RspCode": "00", "Message": "Confirm Success"})
    else:
        tx.status = DepositStatus.REJECTED
        tx.note = f"IPN fail code={result.get('response_code')}"
        db.commit()
        return JSONResponse({"RspCode": "00", "Message": "Confirm Success"})  # VNPAY yêu cầu luôn trả 00


# ==============================================================================
# ADMIN ENDPOINTS
# ==============================================================================

@router.get("/admin/list", summary="Admin: Danh sách yêu cầu nạp ký quỹ")
async def admin_list_deposits(
    page:      int = Query(1, ge=1),
    per_page:  int = Query(20, ge=1, le=100),
    status:    Optional[str] = Query(None, description="PENDING | CONFIRMED | REJECTED"),
    seller_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    q = db.query(DepositTransaction)
    if status:
        try:
            q = q.filter(DepositTransaction.status == DepositStatus(status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Status khong hop le: {status}")
    if seller_id:
        q = q.filter(DepositTransaction.seller_id == seller_id)

    total = q.count()
    items = q.order_by(DepositTransaction.created_at.desc()) \
             .offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for t in items:
        seller = db.query(User).filter(User.id == t.seller_id).first()
        result.append({
            "id":             t.id,
            "seller_id":      t.seller_id,
            "seller_name":    seller.name if seller else None,
            "seller_email":   seller.email if seller else None,
            "amount":         str(t.amount),
            "tx_type":        t.tx_type,
            "status":         t.status,
            "payment_method": t.payment_method,
            "bank_ref":       t.bank_ref,
            "receipt_url":    t.receipt_url,
            "note":           t.note,
            "created_at":     t.created_at.isoformat() if t.created_at else None,
            "reviewed_at":    t.reviewed_at.isoformat() if t.reviewed_at else None,
        })

    return {
        "success": True,
        "data": result,
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/admin/{tx_id}/confirm", summary="Admin: Xác nhận yêu cầu nạp tiền")
async def admin_confirm_deposit(
    tx_id: int,
    body:  AdminConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    tx = db.query(DepositTransaction).filter(DepositTransaction.id == tx_id).with_for_update().first()
    if not tx:
        raise HTTPException(status_code=404, detail="Khong tim thay giao dich.")
    if tx.status != DepositStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Giao dich dang o trang thai {tx.status}, khong the duyet.")

    _confirm_deposit_tx(tx, db)
    tx.note        = body.note
    tx.reviewed_by = current_user.id
    db.commit()

    logger.info("[Deposit] Admin #%s xac nhan tx #%s (seller #%s, amount=%s)", current_user.id, tx.id, tx.seller_id, tx.amount)
    return {"success": True, "message": "Da xac nhan nap ky quy thanh cong."}


@router.post("/admin/{tx_id}/reject", summary="Admin: Từ chối yêu cầu nạp tiền")
async def admin_reject_deposit(
    tx_id: int,
    body:  AdminRejectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    tx = db.query(DepositTransaction).filter(DepositTransaction.id == tx_id).with_for_update().first()
    if not tx:
        raise HTTPException(status_code=404, detail="Khong tim thay giao dich.")
    if tx.status != DepositStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Giao dich dang o trang thai {tx.status}, khong the tu choi.")

    tx.status      = DepositStatus.REJECTED
    tx.note        = body.note
    tx.reviewed_by = current_user.id
    tx.reviewed_at = datetime.now(timezone.utc)
    db.commit()

    logger.info("[Deposit] Admin #%s tu choi tx #%s ly do: %s", current_user.id, tx.id, body.note)
    return {"success": True, "message": "Da tu choi yeu cau nap tien."}


@router.post("/admin/deduct", summary="Admin: Khấu trừ ký quỹ seller (xử lý gian lận)")
async def admin_deduct_deposit(
    body: AdminDeductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Admin khấu trừ từ deposit_balance của seller để xử lý:
      - Trường hợp gian lận
      - Hoàn tiền cho buyer khi seller không phối hợp
    """
    _require_admin(current_user)
    amount = Decimal(str(body.amount))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="So tien khau tru phai > 0.")

    wallet = db.query(SellerDepositWallet).filter(
        SellerDepositWallet.seller_id == body.seller_id
    ).with_for_update().first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Seller chua co vi ky quy.")

    current_balance = Decimal(str(wallet.deposit_balance))
    new_balance     = current_balance - amount

    wallet.deposit_balance = new_balance
    wallet.total_deducted  = Decimal(str(wallet.total_deducted)) + amount

    # Ghi lịch sử
    tx = DepositTransaction(
        seller_id=body.seller_id,
        amount=amount,
        tx_type=DepositTransactionType.DEDUCT,
        status=DepositStatus.CONFIRMED,
        payment_method=None,
        note=body.note,
        reviewed_by=current_user.id,
        reviewed_at=datetime.now(timezone.utc),
    )
    db.add(tx)
    db.commit()

    logger.warning(
        "[Deposit] Admin #%s khau tru %s VND tu seller #%s. Balance: %s -> %s. Ly do: %s",
        current_user.id, amount, body.seller_id, current_balance, new_balance, body.note,
    )
    return {
        "success": True,
        "message": f"Da khau tru {int(amount):,}d tu seller #{body.seller_id}.",
        "data": {
            "new_balance": str(new_balance),
            "is_sufficient": new_balance >= MIN_DEPOSIT_REQUIRED,
        },
    }


@router.get("/admin/wallets", summary="Admin: Danh sách ví ký quỹ tất cả seller")
async def admin_list_wallets(
    page:     int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    low_balance: bool = Query(False, description="Chỉ lấy seller thiếu ký quỹ"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    q = db.query(SellerDepositWallet)
    if low_balance:
        q = q.filter(SellerDepositWallet.deposit_balance < float(MIN_DEPOSIT_REQUIRED))

    total = q.count()
    items = q.order_by(SellerDepositWallet.deposit_balance.asc()) \
             .offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for w in items:
        seller = db.query(User).filter(User.id == w.seller_id).first()
        bal = Decimal(str(w.deposit_balance))
        result.append({
            "seller_id":       w.seller_id,
            "seller_name":     seller.name  if seller else None,
            "seller_email":    seller.email if seller else None,
            "deposit_balance": str(bal),
            "total_deposited": str(w.total_deposited),
            "total_deducted":  str(w.total_deducted),
            "is_sufficient":   bal >= MIN_DEPOSIT_REQUIRED,
            "updated_at":      w.updated_at.isoformat() if w.updated_at else None,
        })

    return {
        "success": True,
        "data": result,
        "meta": {"total": total, "page": page, "per_page": per_page},
    }
