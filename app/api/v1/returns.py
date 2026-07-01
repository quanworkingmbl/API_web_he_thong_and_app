"""
Returns API – Yêu cầu đổi/trả hàng

Luồng mới:
  Khách → tạo PENDING → [Seller xử lý trước]
    ├─ Seller chấp nhận → SELLER_APPROVED → Admin xác nhận nhận hàng (RECEIVED → REFUNDED/EXCHANGED)
    └─ Seller từ chối  → SELLER_REJECTED  → Admin xem xét lại
        ├─ Admin duyệt (override) → APPROVED  → RECEIVED → REFUNDED/EXCHANGED
        └─ Admin từ chối          → REJECTED  (cuối cùng)

Endpoints:
- POST /returns                        – Khách hàng tạo yêu cầu
- GET  /returns/my                     – Khách hàng xem yêu cầu của mình
- PUT  /returns/{id}/cancel            – Khách hàng hủy yêu cầu (chỉ khi PENDING)
- GET  /returns/seller                 – Seller xem yêu cầu liên quan đơn hàng của mình
- PUT  /returns/{id}/seller-approve    – Seller chấp nhận → SELLER_APPROVED
- PUT  /returns/{id}/seller-reject     – Seller từ chối   → SELLER_REJECTED (escalate Admin)
- GET  /returns                        – Admin xem tất cả yêu cầu
- PUT  /returns/{id}/approve           – Admin duyệt (override khi SELLER_REJECTED)
- PUT  /returns/{id}/reject            – Admin từ chối (cuối cùng)
- PUT  /returns/{id}/received          – Admin đánh dấu đã nhận hàng trả về
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import json
from app.core.database import get_db
from app.models.return_request import ReturnRequest, ReturnType, ReturnStatus
from app.models.order import Order, OrderStatus
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field


def _parse_images(raw: Optional[str]) -> List[str]:
    """Parse chuỗi JSON array ảnh thành list URL."""
    if not raw:
        return []
    try:
        result = json.loads(raw)
        return [str(u) for u in result if u] if isinstance(result, list) else []
    except Exception:
        return []
from app.services.notification import (
    notify_return_request_to_admin,
    notify_return_request_to_seller,
    notify_return_seller_approved_to_buyer,
    notify_return_seller_rejected_to_buyer,
    notify_return_escalated_to_admin,
    notify_return_approved_to_buyer,
    notify_return_rejected_to_buyer,
    notify_return_received_to_buyer,
)

import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CreateReturnRequest(BaseModel):
    order_id: int
    return_type: str = Field(default="RETURN", pattern="^(RETURN|EXCHANGE)$")
    reason: str = Field(..., min_length=10, max_length=1000)
    images: Optional[List[str]] = None  # Danh sách URL ảnh làm bằng chứng (tối đa 5)


class AdminHandleRequest(BaseModel):
    note: Optional[str] = Field(None, max_length=500)


class SellerHandleRequest(BaseModel):
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

    # Kiểm tra đã có yêu cầu đang xử lý chưa
    active_statuses = [
        ReturnStatus.PENDING,
        ReturnStatus.SELLER_APPROVED,
        ReturnStatus.SELLER_REJECTED,
        ReturnStatus.APPROVED,
    ]
    existing = db.query(ReturnRequest).filter(
        ReturnRequest.order_id == return_data.order_id,
        ReturnRequest.user_id == current_user.id,
        ReturnRequest.status.in_(active_statuses)
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
        images=json.dumps(return_data.images) if return_data.images else None,
        status=ReturnStatus.PENDING
    )
    db.add(return_req)
    db.commit()
    db.refresh(return_req)

    order_obj = db.query(Order).filter(Order.id == return_data.order_id).first()
    order_number = order_obj.order_number if order_obj else str(return_data.order_id)
    return_type_val = return_req.return_type.value if hasattr(return_req.return_type, "value") else return_req.return_type

    # [NOTIFICATION R1-A] Thông báo Seller: có yêu cầu đổi/trả mới cần xử lý
    try:
        if order_obj and order_obj.seller_id:
            notify_return_request_to_seller(
                db=db,
                seller_id=order_obj.seller_id,
                return_id=return_req.id,
                order_number=order_number,
                customer_name=current_user.name or "Khách hàng",
                return_type=return_type_val,
                reason=return_data.reason,
            )
            db.commit()
    except Exception as _e:
        logger.warning("[Return] Không gửi được notification yêu cầu trả hàng mới cho seller: %s", _e)

    return {
        "success": True,
        "message": "Yêu cầu đổi/trả đã được gửi. Seller sẽ xem xét trong 1-3 ngày làm việc.",
        "data": {
            "id": return_req.id,
            "order_id": return_req.order_id,
            "return_type": return_type_val,
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
                "images": _parse_images(r.images),
                "status": r.status.value if hasattr(r.status, "value") else r.status,
                "seller_note": r.seller_note,
                "seller_handled_at": r.seller_handled_at.isoformat() if r.seller_handled_at else None,
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
# ENDPOINTS – SELLER
# ==============================================================================

@router.get("/seller", summary="[Seller] Xem yêu cầu đổi/trả liên quan đến đơn hàng của mình")
async def get_seller_return_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    return_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller xem các yêu cầu đổi/trả liên quan đến đơn hàng do mình bán.
    Chỉ trả về những đơn hàng có seller_id = current_user.id.
    """
    if current_user.type not in ("seller", "producer", "admin"):
        raise HTTPException(status_code=403, detail="Chỉ seller mới có quyền truy cập endpoint này")

    # Lấy danh sách order_id của seller hiện tại
    seller_order_ids = [
        o.id for o in db.query(Order.id).filter(Order.seller_id == current_user.id).all()
    ]

    query = db.query(ReturnRequest).filter(ReturnRequest.order_id.in_(seller_order_ids))
    if status:
        query = query.filter(ReturnRequest.status == status)
    if return_type:
        query = query.filter(ReturnRequest.return_type == return_type)

    total = query.count()
    skip = (page - 1) * limit
    requests = query.order_by(ReturnRequest.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for r in requests:
        customer = db.query(User).filter(User.id == r.user_id).first()
        order = db.query(Order).filter(Order.id == r.order_id).first()
        result.append({
            "id": r.id,
            "order_id": r.order_id,
            "order_number": order.order_number if order else None,
            "customer_name": customer.name if customer else None,
            "return_type": r.return_type.value if hasattr(r.return_type, "value") else r.return_type,
            "reason": r.reason,
            "images": _parse_images(r.images),
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "seller_note": r.seller_note,
            "seller_handled_at": r.seller_handled_at.isoformat() if r.seller_handled_at else None,
            "admin_note": r.admin_note,
            "refund_amount": r.refund_amount,
            "created_at": r.created_at.isoformat(),
            "handled_at": r.handled_at.isoformat() if r.handled_at else None,
        })

    return {
        "success": True,
        "data": result,
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }


@router.put("/{return_id}/seller-approve", summary="[Seller] Chấp nhận yêu cầu đổi/trả")
async def seller_approve_return(
    return_id: int,
    handle_data: SellerHandleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller chấp nhận yêu cầu đổi/trả → trạng thái SELLER_APPROVED.
    Admin sẽ xác nhận nhận hàng và hoàn tiền/đổi hàng tiếp theo.
    """
    if current_user.type not in ("seller", "producer", "admin"):
        raise HTTPException(status_code=403, detail="Chỉ seller mới có quyền thực hiện thao tác này")

    req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")

    # Kiểm tra đơn hàng thuộc seller này
    if current_user.type != "admin":
        order = db.query(Order).filter(
            Order.id == req.order_id,
            Order.seller_id == current_user.id
        ).first()
        if not order:
            raise HTTPException(status_code=403, detail="Đơn hàng này không thuộc quyền quản lý của bạn")

    if req.status != ReturnStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ có thể xử lý yêu cầu ở trạng thái PENDING. Hiện tại: {req.status.value}"
        )

    req.status = ReturnStatus.SELLER_APPROVED
    req.seller_note = handle_data.note
    req.seller_handled_by = current_user.id
    req.seller_handled_at = datetime.utcnow()
    db.commit()

    # [NOTIFICATION R2] Thông báo buyer: seller đã chấp nhận
    try:
        return_type_val = req.return_type.value if hasattr(req.return_type, "value") else str(req.return_type)
        notify_return_seller_approved_to_buyer(
            db=db,
            buyer_id=req.user_id,
            return_id=return_id,
            return_type=return_type_val,
            note=handle_data.note,
        )
        db.commit()
    except Exception as _e:
        logger.warning("[Return] Không gửi được notification seller duyệt cho buyer: %s", _e)

    return {
        "success": True,
        "message": "Đã chấp nhận yêu cầu đổi/trả. Admin sẽ xác nhận nhận hàng và tiến hành hoàn tiền/đổi hàng.",
        "return_id": return_id,
        "status": "SELLER_APPROVED"
    }


@router.put("/{return_id}/seller-reject", summary="[Seller] Từ chối yêu cầu đổi/trả")
async def seller_reject_return(
    return_id: int,
    handle_data: SellerHandleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller từ chối yêu cầu đổi/trả → trạng thái SELLER_REJECTED.
    Yêu cầu sẽ được escalate lên Admin để xem xét lại.
    """
    if current_user.type not in ("seller", "producer", "admin"):
        raise HTTPException(status_code=403, detail="Chỉ seller mới có quyền thực hiện thao tác này")

    req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")

    if current_user.type != "admin":
        order = db.query(Order).filter(
            Order.id == req.order_id,
            Order.seller_id == current_user.id
        ).first()
        if not order:
            raise HTTPException(status_code=403, detail="Đơn hàng này không thuộc quyền quản lý của bạn")

    if req.status != ReturnStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ có thể xử lý yêu cầu ở trạng thái PENDING. Hiện tại: {req.status.value}"
        )

    req.status = ReturnStatus.SELLER_REJECTED
    req.seller_note = handle_data.note
    req.seller_handled_by = current_user.id
    req.seller_handled_at = datetime.utcnow()
    db.commit()

    # [NOTIFICATION R3-A] Thông báo buyer: seller từ chối, đang escalate Admin
    try:
        return_type_val = req.return_type.value if hasattr(req.return_type, "value") else str(req.return_type)
        notify_return_seller_rejected_to_buyer(
            db=db,
            buyer_id=req.user_id,
            return_id=return_id,
            return_type=return_type_val,
            note=handle_data.note,
        )
        db.commit()
    except Exception as _e:
        logger.warning("[Return] Không gửi được notification seller từ chối cho buyer: %s", _e)

    # [NOTIFICATION R3-B] Thông báo Admin: yêu cầu bị seller từ chối, cần xem xét
    try:
        order_obj = db.query(Order).filter(Order.id == req.order_id).first()
        order_number = order_obj.order_number if order_obj else str(req.order_id)
        buyer = db.query(User).filter(User.id == req.user_id).first()
        admin_ids = [u.id for u in db.query(User).filter(User.type == "admin").all()]
        if admin_ids:
            notify_return_escalated_to_admin(
                db=db,
                admin_user_ids=admin_ids,
                return_id=return_id,
                order_number=order_number,
                customer_name=buyer.name if buyer else "Khách hàng",
                seller_note=handle_data.note,
            )
            db.commit()
    except Exception as _e:
        logger.warning("[Return] Không gửi được notification escalate cho admin: %s", _e)

    return {
        "success": True,
        "message": "Đã từ chối yêu cầu. Hệ thống sẽ chuyển lên Admin để xem xét lại.",
        "return_id": return_id,
        "status": "SELLER_REJECTED"
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
        seller = db.query(User).filter(User.id == r.seller_handled_by).first() if r.seller_handled_by else None
        result.append({
            "id": r.id,
            "order_id": r.order_id,
            "order_number": order.order_number if order else None,
            "customer_name": user.name if user else None,
            "customer_email": user.email if user else None,
            "return_type": r.return_type.value if hasattr(r.return_type, "value") else r.return_type,
            "reason": r.reason,
            "images": _parse_images(r.images),
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "seller_note": r.seller_note,
            "seller_handled_by_name": seller.name if seller else None,
            "seller_handled_at": r.seller_handled_at.isoformat() if r.seller_handled_at else None,
            "admin_note": r.admin_note,
            "created_at": r.created_at.isoformat(),
            "handled_at": r.handled_at.isoformat() if r.handled_at else None
        })

    return {
        "success": True,
        "data": result,
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }


@router.put("/{return_id}/approve", summary="[Admin] Duyệt yêu cầu đổi/trả (override seller từ chối)")
async def approve_return_request(
    return_id: int,
    handle_data: AdminHandleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin duyệt yêu cầu đổi/trả → trạng thái APPROVED.
    Áp dụng khi: Seller đã từ chối (SELLER_REJECTED) và Admin muốn override để bảo vệ quyền lợi buyer.
    """
    _require_admin(current_user)

    req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")
    if req.status not in {ReturnStatus.SELLER_REJECTED, ReturnStatus.PENDING}:
        raise HTTPException(status_code=400, detail=f"Không thể duyệt yêu cầu ở trạng thái {req.status.value}")

    req.status = ReturnStatus.APPROVED
    req.admin_note = handle_data.note
    req.handled_by = current_user.id
    req.handled_at = datetime.utcnow()
    db.commit()

    # [NOTIFICATION R2] Thông báo Buyer: yêu cầu được duyệt
    try:
        return_type_val = req.return_type.value if hasattr(req.return_type, "value") else str(req.return_type)
        notify_return_approved_to_buyer(
            db=db,
            buyer_id=req.user_id,
            return_id=return_id,
            return_type=return_type_val,
            note=handle_data.note,
        )
        db.commit()
    except Exception as _e:
        logger.warning("[Return] Không gửi được notification duyệt trả hàng cho buyer: %s", _e)

    return {
        "success": True,
        "message": "Đã duyệt yêu cầu đổi/trả. Khách hàng sẽ được thông báo gửi hàng về.",
        "return_id": return_id,
        "status": "APPROVED"
    }


@router.put("/{return_id}/reject", summary="[Admin] Từ chối yêu cầu đổi/trả (quyết định cuối cùng)")
async def reject_return_request(
    return_id: int,
    handle_data: AdminHandleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin từ chối yêu cầu đổi/trả → trạng thái REJECTED (cuối cùng).
    Áp dụng khi Seller đã từ chối (SELLER_REJECTED) và Admin đồng ý với quyết định của Seller.
    """
    _require_admin(current_user)

    req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Yêu cầu không tồn tại")
    if req.status not in {ReturnStatus.SELLER_REJECTED, ReturnStatus.PENDING, ReturnStatus.APPROVED}:
        raise HTTPException(status_code=400, detail=f"Không thể từ chối yêu cầu ở trạng thái {req.status.value}")

    req.status = ReturnStatus.REJECTED
    req.admin_note = handle_data.note
    req.handled_by = current_user.id
    req.handled_at = datetime.utcnow()
    db.commit()

    # [NOTIFICATION R3] Thông báo Buyer: yêu cầu bị từ chối
    try:
        return_type_val = req.return_type.value if hasattr(req.return_type, "value") else str(req.return_type)
        notify_return_rejected_to_buyer(
            db=db,
            buyer_id=req.user_id,
            return_id=return_id,
            return_type=return_type_val,
            note=handle_data.note,
        )
        db.commit()
    except Exception as _e:
        logger.warning("[Return] Không gửi được notification từ chối trả hàng cho buyer: %s", _e)

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
    if req.status not in {ReturnStatus.APPROVED, ReturnStatus.SELLER_APPROVED}:
        raise HTTPException(
            status_code=400,
            detail="Yêu cầu phải ở trạng thái APPROVED hoặc SELLER_APPROVED trước"
        )

    req.status = ReturnStatus.RECEIVED
    req.handled_at = datetime.utcnow()
    db.commit()

    # [NOTIFICATION R4] Thông báo Buyer: hệ thống đã nhận hàng trả về
    try:
        return_type_val = req.return_type.value if hasattr(req.return_type, "value") else str(req.return_type)
        notify_return_received_to_buyer(
            db=db,
            buyer_id=req.user_id,
            return_id=return_id,
            return_type=return_type_val,
        )
        db.commit()
    except Exception as _e:
        logger.warning("[Return] Không gửi được notification nhận hàng trả cho buyer: %s", _e)

    return {
        "success": True,
        "message": "Đã nhận hàng trả về. Tiến hành hoàn tiền hoặc gửi hàng đổi.",
        "return_id": return_id,
        "status": "RECEIVED"
    }

