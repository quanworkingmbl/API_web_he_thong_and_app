"""
Notification Service – Helper functions để tạo thông báo

action_url mapping (khớp với routes CMS thực tế – createHashRouter):
  /seller/orders?highlight={id}          – Seller: trang orders
  /orders?highlight={id}                 – Buyer: trang orders
  /products?highlight={id}              – Admin: trang duyệt sản phẩm
  /seller/products?highlight={id}       – Seller: trang sản phẩm của mình
  /content?highlight={id}               – Admin: trang duyệt bài viết
  /seller/posts?highlight={id}          – Seller: trang bài viết của mình
  /management/seller-kyc?highlight={id} – Admin: trang duyệt KYC seller
  /seller                               – Seller: dashboard (sau khi KYC OK)
  /seller/kyc                           – Seller: trang KYC (sau khi bị từ chối)
  /complaint?highlight={id}             – Admin: trang khiếu nại
  /returns?highlight={id}               – Admin: trang đổi/trả
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.notification import Notification
import logging

logger = logging.getLogger(__name__)


# ==============================================================================
# CORE HELPER
# ==============================================================================

def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    category: str = "SYSTEM",
    ref_type: Optional[str] = None,
    ref_id: Optional[int] = None,
    action_url: Optional[str] = None,
    push: bool = True,
) -> Notification:
    """
    Tạo một thông báo mới và thêm vào session (chưa commit).
    Nếu user có fcm_token và push=True → tự động gửi FCM push notification.
    """
    notif = Notification(
        user_id=user_id,
        category=category,
        title=title,
        message=message,
        ref_type=ref_type,
        ref_id=ref_id,
        action_url=action_url,
        is_read=False,
    )
    db.add(notif)

    # ── FCM Push ─────────────────────────────────────────────────────
    if push:
        try:
            from app.models.user import User
            from app.services.fcm_push import send_fcm_push

            user = db.query(User).filter(User.id == user_id).first()
            if user and user.fcm_token:
                push_data: dict = {"category": category}
                if action_url:
                    push_data["action_url"] = action_url
                if ref_type:
                    push_data["ref_type"] = ref_type
                if ref_id is not None:
                    push_data["ref_id"] = str(ref_id)

                success = send_fcm_push(
                    token=user.fcm_token,
                    title=title,
                    body=message,
                    data=push_data,
                )
                logger.debug(f"[FCM] user_id={user_id} push={'OK' if success else 'SKIP'}")
        except Exception as e:
            logger.warning(f"[FCM] Push error for user_id={user_id}: {e}")

    return notif


# ==============================================================================
# ORDER NOTIFICATIONS – Tiện ích theo từng sự kiện đơn hàng
# ==============================================================================

def notify_new_order_to_seller(
    db: Session,
    seller_id: int,
    order_id: int,
    order_number: str,
    customer_name: str,
    total_amount,
) -> Notification:
    """[O1] Seller nhận thông báo có đơn hàng mới."""
    return create_notification(
        db=db,
        user_id=seller_id,
        category="ORDER",
        title=f"🛒 Đơn hàng mới #{order_number}",
        message=f"Khách hàng {customer_name} vừa đặt đơn {order_number} — {int(total_amount):,}₫. Xác nhận ngay!",
        ref_type="order",
        ref_id=order_id,
        action_url=f"/seller/orders?highlight={order_id}",
    )


def notify_order_placed_to_buyer(
    db: Session,
    buyer_id: int,
    order_id: int,
    order_number: str,
    total_amount,
) -> Notification:
    """[O2] Buyer nhận thông báo đặt hàng thành công."""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="ORDER",
        title=f"✅ Đặt hàng thành công #{order_number}",
        message=f"Đơn hàng {order_number} ({int(total_amount):,}₫) đã được gửi đến người bán. Chờ xác nhận.",
        ref_type="order",
        ref_id=order_id,
        action_url=f"/orders?highlight={order_id}",
    )


def notify_order_confirmed_to_buyer(
    db: Session,
    buyer_id: int,
    order_id: int,
    order_number: str,
) -> Notification:
    """[O3] Buyer nhận thông báo seller đã xác nhận đơn."""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="ORDER",
        title=f"☑️ Đơn hàng đã xác nhận #{order_number}",
        message=f"Đơn hàng {order_number} đã được người bán xác nhận và đang chuẩn bị hàng.",
        ref_type="order",
        ref_id=order_id,
        action_url=f"/orders?highlight={order_id}",
    )


def notify_order_rejected_to_buyer(
    db: Session,
    buyer_id: int,
    order_id: int,
    order_number: str,
    reason: str,
) -> Notification:
    """[O4] Buyer nhận thông báo seller từ chối đơn."""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="ORDER",
        title=f"❌ Đơn hàng bị từ chối #{order_number}",
        message=f"Đơn hàng {order_number} đã bị người bán từ chối. Lý do: {reason}",
        ref_type="order",
        ref_id=order_id,
        action_url=f"/orders?highlight={order_id}",
    )


def notify_order_processing_to_buyer(
    db: Session,
    buyer_id: int,
    order_id: int,
    order_number: str,
) -> Notification:
    """[O5] Buyer nhận thông báo đơn đang được đóng gói."""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="ORDER",
        title=f"📦 Đang đóng gói đơn #{order_number}",
        message=f"Đơn hàng {order_number} đang được người bán đóng gói và chuẩn bị giao.",
        ref_type="order",
        ref_id=order_id,
        action_url=f"/orders?highlight={order_id}",
    )


def notify_order_shipping_to_buyer(
    db: Session,
    buyer_id: int,
    order_id: int,
    order_number: str,
) -> Notification:
    """[O6] Buyer nhận thông báo đơn đang giao."""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="ORDER",
        title=f"🚚 Đơn hàng đang giao #{order_number}",
        message=f"Đơn hàng {order_number} đã được giao cho đơn vị vận chuyển. Chuẩn bị nhận hàng!",
        ref_type="order",
        ref_id=order_id,
        action_url=f"/orders?highlight={order_id}",
    )


def notify_order_delivered_to_seller(
    db: Session,
    seller_id: int,
    order_id: int,
    order_number: str,
    seller_amount,
) -> Notification:
    """[O7] Seller nhận thông báo khách đã nhận hàng."""
    return create_notification(
        db=db,
        user_id=seller_id,
        category="ORDER",
        title=f"🎉 Đơn hàng hoàn thành #{order_number}",
        message=f"Khách hàng đã xác nhận nhận hàng đơn {order_number}. Doanh thu {int(seller_amount):,}₫ đã được ghi nhận.",
        ref_type="order",
        ref_id=order_id,
        action_url=f"/seller/orders?highlight={order_id}",
    )


def notify_order_cancelled_to_seller(
    db: Session,
    seller_id: int,
    order_id: int,
    order_number: str,
    reason: Optional[str] = None,
) -> Notification:
    """[O8] Seller nhận thông báo buyer hủy đơn."""
    msg = f"Đơn hàng {order_number} đã bị khách hàng hủy."
    if reason:
        msg += f" Lý do: {reason}"
    return create_notification(
        db=db,
        user_id=seller_id,
        category="ORDER",
        title=f"Đơn hàng bị hủy #{order_number}",
        message=msg,
        ref_type="order",
        ref_id=order_id,
        action_url=f"/seller/orders?highlight={order_id}",
    )


def notify_order_cancelled_by_admin(
    db: Session,
    target_user_id: int,
    order_id: int,
    order_number: str,
    reason: Optional[str] = None,
) -> Notification:
    """[O9] Admin hủy đơn – gửi cho Buyer hoặc Seller."""
    msg = f"Đơn hàng {order_number} đã bị hệ thống hủy."
    if reason:
        msg += f" Lý do: {reason}"
    return create_notification(
        db=db,
        user_id=target_user_id,
        category="ORDER",
        title=f"Đơn hàng bị hủy #{order_number}",
        message=msg,
        ref_type="order",
        ref_id=order_id,
        action_url=f"/orders?highlight={order_id}",
    )


# ==============================================================================
# PHASE 3 – PRODUCT APPROVAL NOTIFICATIONS
# ==============================================================================

def notify_product_pending_to_admin(
    db,
    admin_user_ids: list,
    product_id: int,
    product_name: str,
    seller_name: str,
) -> list:
    """[P1] Admin/Content Manager nhận thông báo có sản phẩm mới chờ duyệt."""
    notifs = []
    for uid in admin_user_ids:
        notifs.append(create_notification(
            db=db,
            user_id=uid,
            category="SYSTEM",
            title="📦 Sản phẩm mới chờ duyệt",
            message=f"Sản phẩm '{product_name}' của {seller_name} vừa được nộp và đang chờ xét duyệt.",
            ref_type="product",
            ref_id=product_id,
            action_url=f"/products?highlight={product_id}",
        ))
    return notifs


def notify_product_approved_to_seller(
    db,
    seller_id: int,
    product_id: int,
    product_name: str,
):
    """[P2] Seller nhận thông báo sản phẩm đã được duyệt."""
    return create_notification(
        db=db,
        user_id=seller_id,
        category="SYSTEM",
        title="🎉 Sản phẩm đã được duyệt!",
        message=f"Sản phẩm '{product_name}' đã được duyệt và hiện đang hiển thị trên sàn.",
        ref_type="product",
        ref_id=product_id,
        action_url=f"/seller/products?highlight={product_id}",
    )


def notify_product_rejected_to_seller(
    db,
    seller_id: int,
    product_id: int,
    product_name: str,
    notes=None,
):
    """[P3] Seller nhận thông báo sản phẩm bị từ chối."""
    detail = f" Lý do: {notes}" if notes else " Vui lòng chỉnh sửa và gửi lại."
    return create_notification(
        db=db,
        user_id=seller_id,
        category="SYSTEM",
        title="❌ Sản phẩm bị từ chối",
        message=f"Sản phẩm '{product_name}' chưa được duyệt.{detail}",
        ref_type="product",
        ref_id=product_id,
        action_url=f"/seller/products?highlight={product_id}",
    )


# ==============================================================================
# PHASE 3 – CONTENT/POST APPROVAL NOTIFICATIONS
# ==============================================================================

def notify_content_pending_to_admin(
    db,
    admin_user_ids: list,
    content_id: int,
    content_title: str,
    author_name: str,
) -> list:
    """[C1] Admin/Content Manager nhận thông báo có bài viết mới chờ duyệt."""
    notifs = []
    for uid in admin_user_ids:
        notifs.append(create_notification(
            db=db,
            user_id=uid,
            category="SYSTEM",
            title="📝 Bài viết mới chờ duyệt",
            message=f"Bài viết '{content_title}' của {author_name} đang chờ xét duyệt.",
            ref_type="content",
            ref_id=content_id,
            action_url=f"/content?highlight={content_id}",
        ))
    return notifs


def notify_content_approved_to_author(
    db,
    author_id: int,
    content_id: int,
    content_title: str,
):
    """[C2] Seller/Producer nhận thông báo bài viết đã được duyệt."""
    return create_notification(
        db=db,
        user_id=author_id,
        category="SYSTEM",
        title="🎉 Bài viết đã được duyệt!",
        message=f"Bài viết '{content_title}' đã được duyệt và đăng lên hệ thống.",
        ref_type="content",
        ref_id=content_id,
        action_url=f"/seller/posts?highlight={content_id}",
    )


def notify_content_rejected_to_author(
    db,
    author_id: int,
    content_id: int,
    content_title: str,
    notes=None,
):
    """[C3] Seller/Producer nhận thông báo bài viết bị từ chối."""
    detail = f" Lý do: {notes}" if notes else " Vui lòng chỉnh sửa và gửi lại."
    return create_notification(
        db=db,
        user_id=author_id,
        category="SYSTEM",
        title="❌ Bài viết bị từ chối",
        message=f"Bài viết '{content_title}' chưa được duyệt.{detail}",
        ref_type="content",
        ref_id=content_id,
        action_url=f"/seller/posts?highlight={content_id}",
    )


# ==============================================================================
# PHASE 3 – KYC / SELLER ONBOARDING NOTIFICATIONS
# ==============================================================================

def notify_kyc_pending_to_admin(
    db,
    admin_user_ids: list,
    seller_user_id: int,
    seller_name: str,
    business_name: str,
) -> list:
    """[K1] Admin nhận thông báo có hồ sơ seller mới chờ duyệt."""
    notifs = []
    for uid in admin_user_ids:
        notifs.append(create_notification(
            db=db,
            user_id=uid,
            category="SYSTEM",
            title="🏪 Hồ sơ seller mới chờ duyệt",
            message=f"Người dùng {seller_name} ({business_name}) vừa nộp hồ sơ đăng ký seller.",
            ref_type="seller_profile",
            ref_id=seller_user_id,
            action_url=f"/management/seller-kyc?highlight={seller_user_id}",
        ))
    return notifs


def notify_kyc_verified_to_seller(db, seller_id: int):
    """[K2] Seller nhận thông báo hồ sơ KYC được xác minh."""
    return create_notification(
        db=db,
        user_id=seller_id,
        category="SYSTEM",
        title="🎉 Hồ sơ đã được xác minh!",
        message="Hồ sơ kinh doanh của bạn đã được xác minh thành công. Bạn có thể bắt đầu đăng sản phẩm và bán hàng ngay!",
        ref_type="seller_profile",
        ref_id=seller_id,
        action_url="/seller",
    )


def notify_kyc_rejected_to_seller(db, seller_id: int, rejection_reason: str):
    """[K3] Seller nhận thông báo hồ sơ KYC bị từ chối."""
    return create_notification(
        db=db,
        user_id=seller_id,
        category="SYSTEM",
        title="❌ Hồ sơ bị từ chối",
        message=f"Hồ sơ kinh doanh của bạn chưa được duyệt. Lý do: {rejection_reason}. Vui lòng bổ sung thông tin và nộp lại.",
        ref_type="seller_profile",
        ref_id=seller_id,
        action_url="/seller/kyc",
    )


# ==============================================================================
# PHASE 4 – COMPLAINT NOTIFICATIONS
# ==============================================================================

def notify_new_complaint_to_admin(
    db,
    admin_user_ids: list,
    complaint_id: int,
    order_number,
    customer_name: str,
    title: str,
) -> list:
    """[CP1] Admin/CS nhận thông báo có khiếu nại mới."""
    order_info = f" về đơn #{order_number}" if order_number else ""
    notifs = []
    for uid in admin_user_ids:
        notifs.append(create_notification(
            db=db,
            user_id=uid,
            category="SYSTEM",
            title=f"⚠️ Khiếu nại mới #{complaint_id}",
            message=f"Khách hàng {customer_name}{order_info} vừa gửi khiếu nại: '{title}'.",
            ref_type="complaint",
            ref_id=complaint_id,
            action_url=f"/complaint?highlight={complaint_id}",
        ))
    return notifs


def notify_new_complaint_to_seller(
    db,
    seller_id: int,
    complaint_id: int,
    order_number,
    customer_name: str,
):
    """[CP1] Seller nhận thông báo có khiếu nại liên quan đơn hàng của mình."""
    order_info = f" đơn #{order_number}" if order_number else ""
    return create_notification(
        db=db,
        user_id=seller_id,
        category="SYSTEM",
        title=f"⚠️ Khiếu nại về{order_info}",
        message=f"Khách hàng {customer_name} đã gửi khiếu nại liên quan đến{order_info} của bạn. Vui lòng phối hợp xử lý.",
        ref_type="complaint",
        ref_id=complaint_id,
        # Seller không có trang complaint riêng → dẫn đến trang orders để xem context
        action_url=f"/seller/orders?highlight={order_number}" if order_number else "/seller/orders",
    )


def notify_complaint_assigned_to_cs(
    db,
    cs_user_id: int,
    complaint_id: int,
    order_number,
    assigned_by_name: str,
):
    """[CP2] CS được giao xử lý khiếu nại."""
    order_info = f" về đơn #{order_number}" if order_number else ""
    return create_notification(
        db=db,
        user_id=cs_user_id,
        category="SYSTEM",
        title=f"📋 Được giao xử lý khiếu nại #{complaint_id}",
        message=f"{assigned_by_name} đã giao bạn xử lý khiếu nại #{complaint_id}{order_info}.",
        ref_type="complaint",
        ref_id=complaint_id,
        action_url=f"/complaint?highlight={complaint_id}",
    )


def notify_complaint_comment_to_buyer(
    db,
    buyer_id: int,
    complaint_id: int,
    commenter_name: str,
):
    """[CP3] Buyer nhận thông báo khi Admin/CS phản hồi khiếu nại."""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="SYSTEM",
        title=f"💬 Khiếu nại #{complaint_id} có phản hồi mới",
        message=f"{commenter_name} vừa phản hồi khiếu nại của bạn. Xem chi tiết để tiếp tục trao đổi.",
        ref_type="complaint",
        ref_id=complaint_id,
        # Buyer không có trang complaint riêng → dẫn đến orders
        action_url=f"/orders?highlight={complaint_id}",
    )


def notify_complaint_comment_to_admin(
    db,
    admin_user_ids: list,
    complaint_id: int,
    commenter_name: str,
    role: str,
) -> list:
    """[CP4] Admin/CS nhận thông báo khi Buyer hoặc Seller phản hồi."""
    notifs = []
    role_label = "Khách hàng" if role == "buyer" else "Người bán"
    for uid in admin_user_ids:
        notifs.append(create_notification(
            db=db,
            user_id=uid,
            category="SYSTEM",
            title=f"💬 Phản hồi mới trên khiếu nại #{complaint_id}",
            message=f"{role_label} {commenter_name} vừa phản hồi trên khiếu nại #{complaint_id}.",
            ref_type="complaint",
            ref_id=complaint_id,
            action_url=f"/complaint?highlight={complaint_id}",
        ))
    return notifs


def notify_complaint_resolved_to_buyer(
    db,
    buyer_id: int,
    complaint_id: int,
    resolution=None,
):
    """[CP5] Buyer nhận thông báo khiếu nại đã được giải quyết."""
    detail = f" Giải pháp: {resolution}" if resolution else ""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="SYSTEM",
        title=f"✅ Khiếu nại #{complaint_id} đã được giải quyết",
        message=f"Khiếu nại của bạn đã được xử lý hoàn tất.{detail} Vui lòng xác nhận để đóng khiếu nại.",
        ref_type="complaint",
        ref_id=complaint_id,
        action_url=f"/orders?highlight={complaint_id}",
    )


# ==============================================================================
# PHASE 4 – RETURN REQUEST NOTIFICATIONS
# ==============================================================================

def notify_return_request_to_admin(
    db,
    admin_user_ids: list,
    return_id: int,
    order_number: str,
    customer_name: str,
    return_type: str,
    reason: str,
) -> list:
    """[R1] Admin nhận thông báo có yêu cầu đổi/trả mới."""
    type_label = "đổi hàng" if str(return_type).upper() == "EXCHANGE" else "trả hàng"
    short_reason = reason[:100] + ("..." if len(reason) > 100 else "")
    notifs = []
    for uid in admin_user_ids:
        notifs.append(create_notification(
            db=db,
            user_id=uid,
            category="SYSTEM",
            title=f"↩️ Yêu cầu {type_label} mới #{return_id}",
            message=f"Khách hàng {customer_name} yêu cầu {type_label} đơn #{order_number}: {short_reason}",
            ref_type="return",
            ref_id=return_id,
            action_url=f"/returns?highlight={return_id}",
        ))
    return notifs


def notify_return_approved_to_buyer(
    db,
    buyer_id: int,
    return_id: int,
    return_type: str,
    note=None,
):
    """[R2] Buyer nhận thông báo yêu cầu đổi/trả được duyệt."""
    type_label = "đổi hàng" if str(return_type).upper() == "EXCHANGE" else "trả hàng"
    detail = f" Ghi chú: {note}" if note else ""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="SYSTEM",
        title=f"✅ Yêu cầu {type_label} được duyệt #{return_id}",
        message=f"Yêu cầu {type_label} của bạn đã được chấp nhận.{detail} Vui lòng gửi hàng về địa chỉ được cung cấp.",
        ref_type="return",
        ref_id=return_id,
        action_url=f"/orders?highlight={return_id}",
    )


def notify_return_rejected_to_buyer(
    db,
    buyer_id: int,
    return_id: int,
    return_type: str,
    note=None,
):
    """[R3] Buyer nhận thông báo yêu cầu đổi/trả bị từ chối."""
    type_label = "đổi hàng" if str(return_type).upper() == "EXCHANGE" else "trả hàng"
    detail = f" Lý do: {note}" if note else ""
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="SYSTEM",
        title=f"❌ Yêu cầu {type_label} bị từ chối #{return_id}",
        message=f"Yêu cầu {type_label} của bạn chưa được chấp nhận.{detail}",
        ref_type="return",
        ref_id=return_id,
        action_url=f"/orders?highlight={return_id}",
    )


def notify_return_received_to_buyer(
    db,
    buyer_id: int,
    return_id: int,
    return_type: str,
):
    """[R4] Buyer nhận thông báo hệ thống đã nhận hàng trả về."""
    type_label = "đổi hàng" if str(return_type).upper() == "EXCHANGE" else "hoàn tiền"
    return create_notification(
        db=db,
        user_id=buyer_id,
        category="SYSTEM",
        title=f"📦 Đã nhận hàng trả về #{return_id}",
        message=f"Chúng tôi đã nhận được hàng trả về của bạn. Đang tiến hành xử lý {type_label}.",
        ref_type="return",
        ref_id=return_id,
        action_url=f"/orders?highlight={return_id}",
    )
