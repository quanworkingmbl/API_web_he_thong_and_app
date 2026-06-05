"""
Chat API — v1
Endpoints cho real-time chat giữa User (buyer) và Seller
Data lưu trong Firestore, metadata trong PostgreSQL
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notifications import FcmToken
from app.services import firebase_service

logger = logging.getLogger(__name__)
router = APIRouter()

SELLER_TYPES = {"seller", "producer"}
ADMIN_TYPES  = {"admin", "superadmin"}


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class CreateRoomRequest(BaseModel):
    seller_id: int
    product_id: Optional[int] = None   # context sản phẩm đang hỏi (tuỳ chọn)
    initial_message: Optional[str] = None  # tin nhắn đầu tiên


class SendMessageRequest(BaseModel):
    content: str
    type: str = "text"   # "text" | "image"


class MarkReadRequest(BaseModel):
    pass  # không cần body


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_fcm_tokens(db: Session, user_id: int) -> list[str]:
    """Lấy tất cả FCM token của một user (có thể nhiều thiết bị)."""
    tokens = db.query(FcmToken).filter(
        FcmToken.user_id == user_id,
        FcmToken.is_active == True,
    ).all()
    return [t.token for t in tokens if t.token]


def _get_seller_info(db: Session, seller_id: int) -> User:
    seller = db.query(User).filter(User.id == seller_id).first()
    if not seller or seller.type not in SELLER_TYPES:
        raise HTTPException(status_code=404, detail="Seller không tồn tại")
    return seller


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/rooms", summary="Tạo hoặc lấy phòng chat với seller")
async def create_or_get_room(
    body: CreateRoomRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Buyer tạo/lấy phòng chat với seller.
    Nếu đã có phòng → trả về chat_id hiện tại (không tạo thêm).
    Nếu chưa có → tạo mới trong Firestore.
    """
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat trực tiếp")

    seller = _get_seller_info(db, body.seller_id)
    shop_name = seller.name or f"Shop #{seller.id}"
    buyer_name = current_user.name or f"User #{current_user.id}"

    # Buyer có thể là user thường hoặc seller chat với seller khác
    buyer_id = current_user.id
    seller_id = body.seller_id

    try:
        chat_id, created = firebase_service.get_or_create_chat_room(
            buyer_id=buyer_id,
            seller_id=seller_id,
            shop_name=shop_name,
            buyer_name=buyer_name,
        )
    except Exception as e:
        logger.error(f"[Chat] Firestore error: {e}")
        raise HTTPException(status_code=503, detail="Chat service tạm thời không khả dụng")

    # Gửi tin nhắn đầu tiên nếu có
    if body.initial_message and created:
        try:
            firebase_service.add_message_to_firestore(
                chat_id=chat_id,
                sender_id=buyer_id,
                sender_type="buyer",
                content=body.initial_message,
            )
            # Push FCM cho seller
            seller_tokens = _get_fcm_tokens(db, seller_id)
            if seller_tokens:
                firebase_service.send_fcm_multicast(
                    tokens=seller_tokens,
                    title=f"Tin nhắn mới từ {buyer_name}",
                    body=body.initial_message[:80],
                    data={
                        "category": "chat",
                        "chat_id": chat_id,
                        "action_url": f"/chat/{chat_id}",
                    },
                )
        except Exception as e:
            logger.warning(f"[Chat] Initial message error: {e}")

    return {
        "success": True,
        "data": {
            "chat_id": chat_id,
            "seller_id": seller_id,
            "shop_name": shop_name,
            "created": created,
        },
    }


@router.get("/rooms", summary="Danh sách phòng chat của user hiện tại")
async def list_rooms(
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách phòng chat từ Firestore.
    - Buyer (user): xem phòng mà mình là buyer
    - Seller: xem phòng mà mình là seller
    - Admin: KHÔNG có quyền truy cập
    """
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat")
    try:
        db_fs = firebase_service.get_firestore()
        is_seller = current_user.type in SELLER_TYPES

        if is_seller:
            query = db_fs.collection("chats").where(
                "seller_id", "==", current_user.id
            ).order_by("last_at", direction="DESCENDING").limit(50)
        else:
            query = db_fs.collection("chats").where(
                "buyer_id", "==", current_user.id
            ).order_by("last_at", direction="DESCENDING").limit(50)

        docs = query.stream()
        rooms = []
        for doc in docs:
            d = doc.to_dict()
            rooms.append({
                "chat_id": doc.id,
                "buyer_id": d.get("buyer_id"),
                "seller_id": d.get("seller_id"),
                "shop_name": d.get("shop_name", ""),
                "buyer_name": d.get("buyer_name", ""),
                "last_message": d.get("last_message", ""),
                "last_at": d.get("last_at").isoformat() if d.get("last_at") else None,
                "unread_count": d.get("unread_buyer" if is_seller else "unread_seller", 0),
            })

        return {"success": True, "data": rooms}
    except Exception as e:
        logger.error(f"[Chat] list_rooms error: {e}")
        raise HTTPException(status_code=503, detail="Không thể tải danh sách chat")


@router.post("/rooms/{chat_id}/messages", summary="Gửi tin nhắn")
async def send_message(
    chat_id: str,
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ghi tin nhắn vào Firestore + gửi FCM push cho người nhận.
    Chỉ buyer và seller trong phòng mới gửi được.
    """
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat")
    if not body.content.strip():
        raise HTTPException(status_code=422, detail="Tin nhắn không được trống")

    is_seller = current_user.type in SELLER_TYPES
    sender_type = "seller" if is_seller else "buyer"

    # Parse chat_id để lấy buyer_id và seller_id
    # Format: user{buyerId}_seller{sellerId}
    try:
        parts = chat_id.split("_")
        buyer_id = int(parts[0].replace("user", ""))
        seller_id = int(parts[1].replace("seller", ""))
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="chat_id không hợp lệ")

    # Kiểm tra quyền — chỉ participant mới gửi được
    if is_seller and current_user.id != seller_id:
        raise HTTPException(status_code=403, detail="Không có quyền gửi tin nhắn này")
    if not is_seller and current_user.id != buyer_id:
        raise HTTPException(status_code=403, detail="Không có quyền gửi tin nhắn này")

    try:
        msg_id = firebase_service.add_message_to_firestore(
            chat_id=chat_id,
            sender_id=current_user.id,
            sender_type=sender_type,
            content=body.content,
            msg_type=body.type,
        )
    except Exception as e:
        logger.error(f"[Chat] send_message Firestore error: {e}")
        raise HTTPException(status_code=503, detail="Không thể gửi tin nhắn")

    # Gửi FCM cho người nhận
    recipient_id = buyer_id if is_seller else seller_id
    recipient_tokens = _get_fcm_tokens(db, recipient_id)
    if recipient_tokens:
        sender_name = current_user.name or ("Shop" if is_seller else "Khách")
        firebase_service.send_fcm_multicast(
            tokens=recipient_tokens,
            title=f"Tin nhắn từ {sender_name}",
            body=body.content[:80],
            data={
                "category": "chat",
                "chat_id": chat_id,
                "action_url": f"/chat/{chat_id}",
            },
        )

    return {
        "success": True,
        "data": {"message_id": msg_id, "chat_id": chat_id},
    }


@router.get("/rooms/{chat_id}/messages", summary="Lịch sử tin nhắn")
async def get_messages(
    chat_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy lịch sử tin nhắn của phòng chat (50 tin gần nhất).
    Chỉ buyer và seller trong phòng mới xem được.
    """
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không xem được chat")
    try:
        db_fs = firebase_service.get_firestore()
        messages_ref = (
            db_fs.collection("chats")
            .document(chat_id)
            .collection("messages")
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
        )
        docs = messages_ref.stream()
        messages = []
        for doc in docs:
            d = doc.to_dict()
            messages.append({
                "id": doc.id,
                "sender_id": d.get("sender_id"),
                "sender_type": d.get("sender_type"),
                "content": d.get("content", ""),
                "type": d.get("type", "text"),
                "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
                "read": d.get("read", False),
            })
        messages.reverse()  # chronological order
        return {"success": True, "data": messages}
    except Exception as e:
        logger.error(f"[Chat] get_messages error: {e}")
        raise HTTPException(status_code=503, detail="Không thể tải tin nhắn")


@router.put("/rooms/{chat_id}/read", summary="Đánh dấu đã đọc")
async def mark_as_read(
    chat_id: str,
    current_user: User = Depends(get_current_user),
):
    """Reset unread count cho buyer hoặc seller."""
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat")
    is_seller = current_user.type in SELLER_TYPES
    reader_type = "seller" if is_seller else "buyer"
    try:
        firebase_service.mark_messages_as_read(chat_id, reader_type)
        return {"success": True}
    except Exception as e:
        logger.error(f"[Chat] mark_read error: {e}")
        raise HTTPException(status_code=503, detail="Không thể cập nhật trạng thái đọc")
