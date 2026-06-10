"""
Settlement API – Đối soát & Chi trả cho Seller

Endpoints:
- GET  /settlement/wallet                    – Seller xem ví (kèm max_withdrawable)
- GET  /settlement/history                   – Lịch sử đối soát
- POST /settlement/create                    – Admin tạo kỳ đối soát
- POST /settlement/{id}/approve              – Admin duyệt kỳ đối soát
- POST /settlement/{id}/payout               – Admin chi trả kỳ đối soát
- GET  /settlement/payouts                   – Lịch sử payout
- POST /settlement/withdrawal/request        – Seller tạo yêu cầu rút tiền
- GET  /settlement/withdrawal/my             – Seller xem yêu cầu của mình
- GET  /settlement/withdrawal/admin          – Admin xem tất cả yêu cầu
- POST /settlement/withdrawal/{id}/approve   – Admin duyệt yêu cầu rút
- POST /settlement/withdrawal/{id}/reject    – Admin từ chối yêu cầu rút
- POST /settlement/release-reserves          – Admin/system giải phóng reserve đã đủ 7 ngày
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.database import get_db
from app.models.settlement import (
    SellerWallet, Settlement, SettlementStatus,
    Payout, PayoutStatus,
    WithdrawalRequest, WithdrawalStatus,
)
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.seller_profile import SellerProfile
from app.api.v1.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# HELPERS
# ==============================================================================

ADMIN_TYPES = {"admin", "superadmin"}


def _require_admin(user: User):
    if user.type not in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền thực hiện")


def _require_seller(user: User):
    if user.type not in {"producer", "seller", "admin", "superadmin"}:
        raise HTTPException(status_code=403, detail="Chỉ người bán mới có quyền truy cập")


def _get_or_create_wallet(seller_id: int, db: Session) -> SellerWallet:
    wallet = db.query(SellerWallet).filter(SellerWallet.seller_id == seller_id).first()
    if not wallet:
        wallet = SellerWallet(seller_id=seller_id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CreateSettlementRequest(BaseModel):
    seller_id: int
    period_start: datetime
    period_end: datetime
    note: Optional[str] = None


class PayoutRequest(BaseModel):
    note: Optional[str] = None
    transaction_ref: Optional[str] = None


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("/wallet", summary="Seller xem ví của mình")
async def get_seller_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin ví seller:
    - pending_balance   : Tiền đang giữ 7 ngày chờ khiếu nại
    - available_balance : Tiền đã qua 7 ngày, có thể rút
    - total_withdrawn   : Tổng đã rút ra
    - total_earned      : Tổng doanh thu (seller_amount) đã credited
    - total_order_value : Tổng giá trị đơn hàng (trước phí)
    - total_platform_fee_paid : Tổng phí sàn đã khấu trừ
    """
    _require_seller(current_user)
    wallet = _get_or_create_wallet(current_user.id, db)

    from sqlalchemy import func as sf
    from app.models.order import Order, OrderStatus
    from app.services.wallet import calc_max_withdrawable

    # Tổng tất cả đơn DELIVERED đã credited cho seller
    total_stats = db.query(
        sf.count(Order.id).label("total_orders"),
        sf.coalesce(sf.sum(Order.seller_amount), 0).label("total_earned"),
        sf.coalesce(sf.sum(Order.total_amount), 0).label("total_order_value"),
        sf.coalesce(sf.sum(Order.platform_fee_amount), 0).label("total_platform_fee"),
    ).filter(
        Order.seller_id == current_user.id,
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,
        Order.is_active == True,
    ).first()

    # Tháng hiện tại
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    month_stats = db.query(
        sf.coalesce(sf.sum(Order.seller_amount), 0).label("month_earned"),
        sf.coalesce(sf.sum(Order.total_amount), 0).label("month_order_value"),
    ).filter(
        Order.seller_id == current_user.id,
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,
        Order.is_active == True,
        Order.delivered_at >= month_start,
    ).first()

    max_withdraw = calc_max_withdrawable(current_user.id, db)

    return {
        "success": True,
        "data": {
            "seller_id": current_user.id,
            # Số dư ví
            "pending_balance":   str(wallet.pending_balance   or 0),
            "available_balance": str(wallet.available_balance or 0),
            "reserve_balance":   str(wallet.reserve_balance   or 0),   # legacy
            "total_withdrawn":   str(wallet.total_withdrawn   or 0),
            "max_withdrawable":  str(max_withdraw),
            # Thống kê doanh thu (all time)
            "total_earned":             str(total_stats.total_earned      if total_stats else 0),
            "total_order_value":        str(total_stats.total_order_value if total_stats else 0),
            "total_platform_fee_paid":  str(total_stats.total_platform_fee if total_stats else 0),
            "total_delivered_orders":   total_stats.total_orders           if total_stats else 0,
            # Tháng hiện tại
            "this_month_earned":        str(month_stats.month_earned      if month_stats else 0),
            "this_month_order_value":   str(month_stats.month_order_value if month_stats else 0),
            "updated_at": wallet.updated_at.isoformat() if wallet.updated_at else None,
        }
    }



@router.get("/history", summary="Lịch sử kỳ đối soát")
async def get_settlement_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=500),
    seller_id: Optional[int] = Query(None, description="Filter theo seller (admin)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách kỳ đối soát. Seller chỉ xem của mình, admin xem tất cả."""
    _require_seller(current_user)

    query = db.query(Settlement)
    is_admin = current_user.type in ADMIN_TYPES
    if is_admin and seller_id:
        query = query.filter(Settlement.seller_id == seller_id)
    elif not is_admin:
        query = query.filter(Settlement.seller_id == current_user.id)

    total = query.count()
    skip = (page - 1) * limit
    items = query.order_by(Settlement.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id":                  s.id,
                "seller_id":           s.seller_id,
                "period_start":        s.period_start.isoformat(),
                "period_end":          s.period_end.isoformat(),
                "total_orders":        s.total_orders,
                "total_amount":        str(s.total_amount),
                "total_platform_fee":  str(s.total_platform_fee),
                "total_seller_amount": str(s.total_seller_amount),
                "status":              s.status.value,
                "note":                s.note,
                "created_at":          s.created_at.isoformat() if s.created_at else None
            }
            for s in items
        ],
        "meta": {"total": total, "page": page, "limit": limit}
    }


@router.post("/create", summary="Admin tạo kỳ đối soát cho seller")
async def create_settlement(
    data: CreateSettlementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo kỳ đối soát: tổng hợp đơn hàng DELIVERED trong khoảng thời gian.
    Tự động tính total_orders, total_amount, platform_fee, seller_amount.
    """
    _require_admin(current_user)

    # Lấy các đơn hàng DELIVERED trong kỳ VÀ đã được credited vào ví
    # wallet_credited = True đảm bảo chỉ tính đơn user đã xác nhận nhận hàng
    delivered_orders = db.query(Order).filter(
        Order.seller_id == data.seller_id,
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,      # chỉ đơn đã credited – tránh COD chưa thu
        Order.delivered_at >= data.period_start,
        Order.delivered_at <= data.period_end
    ).all()

    total_orders = len(delivered_orders)
    total_amount = sum(o.subtotal for o in delivered_orders)
    total_platform_fee = sum(o.platform_fee_amount for o in delivered_orders)
    total_seller_amount = sum(o.seller_amount for o in delivered_orders)
    total_vat = sum(o.vat_amount or 0 for o in delivered_orders)

    settlement = Settlement(
        seller_id=data.seller_id,
        period_start=data.period_start,
        period_end=data.period_end,
        total_orders=total_orders,
        total_amount=total_amount,
        total_platform_fee=total_platform_fee,
        total_seller_amount=total_seller_amount,
        status=SettlementStatus.PENDING,
        note=data.note
    )
    db.add(settlement)

    # ⚠️ KHÔNG cộng wallet.pending_balance ở đây!
    # pending_balance đã được cộng bởi credit_seller_wallet()
    # khi user xác nhận nhận hàng (confirm_order_received).
    # Cộng thêm ở đây sẽ gây double-credit.

    db.commit()
    db.refresh(settlement)

    return {
        "success": True,
        "message": f"Đã tạo kỳ đối soát với {total_orders} đơn hàng",
        "data": {
            "settlement_id":      settlement.id,
            "total_orders":       total_orders,
            "total_amount":       str(total_amount),
            "total_vat":          str(total_vat),
            "total_platform_fee": str(total_platform_fee),
            "total_seller_amount": str(total_seller_amount),
        }
    }


@router.post("/{settlement_id}/approve", summary="Admin duyệt kỳ đối soát")
async def approve_settlement(
    settlement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duyệt kỳ đối soát (CHỈ đánh dấu trạng thái — KHÔNG thao tác ví).

    Lý do: Tiền (pending → available) đã được release_matured_holds() xử lý
    tự động theo từng đơn hàng đủ 7 ngày. Settlement là báo cáo tổng hợp,
    không trực tiếp dịch chuyển số dư để tránh double-credit.
    """
    _require_admin(current_user)

    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Kỳ đối soát không tồn tại")

    if settlement.status != SettlementStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể duyệt kỳ đối soát ở trạng thái {settlement.status.value}"
        )

    settlement.status = SettlementStatus.APPROVED
    settlement.approved_by = current_user.id
    settlement.approved_at = datetime.utcnow()

    # ⚠️ KHÔNG thao tác ví tại đây!
    # pending → available được xử lý tự động bởi release_matured_holds()
    # (scheduler hàng ngày hoặc admin bấm "Giải phóng Reserve")
    # Thao tác tại đây sẽ gây double-credit.

    db.commit()

    return {
        "success": True,
        "message": "Đã duyệt kỳ đối soát (xem ví tại trang Đối Soát & Chi Trả)",
        "settlement_id": settlement_id,
        "status": "APPROVED"
    }


@router.post("/{settlement_id}/payout", summary="Admin ghi nhận chi trả (audit-only)")
async def create_payout(
    settlement_id: int,
    payout_data: PayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ghi nhận chi trả kỳ đối soát (CHỈ audit — KHÔNG thao tác ví).

    Luồng chi trả thực tế đã chuyển sang WithdrawalRequest:
    Seller tự tạo yêu cầu rút → Admin duyệt → trừ available_balance.
    Endpoint này chỉ lưu record Payout để tham chiếu lịch sử.
    """
    _require_admin(current_user)

    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Kỳ đối soát không tồn tại")

    if settlement.status != SettlementStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể ghi nhận chi trả kỳ đối soát đã được duyệt"
        )

    # Lấy thông tin ngân hàng từ seller profile
    seller_profile = db.query(SellerProfile).filter(
        SellerProfile.user_id == settlement.seller_id
    ).first()

    payout = Payout(
        seller_id=settlement.seller_id,
        settlement_id=settlement.id,
        amount=settlement.total_seller_amount,
        bank_name=seller_profile.bank_name if seller_profile else None,
        bank_account_number=seller_profile.bank_account_number if seller_profile else None,
        bank_account_name=seller_profile.bank_account_name if seller_profile else None,
        status=PayoutStatus.SUCCESS,
        transaction_ref=payout_data.transaction_ref,
        note=payout_data.note,
        processed_by=current_user.id,
        processed_at=datetime.utcnow()
    )
    db.add(payout)

    # ⚠️ KHÔNG thao tác ví tại đây!
    # Việc trừ available_balance / cộng total_withdrawn được thực hiện
    # bởi approve_withdrawal() khi admin duyệt WithdrawalRequest.

    # Cập nhật settlement → COMPLETED
    settlement.status = SettlementStatus.COMPLETED

    db.commit()
    db.refresh(payout)

    return {
        "success": True,
        "message": "Đã ghi nhận chi trả (luồng rút tiền thực tế qua Yêu cầu rút tiền)",
        "data": {
            "payout_id": payout.id,
            "amount": str(payout.amount),
            "status": "SUCCESS",
            "transaction_ref": payout.transaction_ref
        }
    }


@router.get("/payouts", summary="Lịch sử chi trả")
async def get_payout_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử payout. Seller xem của mình, admin xem tất cả."""
    _require_seller(current_user)

    query = db.query(Payout)
    if current_user.type != "admin":
        query = query.filter(Payout.seller_id == current_user.id)

    total = query.count()
    skip = (page - 1) * limit
    items = query.order_by(Payout.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "settlement_id": p.settlement_id,
                "amount": str(p.amount),
                "bank_name": p.bank_name,
                "bank_account_number": p.bank_account_number,
                "status": p.status.value,
                "transaction_ref": p.transaction_ref,
                "note": p.note,
                "processed_at": p.processed_at.isoformat() if p.processed_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in items
        ],
        "meta": {"total": total, "page": page, "limit": limit}
    }


# ==============================================================================
# WITHDRAWAL REQUEST – Seller rút tiền (luồng mới)
# ==============================================================================

class WithdrawalRequestCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Số tiền muốn rút (> 0)")
    note: Optional[str] = None


class WithdrawalReviewRequest(BaseModel):
    admin_note: Optional[str] = None
    transaction_ref: Optional[str] = None


@router.post("/withdrawal/request", summary="Seller tạo yêu cầu rút tiền")
async def create_withdrawal_request(
    data: WithdrawalRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Seller tạo yêu cầu rút tiền.
    Chỉ rút được: available_balance - min_reserve.
    Không được có yêu cầu PENDING khác đang chờ duyệt.
    """
    _require_seller(current_user)
    from app.services.wallet import calc_max_withdrawable
    from decimal import Decimal as D

    wallet = _get_or_create_wallet(current_user.id, db)
    max_withdraw = calc_max_withdrawable(current_user.id, db)
    min_reserve  = D("0")   # Không giữ dự phòng — tiền đã qua 7 ngày là rút được hết

    if data.amount > max_withdraw:
        raise HTTPException(
            status_code=400,
            detail=f"Số tiền vượt quá giới hạn. Tối đa có thể rút: {max_withdraw:,.0f} VND "
                   f"(available_balance={wallet.available_balance:,.0f})"
        )

    # Kiểm tra không có yêu cầu PENDING nào đang chờ
    pending_exists = db.query(WithdrawalRequest).filter(
        WithdrawalRequest.seller_id == current_user.id,
        WithdrawalRequest.status == WithdrawalStatus.PENDING,
    ).first()
    if pending_exists:
        raise HTTPException(status_code=400, detail="Bạn đang có yêu cầu rút tiền chờ duyệt. Vui lòng chờ admin xử lý.")

    # Snapshot thông tin ngân hàng
    profile = db.query(SellerProfile).filter(SellerProfile.user_id == current_user.id).first()

    wr = WithdrawalRequest(
        seller_id=current_user.id,
        amount=data.amount,
        available_snapshot=wallet.available_balance,
        min_reserve_snapshot=min_reserve,
        bank_name=profile.bank_name if profile else None,
        bank_account_number=profile.bank_account_number if profile else None,
        bank_account_name=profile.bank_account_name if profile else None,
        note=data.note,
        status=WithdrawalStatus.PENDING,
    )
    db.add(wr)
    db.commit()
    db.refresh(wr)

    return {
        "success": True,
        "message": "Đã tạo yêu cầu rút tiền, chờ admin duyệt.",
        "data": {
            "id": wr.id,
            "amount": str(wr.amount),
            "status": wr.status.value,
            "bank_account_number": wr.bank_account_number,
            "created_at": wr.created_at.isoformat() if wr.created_at else None,
        }
    }


@router.get("/withdrawal/my", summary="Seller xem danh sách yêu cầu rút của mình")
async def get_my_withdrawal_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_seller(current_user)
    query = db.query(WithdrawalRequest).filter(WithdrawalRequest.seller_id == current_user.id)
    total = query.count()
    items = query.order_by(WithdrawalRequest.created_at.desc()).offset((page-1)*limit).limit(limit).all()
    return {
        "success": True,
        "data": [
            {
                "id": w.id,
                "amount": str(w.amount),
                "status": w.status.value,
                "note": w.note,
                "admin_note": w.admin_note,
                "bank_account_number": w.bank_account_number,
                "transaction_ref": w.transaction_ref,
                "created_at": w.created_at.isoformat() if w.created_at else None,
                "reviewed_at": w.reviewed_at.isoformat() if w.reviewed_at else None,
            } for w in items
        ],
        "meta": {"total": total, "page": page, "limit": limit}
    }


@router.get("/withdrawal/admin", summary="Admin xem tất cả yêu cầu rút")
async def admin_list_withdrawal_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    seller_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    query = db.query(WithdrawalRequest)
    if seller_id:
        query = query.filter(WithdrawalRequest.seller_id == seller_id)
    if status:
        try:
            query = query.filter(WithdrawalRequest.status == WithdrawalStatus(status.upper()))
        except ValueError:
            pass
    total = query.count()
    items = query.order_by(WithdrawalRequest.created_at.desc()).offset((page-1)*limit).limit(limit).all()

    # Lấy tên seller
    seller_ids = list({w.seller_id for w in items})
    sellers = {u.id: u.name for u in db.query(User).filter(User.id.in_(seller_ids)).all()}

    return {
        "success": True,
        "data": [
            {
                "id": w.id,
                "seller_id": w.seller_id,
                "seller_name": sellers.get(w.seller_id, f"Seller #{w.seller_id}"),
                "amount": str(w.amount),
                "available_snapshot": str(w.available_snapshot or 0),
                "min_reserve_snapshot": str(w.min_reserve_snapshot or 0),
                "status": w.status.value,
                "note": w.note,
                "admin_note": w.admin_note,
                "bank_name": w.bank_name,
                "bank_account_number": w.bank_account_number,
                "bank_account_name": w.bank_account_name,
                "transaction_ref": w.transaction_ref,
                "created_at": w.created_at.isoformat() if w.created_at else None,
                "reviewed_at": w.reviewed_at.isoformat() if w.reviewed_at else None,
            } for w in items
        ],
        "meta": {"total": total, "page": page, "limit": limit}
    }


@router.post("/withdrawal/{wr_id}/approve", summary="Admin duyệt yêu cầu rút tiền")
async def approve_withdrawal(
    wr_id: int,
    data: WithdrawalReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Admin duyệt → trừ available_balance, cộng total_withdrawn.
    """
    _require_admin(current_user)
    wr = db.query(WithdrawalRequest).filter(WithdrawalRequest.id == wr_id).first()
    if not wr:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")
    if wr.status != WithdrawalStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Yêu cầu đang ở trạng thái {wr.status.value}, không thể duyệt")

    wallet = _get_or_create_wallet(wr.seller_id, db)
    if wallet.available_balance < wr.amount:
        raise HTTPException(status_code=400, detail="Số dư khả dụng của seller không đủ")

    wallet.available_balance -= wr.amount
    wallet.total_withdrawn   += wr.amount

    wr.status          = WithdrawalStatus.COMPLETED
    wr.admin_note      = data.admin_note
    wr.transaction_ref = data.transaction_ref
    wr.reviewed_by     = current_user.id
    wr.reviewed_at     = datetime.utcnow()

    db.commit()
    return {"success": True, "message": "Đã duyệt và ghi nhận chi trả.", "withdrawal_id": wr_id}


@router.post("/withdrawal/{wr_id}/reject", summary="Admin từ chối yêu cầu rút tiền")
async def reject_withdrawal(
    wr_id: int,
    data: WithdrawalReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    wr = db.query(WithdrawalRequest).filter(WithdrawalRequest.id == wr_id).first()
    if not wr:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")
    if wr.status != WithdrawalStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Yêu cầu đang ở trạng thái {wr.status.value}")

    wr.status      = WithdrawalStatus.REJECTED
    wr.admin_note  = data.admin_note
    wr.reviewed_by = current_user.id
    wr.reviewed_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": "Đã từ chối yêu cầu rút tiền.", "withdrawal_id": wr_id}



@router.post("/release-reserves", summary="Admin giải phóng reserve đã đủ 14 ngày")
async def release_seller_reserves(
    seller_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Giải phóng phần reserve 20% của các đơn đã quá 14 ngày về available_balance.
    - Nếu truyền seller_id → chỉ xử lý seller đó.
    - Nếu không truyền → xử lý tất cả sellers.
    """
    _require_admin(current_user)
    from app.services.wallet import release_matured_reserves

    if seller_id:
        total_released = release_matured_reserves(seller_id, db)
        db.commit()
        return {"success": True, "seller_id": seller_id, "released": str(total_released)}

    # Tất cả sellers có reserve chờ giải phóng
    from app.models.order import Order, OrderStatus
    now = datetime.utcnow()
    seller_ids = db.query(Order.seller_id).filter(
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,
        Order.reserve_released == False,
        Order.reserve_release_at <= now,
    ).distinct().all()

    results = []
    for (sid,) in seller_ids:
        released = release_matured_reserves(sid, db)
        results.append({"seller_id": sid, "released": str(released)})

    db.commit()
    return {"success": True, "processed": len(results), "details": results}


# ==============================================================================
# RESERVE SCHEDULE — Seller xem lịch giải phóng reserve sắp tới
# ==============================================================================

@router.get("/reserve-schedule", summary="Lịch giải phóng reserve sắp tới (Seller)")
async def get_reserve_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Seller xem danh sách các khoản reserve đang bị giữ và ngày dự kiến được giải phóng.
    Sắp xếp theo ngày giải phóng gần nhất.
    """
    _require_seller(current_user)

    now = datetime.utcnow()
    from decimal import Decimal as D

    # Luồng mới: 100% seller_amount nằm trong pending_balance (không còn 20% reserve)
    upcoming = db.query(Order).filter(
        Order.seller_id == current_user.id,
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,
        Order.reserve_released == False,
        Order.reserve_release_at != None,
    ).order_by(Order.reserve_release_at.asc()).limit(30).all()

    items = []
    total_pending = D("0")
    for o in upcoming:
        # 100% seller_amount đang giữ (không phải 20% như phiên bản cũ)
        reserve_amt = D(str(o.seller_amount or 0)).quantize(D("0.01"))
        total_pending += reserve_amt
        release_dt = o.reserve_release_at
        # Tính số ngày còn lại (có thể âm nếu đã quá hạn nhưng chưa được giải phóng)
        delta = (release_dt - now).total_seconds()
        days_left = max(0, int(delta // 86400))
        items.append({
            "order_id": o.id,
            "order_number": o.order_number,
            "reserve_amount": str(reserve_amt),
            "release_date": release_dt.isoformat(),
            "days_left": days_left,
            "overdue": delta < 0,  # Đã quá hạn nhưng chưa được admin giải phóng
        })

    return {
        "success": True,
        "data": {
            "items": items,
            "total_pending_reserve": str(total_pending),
        },
        "meta": {"total": len(items)},
    }


# ==============================================================================
# AUTO-CONFIRM ORDERS — Admin trigger tự động xác nhận đơn quá 7 ngày
# ==============================================================================

@router.post("/auto-confirm-orders", summary="Admin: Tự động xác nhận đơn SHIPPING quá 7 ngày")
async def auto_confirm_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tự động chuyển đơn SHIPPING sang DELIVERED + credit ví seller
    nếu buyer không bấm xác nhận sau 7 ngày kể từ ngày giao (shipped_at).

    Gọi thủ công bởi admin, hoặc schedule bằng cron job hàng ngày.
    """
    _require_admin(current_user)
    from app.services.wallet import credit_seller_wallet

    AUTO_CONFIRM_DAYS = 7
    cutoff = datetime.utcnow() - timedelta(days=AUTO_CONFIRM_DAYS)

    overdue_orders = db.query(Order).filter(
        Order.status == OrderStatus.SHIPPING,
        Order.shipped_at <= cutoff,
        Order.is_active == True,
        Order.wallet_credited == False,
    ).all()

    confirmed_ids = []
    for order in overdue_orders:
        order.status = OrderStatus.DELIVERED
        order.delivered_at = datetime.utcnow()
        order.payment_status = "PAID"
        credit_seller_wallet(db=db, order=order)
        confirmed_ids.append(order.id)

    db.commit()

    return {
        "success": True,
        "message": f"Đã tự động xác nhận {len(confirmed_ids)} đơn hàng (shipping > {AUTO_CONFIRM_DAYS} ngày).",
        "confirmed_count": len(confirmed_ids),
        "confirmed_order_ids": confirmed_ids,
    }


# ==============================================================================
# ADMIN FINANCIAL OVERVIEW — Tổng quan tài chính toàn sàn
# ==============================================================================

@router.get("/admin/financial-overview", summary="Admin: Tổng quan tài chính toàn sàn")
async def admin_financial_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tổng quan tài chính toàn sàn cho Admin:
    - Tổng tiền khách trả
    - Tổng phí sàn thu được
    - Tổng seller nhận (sau phí)
    - Tổng đang giữ (pending, chưa giải phóng)
    - Tổng đã khả dụng cho sellers
    - Tổng đã rút ra
    """
    _require_admin(current_user)

    from sqlalchemy import func as sf
    from app.models.order import Order, OrderStatus

    # Tổng từ các đơn DELIVERED đã credited (toàn sàn)
    order_stats = db.query(
        sf.count(Order.id).label("total_orders"),
        sf.coalesce(sf.sum(Order.total_amount), 0).label("total_customer_paid"),
        sf.coalesce(sf.sum(Order.platform_fee_amount), 0).label("total_platform_fee"),
        sf.coalesce(sf.sum(Order.seller_amount), 0).label("total_seller_amount"),
    ).filter(
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,
        Order.is_active == True,
    ).first()

    # Tổng ví tất cả sellers
    wallet_stats = db.query(
        sf.coalesce(sf.sum(SellerWallet.pending_balance), 0).label("total_pending"),
        sf.coalesce(sf.sum(SellerWallet.available_balance), 0).label("total_available"),
        sf.coalesce(sf.sum(SellerWallet.reserve_balance), 0).label("total_reserve"),
        sf.coalesce(sf.sum(SellerWallet.total_withdrawn), 0).label("total_withdrawn"),
    ).first()

    # Số seller có tiền đang giữ
    active_sellers_count = db.query(sf.count(sf.distinct(SellerWallet.seller_id))).filter(
        SellerWallet.pending_balance > 0
    ).scalar() or 0

    # Tổng đơn hàng đang chờ xử lý
    pending_orders_count = db.query(sf.count(Order.id)).filter(
        Order.status == OrderStatus.SHIPPING,
        Order.wallet_credited == False,
        Order.is_active == True,
    ).scalar() or 0

    return {
        "success": True,
        "data": {
            # Từ đơn hàng
            "total_delivered_orders":   order_stats.total_orders          if order_stats else 0,
            "total_customer_paid":      str(order_stats.total_customer_paid  if order_stats else 0),
            "total_platform_fee":       str(order_stats.total_platform_fee   if order_stats else 0),
            "total_seller_amount":      str(order_stats.total_seller_amount  if order_stats else 0),
            # Từ ví sellers
            "total_pending_all_sellers":    str(wallet_stats.total_pending   if wallet_stats else 0),
            "total_available_all_sellers":  str(wallet_stats.total_available if wallet_stats else 0),
            "total_reserve_legacy":         str(wallet_stats.total_reserve   if wallet_stats else 0),
            "total_withdrawn_all_sellers":  str(wallet_stats.total_withdrawn if wallet_stats else 0),
            # Metadata
            "sellers_with_pending_funds":   active_sellers_count,
            "orders_pending_confirmation":  pending_orders_count,
        }
    }
