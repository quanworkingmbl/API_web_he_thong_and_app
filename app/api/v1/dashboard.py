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
    
    from app.models.complaint import Complaint

    # Pending complaints
    try:
        pending_complaints = db.query(Complaint).filter(
            Complaint.status == "PENDING"
        ).count()
    except Exception:
        pending_complaints = 0

    # Platform fee tháng này
    this_month_platform_fee = sum(o.platform_fee_amount for o in this_month_orders) if this_month_orders else 0

    # Đơn hàng gần đây (10 đơn mới nhất)
    recent_orders_raw = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    recent_orders_list = [
        {
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "total_amount": _to_vnd_int(o.total_amount),
            "status": o.status.value if hasattr(o.status, "value") else str(o.status),
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in recent_orders_raw
    ]

    return {
        "success": True,
        "data": {
            # ── Flat fields — Web đọc trực tiếp ──────────────────────────────
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": _to_vnd_int(total_revenue),
            "platform_fee_total": _to_vnd_int(total_platform_fee),
            "platform_fee_this_month": _to_vnd_int(this_month_platform_fee),
            "pending_products": pending_products,
            "pending_orders": pending_orders,
            "pending_complaints": pending_complaints,
            "recent_orders": recent_orders_list,
            # ── Nested structure — giữ lại để tương thích ────────────────────
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
                "platform_fee_10pct": _to_vnd_int(total_platform_fee),
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
    """Thống kê doanh thu theo thời gian"""
    check_dashboard_access(current_user)

    from app.models.order import Order, OrderStatus

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


@router.get("/dashboard/finance", summary="Admin – Tổng hợp tài chính toàn nền tảng")
async def get_finance_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tổng hợp dòng tiền toàn platform dành cho Admin:
    - GMV (tổng tiền hàng khách trả)
    - VAT thu được
    - Phí nền tảng thu được
    - Tiền đã trả cho sellers
    - Top 10 sellers doanh thu cao nhất
    - 6 tháng gần nhất (theo tháng)
    """
    check_dashboard_access(current_user)
    if current_user.type != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Chỉ admin mới truy cập được")

    from app.models.order import Order, OrderStatus
    from app.models.user import User as UserModel
    from app.models.settlement import SellerWallet
    from sqlalchemy import func as sf

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year_start  = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # ── 1. Tổng tất cả đơn DELIVERED ────────────────────────────────────────
    all_delivered = db.query(Order).filter(
        Order.status == OrderStatus.DELIVERED,
        Order.is_active == True,
    ).all()

    gmv              = sum(o.subtotal           for o in all_delivered)  # tiền hàng thuần (không kể ship)
    total_shipping   = sum(o.shipping_fee       for o in all_delivered)
    total_discount   = sum(o.discount_amount    for o in all_delivered)
    total_vat        = sum(o.vat_amount or 0    for o in all_delivered)
    total_fee        = sum(o.platform_fee_amount for o in all_delivered)
    total_seller_out = sum(o.seller_amount      for o in all_delivered)
    order_count      = len(all_delivered)

    # ── 2. Tháng này ────────────────────────────────────────────────────────
    this_month = [o for o in all_delivered if (o.delivered_at or o.created_at) and (o.delivered_at or o.created_at) >= month_start]
    month_gmv        = sum(o.subtotal            for o in this_month)
    month_vat        = sum(o.vat_amount or 0     for o in this_month)
    month_fee        = sum(o.platform_fee_amount  for o in this_month)
    month_seller_out = sum(o.seller_amount        for o in this_month)

    # ── 3. Năm này ──────────────────────────────────────────────────────────
    this_year = [o for o in all_delivered if (o.delivered_at or o.created_at) and (o.delivered_at or o.created_at) >= year_start]
    year_gmv         = sum(o.subtotal            for o in this_year)
    year_vat         = sum(o.vat_amount or 0     for o in this_year)
    year_fee         = sum(o.platform_fee_amount  for o in this_year)
    year_seller_out  = sum(o.seller_amount        for o in this_year)

    # ── 4. 6 tháng gần nhất (by month) ─────────────────────────────────────
    monthly = []
    for i in range(5, -1, -1):  # tháng -5 → tháng hiện tại
        if now.month - i <= 0:
            y = now.year - 1
            m = now.month - i + 12
        else:
            y = now.year
            m = now.month - i
        m_start = datetime(y, m, 1)
        m_end   = datetime(y, m+1, 1) if m < 12 else datetime(y+1, 1, 1)
        m_orders = [
            o for o in all_delivered
            if (o.delivered_at or o.created_at) and m_start <= (o.delivered_at or o.created_at) < m_end
        ]
        monthly.append({
            "month":      f"{y}-{m:02d}",
            "gmv":        _to_vnd_int(sum(o.subtotal            for o in m_orders)),
            "vat":        _to_vnd_int(sum(o.vat_amount or 0     for o in m_orders)),
            "fee":        _to_vnd_int(sum(o.platform_fee_amount  for o in m_orders)),
            "seller_out": _to_vnd_int(sum(o.seller_amount        for o in m_orders)),
            "orders":     len(m_orders),
        })

    # ── 5. Top 10 sellers doanh thu cao nhất (tổng seller_amount) ──────────
    from collections import defaultdict
    seller_totals: dict = defaultdict(lambda: {"gmv": Decimal("0"), "vat": Decimal("0"),
                                                "fee": Decimal("0"), "net": Decimal("0"), "cnt": 0})
    for o in all_delivered:
        sid = o.seller_id
        seller_totals[sid]["gmv"] += o.subtotal or Decimal("0")
        seller_totals[sid]["vat"] += o.vat_amount or Decimal("0")
        seller_totals[sid]["fee"] += o.platform_fee_amount or Decimal("0")
        seller_totals[sid]["net"] += o.seller_amount or Decimal("0")
        seller_totals[sid]["cnt"] += 1

    top_seller_ids = sorted(seller_totals, key=lambda s: seller_totals[s]["net"], reverse=True)[:10]
    seller_names = {
        u.id: u.name
        for u in db.query(UserModel).filter(UserModel.id.in_(top_seller_ids)).all()
    }
    top_sellers = [
        {
            "seller_id":   sid,
            "seller_name": seller_names.get(sid, f"Seller #{sid}"),
            "gmv":         _to_vnd_int(seller_totals[sid]["gmv"]),
            "vat":         _to_vnd_int(seller_totals[sid]["vat"]),
            "platform_fee":_to_vnd_int(seller_totals[sid]["fee"]),
            "seller_net":  _to_vnd_int(seller_totals[sid]["net"]),
            "order_count": seller_totals[sid]["cnt"],
        }
        for sid in top_seller_ids
    ]

    # ── 6. Tổng ví sellers ──────────────────────────────────────────────────
    wallet_totals = db.query(
        sf.coalesce(sf.sum(SellerWallet.pending_balance),   0).label("total_pending"),
        sf.coalesce(sf.sum(SellerWallet.available_balance), 0).label("total_available"),
        sf.coalesce(sf.sum(SellerWallet.total_withdrawn),   0).label("total_withdrawn"),
    ).first()

    return {
        "success": True,
        "data": {
            # ── Tổng tích lũy ──────────────────────────────────────────────
            "all_time": {
                "gmv":              _to_vnd_int(gmv),
                "shipping_fee":     _to_vnd_int(total_shipping),
                "discount":         _to_vnd_int(total_discount),
                "vat_collected":    _to_vnd_int(total_vat),      # VAT nền tảng thu
                "platform_fee":     _to_vnd_int(total_fee),      # Phí 10% nền tảng thu
                "seller_payout":    _to_vnd_int(total_seller_out),# Tổng trả về seller
                "order_count":      order_count,
            },
            # ── Tháng này ──────────────────────────────────────────────────
            "this_month": {
                "gmv":           _to_vnd_int(month_gmv),
                "vat_collected": _to_vnd_int(month_vat),
                "platform_fee":  _to_vnd_int(month_fee),
                "seller_payout": _to_vnd_int(month_seller_out),
                "order_count":   len(this_month),
            },
            # ── Năm này ────────────────────────────────────────────────────
            "this_year": {
                "gmv":           _to_vnd_int(year_gmv),
                "vat_collected": _to_vnd_int(year_vat),
                "platform_fee":  _to_vnd_int(year_fee),
                "seller_payout": _to_vnd_int(year_seller_out),
                "order_count":   len(this_year),
            },
            # ── 6 tháng theo từng tháng ─────────────────────────────────
            "monthly_chart": monthly,
            # ── Top 10 sellers ──────────────────────────────────────────
            "top_sellers":  top_sellers,
            # ── Tổng số dư ví toàn sellers ─────────────────────────────
            "wallet_summary": {
                "total_pending":   _to_vnd_int(wallet_totals.total_pending),
                "total_available": _to_vnd_int(wallet_totals.total_available),
                "total_withdrawn": _to_vnd_int(wallet_totals.total_withdrawn),
            },
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
