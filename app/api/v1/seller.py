"""
Seller API – Dành riêng cho người bán (producer/seller)

Endpoints:
- GET  /seller/dashboard              – Thống kê tổng quan (đơn, doanh thu, sản phẩm)
- GET  /seller/orders                 – Danh sách đơn hàng của seller
- PUT  /seller/orders/{id}/confirm    – Xác nhận đơn → CONFIRMED
- PUT  /seller/orders/{id}/reject     – Từ chối đơn   → CANCELLED
- PUT  /seller/orders/{id}/ship       – Chuyển sang Đang giao hàng → SHIPPING
- GET  /seller/products               – Danh sách sản phẩm của seller
- POST /seller/products               – Tạo sản phẩm mới (auto producer_id)
- PUT  /seller/products/{id}          – Chỉnh sửa sản phẩm đầy đủ (ownership check)
- DELETE /seller/products/{id}        – Xóa sản phẩm (ownership check)
- PUT  /seller/products/{id}/stock    – Cập nhật tồn kho nhanh
- GET  /seller/profile                – Thông tin shop / profile
- PUT  /seller/profile                – Cập nhật thông tin cá nhân
- GET  /seller/posts                  – Danh sách bài đăng
- POST /seller/posts                  – Tạo bài đăng
- PUT  /seller/posts/{id}             – Cập nhật bài đăng
- DELETE /seller/posts/{id}           – Xóa bài đăng
- GET  /seller/contracts              – Danh sách hợp đồng QC
- POST /seller/contracts              – Tạo hợp đồng QC
- PUT  /seller/contracts/{id}         – Cập nhật hợp đồng QC
- DELETE /seller/contracts/{id}       – Xóa hợp đồng QC
- GET  /seller/returns                – Xem yêu cầu đổi trả thuộc đơn của seller
- PUT  /seller/returns/{id}           – Cập nhật yêu cầu đổi trả
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from app.core.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product, ProductStatus
from app.models.traceability import ProductOrigin, OriginStatus
from app.models.content import Content, ContentStatus
from app.models.partner_contract import PartnerContract, ContractStatus
from app.models.return_request import ReturnRequest, ReturnStatus
from app.models.category import Category
from app.models.region import Region
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.core.permissions import check_seller_kyc_verified
from app.services.order_state import log_status_change
from app.services.inventory import increment_stock
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# PERMISSION HELPER
# ==============================================================================

def _require_seller(current_user: User):
    """Chặn truy cập nếu không phải seller / producer / admin."""
    allowed_types = {"producer", "seller", "admin"}
    if current_user.type not in allowed_types:
        raise HTTPException(status_code=403, detail="Chỉ người bán mới có quyền truy cập")
    return current_user


def _to_vnd_int(value: Optional[Decimal]) -> Optional[int]:
    """Chuẩn hóa tiền về số nguyên VND để API trả dạng số."""
    if value is None:
        return None
    decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    return int(decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _validate_origin_payload(origin_data: dict, db: Session):
    production_date = origin_data.get("production_date")
    expiry_date = origin_data.get("expiry_date")
    if production_date and expiry_date and expiry_date < production_date:
        raise HTTPException(status_code=400, detail="Hạn sử dụng phải lớn hơn hoặc bằng ngày sản xuất")

    region_id = origin_data.get("region_id")
    if region_id is not None:
        region = db.query(Region).filter(Region.id == region_id).first()
        if not region:
            raise HTTPException(status_code=400, detail="Vùng miền không tồn tại")


# ==============================================================================
# SCHEMAS
# ==============================================================================

class StockUpdateRequest(BaseModel):
    stock_quantity: int = Field(..., ge=0)


class RejectOrderRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)


class CreateSellerOriginRequest(BaseModel):
    village_name: str = Field(..., min_length=2, max_length=255)
    region_id: Optional[int] = None
    producer_name: str = Field(..., min_length=2, max_length=255)
    batch_number: str = Field(..., min_length=1, max_length=100)
    production_date: date
    expiry_date: Optional[date] = None
    ingredients: str = Field(..., min_length=2)
    process_summary: str = Field(..., min_length=10)


class UpdateSellerOriginRequest(BaseModel):
    village_name: Optional[str] = Field(None, min_length=2, max_length=255)
    region_id: Optional[int] = None
    producer_name: Optional[str] = Field(None, min_length=2, max_length=255)
    batch_number: Optional[str] = Field(None, min_length=1, max_length=100)
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    ingredients: Optional[str] = Field(None, min_length=2)
    process_summary: Optional[str] = Field(None, min_length=10)


class CreateSellerProductRequest(BaseModel):
    """Schema tạo sản phẩm mới – dùng tại Web Seller Portal"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    label: Optional[str] = Field(None, pattern="^(CLEAN_AGRICULTURE|TRADITIONAL_CRAFT|OCOP)$")
    images: Optional[str] = None   # JSON array of image URLs
    stock_quantity: int = Field(default=0, ge=0)
    origin: CreateSellerOriginRequest


class UpdateSellerProductRequest(BaseModel):
    """Schema chỉnh sửa sản phẩm – dùng tại Web Seller Portal"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    label: Optional[str] = Field(None, pattern="^(CLEAN_AGRICULTURE|TRADITIONAL_CRAFT|OCOP)$")
    images: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    origin: Optional[UpdateSellerOriginRequest] = None


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("/dashboard", summary="Thống kê tổng quan của seller")
async def get_seller_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard dành cho người bán:
    - Tổng đơn hàng
    - Đơn theo trạng thái
    - Doanh thu (đơn đã giao)
    - Tổng sản phẩm
    """
    _require_seller(current_user)
    seller_id = current_user.id

    # Thống kê đơn hàng
    total_orders = db.query(Order).filter(Order.seller_id == seller_id).count()

    orders_by_status = {}
    for status in OrderStatus:
        cnt = db.query(Order).filter(
            Order.seller_id == seller_id,
            Order.status == status
        ).count()
        orders_by_status[status.value.lower()] = cnt

    # Doanh thu (đơn DELIVERED)
    delivered_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.status == OrderStatus.DELIVERED
    ).all()
    total_revenue = sum(o.seller_amount for o in delivered_orders)
    total_platform_fee = sum(o.platform_fee_amount for o in delivered_orders)

    # Thống kê 30 ngày gần nhất
    last_30_days = datetime.utcnow() - timedelta(days=30)
    recent_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.created_at >= last_30_days
    ).count()
    recent_revenue_orders = db.query(Order).filter(
        Order.seller_id == seller_id,
        Order.status == OrderStatus.DELIVERED,
        Order.created_at >= last_30_days
    ).all()
    recent_revenue = sum(o.seller_amount for o in recent_revenue_orders)

    # Sản phẩm
    total_products = db.query(Product).filter(Product.producer_id == seller_id).count()
    approved_products = db.query(Product).filter(
        Product.producer_id == seller_id,
        Product.status == ProductStatus.APPROVED
    ).count()
    low_stock_products = db.query(Product).filter(
        Product.producer_id == seller_id,
        Product.stock_quantity < 5
    ).count()

    return {
        "success": True,
        "data": {
            "seller": {
                "id": current_user.id,
                "name": current_user.name,
                "type": current_user.type
            },
            "orders": {
                "total": total_orders,
                "last_30_days": recent_orders,
                "by_status": orders_by_status
            },
            "revenue": {
                "total_seller_amount": _to_vnd_int(total_revenue),
                "total_platform_fee": _to_vnd_int(total_platform_fee),
                "last_30_days": _to_vnd_int(recent_revenue)
            },
            "products": {
                "total": total_products,
                "approved": approved_products,
                "low_stock": low_stock_products
            }
        }
    }


@router.get("/orders", summary="Danh sách đơn hàng của seller")
async def get_seller_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter theo trạng thái"),
    search: Optional[str] = Query(None, description="Tìm theo mã đơn hàng"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách đơn hàng của seller đang đăng nhập."""
    _require_seller(current_user)

    query = db.query(Order).filter(Order.seller_id == current_user.id)

    if status:
        query = query.filter(Order.status == status)
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))

    total = query.count()
    skip = (page - 1) * limit
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    order_list = []
    for o in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        order_list.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "shipping_address": o.shipping_address,
            "total_amount": _to_vnd_int(o.total_amount),
            "seller_amount": _to_vnd_int(o.seller_amount),
            "platform_fee_amount": _to_vnd_int(o.platform_fee_amount),
            "status": o.status.value if hasattr(o.status, "value") else str(o.status),
            "payment_method": o.payment_method.value if hasattr(o.payment_method, "value") else str(o.payment_method),
            "payment_status": o.payment_status,
            "item_count": len(items),
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": _to_vnd_int(item.unit_price),
                    "total_price": _to_vnd_int(item.total_price)
                }
                for item in items
            ],
            "created_at": o.created_at.isoformat()
        })

    return {
        "success": True,
        "data": order_list,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.put("/orders/{order_id}/confirm", summary="Xác nhận đơn hàng")
async def confirm_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller xác nhận đơn hàng → chuyển sang CONFIRMED.
    Chỉ được xác nhận khi đơn đang ở trạng thái PENDING.
    """
    _require_seller(current_user)

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.seller_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể xác nhận đơn hàng đang ở trạng thái {order.status.value}"
        )

    # Tồn kho đã trừ khi khách đặt hàng (checkout). Xác nhận đơn không trừ thêm để tránh double-deduct.

    order.status = OrderStatus.CONFIRMED
    order.confirmed_at = datetime.utcnow()

    # [AUDIT] Ghi log xác nhận đơn
    log_status_change(
        db=db,
        order_id=order_id,
        old_status=OrderStatus.PENDING.value,
        new_status=OrderStatus.CONFIRMED.value,
        actor_id=current_user.id,
        role="seller",
        note="Seller xác nhận đơn hàng",
        auto_flush=True,
    )

    db.commit()

    return {
        "success": True,
        "message": "Đã xác nhận đơn hàng",
        "order_id": order_id,
        "status": "CONFIRMED"
    }


@router.put("/orders/{order_id}/reject", summary="Từ chối / hủy đơn hàng")
async def reject_order(
    order_id: int,
    reject_data: RejectOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller từ chối đơn hàng → chuyển sang CANCELLED.
    Chỉ được từ chối khi đơn đang ở PENDING hoặc CONFIRMED.
    """
    _require_seller(current_user)

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.seller_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    cancellable_statuses = {OrderStatus.PENDING, OrderStatus.CONFIRMED}
    if order.status not in cancellable_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể hủy đơn hàng đang ở trạng thái {order.status.value}"
        )

    # Hoàn tồn: đã trừ khi đặt hàng — hoàn khi hủy từ PENDING hoặc CONFIRMED
    old_cancel_status = order.status.value if hasattr(order.status, "value") else str(order.status)

    if order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                increment_stock(db, product, item.quantity, item.variant_id)

    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()
    order.cancel_reason = reject_data.reason

    # [AUDIT] Ghi log hủy đơn
    log_status_change(
        db=db,
        order_id=order_id,
        old_status=old_cancel_status,
        new_status=OrderStatus.CANCELLED.value,
        actor_id=current_user.id,
        role="seller",
        note=f"Seller từ chối đơn: {reject_data.reason}",
        auto_flush=True,
    )

    db.commit()

    return {
        "success": True,
        "message": "Đã hủy đơn hàng",
        "order_id": order_id,
        "reason": reject_data.reason
    }


@router.put("/orders/{order_id}/ship", summary="Chuyển đơn sang Đang giao hàng")
async def mark_order_shipping(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller đánh dấu đơn hàng đã giao cho đơn vị vận chuyển."""
    _require_seller(current_user)

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.seller_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    if order.status not in {OrderStatus.CONFIRMED, OrderStatus.PROCESSING}:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển sang giao hàng từ trạng thái {order.status.value}"
        )

    old_ship_status = order.status.value if hasattr(order.status, "value") else str(order.status)

    order.status = OrderStatus.SHIPPING
    order.shipped_at = datetime.utcnow()

    # [AUDIT] Ghi log chuyển sang shipping
    log_status_change(
        db=db,
        order_id=order_id,
        old_status=old_ship_status,
        new_status=OrderStatus.SHIPPING.value,
        actor_id=current_user.id,
        role="seller",
        note="Seller chuyển sang đang giao hàng",
        auto_flush=True,
    )

    db.commit()

    return {
        "success": True,
        "message": "Đã chuyển đơn sang trạng thái Đang giao hàng",
        "order_id": order_id,
        "status": "SHIPPING"
    }


@router.get("/products", summary="Sản phẩm của seller")
async def get_seller_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo tên sản phẩm"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách sản phẩm của seller đang đăng nhập."""
    _require_seller(current_user)

    query = db.query(Product).filter(Product.producer_id == current_user.id)
    if status:
        query = query.filter(Product.status == status)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()
    skip = (page - 1) * limit
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "price": _to_vnd_int(p.price),
                "stock_quantity": p.stock_quantity,
                "is_active": p.is_active,
                "label": p.label,
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                "images": p.images,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in products
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.post("/products", summary="Seller tạo sản phẩm mới (Web)")
async def create_seller_product(
    product_data: CreateSellerProductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller tạo sản phẩm mới từ Web Seller Portal.
    - `producer_id` tự động gán = `current_user.id` (không nhập tay).
    - Sản phẩm tạo xong ở trạng thái **PENDING** chờ Admin duyệt.
    """
    _require_seller(current_user)
    check_seller_kyc_verified(current_user, db)

    origin_data = product_data.origin.dict()
    _validate_origin_payload(origin_data, db)

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        producer_id=current_user.id,          # ← auto gán, không để client truyền
        status=ProductStatus.PENDING,
        label=product_data.label,
        images=product_data.images,
        stock_quantity=product_data.stock_quantity,
        is_active=True,
    )
    db.add(new_product)
    db.flush()

    origin = ProductOrigin(
        product_id=new_product.id,
        village_name=origin_data.get("village_name"),
        region_id=origin_data.get("region_id"),
        producer_name=origin_data.get("producer_name"),
        batch_number=origin_data.get("batch_number"),
        production_date=origin_data.get("production_date"),
        expiry_date=origin_data.get("expiry_date"),
        ingredients=origin_data.get("ingredients"),
        process_summary=origin_data.get("process_summary"),
        verification_status=OriginStatus.PENDING,
    )
    db.add(origin)

    db.commit()
    db.refresh(new_product)
    db.refresh(origin)

    return {
        "success": True,
        "message": "Sản phẩm đã được tạo. Chờ Admin duyệt sản phẩm và nguồn gốc.",
        "data": {
            "id": new_product.id,
            "name": new_product.name,
            "price": _to_vnd_int(new_product.price),
            "stock_quantity": new_product.stock_quantity,
            "label": new_product.label,
            "status": "PENDING",
            "origin_status": origin.verification_status.value if hasattr(origin.verification_status, "value") else str(origin.verification_status),
            "images": new_product.images,
            "created_at": new_product.created_at.isoformat() if new_product.created_at else None,
        },
    }


@router.put("/products/{product_id}", summary="Seller chỉnh sửa sản phẩm (Web)")
async def update_seller_product(
    product_id: int,
    product_data: UpdateSellerProductRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller chỉnh sửa thông tin đầy đủ sản phẩm của mình từ Web Seller Portal.
    - Chỉ được sửa sản phẩm của **chính mình** (ownership check).
    - Sau khi sửa nội dung (name/description/price/images), trạng thái reset về **PENDING** để Admin duyệt lại.
    - Chỉ cập nhật stock/is_active sẽ KHÔNG reset trạng thái.
    """
    _require_seller(current_user)

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == current_user.id   # ← ownership check
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Sản phẩm không tồn tại hoặc bạn không có quyền chỉnh sửa"
        )

    update_data = product_data.dict(exclude_unset=True)
    origin_input = update_data.pop("origin", None)
    origin_changed = False
    origin_record = db.query(ProductOrigin).filter(ProductOrigin.product_id == product.id).first()

    # Các field nội dung khi thay đổi cần duyệt lại
    content_fields = {"name", "description", "price", "images", "label"}
    needs_reapproval = bool(content_fields & update_data.keys())

    for key, value in update_data.items():
        setattr(product, key, value)

    if origin_input is not None:
        origin_data = {k: v for k, v in origin_input.items() if v is not None}

        existing_values = {}
        if origin_record:
            existing_values = {
                "village_name": origin_record.village_name,
                "region_id": origin_record.region_id,
                "producer_name": origin_record.producer_name,
                "batch_number": origin_record.batch_number,
                "production_date": origin_record.production_date,
                "expiry_date": origin_record.expiry_date,
                "ingredients": origin_record.ingredients,
                "process_summary": origin_record.process_summary,
            }

        merged_origin = {**existing_values, **origin_data}

        required_origin_fields = [
            "village_name",
            "producer_name",
            "batch_number",
            "production_date",
            "ingredients",
            "process_summary",
        ]
        missing_fields = [field for field in required_origin_fields if not merged_origin.get(field)]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Thiếu trường nguồn gốc bắt buộc: {', '.join(missing_fields)}",
            )

        _validate_origin_payload(merged_origin, db)

        if origin_record:
            for key, value in merged_origin.items():
                setattr(origin_record, key, value)
        else:
            origin_record = ProductOrigin(
                product_id=product.id,
                village_name=merged_origin.get("village_name"),
                region_id=merged_origin.get("region_id"),
                producer_name=merged_origin.get("producer_name"),
                batch_number=merged_origin.get("batch_number"),
                production_date=merged_origin.get("production_date"),
                expiry_date=merged_origin.get("expiry_date"),
                ingredients=merged_origin.get("ingredients"),
                process_summary=merged_origin.get("process_summary"),
            )
            db.add(origin_record)

        origin_record.verification_status = OriginStatus.PENDING
        origin_record.verified_by = None
        origin_record.verified_at = None
        origin_record.rejection_reason = None
        origin_changed = True

    if needs_reapproval:
        product.status = ProductStatus.PENDING

    db.commit()
    db.refresh(product)
    if origin_record:
        db.refresh(origin_record)

    return {
        "success": True,
        "message": "Đã cập nhật sản phẩm."
        + (" Chờ Admin duyệt lại." if needs_reapproval else "")
        + (" Nguồn gốc đang chờ duyệt lại." if origin_changed else ""),
        "data": {
            "id": product.id,
            "name": product.name,
            "price": _to_vnd_int(product.price),
            "stock_quantity": product.stock_quantity,
            "is_active": product.is_active,
            "label": product.label,
            "status": product.status.value if hasattr(product.status, "value") else str(product.status),
            "origin_status": (
                origin_record.verification_status.value
                if origin_record and hasattr(origin_record.verification_status, "value")
                else (str(origin_record.verification_status) if origin_record else None)
            ),
            "images": product.images,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        },
    }


@router.put("/products/{product_id}/stock", summary="Cập nhật tồn kho sản phẩm")
async def update_product_stock(
    product_id: int,
    stock_data: StockUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller cập nhật số lượng tồn kho của sản phẩm."""
    _require_seller(current_user)

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại hoặc không có quyền")

    old_qty = product.stock_quantity
    product.stock_quantity = stock_data.stock_quantity
    db.commit()

    return {
        "success": True,
        "message": f"Đã cập nhật tồn kho từ {old_qty} → {stock_data.stock_quantity}",
        "product_id": product_id,
        "stock_quantity": stock_data.stock_quantity
    }


@router.get("/profile", summary="Thông tin shop/profile của seller")
async def get_seller_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Thông tin profile của seller."""
    _require_seller(current_user)

    total_products = db.query(Product).filter(Product.producer_id == current_user.id).count()
    approved_products = db.query(Product).filter(
        Product.producer_id == current_user.id,
        Product.status == ProductStatus.APPROVED
    ).count()
    total_orders = db.query(Order).filter(Order.seller_id == current_user.id).count()

    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "type": current_user.type,
            "gender": current_user.gender,
            "activated": current_user.activated,
            "stats": {
                "total_products": total_products,
                "approved_products": approved_products,
                "total_orders": total_orders
            },
            "member_since": current_user.created_at.isoformat() if current_user.created_at else None
        }
    }


# ==============================================================================
# DELETE PRODUCT
# ==============================================================================

@router.delete("/products/{product_id}", summary="Seller ẩn sản phẩm (soft-delete)")
async def delete_seller_product(
    product_id: int,
    reason: Optional[str] = Query(None, description="Lý do ẩn sản phẩm"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller ẩn sản phẩm (soft-delete: is_active=False).
    - Không xóa vĩnh viễn để giữ lịch sử đơn hàng.
    - Chặn ẩn nếu sản phẩm còn trong đơn hàng đang hoạt động (PENDING/CONFIRMED/PROCESSING/SHIPPING).
    """
    _require_seller(current_user)

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại hoặc không có quyền xóa")

    if not product.is_active:
        raise HTTPException(status_code=400, detail="Sản phẩm đã được ẩn trước đó")

    # Kiểm tra đơn hàng đang active liên quan đến sản phẩm này
    ACTIVE_ORDER_STATUSES = [
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PROCESSING,
        OrderStatus.SHIPPING,
    ]
    active_order_count = (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            OrderItem.product_id == product_id,
            Order.status.in_(ACTIVE_ORDER_STATUSES),
            Order.is_active == True,
        )
        .count()
    )
    if active_order_count > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Không thể ẩn sản phẩm vì còn {active_order_count} đơn hàng đang xử lý "
                f"(PENDING/CONFIRMED/PROCESSING/SHIPPING). Hãy đợi đơn hoàn tất."
            )
        )

    # [SOFT DELETE] Ẩn sản phẩm thay vì xóa
    product.is_active = False
    db.commit()

    return {"success": True, "message": "Sản phẩm đã được ẩn. Dữ liệu lịch sử được giữ lại."}


# ==============================================================================
# UPDATE PROFILE
# ==============================================================================

class UpdateSellerProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    gender: Optional[str] = None


@router.put("/profile", summary="Seller cập nhật thông tin cá nhân")
async def update_seller_profile(
    profile_data: UpdateSellerProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller cập nhật thông tin cá nhân."""
    _require_seller(current_user)

    update_data = profile_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Đã cập nhật thông tin cá nhân",
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "gender": current_user.gender,
        }
    }


# ==============================================================================
# SELLER POSTS (Bài đăng)
# ==============================================================================

class CreateSellerPostRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: Optional[str] = None
    content_type: str = Field(default="POST", pattern="^(POST|PRODUCT_DESCRIPTION|NEWS|ANNOUNCEMENT)$")
    product_id: Optional[int] = None
    images: Optional[str] = None
    videos: Optional[str] = None


class UpdateSellerPostRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = None
    content_type: Optional[str] = None
    images: Optional[str] = None
    videos: Optional[str] = None


@router.get("/posts", summary="Danh sách bài đăng của seller")
async def get_seller_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo tiêu đề"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách bài đăng của seller đang đăng nhập."""
    _require_seller(current_user)

    query = db.query(Content).filter(Content.author_id == current_user.id)
    if status:
        query = query.filter(Content.status == status)
    if search:
        query = query.filter(Content.title.ilike(f"%{search}%"))

    total = query.count()
    skip = (page - 1) * limit
    posts = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "title": p.title,
                "content": p.content,
                "content_type": p.content_type,
                "product_id": p.product_id,
                "status": p.status.value if hasattr(p.status, 'value') else str(p.status),
                "images": p.images,
                "videos": p.videos,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in posts
        ],
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }


@router.post("/posts", summary="Seller tạo bài đăng mới")
async def create_seller_post(
    post_data: CreateSellerPostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller tạo bài đăng mới. Bài đăng ở trạng thái PENDING chờ Admin duyệt."""
    _require_seller(current_user)
    check_seller_kyc_verified(current_user, db)

    new_post = Content(
        title=post_data.title,
        content=post_data.content,
        content_type=post_data.content_type,
        author_id=current_user.id,
        product_id=post_data.product_id,
        status=ContentStatus.PENDING,
        images=post_data.images,
        videos=post_data.videos,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "success": True,
        "message": "Bài đăng đã được tạo. Chờ Admin duyệt.",
        "data": {
            "id": new_post.id,
            "title": new_post.title,
            "status": "PENDING",
            "created_at": new_post.created_at.isoformat() if new_post.created_at else None,
        }
    }


@router.put("/posts/{post_id}", summary="Seller cập nhật bài đăng")
async def update_seller_post(
    post_id: int,
    post_data: UpdateSellerPostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller cập nhật bài đăng của mình. Reset trạng thái về PENDING nếu sửa nội dung."""
    _require_seller(current_user)

    post = db.query(Content).filter(
        Content.id == post_id,
        Content.author_id == current_user.id
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Bài đăng không tồn tại hoặc không có quyền chỉnh sửa")

    update_data = post_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    # Reset trạng thái về PENDING khi sửa nội dung
    content_fields = {"title", "content", "images", "videos"}
    if content_fields & update_data.keys():
        post.status = ContentStatus.PENDING

    db.commit()
    db.refresh(post)

    return {
        "success": True,
        "message": "Đã cập nhật bài đăng",
        "data": {
            "id": post.id,
            "title": post.title,
            "status": post.status.value if hasattr(post.status, 'value') else str(post.status),
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        }
    }


@router.delete("/posts/{post_id}", summary="Seller xóa bài đăng")
async def delete_seller_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller xóa bài đăng của mình."""
    _require_seller(current_user)

    post = db.query(Content).filter(
        Content.id == post_id,
        Content.author_id == current_user.id
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Bài đăng không tồn tại hoặc không có quyền xóa")

    db.delete(post)
    db.commit()

    return {"success": True, "message": "Đã xóa bài đăng"}


# ==============================================================================
# SELLER CONTRACTS (Hợp đồng quảng cáo)
# ==============================================================================

class CreateSellerContractRequest(BaseModel):
    contract_number: str = Field(..., min_length=2, max_length=50)
    contract_type: str = Field(default="ADVERTISING", pattern="^(ADVERTISING|PARTNERSHIP|DISTRIBUTION|OTHER)$")
    start_date: datetime
    end_date: Optional[datetime] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    terms: Optional[str] = None


class UpdateSellerContractRequest(BaseModel):
    contract_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    terms: Optional[str] = None


@router.get("/contracts", summary="Danh sách hợp đồng QC của seller")
async def get_seller_contracts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo số hợp đồng"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller xem hợp đồng quảng cáo của mình."""
    _require_seller(current_user)

    query = db.query(PartnerContract).filter(PartnerContract.partner_id == current_user.id)
    if status:
        query = query.filter(PartnerContract.status == status)
    if search:
        query = query.filter(PartnerContract.contract_number.ilike(f"%{search}%"))

    total = query.count()
    skip = (page - 1) * limit
    contracts = query.order_by(PartnerContract.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": c.id,
                "contract_number": c.contract_number,
                "contract_type": c.contract_type,
                "start_date": c.start_date.isoformat(),
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "amount": _to_vnd_int(c.amount) if c.amount is not None else None,
                "status": c.status.value if hasattr(c.status, 'value') else str(c.status),
                "terms": c.terms,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in contracts
        ],
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }


@router.post("/contracts", summary="Seller tạo hợp đồng QC")
async def create_seller_contract(
    contract_data: CreateSellerContractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller tạo yêu cầu hợp đồng quảng cáo. Trạng thái DRAFT chờ admin duyệt."""
    _require_seller(current_user)

    existing = db.query(PartnerContract).filter(
        PartnerContract.contract_number == contract_data.contract_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Số hợp đồng đã tồn tại")

    new_contract = PartnerContract(
        contract_number=contract_data.contract_number,
        partner_id=current_user.id,
        contract_type=contract_data.contract_type,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        amount=contract_data.amount,
        status=ContractStatus.DRAFT,
        terms=contract_data.terms,
        created_by=current_user.id,
    )
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    return {
        "success": True,
        "message": "Hợp đồng đã được tạo (DRAFT). Chờ admin duyệt.",
        "data": {
            "id": new_contract.id,
            "contract_number": new_contract.contract_number,
            "status": "DRAFT",
            "created_at": new_contract.created_at.isoformat() if new_contract.created_at else None,
        }
    }


@router.put("/contracts/{contract_id}", summary="Seller cập nhật hợp đồng QC")
async def update_seller_contract(
    contract_id: int,
    contract_data: UpdateSellerContractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller cập nhật hợp đồng QC của mình (chỉ khi DRAFT)."""
    _require_seller(current_user)

    contract = db.query(PartnerContract).filter(
        PartnerContract.id == contract_id,
        PartnerContract.partner_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Hợp đồng không tồn tại hoặc không có quyền")

    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Chỉ được chỉnh sửa hợp đồng ở trạng thái DRAFT")

    update_data = contract_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contract, key, value)

    db.commit()
    db.refresh(contract)

    return {
        "success": True,
        "message": "Đã cập nhật hợp đồng",
        "data": {
            "id": contract.id,
            "contract_number": contract.contract_number,
            "status": contract.status.value if hasattr(contract.status, 'value') else str(contract.status),
        }
    }


@router.delete("/contracts/{contract_id}", summary="Seller xóa hợp đồng QC")
async def delete_seller_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller xóa hợp đồng QC (chỉ khi DRAFT)."""
    _require_seller(current_user)

    contract = db.query(PartnerContract).filter(
        PartnerContract.id == contract_id,
        PartnerContract.partner_id == current_user.id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Hợp đồng không tồn tại hoặc không có quyền")

    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Chỉ được xóa hợp đồng ở trạng thái DRAFT")

    db.delete(contract)
    db.commit()

    return {"success": True, "message": "Đã xóa hợp đồng"}


# ==============================================================================
# SELLER RETURNS (Yêu cầu đổi trả thuộc đơn hàng của seller)
# ==============================================================================

@router.get("/returns", summary="Seller xem yêu cầu đổi trả")
async def get_seller_returns(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo mã đơn hàng"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seller xem danh sách yêu cầu đổi trả thuộc đơn hàng của mình."""
    _require_seller(current_user)

    # Lấy danh sách order_id của seller
    seller_order_ids = [
        o.id for o in db.query(Order.id).filter(Order.seller_id == current_user.id).all()
    ]

    query = db.query(ReturnRequest).filter(ReturnRequest.order_id.in_(seller_order_ids))
    if status:
        query = query.filter(ReturnRequest.status == status)

    if search:
        matching_orders = db.query(Order.id).filter(
            Order.seller_id == current_user.id,
            Order.order_number.ilike(f"%{search}%")
        ).all()
        matching_ids = [o.id for o in matching_orders]
        query = query.filter(ReturnRequest.order_id.in_(matching_ids))

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
            "return_type": r.return_type.value if hasattr(r.return_type, "value") else r.return_type,
            "reason": r.reason,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "admin_note": r.admin_note,
            "created_at": r.created_at.isoformat(),
            "handled_at": r.handled_at.isoformat() if r.handled_at else None,
        })

    return {
        "success": True,
        "data": result,
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }


class SellerReturnUpdateRequest(BaseModel):
    note: Optional[str] = Field(None, max_length=500)
    action: str = Field(..., pattern="^(ACCEPT|REJECT)$")


@router.put("/returns/{return_id}", summary="Seller xử lý yêu cầu đổi trả")
async def update_seller_return(
    return_id: int,
    return_data: SellerReturnUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seller chấp nhận hoặc từ chối yêu cầu đổi trả.
    Chỉ xử lý yêu cầu thuộc đơn hàng của seller.
    """
    _require_seller(current_user)

    return_req = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not return_req:
        raise HTTPException(status_code=404, detail="Yêu cầu đổi trả không tồn tại")

    # Kiểm tra đơn hàng thuộc seller
    order = db.query(Order).filter(
        Order.id == return_req.order_id,
        Order.seller_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=403, detail="Không có quyền xử lý yêu cầu này")

    if return_req.status != ReturnStatus.PENDING:
        raise HTTPException(status_code=400, detail="Chỉ xử lý yêu cầu ở trạng thái PENDING")

    if return_data.action == "ACCEPT":
        return_req.status = ReturnStatus.APPROVED
        message = "Đã chấp nhận yêu cầu đổi trả"
    else:
        return_req.status = ReturnStatus.REJECTED
        message = "Đã từ chối yêu cầu đổi trả"

    return_req.admin_note = return_data.note
    return_req.handled_by = current_user.id
    return_req.handled_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": message,
        "return_id": return_id,
        "status": return_req.status.value if hasattr(return_req.status, "value") else str(return_req.status)
    }
