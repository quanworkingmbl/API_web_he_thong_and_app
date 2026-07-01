"""
Chat API — v1
Endpoints cho real-time chat giữa User (buyer) và Seller
Data lưu trong Firestore, metadata trong PostgreSQL
"""
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google.cloud import storage as gcs

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.services import firebase_service

logger = logging.getLogger(__name__)
router = APIRouter()

SELLER_TYPES = {"seller", "producer"}
ADMIN_TYPES  = {"admin", "superadmin"}

# GCS config cho chat media
_GCS_BUCKET      = os.getenv("GCS_BUCKET_NAME", "mbl-cms-media-bucket")
_GCS_PUBLIC_BASE = f"https://storage.googleapis.com/{_GCS_BUCKET}"
_IMAGE_TYPES     = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_VIDEO_TYPES     = {"video/mp4", "video/quicktime"}
_MAX_IMAGE_SIZE  = 5  * 1024 * 1024   # 5 MB/ảnh
_MAX_VIDEO_SIZE  = 20 * 1024 * 1024   # 20 MB/video
_MAX_IMAGES      = 3                   # tối đa 3 ảnh/lần


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class CreateRoomRequest(BaseModel):
    seller_id: int
    product_id: Optional[int] = None   # context sản phẩm đang hỏi (tuỳ chọn)
    initial_message: Optional[str] = None  # tin nhắn đầu tiên


class SendMessageRequest(BaseModel):
    content: str
    type: str = "text"   # "text"


class SendProductRequest(BaseModel):
    product_id: int


class SendOrderRequest(BaseModel):
    order_id: int


class MarkReadRequest(BaseModel):
    pass  # không cần body


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_fcm_tokens(db: Session, user_id: int) -> list[str]:
    """Lấy FCM token của một user (lưu trong cột fcm_token của User)."""
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.fcm_token:
        return [user.fcm_token]
    return []


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

        # Không dùng orderBy trong Firestore query để tránh cần composite index.
        # Lọc theo buyer_id hoặc seller_id, sau đó sort bằng Python.
        if is_seller:
            query = db_fs.collection("chats").where(
                "seller_id", "==", current_user.id
            ).limit(50)
        else:
            query = db_fs.collection("chats").where(
                "buyer_id", "==", current_user.id
            ).limit(50)

        docs = query.stream()
        rooms = []
        for doc in docs:
            d = doc.to_dict()
            last_at = d.get("last_at")
            rooms.append({
                "chat_id": doc.id,
                "buyer_id": d.get("buyer_id"),
                "seller_id": d.get("seller_id"),
                "shop_name": d.get("shop_name", ""),
                "buyer_name": d.get("buyer_name", ""),
                "last_message": d.get("last_message", ""),
                "last_at": last_at.isoformat() if last_at else None,
                "last_at_raw": last_at,  # dùng để sort
                "unread_count": d.get("unread_seller" if is_seller else "unread_buyer", 0),
            })

        # Sort mới nhất lên đầu (Python-side, không cần composite index)
        rooms.sort(key=lambda r: r.pop("last_at_raw") or 0, reverse=True)

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


# ── GCS upload helper (internal) ─────────────────────────────────────────────

def _upload_chat_media(content: bytes, ext: str, content_type: str) -> str:
    """Upload file vào chat-media/ prefix trên GCS, trả về public URL."""
    key = f"chat-media/{uuid.uuid4()}{ext}"
    client = gcs.Client()
    bucket = client.bucket(_GCS_BUCKET)
    blob   = bucket.blob(key)
    blob.upload_from_string(content, content_type=content_type)
    return f"{_GCS_PUBLIC_BASE}/{key}"


def _delete_chat_media(url: str) -> None:
    """Xoá file GCS từ URL (dùng khi thu hồi ảnh/video)."""
    try:
        prefix = f"{_GCS_PUBLIC_BASE}/"
        if url.startswith(prefix):
            key = url[len(prefix):]
            gcs.Client().bucket(_GCS_BUCKET).blob(key).delete()
    except Exception as e:
        logger.warning(f"[Chat] GCS delete failed: {e}")


def _parse_participants(chat_id: str) -> tuple[int, int]:
    """Parse buyer_id, seller_id từ chat_id dạng user{n}_seller{m}."""
    try:
        parts  = chat_id.split("_")
        buyer  = int(parts[0].replace("user", ""))
        seller = int(parts[1].replace("seller", ""))
        return buyer, seller
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="chat_id không hợp lệ")


# ── Endpoint: Gửi ảnh/video (tối đa 3 ảnh, 1 video) ─────────────────────────

@router.post("/rooms/{chat_id}/messages/media", summary="Gửi ảnh hoặc video trong chat")
async def send_media(
    chat_id: str,
    files: List[UploadFile] = File(..., description="Tối đa 3 ảnh (≤5MB/ảnh) hoặc 1 video (≤20MB)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload ảnh/video lên GCS → ghi messages vào Firestore.
    - Ảnh: tối đa 3 file, mỗi file ≤ 5MB
    - Video: chỉ 1 file, ≤ 20MB
    """
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat")

    buyer_id, seller_id = _parse_participants(chat_id)
    is_seller   = current_user.type in SELLER_TYPES
    sender_type = "seller" if is_seller else "buyer"
    if is_seller and current_user.id != seller_id:
        raise HTTPException(status_code=403, detail="Không có quyền")
    if not is_seller and current_user.id != buyer_id:
        raise HTTPException(status_code=403, detail="Không có quyền")

    if not files:
        raise HTTPException(status_code=422, detail="Chưa chọn file")

    # Xác định loại: ảnh hay video
    first_ct = (files[0].content_type or "").lower()
    is_video  = first_ct in _VIDEO_TYPES

    if is_video:
        if len(files) > 1:
            raise HTTPException(status_code=422, detail="Chỉ gửi 1 video mỗi lần")
        file = files[0]
        ct   = (file.content_type or "").lower()
        if ct not in _VIDEO_TYPES:
            raise HTTPException(status_code=400, detail=f"Loại video không hỗ trợ: {ct}")
        content = await file.read()
        if len(content) > _MAX_VIDEO_SIZE:
            raise HTTPException(status_code=400, detail="Video vượt quá 20MB")
        ext = os.path.splitext(file.filename or "video")[1].lower() or ".mp4"
        url = _upload_chat_media(content, ext, ct)
        msg_ids = firebase_service.add_media_messages_to_firestore(
            chat_id=chat_id, sender_id=current_user.id,
            sender_type=sender_type, media_urls=[url], msg_type="video",
        )
        return {"success": True, "data": {"message_ids": msg_ids, "urls": [url], "type": "video"}}

    # ── Ảnh ──
    if len(files) > _MAX_IMAGES:
        raise HTTPException(status_code=422, detail=f"Chỉ được gửi tối đa {_MAX_IMAGES} ảnh cùng lúc")

    urls: list[str] = []
    for file in files:
        ct = (file.content_type or "").lower()
        if ct not in _IMAGE_TYPES:
            raise HTTPException(status_code=400, detail=f"Loại ảnh không hỗ trợ: {ct}")
        content = await file.read()
        if len(content) > _MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail=f"Ảnh {file.filename!r} vượt quá 5MB")
        ext = os.path.splitext(file.filename or "img")[1].lower() or ".jpg"
        urls.append(_upload_chat_media(content, ext, ct))

    msg_ids = firebase_service.add_media_messages_to_firestore(
        chat_id=chat_id, sender_id=current_user.id,
        sender_type=sender_type, media_urls=urls, msg_type="image",
    )

    # FCM push cho người nhận
    recipient_id     = buyer_id if is_seller else seller_id
    recipient_tokens = _get_fcm_tokens(db, recipient_id)
    if recipient_tokens:
        sender_name = current_user.name or ("Shop" if is_seller else "Khách")
        firebase_service.send_fcm_multicast(
            tokens=recipient_tokens,
            title=f"Ảnh mới từ {sender_name}",
            body=f"Đã gửi {len(urls)} ảnh",
            data={"category": "chat", "chat_id": chat_id},
        )

    return {"success": True, "data": {"message_ids": msg_ids, "urls": urls, "type": "image"}}


# ── Endpoint: Thu hồi tin nhắn ─────────────────────────────────────────────

@router.delete("/rooms/{chat_id}/messages/{message_id}", summary="Thu hồi tin nhắn")
async def recall_message(
    chat_id: str,
    message_id: str,
    current_user: User = Depends(get_current_user),
):
    """Thu hồi tin nhắn (vô thời hạn). Chỉ người gửi mới thu hồi được."""
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat")
    try:
        result = firebase_service.recall_message(
            chat_id=chat_id,
            message_id=message_id,
            sender_id=current_user.id,
        )
        # Nếu là ảnh/video → xoá file GCS
        if result["old_type"] in ("image", "video") and result["old_content"]:
            _delete_chat_media(result["old_content"])
        return {"success": True, "message": "Tin nhắn đã được thu hồi"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"[Chat] recall_message error: {e}")
        raise HTTPException(status_code=503, detail="Không thể thu hồi tin nhắn")


# ── Endpoint: Gửi sản phẩm (App only) ────────────────────────────────────────

@router.post("/rooms/{chat_id}/messages/product", summary="Gửi sản phẩm vào chat")
async def send_product(
    chat_id: str,
    body: SendProductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gửi product card vào chat. Buyer hoặc Seller đều dùng được."""
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat")

    buyer_id, seller_id = _parse_participants(chat_id)
    is_seller   = current_user.type in SELLER_TYPES
    sender_type = "seller" if is_seller else "buyer"
    if is_seller and current_user.id != seller_id:
        raise HTTPException(status_code=403, detail="Không có quyền")
    if not is_seller and current_user.id != buyer_id:
        raise HTTPException(status_code=403, detail="Không có quyền")

    # Lấy product — phải thuộc seller của chat này
    product = db.query(Product).filter(
        Product.id == body.product_id,
        Product.seller_id == seller_id,
        Product.is_active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại hoặc không thuộc shop này")

    # Lấy ảnh đầu tiên
    import json
    images = []
    try:
        images = json.loads(product.images or "[]")
    except Exception:
        pass
    thumb = images[0] if images else ""

    # Số đã bán (nếu có field sold_count, fallback = 0)
    sold = getattr(product, "sold_count", 0) or 0

    metadata = {
        "product_id":  product.id,
        "name":        product.name,
        "price":       float(product.price),
        "image_url":   thumb,
        "sold_count":  sold,
        "seller_id":   seller_id,
    }

    try:
        msg_id = firebase_service.add_message_to_firestore(
            chat_id=chat_id,
            sender_id=current_user.id,
            sender_type=sender_type,
            content=f"Sản phẩm: {product.name}",
            msg_type="product_card",
            metadata=metadata,
        )
    except Exception as e:
        logger.error(f"[Chat] send_product error: {e}")
        raise HTTPException(status_code=503, detail="Không thể gửi sản phẩm")

    return {"success": True, "data": {"message_id": msg_id}}


# ── Endpoint: Gửi đơn hàng (App only) ────────────────────────────────────────

@router.post("/rooms/{chat_id}/messages/order", summary="Gửi đơn hàng vào chat")
async def send_order(
    chat_id: str,
    body: SendOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gửi order card vào chat. Buyer hoặc Seller đều dùng được."""
    if current_user.type in ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin không tham gia chat")

    buyer_id, seller_id = _parse_participants(chat_id)
    is_seller   = current_user.type in SELLER_TYPES
    sender_type = "seller" if is_seller else "buyer"
    if is_seller and current_user.id != seller_id:
        raise HTTPException(status_code=403, detail="Không có quyền")
    if not is_seller and current_user.id != buyer_id:
        raise HTTPException(status_code=403, detail="Không có quyền")

    # Lấy order — phải liên quan tới buyer+seller của chat này
    order = db.query(Order).filter(
        Order.id == body.order_id,
        Order.customer_id == buyer_id,
        Order.seller_id == seller_id,
        Order.is_active == True,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại hoặc không thuộc cuộc trò chuyện này")

    # Lấy items
    items_data = []
    for item in order.items:
        items_data.append({
            "product_name":  item.product_name,
            "product_image": item.product_image or "",
            "quantity":      item.quantity,
            "unit_price":    float(item.unit_price),
        })

    # Ảnh đại diện = ảnh item đầu tiên
    thumb = items_data[0]["product_image"] if items_data else ""

    # Label trạng thái tiếng Việt
    status_labels = {
        "PENDING":    "Chờ xác nhận",
        "CONFIRMED":  "Đã xác nhận",
        "PROCESSING": "Đang xử lý",
        "SHIPPING":   "Đang giao",
        "DELIVERED":  "Đã giao",
        "CANCELLED":  "Đã hủy",
        "REFUNDED":   "Đã hoàn tiền",
    }
    status_label = status_labels.get(order.status.value if hasattr(order.status, 'value') else str(order.status), str(order.status))

    metadata = {
        "order_id":     order.id,
        "order_number": order.order_number,
        "status":       str(order.status.value if hasattr(order.status, 'value') else order.status),
        "status_label": status_label,
        "total_amount": float(order.total_amount),
        "items_count":  len(items_data),
        "thumb":        thumb,
        "items":        items_data[:3],   # tối đa 3 items trong card
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "shipping_address": order.shipping_address,
    }

    content_preview = f"Đơn hàng #{order.order_number} · {len(items_data)} sản phẩm · {int(order.total_amount):,}₫"

    try:
        msg_id = firebase_service.add_message_to_firestore(
            chat_id=chat_id,
            sender_id=current_user.id,
            sender_type=sender_type,
            content=content_preview,
            msg_type="order_card",
            metadata=metadata,
        )
    except Exception as e:
        logger.error(f"[Chat] send_order error: {e}")
        raise HTTPException(status_code=503, detail="Không thể gửi đơn hàng")

    return {"success": True, "data": {"message_id": msg_id}}
