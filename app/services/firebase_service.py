"""
Firebase Admin SDK — Singleton service
Dùng cho: Firestore (chat) + FCM (push notification)
"""
import os
import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, messaging
from google.cloud.firestore_v1 import AsyncClient

logger = logging.getLogger(__name__)

# ── Khởi tạo Firebase App (Singleton) ────────────────────────────────────────

def _get_firebase_app() -> firebase_admin.App:
    """Trả về Firebase app đã khởi tạo (singleton)."""
    if firebase_admin._apps:
        return firebase_admin.get_app()

    # Ưu tiên: biến môi trường FIREBASE_SERVICE_ACCOUNT_JSON (production)
    env_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if env_json:
        try:
            cred_dict = json.loads(env_json)
            cred = credentials.Certificate(cred_dict)
            logger.info("[Firebase] Initialized from env var")
            return firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.warning(f"[Firebase] Env var parse failed: {e}")

    # Fallback: file JSON (development)
    base_dir = Path(__file__).parent.parent.parent  # Du_an_cms_API/
    key_paths = [
        base_dir / "firebase-service-account.json",
        base_dir / "app" / "firebase-service-account.json",
    ]
    for key_path in key_paths:
        if key_path.exists():
            cred = credentials.Certificate(str(key_path))
            logger.info(f"[Firebase] Initialized from file: {key_path}")
            return firebase_admin.initialize_app(cred)

    raise RuntimeError(
        "Firebase service account not found. "
        "Set FIREBASE_SERVICE_ACCOUNT_JSON env var or place firebase-service-account.json in project root."
    )


@lru_cache(maxsize=1)
def get_firebase_app() -> firebase_admin.App:
    return _get_firebase_app()


# ── Firestore Client ──────────────────────────────────────────────────────────

def get_firestore() -> firestore.client:
    """Trả về Firestore sync client."""
    get_firebase_app()
    return firestore.client()


# ── FCM Push Notification ─────────────────────────────────────────────────────

def send_fcm_notification(
    token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    image: Optional[str] = None,
) -> bool:
    """
    Gửi FCM push notification đến một thiết bị.
    
    Args:
        token: FCM registration token của thiết bị
        title: Tiêu đề notification
        body: Nội dung notification
        data: Dict dữ liệu bổ sung (dùng để navigate trong app)
        image: URL ảnh hiển thị trong notification
    
    Returns:
        True nếu gửi thành công
    """
    try:
        get_firebase_app()
        msg = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image,
            ),
            data={str(k): str(v) for k, v in (data or {}).items()},
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="chat",
                    click_action="FLUTTER_NOTIFICATION_CLICK",
                ),
            ),
        )
        response = messaging.send(msg)
        logger.debug(f"[FCM] Sent: {response}")
        return True
    except Exception as e:
        logger.error(f"[FCM] Send failed (token={token[:20]}...): {e}")
        return False


def send_fcm_multicast(
    tokens: list[str],
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> int:
    """
    Gửi FCM đến nhiều thiết bị cùng lúc.
    Trả về số lượng gửi thành công.
    """
    if not tokens:
        return 0
    try:
        get_firebase_app()
        msg = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title, body=body),
            data={str(k): str(v) for k, v in (data or {}).items()},
            android=messaging.AndroidConfig(priority="high"),
        )
        response = messaging.send_each_for_multicast(msg)
        logger.debug(f"[FCM] Multicast: {response.success_count}/{len(tokens)} success")
        return response.success_count
    except Exception as e:
        logger.error(f"[FCM] Multicast failed: {e}")
        return 0


# ── Firestore Chat Helpers ────────────────────────────────────────────────────

def get_or_create_chat_room(
    buyer_id: int,
    seller_id: int,
    shop_name: str,
    buyer_name: str,
) -> tuple[str, bool]:
    """
    Lấy hoặc tạo phòng chat giữa buyer và seller.
    
    Returns:
        (chat_id, created) — True nếu vừa tạo mới
    """
    db = get_firestore()
    chat_id = f"user{buyer_id}_seller{seller_id}"
    ref = db.collection("chats").document(chat_id)
    doc = ref.get()

    if doc.exists:
        return chat_id, False

    # Tạo mới
    import datetime
    ref.set({
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "buyer_name": buyer_name,
        "shop_name": shop_name,
        "last_message": "",
        "last_at": datetime.datetime.utcnow(),
        "unread_buyer": 0,
        "unread_seller": 0,
        "created_at": datetime.datetime.utcnow(),
    })
    return chat_id, True


def add_message_to_firestore(
    chat_id: str,
    sender_id: int,
    sender_type: str,  # "buyer" | "seller"
    content: str,
    msg_type: str = "text",  # "text" | "image"
) -> str:
    """
    Ghi tin nhắn vào Firestore.
    Trả về message document ID.
    """
    import datetime
    db = get_firestore()
    chat_ref = db.collection("chats").document(chat_id)
    messages_ref = chat_ref.collection("messages")

    now = datetime.datetime.utcnow()

    # Thêm tin nhắn
    _, msg_ref = messages_ref.add({
        "sender_id": sender_id,
        "sender_type": sender_type,
        "content": content,
        "type": msg_type,
        "created_at": now,
        "read": False,
    })

    # Cập nhật last_message trên room
    unread_field = "unread_buyer" if sender_type == "seller" else "unread_seller"
    chat_ref.update({
        "last_message": content[:100],
        "last_at": now,
        unread_field: firestore.Increment(1),
    })

    return msg_ref.id


def mark_messages_as_read(chat_id: str, reader_type: str) -> None:
    """
    Reset unread count cho buyer hoặc seller.
    reader_type: "buyer" | "seller"
    """
    db = get_firestore()
    field = f"unread_{reader_type}"
    db.collection("chats").document(chat_id).update({field: 0})


def send_order_notification_to_chat(
    buyer_id: int,
    seller_id: int,
    buyer_name: str,
    shop_name: str,
    order_number: str,
    total_amount: str,
    items_summary: str,
) -> str:
    """
    Ghi thông báo đơn hàng mới vào phòng chat buyer↔seller.
    sender_type="system" — chỉ seller thấy, buyer UI sẽ ẩn.

    Returns: chat_id
    """
    import datetime

    # 1. Tạo/lấy phòng chat
    chat_id, _ = get_or_create_chat_room(
        buyer_id=buyer_id,
        seller_id=seller_id,
        shop_name=shop_name,
        buyer_name=buyer_name,
    )

    # 2. Nội dung thông báo
    content = (
        f"🛒 Đơn hàng mới: #{order_number}\n"
        f"👤 Khách: {buyer_name}\n"
        f"📦 {items_summary}\n"
        f"💰 Tổng tiền: {total_amount}"
    )

    # 3. Ghi vào Firestore (type="order_notification", sender_type="system")
    db = get_firestore()
    chat_ref = db.collection("chats").document(chat_id)
    messages_ref = chat_ref.collection("messages")

    now = datetime.datetime.utcnow()
    _, msg_ref = messages_ref.add({
        "sender_id": 0,               # 0 = system
        "sender_type": "system",      # marker để buyer UI ẩn đi
        "content": content,
        "type": "order_notification", # loại đặc biệt
        "order_number": order_number, # metadata thêm
        "created_at": now,
        "read": False,
    })

    # 4. Cập nhật last_message và tăng unread_seller
    chat_ref.update({
        "last_message": f"🛒 Đơn hàng mới #{order_number}",
        "last_at": now,
        "unread_seller": firestore.Increment(1),
        # KHÔNG tăng unread_buyer — buyer không cần xem cái này
    })

    logger.info(f"[Chat] Order notification sent: chat={chat_id}, order={order_number}")
    return chat_id
