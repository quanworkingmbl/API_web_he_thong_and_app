"""
Notifications API – Quản lý thông báo người dùng

Endpoints (Mobile + Seller Web):
  GET    /notifications              – Danh sách thông báo (có lọc category)
  GET    /notifications/unread-count – Số thông báo chưa đọc (badge count)
  PUT    /notifications/{id}/read   – Đánh dấu 1 thông báo đã đọc
  PUT    /notifications/read-all    – Đánh dấu tất cả đã đọc
  DELETE /notifications/{id}        – Xóa 1 thông báo
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.models.notification import Notification
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()


# ==============================================================================
# GET: Danh sách thông báo
# ==============================================================================

@router.get("", summary="Lấy danh sách thông báo")
async def get_my_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    category: Optional[str] = Query(
        None,
        description="Lọc theo loại: ORDER | SYSTEM | PROMOTION | PAYMENT"
    ),
    is_read: Optional[bool] = Query(None, description="Lọc đã đọc/chưa đọc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách thông báo của user hiện tại.
    Hỗ trợ lọc theo category và trạng thái đọc.
    Sắp xếp mới nhất lên đầu.
    """
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )

    if category:
        query = query.filter(Notification.category == category.upper())

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    total = query.count()
    skip = (page - 1) * limit
    notifications = (
        query
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    data = []
    for n in notifications:
        ref_name: str | None = None
        ref_image: str | None = None

        try:
            if n.ref_type == "order" and n.ref_id:
                from app.models.order import Order
                obj = db.query(Order).filter(Order.id == n.ref_id).first()
                if obj:
                    ref_name = f"Đơn hàng #{getattr(obj, 'order_number', n.ref_id)}"
            elif n.ref_type == "product" and n.ref_id:
                from app.models.product import Product
                obj = db.query(Product).filter(Product.id == n.ref_id).first()
                if obj:
                    ref_name = obj.name
                    # Lấy ảnh đầu tiên từ field images (có thể là JSON array hoặc URL đơn)
                    import json as _json
                    raw = obj.images or ""
                    try:
                        imgs = _json.loads(raw)
                        ref_image = imgs[0] if isinstance(imgs, list) and imgs else raw or None
                    except Exception:
                        ref_image = raw or None
            elif n.ref_type == "content" and n.ref_id:
                from app.models.content import Content
                obj = db.query(Content).filter(Content.id == n.ref_id).first()
                if obj:
                    ref_name = obj.title
                    ref_image = obj.images or None
            elif n.ref_type == "complaint" and n.ref_id:
                from app.models.complaint import Complaint
                obj = db.query(Complaint).filter(Complaint.id == n.ref_id).first()
                if obj:
                    ref_name = f"Khiếu nại #{n.ref_id}: {getattr(obj, 'title', '') or ''}"
            elif n.ref_type == "seller_profile" and n.ref_id:
                from app.models.user import User as _User
                obj = db.query(_User).filter(_User.id == n.ref_id).first()
                if obj:
                    ref_name = obj.full_name or obj.name or f"Người dùng #{n.ref_id}"
        except Exception:
            pass  # Không break nếu enrich lỗi

        data.append({
            "id": n.id,
            "category": n.category,
            "title": n.title,
            "message": n.message,
            "action_url": n.action_url,
            "ref_type": n.ref_type,
            "ref_id": n.ref_id,
            "ref_name": ref_name,
            "ref_image": ref_image,
            "is_read": n.is_read,
            "read_at": n.read_at.isoformat() if n.read_at else None,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        })


    return {
        "success": True,
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        },
    }


# ==============================================================================
# GET: Số thông báo chưa đọc (badge count)
# ==============================================================================

@router.get("/unread-count", summary="Số thông báo chưa đọc")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trả về tổng số thông báo chưa đọc của user.
    Dùng để hiển thị badge icon chuông.
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    return {
        "success": True,
        "data": {
            "unread_count": count,
        },
    }


# ==============================================================================
# PUT: Đánh dấu 1 thông báo đã đọc
# ==============================================================================

@router.put("/{notification_id}/read", summary="Đánh dấu thông báo đã đọc")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Đánh dấu một thông báo cụ thể đã được đọc."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Thông báo không tồn tại")

    if not notif.is_read:
        notif.is_read = True
        notif.read_at = datetime.utcnow()
        db.commit()

    return {
        "success": True,
        "message": "Đã đánh dấu đã đọc",
        "notification_id": notification_id,
    }


# ==============================================================================
# PUT: Đánh dấu tất cả đã đọc
# ==============================================================================

@router.put("/read-all", summary="Đánh dấu tất cả thông báo đã đọc")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Đánh dấu tất cả thông báo chưa đọc của user là đã đọc."""
    now = datetime.utcnow()
    updated = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .all()
    )

    count = len(updated)
    for n in updated:
        n.is_read = True
        n.read_at = now

    if count > 0:
        db.commit()

    return {
        "success": True,
        "message": f"Đã đánh dấu {count} thông báo là đã đọc",
        "updated_count": count,
    }


# ==============================================================================
# DELETE: Xóa 1 thông báo
# ==============================================================================

@router.delete("/{notification_id}", summary="Xóa thông báo")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa một thông báo khỏi inbox (chỉ được xóa thông báo của chính mình)."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Thông báo không tồn tại")

    db.delete(notif)
    db.commit()

    return {
        "success": True,
        "message": "Đã xóa thông báo",
        "notification_id": notification_id,
    }


# ==============================================================================
# POST: Đăng ký / Cập nhật FCM Token
# ==============================================================================

from pydantic import BaseModel

class FCMTokenRequest(BaseModel):
    token: str


@router.post("/fcm-token", summary="Đăng ký FCM device token")
async def register_fcm_token(
    body: FCMTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lưu FCM token của thiết bị hiện tại vào tài khoản user.
    Gọi endpoint này ngay sau khi user login hoặc khi token mới được cấp bởi Firebase.

    Request body:
        { "token": "<fcm_device_token>" }
    """
    if not body.token or len(body.token) < 10:
        raise HTTPException(status_code=400, detail="FCM token không hợp lệ")

    user = db.query(User).filter(User.id == current_user.id).first()
    if user and user.fcm_token != body.token:
        user.fcm_token = body.token
        db.commit()

    return {
        "success": True,
        "message": "FCM token đã được cập nhật",
    }


@router.delete("/fcm-token", summary="Xóa FCM token (logout)")
async def clear_fcm_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Xóa FCM token của user. Gọi khi user logout để không còn nhận push notification.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if user and user.fcm_token:
        user.fcm_token = None
        db.commit()

    return {
        "success": True,
        "message": "Đã xóa FCM token",
    }
