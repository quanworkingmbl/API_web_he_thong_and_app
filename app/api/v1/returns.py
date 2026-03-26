"""
Returns API – Yêu cầu đổi/trả hàng

Endpoints:
- POST /returns              – Khách hàng tạo yêu cầu đổi/trả
- GET  /returns/my           – Khách hàng xem yêu cầu của mình
- GET  /returns              – Admin xem tất cả yêu cầu
- PUT  /returns/{id}/approve – Admin duyệt yêu cầu
- PUT  /returns/{id}/reject  – Admin từ chối yêu cầu
- PUT  /returns/{id}/received – Admin đánh dấu đã nhận hàng trả về
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.return_request import ReturnRequest, ReturnType, ReturnStatus
from app.models.order import Order, OrderStatus
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CreateReturnRequest(BaseModel):
    order_id: int
    return_type: str = Field(default="RETURN", pattern="^(RETURN|EXCHANGE)$")
    reason: str = Field(..., min_length=10, max_length=1000)
    images: Optional[str] = None  # JSON array of image URLs


class AdminHandleRequest(BaseModel):
    note: Optional[str] = Field(None, max_length=500)


# ==============================================================================
# ENDPOINTS – CUSTOMER
# ==============================================================================

@router.post("", summary="Tạo yêu cầu đổi/trả hàng")
async def create_return_request(
    return_data: CreateReturnRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Khách hàng tạo yêu cầu đổi/trả.
    Chỉ được tạo khi đơn hàng ở trạng thái DELIVERED.
    """
    # Kiểm tra đơn hàng
    order = db.query(Order).filter(
        Order.id == return_data.order_id,
        Order.customer_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại hoặc không phải của bạn")

    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ có thể đổi/trả khi đơn hàng đã được giao. Trạng thái hiện tại: {order.status.value}"
        )

    # Kiểm tra đã có yêu cầu chưa
    existing = db.query(ReturnRequest).filter(
        ReturnRequest.order_id == return_data.order_id,
        ReturnRequest.user_id == current_user.id,
        ReturnRequest.status.in_([ReturnStatus.PENDING, ReturnStatus.APPROVED])
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Đã có yêu cầu đổi/trả đang xử lý cho đơn hàng này"
        )

    return_req = ReturnRequest(
        order_id=return_data.order_id,
        user_id=current_user.id,
        return_type=return_data.return_type,
        reason=return_data.reason,
        images=return_data.images,
        status=ReturnStatus.PENDING
    )
    db.add(return_req)
    db.commit()
    db.refresh(return_req)

    return {
        "success": True,
        "message": "Yêu cầu đổi/trả đã được gửi. Chúng tôi sẽ xử lý trong 1-3 ngày làm việc.",
        "data": {
            "id": return_req.id,
            "order_id": return_req.order_id,
            "return_type": return_req.return_type.value if hasattr(return_req.return_type, "value") else return_req.return_type,
            "reason": return_req.reason,
            "status": "PENDING",
            "created_at": return_req.created_at.isoformat()
        }
    }


@router.get("/my", summary="Xem yêu cầu đổi/trả của tôi")
async def get_my_return_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo mã đơn hàng"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Danh sách yêu cầu đổi/trả của người dùng đang đăng nhập."""
    query = db.query(ReturnRequest).filter(ReturnRequest.user_id == current_user.id)
    if status:
        query = query.filter(ReturnRequest.status == status)
    if search:
        matching_orders = db.query(Order.id).filter(
            Order.customer_id == current_user.id,
            Order.order_number.ilike(f"%{search}%")
        ).all()
        matching_ids = [o.id for o in matching_orders]
        query = query.filter(ReturnRequest.order_id.in_(matching_ids))

    total = query.count()
    skip = (page - 1) * limit
    requests = query.order_by(ReturnRequest.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": r.id,
                "order_id": r.order_id,
                "return_type": r.return_type.value if hasattr(r.return_type, "value") else r.return_type,
                "reason": r.reason,
                "status": r.status.value if hasattr(r.status, "value") else r.status,
                "admin_note": r.admin_note,
                "created_at": r.created_at.isoformat(),
                "handled_at": r.handled_at.isoformat() if r.handled_at else None
            }
            for r in requests
        ],
        "meta": {"total": total, "page": page, "limit": limit}
    }


@router.put("/{return_id}/cancel", summary="Khách hàng hủy yêu cầu đổi/trả")
async def cancel_return_request(
    return_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Khách hàng hủy yêu cầu đổi/trả.
    Chỉ hủy được khi yêu cầu đang ở trạng thái PENDING.
    """
    req = db.query(ReturnRequest).filter(
        ReturnRequest.id == return_id,
        ReturnRequest.user_id == current_user.id
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại hoặc không phải của bạn")

    if req.status != ReturnStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ hủy được yêu cầu ở trạng thái PENDING. Hiện tại: {req.status.value}"
        )

    req.status = ReturnStatus.CANCELLED
    req.handled_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Đã hủy yêu cầu đổi/trả",
        "return_id": return_id,
        "status": "CANCELLED"
    }


# ==============================================================================
# ENDPOINTS – ADMIN
# ==============================================================================

def _require_admin(current_user: User):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập")


@router.get("", summary="[Admin] Xem tất cả yêu cầu đổi/trả")
async def get_all_return_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    return_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin xem toàn bộ yêu cầu đổi/trả."""
    _require_admin(current_user)

    query = db.query(ReturnRequest)
    if status:
        query = query.filter(ReturnRequest.status == status)
    if return_type:
        query = query.filter(ReturnRequest.return_type == return_type)

    total = query.count()
    skip = (page - 1) * limit
    requests = query.order_by(ReturnRequest.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for r in requests:
        user = db.query(User).filter(User.id == r.user_id).first()
        order = db.query(Order).filter(Order.id == r.order_id).first()
        result.append({
            "id": r.id,
            "order_id": r.order_id,
            "order_number": order.order_number if order else None,
            "customer_name": user.name if user else None,
            "customer_email": user.email if user else None,
            "return_type": r.return_type.value if hasattr(r.return_type, "value") else r.return_type,
            "reason": r.reason,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "admin_note": r.admin_note,
            "created_at": r.created_at.isoformat(),
            "handled_at": r.handled_at.isoformat() if r.handled_at else None
        })

    return {
        "success": True,
        "data": result,
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }


@router.put("/{return_id}/approve", summary="[Admin] Duyệt yêu cầu đổi/trả")
async def approve_return_request(
    return_id: int,
    handle_data: AdminHandleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin duyệt yêu cầu đổi/trả → trạng thái APPROVED."""
    _require_admin(current_user)

    req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")
    if req.status != ReturnStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Không thể duyệt yêu cầu ở trạng thái {req.status.value}")

    req.status = ReturnStatus.APPROVED
    req.admin_note = handle_data.note
    req.handled_by = current_user.id
    req.handled_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Đã duyệt yêu cầu đổi/trả. Khách hàng sẽ được thông báo gửi hàng về.",
        "return_id": return_id,
        "status": "APPROVED"
    }


@router.put("/{return_id}/reject", summary="[Admin] Từ chối yêu cầu đổi/trả")
async def reject_return_request(
    return_id: int,
    handle_data: AdminHandleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin từ chối yêu cầu đổi/trả → trạng thái REJECTED."""
    _require_admin(current_user)

    req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")
    if req.status not in {ReturnStatus.PENDING, ReturnStatus.APPROVED}:
        raise HTTPException(status_code=400, detail=f"Không thể từ chối yêu cầu ở trạng thái {req.status.value}")

    req.status = ReturnStatus.REJECTED
    req.admin_note = handle_data.note
    req.handled_by = current_user.id
    req.handled_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Đã từ chối yêu cầu đổi/trả",
        "return_id": return_id,
        "status": "REJECTED"
    }


@router.put("/{return_id}/received", summary="[Admin] Đã nhận hàng trả về")
async def mark_return_received(
    return_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin đánh dấu đã nhận hàng trả về. Bước tiếp theo sẽ là hoàn tiền hoặc gửi hàng đổi."""
    _require_admin(current_user)

    req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")
    if req.status != ReturnStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Yêu cầu phải ở trạng thái APPROVED trước")

    req.status = ReturnStatus.RECEIVED
    req.handled_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Đã nhận hàng trả về. Tiến hành hoàn tiền hoặc gửi hàng đổi.",
        "return_id": return_id,
        "status": "RECEIVED"
    }

