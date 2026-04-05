"""
Complaint Management API
========================
Endpoints:
  [Public/Auth]
  GET  /complaints/            – Danh sách khiếu nại (buyer: chỉ của mình; seller: đơn mình; admin: tất cả)
  POST /complaints/            – Buyer tạo khiếu nại mới (bắt buộc nội dung, khuyến khích ảnh)
  GET  /complaints/{id}        – Chi tiết + thread comment
  POST /complaints/{id}/comments  – Gửi comment trong thread (buyer/seller/admin)
  PUT  /complaints/{id}/status    – Admin/CS cập nhật trạng thái (state machine + audit)
  PUT  /complaints/{id}/assign    – Admin giao cho CS cụ thể
  GET  /reviews/               – Danh sách đánh giá sản phẩm
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.complaint import (
    Complaint, ComplaintStatus, ComplaintCategory, ComplaintPriority,
    ComplaintComment, ComplaintStatusLog, CommentRole,
    Review, ModerationStatus,
)
from app.models.order import Order
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel, Field
import json

router = APIRouter()


# ==============================================================================
# STATE MACHINE – chuyển trạng thái hợp lệ theo vai trò
# ==============================================================================

# role → old_status → allowed_new_statuses
COMPLAINT_TRANSITIONS = {
    "buyer": {
        ComplaintStatus.PENDING:     {ComplaintStatus.CLOSED},     # buyer đóng khiếu nại của mình
        ComplaintStatus.RESOLVED:    {ComplaintStatus.CLOSED},     # buyer xác nhận đã giải quyết
    },
    "seller": {
        ComplaintStatus.IN_PROGRESS: {ComplaintStatus.RESOLVED},   # seller đề xuất giải quyết
    },
    "admin": None,  # admin không hạn chế
    "cs":    None,  # customer support không hạn chế
}

VALID_ADMIN_ROLES = {"admin", "cs"}


def _resolve_role(user: User) -> str:
    """Chuẩn hoá role string."""
    t = (user.type or "").lower()
    if t == "admin":
        return "admin"
    if t in ("producer", "seller"):
        return "seller"
    return "buyer"


def _validate_complaint_transition(old: ComplaintStatus, new: ComplaintStatus, role: str):
    if old == new:
        raise HTTPException(400, f"Khiếu nại đã ở trạng thái {old.value}")

    if role in VALID_ADMIN_ROLES:
        return   # admin/CS tự do

    allowed_map = COMPLAINT_TRANSITIONS.get(role, {})
    if allowed_map is None:
        return   # None = không hạn chế

    allowed_next = allowed_map.get(old)
    if allowed_next is None:
        raise HTTPException(403, f"Vai trò '{role}' không được phép cập nhật khiếu nại ở trạng thái {old.value}")

    if new not in allowed_next:
        names = ", ".join(s.value for s in allowed_next)
        raise HTTPException(400, f"Không thể chuyển từ {old.value} → {new.value}. Được phép: [{names}]")


def _log_complaint_status(db: Session, complaint_id: int, old: Optional[str], new: str,
                           actor_id: Optional[int], note: Optional[str] = None):
    log = ComplaintStatusLog(
        complaint_id=complaint_id,
        old_status=old,
        new_status=new,
        actor_id=actor_id,
        note=note,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.flush()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CreateComplaintRequest(BaseModel):
    order_id:    Optional[int]    = None
    product_id:  Optional[int]    = None
    category:    ComplaintCategory = ComplaintCategory.OTHER
    priority:    ComplaintPriority = ComplaintPriority.MEDIUM
    title:       str              = Field(..., min_length=10, max_length=255)
    description: str              = Field(..., min_length=30, description="Mô tả chi tiết khiếu nại (tối thiểu 30 ký tự)")
    images:      Optional[str]    = Field(None, description="JSON array URL ảnh bằng chứng")


class AddCommentRequest(BaseModel):
    message:     str           = Field(..., min_length=5, max_length=2000)
    attachments: Optional[str] = Field(None, description="JSON array URL ảnh/file đính kèm")
    is_internal: bool          = Field(False, description="True = chỉ admin/CS thấy")


class UpdateStatusRequest(BaseModel):
    status:          str            = Field(..., pattern="^(PENDING|ASSIGNED|IN_PROGRESS|RESOLVED|CLOSED|REJECTED)$")
    note:            Optional[str]  = Field(None, max_length=1000)
    resolution:      Optional[str]  = Field(None, description="Nội dung giải quyết")
    resolution_type: Optional[str]  = Field(None, pattern="^(REFUND|RETURN|REPLACEMENT|NONE)?$")


class AssignRequest(BaseModel):
    assigned_to: int = Field(..., description="User ID của CS/admin được giao")
    note:        Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedReviewResponse(BaseModel):
    total: int
    page:  int
    limit: int
    data:  List[ReviewResponse]


# ==============================================================================
# HELPERS
# ==============================================================================

def _complaint_detail(c: Complaint, db: Session, current_user: Optional[User] = None) -> dict:
    """Serialize complaint + thread."""
    role = _resolve_role(current_user) if current_user else "buyer"
    is_privileged = role in VALID_ADMIN_ROLES

    # Filter comment: internal chỉ admin/CS thấy
    visible_comments = [
        {
            "id": cm.id,
            "author_id": cm.author_id,
            "author_name": cm.author.name if cm.author else None,
            "role": cm.role.value if hasattr(cm.role, "value") else cm.role,
            "message": cm.message,
            "attachments": cm.attachments,
            "is_internal": cm.is_internal,
            "created_at": cm.created_at.isoformat(),
        }
        for cm in c.comments
        if (not cm.is_internal) or is_privileged
    ]

    result = {
        "id": c.id,
        "order_id": c.order_id,
        "product_id": c.product_id,
        "user_id": c.user_id,
        "category": c.category.value if hasattr(c.category, "value") else c.category,
        "priority": c.priority.value if hasattr(c.priority, "value") else c.priority,
        "title": c.title,
        "description": c.description,
        "images": c.images,
        "status": c.status.value if hasattr(c.status, "value") else c.status,
        "handled_by": c.handled_by,
        "resolution": c.resolution,
        "resolution_type": c.resolution_type,
        "return_request_id": c.return_request_id,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "assigned_at": c.assigned_at.isoformat() if c.assigned_at else None,
        "first_response_at": c.first_response_at.isoformat() if c.first_response_at else None,
        "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
        "comments": visible_comments,
        "comment_count": len(visible_comments),
    }

    if is_privileged:
        result["status_logs"] = [
            {
                "old_status": log.old_status,
                "new_status": log.new_status,
                "actor_id": log.actor_id,
                "note": log.note,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in c.status_logs
        ]

    return result


def _check_complaint_access(complaint: Complaint, current_user: User, db: Session) -> str:
    """
    Kiểm tra quyền truy cập complaint. Trả về role string.
    - buyer: phải là người tạo complaint
    - seller: phải là seller_id của đơn hàng liên quan
    - admin: không hạn chế
    """
    role = _resolve_role(current_user)

    if role in VALID_ADMIN_ROLES:
        return role

    if role == "buyer":
        if complaint.user_id != current_user.id:
            raise HTTPException(403, "Bạn không có quyền xem khiếu nại này")
        return role

    if role == "seller":
        if complaint.order_id:
            order = db.query(Order).filter(Order.id == complaint.order_id).first()
            if order and order.seller_id == current_user.id:
                return role
        raise HTTPException(403, "Khiếu nại này không thuộc đơn hàng của bạn")

    raise HTTPException(403, "Không có quyền truy cập")


# ==============================================================================
# COMPLAINT ENDPOINTS
# ==============================================================================

@router.get("/complaints")
async def get_complaints(
    page:     int             = Query(1, ge=1),
    limit:    int             = Query(20, ge=1, le=100),
    status:   Optional[str]  = Query(None, description="Filter theo trạng thái"),
    category: Optional[str]  = Query(None, description="DELIVERY/QUALITY/REFUND/FRAUD/SERVICE/OTHER"),
    priority: Optional[str]  = Query(None, description="LOW/MEDIUM/HIGH/URGENT"),
    order_id: Optional[int]  = Query(None),
    search:   Optional[str]  = Query(None, description="Tìm theo tiêu đề"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Danh sách khiếu nại có lọc/tìm kiếm.
    - buyer   → chỉ xem của mình
    - seller  → chỉ xem liên quan đơn của mình
    - admin   → xem tất cả + đầy đủ filter
    """
    role = _resolve_role(current_user)
    query = db.query(Complaint)

    # Phân quyền đọc
    if role == "buyer":
        query = query.filter(Complaint.user_id == current_user.id)
    elif role == "seller":
        seller_order_ids = [
            o.id for o in db.query(Order.id).filter(Order.seller_id == current_user.id).all()
        ]
        query = query.filter(Complaint.order_id.in_(seller_order_ids))
    # admin: không lọc

    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category == category)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if order_id:
        query = query.filter(Complaint.order_id == order_id)
    if search:
        query = query.filter(Complaint.title.ilike(f"%{search}%"))

    total = query.count()
    skip  = (page - 1) * limit
    complaints = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": c.id,
                "order_id": c.order_id,
                "category": c.category.value if hasattr(c.category, "value") else c.category,
                "priority": c.priority.value if hasattr(c.priority, "value") else c.priority,
                "title": c.title,
                "status": c.status.value if hasattr(c.status, "value") else c.status,
                "handled_by": c.handled_by,
                "comment_count": len(c.comments),
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "first_response_at": c.first_response_at.isoformat() if c.first_response_at else None,
            }
            for c in complaints
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.post("/complaints")
async def create_complaint(
    complaint_data: CreateComplaintRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buyer/Consumer tạo khiếu nại mới.
    - Bắt buộc: tiêu đề ≥10 ký tự, mô tả ≥30 ký tự.
    - Nên có ảnh bằng chứng (khuyến khích, không bắt buộc).
    - Nếu gắn order_id: phải là đơn của chính mình.
    """
    # Kiểm tra order ownership nếu có
    if complaint_data.order_id:
        order = db.query(Order).filter(
            Order.id == complaint_data.order_id,
            Order.customer_id == current_user.id
        ).first()
        if not order:
            raise HTTPException(400, "Đơn hàng không tồn tại hoặc không thuộc về bạn")

    # Warn nếu không có ảnh (không chặn, chỉ phát cảnh báo trong response)
    has_images = bool(complaint_data.images)

    new_complaint = Complaint(
        product_id=complaint_data.product_id,
        order_id=complaint_data.order_id,
        user_id=current_user.id,
        category=complaint_data.category,
        priority=complaint_data.priority,
        complaint_type=complaint_data.category.value,  # backward-compat
        title=complaint_data.title,
        description=complaint_data.description,
        images=complaint_data.images,
        status=ComplaintStatus.PENDING,
    )
    db.add(new_complaint)
    db.flush()

    # Audit log: tạo mới
    _log_complaint_status(db, new_complaint.id, None, ComplaintStatus.PENDING.value,
                          current_user.id, "Khiếu nại được tạo mới")

    db.commit()
    db.refresh(new_complaint)

    return {
        "success": True,
        "message": "Khiếu nại đã được gửi" + ("" if has_images else ". Nên bổ sung ảnh bằng chứng để xử lý nhanh hơn"),
        "data": {
            "id": new_complaint.id,
            "status": "PENDING",
            "has_images": has_images,
        }
    }


@router.get("/complaints/{complaint_id}")
async def get_complaint_detail(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chi tiết khiếu nại + thread comment + audit log (admin/CS)."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Khiếu nại không tồn tại")

    _check_complaint_access(complaint, current_user, db)

    return {
        "success": True,
        "data": _complaint_detail(complaint, db, current_user)
    }


@router.post("/complaints/{complaint_id}/comments")
async def add_comment(
    complaint_id: int,
    comment_data: AddCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gửi comment trong thread khiếu nại (buyer/seller/admin).
    - is_internal=True: chỉ admin/CS thấy (ghi chú nội bộ).
    - Ghi nhận first_response_at nếu admin/CS phản hồi lần đầu.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Khiếu nại không tồn tại")

    role = _check_complaint_access(complaint, current_user, db)

    # Không được comment trên khiếu nại đã CLOSED/REJECTED
    if complaint.status in (ComplaintStatus.CLOSED, ComplaintStatus.REJECTED):
        raise HTTPException(400, f"Không thể thêm comment khi khiếu nại đã {complaint.status.value}")

    # Buyer không được gửi internal comment
    if comment_data.is_internal and role not in VALID_ADMIN_ROLES:
        raise HTTPException(403, "Chỉ admin/CS mới được gửi ghi chú nội bộ")

    comment_role = CommentRole.ADMIN if role in VALID_ADMIN_ROLES else (
        CommentRole.SELLER if role == "seller" else CommentRole.BUYER
    )

    new_comment = ComplaintComment(
        complaint_id=complaint_id,
        author_id=current_user.id,
        role=comment_role,
        message=comment_data.message,
        attachments=comment_data.attachments,
        is_internal=comment_data.is_internal,
    )
    db.add(new_comment)

    # Cập nhật SLA: first_response_at nếu admin/CS phản hồi lần đầu
    if role in VALID_ADMIN_ROLES and not complaint.first_response_at:
        complaint.first_response_at = datetime.utcnow()

    # Tự động chuyển PENDING → IN_PROGRESS khi CS bắt đầu reply
    if role in VALID_ADMIN_ROLES and complaint.status == ComplaintStatus.PENDING:
        old_st = complaint.status.value
        complaint.status = ComplaintStatus.IN_PROGRESS
        _log_complaint_status(db, complaint_id, old_st, ComplaintStatus.IN_PROGRESS.value,
                              current_user.id, "Tự động chuyển IN_PROGRESS khi CS phản hồi lần đầu")

    db.commit()
    db.refresh(new_comment)

    return {
        "success": True,
        "message": "Đã gửi phản hồi",
        "data": {
            "id": new_comment.id,
            "complaint_id": complaint_id,
            "role": comment_role.value,
            "message": new_comment.message,
            "created_at": new_comment.created_at.isoformat() if new_comment.created_at else None,
        }
    }


@router.put("/complaints/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: int,
    status_data: UpdateStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật trạng thái khiếu nại với state machine + audit log.
    - Admin/CS: mọi chuyển đổi.
    - Buyer: chỉ RESOLVED→CLOSED (xác nhận) hoặc PENDING→CLOSED (rút đơn).
    - Seller: IN_PROGRESS→RESOLVED (đề xuất giải quyết).
    - Nếu RESOLVED + resolution_type=REFUND/RETURN: đánh dấu cần xử lý hoàn tiền/đổi hàng.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Khiếu nại không tồn tại")

    role = _check_complaint_access(complaint, current_user, db)

    old_status = complaint.status
    try:
        new_status = ComplaintStatus(status_data.status)
    except ValueError:
        raise HTTPException(400, f"Trạng thái không hợp lệ: {status_data.status}")

    # State machine
    _validate_complaint_transition(old_status, new_status, role)

    # Cập nhật trạng thái
    complaint.status = new_status

    # SLA timestamps
    now = datetime.utcnow()
    if new_status == ComplaintStatus.ASSIGNED and not complaint.assigned_at:
        complaint.assigned_at = now
    elif new_status == ComplaintStatus.RESOLVED:
        complaint.resolved_at = now
        if status_data.resolution:
            complaint.resolution = status_data.resolution
        if status_data.resolution_type:
            complaint.resolution_type = status_data.resolution_type
    elif new_status == ComplaintStatus.CLOSED:
        complaint.closed_at = now

    # Xử lý liên kết refund/return
    refund_note = ""
    if new_status == ComplaintStatus.RESOLVED and status_data.resolution_type in ("REFUND", "RETURN"):
        refund_note = (
            f" | [ACTION REQUIRED] Cần tạo {status_data.resolution_type} request cho complaint #{complaint_id}. "
            "Admin hãy xử lý thủ công qua /returns hoặc /payments."
        )
        # Nếu có return_request_id thì gắn
        # (việc tạo ReturnRequest thực sự cần thêm data → để admin tạo thủ công)

    # Admin/CS được giao
    if role in VALID_ADMIN_ROLES:
        complaint.handled_by = current_user.id

    # Audit log
    _log_complaint_status(
        db, complaint_id,
        old_status.value, new_status.value,
        current_user.id,
        (status_data.note or "") + refund_note,
    )

    db.commit()

    response = {
        "success": True,
        "message": f"Đã cập nhật trạng thái: {old_status.value} → {new_status.value}",
        "complaint_id": complaint_id,
        "old_status": old_status.value,
        "new_status": new_status.value,
    }
    if refund_note:
        response["action_required"] = f"Cần tạo {status_data.resolution_type} request thủ công"
    return response


@router.put("/complaints/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: int,
    assign_data: AssignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Giao khiếu nại cho CS/admin cụ thể xử lý."""
    if current_user.type != "admin":
        raise HTTPException(403, "Chỉ admin mới có quyền phân công")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Khiếu nại không tồn tại")

    # Validate CS user exists
    cs_user = db.query(User).filter(User.id == assign_data.assigned_to).first()
    if not cs_user:
        raise HTTPException(400, "User được giao không tồn tại")

    old_status = complaint.status.value if hasattr(complaint.status, "value") else str(complaint.status)

    complaint.handled_by = assign_data.assigned_to
    if complaint.status == ComplaintStatus.PENDING:
        complaint.status = ComplaintStatus.ASSIGNED
        complaint.assigned_at = datetime.utcnow()

    _log_complaint_status(
        db, complaint_id, old_status,
        complaint.status.value,
        current_user.id,
        f"Giao cho user #{assign_data.assigned_to} ({cs_user.name}). {assign_data.note or ''}"
    )

    db.commit()

    return {
        "success": True,
        "message": f"Đã giao khiếu nại cho {cs_user.name}",
        "assigned_to": assign_data.assigned_to,
        "complaint_status": complaint.status.value,
    }


@router.delete("/complaints/{complaint_id}")
async def delete_complaint(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[Admin] Xóa khiếu nại (chỉ PENDING hoặc CLOSED)."""
    if current_user.type != "admin":
        raise HTTPException(403, "Chỉ admin mới có quyền xóa khiếu nại")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Khiếu nại không tồn tại")

    if complaint.status not in (ComplaintStatus.PENDING, ComplaintStatus.CLOSED, ComplaintStatus.REJECTED):
        raise HTTPException(
            400,
            f"Chỉ xóa được khiếu nại ở trạng thái PENDING/CLOSED/REJECTED. Hiện tại: {complaint.status.value}"
        )

    db.delete(complaint)
    db.commit()

    return {"success": True, "message": "Đã xóa khiếu nại"}


# ==============================================================================
# REVIEW ENDPOINTS (giữ nguyên)
# ==============================================================================

@router.get("/reviews", response_model=PaginatedReviewResponse)
async def get_reviews(
    page:       int           = Query(1, ge=1),
    limit:      int           = Query(20, ge=1, le=100),
    product_id: Optional[int] = Query(None),
    user_id:    Optional[int] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lấy danh sách đánh giá sản phẩm có phân trang."""
    query = db.query(Review)
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)

    total    = query.count()
    skip     = (page - 1) * limit
    reviews  = query.offset(skip).limit(limit).all()

    return PaginatedReviewResponse(
        total=total, page=page, limit=limit,
        data=[ReviewResponse.from_orm(r) for r in reviews]
    )
