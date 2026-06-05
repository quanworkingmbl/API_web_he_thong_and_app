"""
app/services/wallet.py
======================
Xử lý logic ví seller (SellerWallet).

Nguyên tắc (100% Hold 7 ngày — áp dụng từ phiên bản hiện tại):
─────────────────────────────────────────────────────────────────
  Khi buyer xác nhận nhận hàng (hoặc auto-confirm sau 7 ngày shipping):
    100% seller_amount → pending_balance  (giữ 7 ngày chờ khiếu nại)

  Sau 7 ngày không có khiếu nại:
    pending_balance → available_balance   (có thể rút toàn bộ)

  Seller rút tiền:
    available_balance → total_withdrawn

Luồng tiền mẫu (đơn 80.000đ, phí sàn 10%):
  Khách trả: 80.000đ
  Phí sàn (10%): 8.000đ  → Admin
  Seller nhận:   72.000đ → pending_balance (7 ngày)
  Sau 7 ngày:    72.000đ → available_balance (rút được)

Ghi chú backward compat:
  - Đơn cũ (đã credit theo 80/20) KHÔNG bị ảnh hưởng.
    reserve_balance cũ vẫn giữ đúng, được giải phóng bình thường.
  - Đơn mới (wallet_credited = True sau khi cập nhật code):
    100% vào pending_balance.
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.settlement import SellerWallet

logger = logging.getLogger(__name__)

# ── Hằng số ───────────────────────────────────────────────────────────────────
HOLD_DAYS = 7   # Giữ 100% seller_amount 7 ngày trước khi chuyển sang available


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_create_wallet(seller_id: int, db: Session) -> SellerWallet:
    """Lấy ví của seller, tạo mới nếu chưa tồn tại."""
    wallet = db.query(SellerWallet).filter(
        SellerWallet.seller_id == seller_id
    ).first()

    if not wallet:
        wallet = SellerWallet(
            seller_id=seller_id,
            pending_balance=Decimal("0"),
            available_balance=Decimal("0"),
            reserve_balance=Decimal("0"),
            total_withdrawn=Decimal("0"),
        )
        db.add(wallet)
        db.flush()

    return wallet


def calc_max_withdrawable(seller_id: int, db: Session) -> Decimal:
    """
    Số tiền tối đa seller có thể rút = available_balance.
    (Bỏ min_reserve — tiền đã giữ 7 ngày nên không cần giữ thêm.)
    """
    wallet = _get_or_create_wallet(seller_id, db)
    return max(Decimal("0"), Decimal(str(wallet.available_balance or 0)))


# ── Core functions ─────────────────────────────────────────────────────────────

def credit_seller_wallet(db: Session, order: Order) -> bool:
    """
    Ghi 100% seller_amount vào pending_balance (giữ 7 ngày).

    Chỉ được gọi khi:
      - Buyer xác nhận nhận hàng (confirm_order_received)
      - Auto-confirm sau 7 ngày shipping

    Returns:
        True  – cộng thành công
        False – đã cộng rồi (wallet_credited = True), bỏ qua
    """
    if order.wallet_credited:
        logger.warning("[Wallet] Order #%s đã credited trước đó, bỏ qua.", order.id)
        return False

    seller_amount = Decimal(str(order.seller_amount or 0))
    if seller_amount <= 0:
        logger.warning("[Wallet] Order #%s seller_amount=%s, không cộng.", order.id, seller_amount)
        return False

    # ── Khóa row Order (FOR UPDATE) để chống concurrent double-credit ───────
    locked_order = (
        db.query(Order)
        .filter(Order.id == order.id)
        .with_for_update()
        .first()
    )
    if not locked_order or locked_order.wallet_credited:
        logger.warning("[Wallet] Order #%s đã credited (after lock), bỏ qua.", order.id)
        return False

    # Cập nhật flag ngay để các transaction khác thấy sau khi commit
    locked_order.wallet_credited = True

    # ── 100% vào pending_balance (giữ 7 ngày) ─────────────────────────────
    wallet = (
        db.query(SellerWallet)
        .filter(SellerWallet.seller_id == locked_order.seller_id)
        .with_for_update()
        .first()
    )
    if not wallet:
        wallet = SellerWallet(
            seller_id=locked_order.seller_id,
            pending_balance=Decimal("0"),
            available_balance=Decimal("0"),
            reserve_balance=Decimal("0"),
            total_withdrawn=Decimal("0"),
        )
        db.add(wallet)
        db.flush()

    wallet.pending_balance = Decimal(str(wallet.pending_balance or 0)) + seller_amount

    # Lưu thời điểm giải phóng (now + 7 ngày)
    if hasattr(locked_order, "reserve_release_at"):
        locked_order.reserve_release_at = datetime.utcnow() + timedelta(days=HOLD_DAYS)

    # Đồng bộ lại object order được truyền vào
    order.wallet_credited = True

    logger.info(
        "[Wallet] Order #%s → pending +%s (seller #%s) — giải phóng sau %d ngày",
        order.id, seller_amount, order.seller_id, HOLD_DAYS,
    )
    return True


def release_matured_holds(seller_id: int, db: Session) -> Decimal:
    """
    Giải phóng tiền đã qua 7 ngày từ pending_balance → available_balance.
    Gọi thủ công bởi admin hoặc trigger định kỳ.

    Xử lý cả đơn cũ (20% reserve) lẫn đơn mới (100% pending).

    Returns: tổng số tiền đã giải phóng
    """
    from app.models.order import Order, OrderStatus

    now = datetime.utcnow()
    matured_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.status == OrderStatus.DELIVERED,
        Order.wallet_credited == True,
        Order.reserve_release_at != None,
        Order.reserve_release_at <= now,
        Order.reserve_released == False,
    ).all()

    total_released = Decimal("0")
    if not matured_orders:
        return total_released

    wallet = _get_or_create_wallet(seller_id, db)

    for o in matured_orders:
        seller_amt = Decimal(str(o.seller_amount or 0))
        # Đơn cũ (80/20): giải phóng phần reserve (20%)
        old_reserve_ratio = Decimal("0.20")
        old_reserve = (seller_amt * old_reserve_ratio).quantize(Decimal("0.01"))

        # Kiểm tra đây là đơn mới (100% pending) hay đơn cũ (20% reserve)
        # Đơn mới: toàn bộ seller_amount nằm trong pending_balance
        # Heuristic: nếu pending_balance đủ chứa seller_amount → đơn mới
        current_pending = Decimal(str(wallet.pending_balance or 0))
        if current_pending >= seller_amt:
            # Đơn mới: giải phóng 100%
            release_amt = seller_amt
            wallet.pending_balance = max(Decimal("0"), current_pending - release_amt)
        else:
            # Đơn cũ: giải phóng 20% reserve (từ reserve_balance)
            release_amt = old_reserve
            wallet.reserve_balance = max(
                Decimal("0"),
                Decimal(str(wallet.reserve_balance or 0)) - release_amt
            )

        wallet.available_balance = Decimal(str(wallet.available_balance or 0)) + release_amt
        o.reserve_released = True
        total_released += release_amt

    logger.info(
        "[Wallet] Giải phóng %s cho seller #%s (%d đơn)",
        total_released, seller_id, len(matured_orders)
    )
    return total_released


# Alias backward compat (một số nơi gọi release_matured_reserves)
release_matured_reserves = release_matured_holds
