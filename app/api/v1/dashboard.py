from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.core.permissions import check_dashboard_access
from pydantic import BaseModel
from decimal import Decimal, ROUND_HALF_UP

router = APIRouter()


def _to_vnd_int(value: Optional[Decimal]) -> int:
    """Chuẩn hóa tiền về số nguyên VND để API trả dạng số nhất quán."""
    if value is None:
        return 0
    decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    return int(decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

# ==============================================================================
# RESPONSE SCHEMAS
# ==============================================================================

class OverviewStatsResponse(BaseModel):
    total_users: int
    total_producers: int
    total_consumers: int
    total_products: int
    total_orders: int
    total_revenue: Decimal
    pending_products: int
    pending_orders: int

class RevenueStatsResponse(BaseModel):
    period: str
    total_revenue: Decimal
    platform_commission: Decimal
    seller_revenue: Decimal
    order_count: int

class ProductStatsResponse(BaseModel):
    total: int
    by_status: dict
    by_label: dict

class OrderStatsResponse(BaseModel):
    total: int
    by_status: dict
    recent_orders: list


# ==============================================================================
# NEW DASHBOARD ENDPOINTS - Phù hợp với hệ thống nông sản
# ==============================================================================

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tổng quan dashboard - hiển thị các thống kê chính của hệ thống
    """
    check_dashboard_access(current_user)

    from app.models.user import User
    from app.models.product import Product, ProductStatus
    from app.models.order import Order, OrderStatus
    
    # Đếm users theo loại
    total_users = db.query(User).filter(User.deleted_at.is_(None)).count()
    total_producers = db.query(User).filter(
        User.type == "producer",
        User.deleted_at.is_(None)
    ).count()
    total_consumers = db.query(User).filter(
        User.type == "consumer", 
        User.deleted_at.is_(None)
    ).count()
    
    # Đếm products
    total_products = db.query(Product).count()
    pending_products = db.query(Product).filter(
        Product.status == ProductStatus.PENDING
    ).count()
    
    # Thống kê orders
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()

    # Revenue
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).all()
    total_revenue = sum(o.total_amount for o in delivered_orders) if delivered_orders else 0
    total_platform_fee = sum(o.platform_fee_amount for o in delivered_orders) if delivered_orders else 0

    # Revenue tháng này
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_orders = db.query(Order).filter(
        Order.status == OrderStatus.DELIVERED,
        Order.created_at >= first_day_of_month
    ).all()
    this_month_revenue = sum(o.total_amount for o in this_month_orders) if this_month_orders else 0
    
    return {
        "success": True,
        "data": {
            "users": {
                "total": total_users,
                "producers": total_producers,
                "consumers": total_consumers
            },
            "products": {
                "total": total_products,
                "pending": pending_products
            },
            "orders": {
                "total": total_orders,
                "pending": pending_orders
            },
            "revenue": {
                "total": _to_vnd_int(total_revenue),
                "platform_fee": _to_vnd_int(total_platform_fee),
                "this_month": _to_vnd_int(this_month_revenue)
            }
        }
    }


@router.get("/dashboard/revenue")
async def get_revenue_stats(
    period: str = Query("month", pattern="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê doanh thu theo thời gian
    """
    check_dashboard_access(current_user)

    from app.models.order import Order, OrderStatus

    # Tính ngày bắt đầu dựa trên period
    now = datetime.utcnow()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # year
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    delivered_orders = db.query(Order).filter(
        Order.status == OrderStatus.DELIVERED,
        Order.created_at >= start_date
    ).all()

    total_revenue = sum(o.total_amount for o in delivered_orders) if delivered_orders else 0
    platform_commission = sum(o.platform_fee_amount for o in delivered_orders) if delivered_orders else 0
    seller_revenue = sum(o.seller_amount for o in delivered_orders) if delivered_orders else 0
    order_count = len(delivered_orders)

    return {
        "success": True,
        "data": {
            "period": period,
            "total_revenue": _to_vnd_int(total_revenue),
            "platform_commission": _to_vnd_int(platform_commission),
            "seller_revenue": _to_vnd_int(seller_revenue),
            "order_count": order_count,
        }
    }


@router.get("/dashboard/products")
async def get_product_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê sản phẩm theo trạng thái và loại nhãn
    """
    check_dashboard_access(current_user)

    from app.models.product import Product, ProductStatus, ProductLabel
    
    total = db.query(Product).count()
    
    # Đếm theo trạng thái
    by_status = {
        "pending": db.query(Product).filter(Product.status == ProductStatus.PENDING).count(),
        "approved": db.query(Product).filter(Product.status == ProductStatus.APPROVED).count(),
        "rejected": db.query(Product).filter(Product.status == ProductStatus.REJECTED).count()
    }
    
    # Đếm theo nhãn
    by_label = {
        "clean_agriculture": db.query(Product).filter(Product.label == "CLEAN_AGRICULTURE").count(),
        "traditional_craft": db.query(Product).filter(Product.label == "TRADITIONAL_CRAFT").count(),
        "ocop": db.query(Product).filter(Product.label == "OCOP").count(),
        "no_label": db.query(Product).filter(Product.label.is_(None)).count()
    }
    
    return {
        "success": True,
        "data": {
            "total": total,
            "by_status": by_status,
            "by_label": by_label
        }
    }


@router.get("/dashboard/orders")
async def get_order_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê đơn hàng
    """
    check_dashboard_access(current_user)

    from app.models.order import Order, OrderStatus

    total = db.query(Order).count()
    by_status = {}
    for status in OrderStatus:
        cnt = db.query(Order).filter(Order.status == status).count()
        by_status[status.value.lower()] = cnt

    # Đơn hàng gần đây (7 ngày)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders = db.query(Order).filter(
        Order.created_at >= seven_days_ago
    ).order_by(Order.created_at.desc()).limit(10).all()

    return {
        "success": True,
        "data": {
            "total": total,
            "by_status": by_status,
            "recent_orders": [
                {
                    "id": o.id,
                    "order_number": o.order_number,
                    "customer_name": o.customer_name,
                    "total_amount": _to_vnd_int(o.total_amount),
                    "status": o.status.value if hasattr(o.status, 'value') else str(o.status),
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                }
                for o in recent_orders
            ]
        }
    }



@router.get("/dashboard/users")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê người dùng theo loại và trạng thái
    """
    check_dashboard_access(current_user)

    from app.models.user import User
    
    total = db.query(User).filter(User.deleted_at.is_(None)).count()
    
    # Đếm theo loại
    by_type = {
        "admin": db.query(User).filter(User.type == "admin", User.deleted_at.is_(None)).count(),
        "producer": db.query(User).filter(User.type == "producer", User.deleted_at.is_(None)).count(),
        "consumer": db.query(User).filter(User.type == "consumer", User.deleted_at.is_(None)).count(),
        "other": db.query(User).filter(
            ~User.type.in_(["admin", "producer", "consumer"]),
            User.deleted_at.is_(None)
        ).count() if db.query(User).filter(User.type.isnot(None)).count() > 0 else 0
    }
    
    # Đếm theo trạng thái
    by_status = {
        "active": db.query(User).filter(User.activated == 1, User.deleted_at.is_(None)).count(),
        "inactive": db.query(User).filter(User.activated == 0, User.deleted_at.is_(None)).count()
    }
    
    # User mới trong 7 ngày
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_users = db.query(User).filter(
        User.created_at >= seven_days_ago,
        User.deleted_at.is_(None)
    ).count()
    
    return {
        "success": True,
        "data": {
            "total": total,
            "by_type": by_type,
            "by_status": by_status,
            "new_users_7days": new_users
        }
    }


# ==============================================================================
# DEPRECATED ENDPOINTS - Comment out, giữ lại để tham khảo
# ==============================================================================

# class PublisherResponse(BaseModel):
#     id: int
#     email: str
#     name: str
#     type: Optional[str]
#     activated: int
#
#     class Config:
#         from_attributes = True
#
# class AdvertiserPrivateResponse(BaseModel):
#     id: int
#     name: str
#     email: str
#
#     class Config:
#         from_attributes = True
#
# class FlightResponse(BaseModel):
#     id: int
#     name: str
#     running: int
#     status: str
#
#     class Config:
#         from_attributes = True

# @router.get("/accounts")
# async def get_accounts(
#     model: Optional[str] = Query(None),
#     activated: Optional[int] = Query(None),
#     limit: int = Query(500, ge=1, le=500),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get accounts (publishers, advertisers, etc.) - DEPRECATED"""
#     pass

# @router.get("/advertiser-private")
# async def get_advertiser_private(
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get private advertisers - DEPRECATED: Không phù hợp với hệ thống nông sản"""
#     pass

# @router.get("/flights")
# async def get_flights(
#     running: Optional[int] = Query(None),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get flights - DEPRECATED: Không phù hợp với hệ thống nông sản"""
#     pass

# @router.get("/report/flights/realtime")
# async def get_flight_realtime(
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get realtime flight reports - DEPRECATED: Không phù hợp với hệ thống nông sản"""
#     pass
