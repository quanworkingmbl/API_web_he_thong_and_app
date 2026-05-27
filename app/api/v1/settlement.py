"""
Settlement API – Đối soát & Chi trả cho Seller

Endpoints:
- GET  /settlement/wallet           – Seller xem ví
- GET  /settlement/history          – Lịch sử đối soát
- POST /settlement/create           – Admin tạo kỳ đối soát
- POST /settlement/{id}/approve     – Admin duyệt
- POST /settlement/{id}/payout      – Admin chi trả
- GET  /settlement/payouts          – Lịch sử payout
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.database import get_db
from app.models.settlement import SellerWallet, Settlement, SettlementStatus, Payout, PayoutStatus
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.seller_profile import SellerProfile
from app.api.v1.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# HELPERS
# ==============================================================================

def _require_admin(user: User):
    if user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền thực hiện")


def _require_seller(user: User):
    if user.type not in {"producer", "seller", "admin"}:
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
    """Lấy thông tin ví: pending, available, đã rút + thống kê doanh thu."""
    _require_seller(current_user)
    wallet = _get_or_create_wallet(current_user.id, db)

    from sqlalchemy import func as sf
    from app.models.order import Order, OrderStatus

    # Tổng tất cả đơn DELIVERED đã credited cho seller
    total_stats = db.query(
        sf.count(Order.id).label("total_orders"),
        sf.coalesce(sf.sum(Order.seller_amount), 0).label("total_earned"),
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
    ).filter(
        Order.seller_id == current_user.id,
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,
        Order.is_active == True,
        Order.delivered_at >= month_start,
    ).first()

    return {
        "success": True,
        "data": {
            "seller_id": current_user.id,
            "pending_balance": str(wallet.pending_balance or 0),
            "available_balance": str(wallet.available_balance or 0),
            "total_withdrawn": str(wallet.total_withdrawn or 0),
            "total_earned": str(total_stats.total_earned if total_stats else 0),
            "total_delivered_orders": total_stats.total_orders if total_stats else 0,
            "this_month_earned": str(month_stats.month_earned if month_stats else 0),
            "updated_at": wallet.updated_at.isoformat() if wallet.updated_at else None,
        }
    }



@router.get("/history", summary="Lịch sử kỳ đối soát")
async def get_settlement_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    seller_id: Optional[int] = Query(None, description="Filter theo seller (admin)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách kỳ đối soát. Seller chỉ xem của mình, admin xem tất cả."""
    _require_seller(current_user)

    query = db.query(Settlement)
    if current_user.type == "admin" and seller_id:
        query = query.filter(Settlement.seller_id == seller_id)
    elif current_user.type != "admin":
        query = query.filter(Settlement.seller_id == current_user.id)

    total = query.count()
    skip = (page - 1) * limit
    items = query.order_by(Settlement.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "seller_id": s.seller_id,
                "period_start": s.period_start.isoformat(),
                "period_end": s.period_end.isoformat(),
                "total_orders": s.total_orders,
                "total_amount": str(s.total_amount),
                "total_platform_fee": str(s.total_platform_fee),
                "total_seller_amount": str(s.total_seller_amount),
                "status": s.status.value,
                "note": s.note,
                "created_at": s.created_at.isoformat() if s.created_at else None
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

    # Lấy các đơn hàng DELIVERED trong kỳ
    delivered_orders = db.query(Order).filter(
        Order.seller_id == data.seller_id,
        Order.status == OrderStatus.DELIVERED,
        Order.delivered_at >= data.period_start,
        Order.delivered_at <= data.period_end
    ).all()

    total_orders = len(delivered_orders)
    total_amount = sum(o.subtotal for o in delivered_orders)
    total_platform_fee = sum(o.platform_fee_amount for o in delivered_orders)
    total_seller_amount = sum(o.seller_amount for o in delivered_orders)

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

    # Cập nhật pending_balance trong ví seller
    wallet = _get_or_create_wallet(data.seller_id, db)
    wallet.pending_balance += total_seller_amount

    db.commit()
    db.refresh(settlement)

    return {
        "success": True,
        "message": f"Đã tạo kỳ đối soát với {total_orders} đơn hàng",
        "data": {
            "settlement_id": settlement.id,
            "total_orders": total_orders,
            "total_amount": str(total_amount),
            "total_platform_fee": str(total_platform_fee),
            "total_seller_amount": str(total_seller_amount)
        }
    }


@router.post("/{settlement_id}/approve", summary="Admin duyệt kỳ đối soát")
async def approve_settlement(
    settlement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duyệt kỳ đối soát → chuyển tiền từ pending sang available trong ví seller.
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

    # Chuyển tiền từ pending → available
    wallet = _get_or_create_wallet(settlement.seller_id, db)
    wallet.pending_balance -= settlement.total_seller_amount
    wallet.available_balance += settlement.total_seller_amount

    db.commit()

    return {
        "success": True,
        "message": "Đã duyệt kỳ đối soát",
        "settlement_id": settlement_id,
        "status": "APPROVED"
    }


@router.post("/{settlement_id}/payout", summary="Admin chi trả cho seller")
async def create_payout(
    settlement_id: int,
    payout_data: PayoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo payout từ kỳ đối soát đã duyệt.
    Trừ available_balance, cộng total_withdrawn.
    """
    _require_admin(current_user)

    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Kỳ đối soát không tồn tại")

    if settlement.status != SettlementStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể chi trả kỳ đối soát đã được duyệt"
        )

    wallet = _get_or_create_wallet(settlement.seller_id, db)
    if wallet.available_balance < settlement.total_seller_amount:
        raise HTTPException(status_code=400, detail="Số dư khả dụng không đủ")

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

    # Cập nhật ví
    wallet.available_balance -= settlement.total_seller_amount
    wallet.total_withdrawn += settlement.total_seller_amount

    # Cập nhật settlement
    settlement.status = SettlementStatus.COMPLETED

    db.commit()
    db.refresh(payout)

    return {
        "success": True,
        "message": "Đã chi trả thành công",
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
