from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter()

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
    from app.models.user import User
    from app.models.product import Product, ProductStatus
    
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
    
    # TODO: Thêm thống kê orders và revenue khi có Order model
    
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
                "total": 0,  # TODO: Implement when Order model is ready
                "pending": 0
            },
            "revenue": {
                "total": "0.00",  # TODO: Implement when Payment integration is complete
                "this_month": "0.00"
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
    # TODO: Implement revenue stats when Order/Payment models are complete
    return {
        "success": True,
        "data": {
            "period": period,
            "total_revenue": "0.00",
            "platform_commission": "0.00", 
            "seller_revenue": "0.00",
            "order_count": 0,
            "chart_data": []
        },
        "message": "Revenue stats - will be implemented with Order model"
    }


@router.get("/dashboard/products")  
async def get_product_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê sản phẩm theo trạng thái và loại nhãn
    """
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
    # TODO: Implement when Order model is ready
    return {
        "success": True,
        "data": {
            "total": 0,
            "by_status": {
                "pending": 0,
                "confirmed": 0,
                "shipping": 0,
                "delivered": 0,
                "cancelled": 0
            },
            "recent_orders": []
        },
        "message": "Order stats - will be implemented with Order model"
    }


@router.get("/dashboard/users")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê người dùng theo loại và trạng thái
    """
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
