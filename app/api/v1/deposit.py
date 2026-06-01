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

    # TxnRef: chỉ chữ+số (VNPAY Alphanumeric) — DEP + id + timestamp
    now_str = datetime.now(_TZ_VN).strftime("%Y%m%d%H%M%S")
    txn_ref = f"DEP{tx.id}{now_str}"
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


@router.get("/vnpay/return", summary="VNPay: Redirect callback sau khi thanh toán")
async def vnpay_return(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    VNPay redirect người dùng về đây sau khi thanh toán.
    Xác minh chữ ký → cập nhật trạng thái → trả về HTML thông báo.
    """
    params = dict(request.query_params)
    result = vnpay_service.verify_return_url(params)

    txn_ref = params.get("vnp_TxnRef", "")
    tx = db.query(DepositTransaction).filter(
        DepositTransaction.vnpay_txn_ref == txn_ref
    ).first()

    if not tx:
        return HTMLResponse("<h2>Khong tim thay giao dich. Vui long lien he ho tro.</h2>", status_code=404)

    if tx.status == DepositStatus.CONFIRMED:
        return HTMLResponse("<h2>Giao dich da duoc xu ly truoc do.</h2>")

    tx.vnpay_response = json.dumps(params)

    if result["is_valid"] and vnpay_service.is_payment_success(
        result["response_code"], result["transaction_status"]
    ):
        _confirm_deposit_tx(tx, db)
        db.commit()
        logger.info("[Deposit] VNPay return OK — tx #%s CONFIRMED", tx.id)
        return HTMLResponse(
            f"<h2>Nap ky quy thanh cong: {int(tx.amount):,}d</h2>"
            "<p>Ban co the dong trang nay va quay lai Ky Quy Seller.</p>"
        )
    else:
        tx.status = DepositStatus.REJECTED
        tx.note = f"VNPay response_code={result.get('response_code')}"
        db.commit()
        logger.warning("[Deposit] VNPay return FAIL — tx #%s, code=%s", tx.id, result.get("response_code"))
        return HTMLResponse(
            f"<h2>Thanh toan that bai (ma: {result.get('response_code')})</h2>"
            "<p>Vui long thu lai hoac lien he ho tro.</p>"
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
