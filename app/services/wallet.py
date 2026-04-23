"""
app/services/wallet.py
======================
Xử lý logic ví seller (SellerWallet).

Nguyên tắc:
- Chỉ cộng tiền khi USER xác nhận nhận hàng (confirm_order_received)
- KHÔNG cộng khi seller/admin set DELIVERED
- Dùng wallet_credited để chống double-credit
- Số tiền cộng = order.seller_amount (đã trừ phí nền tảng 5%)
"""

import logging
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.settlement import SellerWallet

logger = logging.getLogger(__name__)


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
            total_withdrawn=Decimal("0"),
        )
        db.add(wallet)
        db.flush()

    return wallet


def credit_seller_wallet(
    db: Session,
    order: Order,
) -> bool:
    """
    Cộng tiền seller_amount vào pending_balance của ví seller.

    Chỉ được gọi khi USER xác nhận nhận hàng (confirm_order_received).
    KHÔNG gọi khi seller/admin set DELIVERED.

    Returns:
        True  – cộng thành công
        False – đã cộng rồi (wallet_credited = True), bỏ qua
    """
    # Idempotent check – tránh double-credit
    if order.wallet_credited:
        logger.warning(
            "[Wallet] Order #%s đã được credited trước đó, bỏ qua.",
            order.id,
        )
        return False

    seller_amount = Decimal(str(order.seller_amount or 0))
    if seller_amount <= 0:
        logger.warning(
            "[Wallet] Order #%s có seller_amount = %s, không cộng ví.",
            order.id,
            seller_amount,
        )
        return False

    # Cộng vào pending_balance
    wallet = _get_or_create_wallet(order.seller_id, db)
    wallet.pending_balance = Decimal(str(wallet.pending_balance or 0)) + seller_amount

    # Đánh dấu đã credited
    order.wallet_credited = True

    logger.info(
        "[Wallet] Cộng %s vào ví seller #%s từ đơn hàng #%s (pending_balance mới: %s)",
        seller_amount,
        order.seller_id,
        order.id,
        wallet.pending_balance,
    )

    # KHÔNG commit ở đây – để caller quyết định khi nào commit
    return True
