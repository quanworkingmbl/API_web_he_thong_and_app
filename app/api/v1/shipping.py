"""
Shipping API – Tích hợp đơn vị vận chuyển (GHN)

Endpoints:
- POST /shipping/fee          – Tính phí vận chuyển
- POST /shipping/create       – Tạo vận đơn GHN
- GET  /shipping/{id}/track   – Tra cứu trạng thái vận đơn
- GET  /shipping/order/{oid}  – Xem thông tin vận đơn theo order_id
- POST /shipping/webhook      – GHN webhook callback
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.models.shipment import Shipment, ShipmentStatus, ShippingProvider
from app.models.order import Order, OrderStatus
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.ghn import ghn_service
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class FeeCalculationRequest(BaseModel):
    to_district_id: int = Field(..., description="Mã quận/huyện người nhận (GHN ID)")
    to_ward_code: str = Field(..., description="Mã phường/xã người nhận")
    weight: int = Field(default=500, ge=1, description="Trọng lượng (gram)")
    from_district_id: int = Field(default=1454, description="Mã quận/huyện người gửi")


class CreateShipmentRequest(BaseModel):
    order_id: int
    weight: int = Field(default=500, ge=1, description="Trọng lượng gói hàng (gram)")
    to_district_id: int = Field(..., description="Mã quận/huyện GHN")
    to_ward_code: str = Field(..., description="Mã phường/xã GHN")
    from_district_id: int = Field(default=1454)
    note: Optional[str] = None


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.post("/fee", summary="Tính phí vận chuyển GHN")
async def calculate_shipping_fee(
    fee_data: FeeCalculationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Tính phí vận chuyển theo địa chỉ nhận, địa chỉ gửi và trọng lượng.
    Sử dụng GHN API – nếu chưa config sẽ trả về phí mặc định 30.000 VND.
    """
    result = await ghn_service.calculate_fee(
        to_district_id=fee_data.to_district_id,
        to_ward_code=fee_data.to_ward_code,
        weight=fee_data.weight,
        from_district_id=fee_data.from_district_id
    )
    if not result.get("success"):
        return {
            "success": False,
            "fee": 30000,
            "message": result.get("error", "Lỗi tính phí, dùng phí mặc định")
        }

    return {
        "success": True,
        "data": {
            "fee": result.get("fee", 30000),
            "expected_delivery_time": result.get("expected_delivery_time"),
            "service_id": result.get("service_id")
        }
    }


@router.post("/create", summary="Tạo vận đơn GHN")
async def create_shipment(
    shipment_data: CreateShipmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo vận đơn tại GHN cho đơn hàng.
    Seller hoặc Admin mới có quyền tạo vận đơn.
    """
    # Kiểm tra đơn hàng
    order = db.query(Order).filter(Order.id == shipment_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    # Phân quyền: chỉ seller sở hữu đơn hoặc admin
    if current_user.type not in {"admin"} and order.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền tạo vận đơn cho đơn hàng này")

    # Kiểm tra đã có vận đơn chưa
    existing = db.query(Shipment).filter(Shipment.order_id == order.id).first()
    if existing and existing.status != ShipmentStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Đã có vận đơn cho đơn hàng này (status: {existing.status.value})"
        )

    # Chuẩn bị data GHN
    ghn_order_data = {
        "service_type_id": 2,
        "to_name": order.customer_name,
        "to_phone": order.customer_phone,
        "to_address": order.shipping_address,
        "to_ward_code": shipment_data.to_ward_code,
        "to_district_id": shipment_data.to_district_id,
        "from_district_id": shipment_data.from_district_id,
        "weight": shipment_data.weight,
        "payment_type_id": 2 if order.payment_method.value == "COD" else 1,  # 2=COD, 1=Prepaid
        "cod_amount": int(order.total_amount) if order.payment_method.value == "COD" else 0,
        "note": shipment_data.note or "",
        "required_note": "CHOXEMHANGKHONGTHU"
    }

    # Gọi GHN API
    ghn_result = await ghn_service.create_order(ghn_order_data)

    # Tạo hoặc update Shipment record
    if existing:
        shipment = existing
    else:
        shipment = Shipment(order_id=order.id)
        db.add(shipment)

    shipment.provider = ShippingProvider.GHN
    shipment.weight = shipment_data.weight
    shipment.fee = Decimal(str(ghn_result.get("fee", 30000)))
    shipment.note = shipment_data.note
    shipment.to_address = order.shipping_address
    shipment.status = ShipmentStatus.CREATED

    if ghn_result.get("success"):
        shipment.provider_order_code = ghn_result.get("order_code")
        shipment.tracking_code = ghn_result.get("order_code")

    db.commit()
    db.refresh(shipment)

    # Cập nhật order status sang SHIPPING
    order.status = OrderStatus.SHIPPING
    order.shipped_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Đã tạo vận đơn thành công",
        "data": {
            "shipment_id": shipment.id,
            "order_id": order.id,
            "tracking_code": shipment.tracking_code,
            "provider": "GHN",
            "fee": str(shipment.fee),
            "status": shipment.status.value,
            "ghn_mock": not ghn_result.get("success", True)
        }
    }


@router.get("/{shipment_id}/track", summary="Tra cứu trạng thái vận đơn")
async def track_shipment(
    shipment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tra cứu trạng thái vận chuyển chi tiết theo shipment ID."""
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Vận đơn không tồn tại")

    tracking_data = {}
    if shipment.tracking_code:
        tracking_data = await ghn_service.get_tracking(shipment.tracking_code)

    return {
        "success": True,
        "data": {
            "shipment_id": shipment.id,
            "order_id": shipment.order_id,
            "provider": shipment.provider.value if hasattr(shipment.provider, "value") else str(shipment.provider),
            "tracking_code": shipment.tracking_code,
            "status": shipment.status.value if hasattr(shipment.status, "value") else str(shipment.status),
            "fee": str(shipment.fee),
            "estimated_delivery": shipment.estimated_delivery.isoformat() if shipment.estimated_delivery else None,
            "actual_delivery": shipment.actual_delivery.isoformat() if shipment.actual_delivery else None,
            "tracking": tracking_data
        }
    }


@router.get("/order/{order_id}", summary="Xem vận đơn theo order_id")
async def get_shipment_by_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin vận đơn theo mã đơn hàng."""
    shipment = db.query(Shipment).filter(Shipment.order_id == order_id).first()
    if not shipment:
        return {
            "success": True,
            "data": None,
            "message": "Chưa có vận đơn cho đơn hàng này"
        }

    return {
        "success": True,
        "data": {
            "shipment_id": shipment.id,
            "order_id": shipment.order_id,
            "provider": shipment.provider.value if hasattr(shipment.provider, "value") else str(shipment.provider),
            "tracking_code": shipment.tracking_code,
            "status": shipment.status.value if hasattr(shipment.status, "value") else str(shipment.status),
            "fee": str(shipment.fee),
            "weight": shipment.weight,
            "note": shipment.note,
            "created_at": shipment.created_at.isoformat() if shipment.created_at else None
        }
    }


@router.post("/webhook", summary="GHN Webhook – cập nhật trạng thái vận đơn")
async def ghn_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    GHN gọi webhook này khi trạng thái vận đơn thay đổi.
    Tự động cập nhật Shipment.status và Order.status.
    """
    try:
        body = await request.json()
    except Exception:
        return {"success": False, "message": "Invalid JSON body"}

    order_code = body.get("OrderCode") or body.get("order_code")
    ghn_status = body.get("Status") or body.get("status", "")

    if not order_code:
        return {"success": False, "message": "Missing OrderCode"}

    # Tìm shipment theo provider_order_code
    shipment = db.query(Shipment).filter(
        Shipment.provider_order_code == order_code
    ).first()

    if not shipment:
        return {"success": False, "message": "Shipment not found"}

    # Map GHN status sang ShipmentStatus local
    status_map = {
        "ready_to_pick": ShipmentStatus.CREATED,
        "picking": ShipmentStatus.PICKED_UP,
        "picked": ShipmentStatus.PICKED_UP,
        "delivering": ShipmentStatus.IN_TRANSIT,
        "delivered": ShipmentStatus.DELIVERED,
        "delivery_fail": ShipmentStatus.FAILED,
        "return": ShipmentStatus.RETURNED,
        "returned": ShipmentStatus.RETURNED,
        "cancle": ShipmentStatus.FAILED,  # GHN typo
    }

    new_status = status_map.get(ghn_status.lower(), ShipmentStatus.IN_TRANSIT)
    shipment.status = new_status

    # Cập nhật Order tương ứng
    order = db.query(Order).filter(Order.id == shipment.order_id).first()
    if order:
        if new_status == ShipmentStatus.DELIVERED:
            order.status = OrderStatus.DELIVERED
            order.delivered_at = datetime.utcnow()
            order.payment_status = "PAID"
            shipment.actual_delivery = datetime.utcnow()
        elif new_status == ShipmentStatus.RETURNED:
            order.status = OrderStatus.REFUNDED
        elif new_status in {ShipmentStatus.IN_TRANSIT, ShipmentStatus.PICKED_UP}:
            order.status = OrderStatus.SHIPPING

    db.commit()

    return {"success": True, "message": f"Updated shipment to {new_status.value}"}
