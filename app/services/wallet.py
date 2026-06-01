"""
app/services/wallet.py
======================
Xử lý logic ví seller (SellerWallet).

Nguyên tắc (80/20 Reserve):
- Khi buyer xác nhận nhận hàng → credit_seller_wallet() tách:
    80% → available_balance  (rút được ngay, trừ min_reserve)
    20% → reserve_balance    (giữ 14 ngày, tự giải phóng về available)
- Dùng wallet_credited để chống double-credit
- min_reserve = số sản phẩm đang bán × MIN_RESERVE_PER_PRODUCT
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.settlement import SellerWallet

logger = logging.getLogger(__name__)

# ── Hằng số ───────────────────────────────────────────────────────────────────
AVAILABLE_RATIO   = Decimal("0.80")   # 80% vào available ngay
RESERVE_RATIO     = Decimal("0.20")   # 20% giữ 14 ngày
RESERVE_HOLD_DAYS = 14                # Số ngày giữ reserve trước khi giải phóng
MIN_RESERVE_PER_PRODUCT = Decimal("50000")  # 50,000 VND / sản phẩm đang bán
MAX_RESERVE_RATIO = Decimal("0.20")   # Tối đa 20% available_balance — tránh khóa seller hoàn toàn


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


def calc_min_reserve(seller_id: int, db: Session, available_balance: Decimal = None) -> Decimal:
    """
    Tính min_reserve dựa trên số sản phẩm đang APPROVED của seller.
    Seller chỉ rút được: available_balance - min_reserve
    Có giới hạn: không vượt quá 20% available_balance (tránh khóa seller hoàn toàn).
    """
    from app.models.product import Product, ProductStatus
    active_count = db.query(Product).filter(
        Product.seller_id == seller_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    ).count()
    product_based = MIN_RESERVE_PER_PRODUCT * active_count

    # Cap: nếu biết available_balance, giới hạn tối đa 20%
    if available_balance is not None and available_balance > 0 and active_count > 0:
        cap = (available_balance * MAX_RESERVE_RATIO).quantize(Decimal("0.01"))
        return min(product_based, cap)
    return product_based


def calc_max_withdrawable(seller_id: int, db: Session) -> Decimal:
    """Số tiền tối đa seller có thể rút = available_balance - min_reserve (có cap 20%)."""
    wallet = _get_or_create_wallet(seller_id, db)
    available = Decimal(str(wallet.available_balance or 0))
    min_r = calc_min_reserve(seller_id, db, available_balance=available)
    return max(Decimal("0"), available - min_r)


# ── Core functions ─────────────────────────────────────────────────────────────

def credit_seller_wallet(db: Session, order: Order) -> bool:
    """
    Tách seller_amount theo tỷ lệ 80/20 vào ví:
        80% → available_balance  (rút được ngay, trừ min_reserve)
        20% → reserve_balance    (giữ 30 ngày)

    Chỉ được gọi khi USER xác nhận nhận hàng (confirm_order_received).
    KHÔNG gọi khi seller/admin set DELIVERED thủ công.

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
    # Tình huống race: 2 request confirm-received cùng lúc, cả 2 đọc
    # wallet_credited=False trước khi cái nào ghi xong → double-credit.
    # SELECT FOR UPDATE đảm bảo chỉ 1 transaction xử lý tại một thời điểm.
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

    available_credit = (seller_amount * AVAILABLE_RATIO).quantize(Decimal("0.01"))
    reserve_credit   = (seller_amount * RESERVE_RATIO).quantize(Decimal("0.01"))
    # Tránh lệch do làm tròn
    available_credit = seller_amount - reserve_credit

    # Khóa ví seller (FOR UPDATE) để ghi số dư an toàn
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

    wallet.available_balance = Decimal(str(wallet.available_balance or 0)) + available_credit
    wallet.reserve_balance   = Decimal(str(wallet.reserve_balance   or 0)) + reserve_credit

    # Lưu thời điểm giải phóng reserve
    if hasattr(locked_order, "reserve_release_at"):
        locked_order.reserve_release_at = datetime.utcnow() + timedelta(days=RESERVE_HOLD_DAYS)

    # Đồng bộ lại object order được truyền vào (tránh stale data)
    order.wallet_credited = True

    logger.info(
        "[Wallet] Order #%s → available +%s | reserve +%s (seller #%s)",
        order.id, available_credit, reserve_credit, order.seller_id,
    )
    return True


def release_matured_reserves(seller_id: int, db: Session) -> Decimal:
    """
    Giải phóng reserve đã quá 30 ngày về available_balance.
    Gọi thủ công bởi admin hoặc trigger định kỳ.

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
        reserve_amt = (Decimal(str(o.seller_amount or 0)) * RESERVE_RATIO).quantize(Decimal("0.01"))
        release_amt = Decimal(str(o.seller_amount or 0)) - reserve_amt  # = available_credit đã ghi
        # Lấy đúng phần reserve của đơn này
        order_reserve = reserve_amt

        wallet.reserve_balance   = max(Decimal("0"), Decimal(str(wallet.reserve_balance or 0)) - order_reserve)
        wallet.available_balance = Decimal(str(wallet.available_balance or 0)) + order_reserve
        o.reserve_released = True
        total_released += order_reserve

    logger.info("[Wallet] Giải phóng reserve %s cho seller #%s (%d đơn)", total_released, seller_id, len(matured_orders))
    return total_released
