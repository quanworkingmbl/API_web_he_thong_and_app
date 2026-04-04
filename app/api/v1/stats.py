from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.permissions import check_dashboard_access
from pydantic import BaseModel

router = APIRouter()

# ==============================================================================
# RESPONSE SCHEMAS
# ==============================================================================

class ProducerStatsResponse(BaseModel):
    total: int
    active: int
    inactive: int
    new_this_month: int

class ConsumerStatsResponse(BaseModel):
    total: int
    active: int
    new_this_month: int

class TrendingProductResponse(BaseModel):
    id: int
    name: str
    producer_name: str
    order_count: int
    rating: float


# ==============================================================================
# NEW STATS ENDPOINTS - Thống kê phù hợp với hệ thống nông sản
# ==============================================================================

@router.get("/stats/producers")
async def get_producer_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê người sản xuất (nông dân, hợp tác xã, làng nghề)
    """
    check_dashboard_access(current_user)

    from app.models.user import User
    
    # Thống kê cơ bản
    total = db.query(User).filter(
        User.type == "producer",
        User.deleted_at.is_(None)
    ).count()
    
    active = db.query(User).filter(
        User.type == "producer",
        User.activated == 1,
        User.deleted_at.is_(None)
    ).count()
    
    inactive = db.query(User).filter(
        User.type == "producer",
        User.activated == 0,
        User.deleted_at.is_(None)
    ).count()
    
    # Mới trong tháng này
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = db.query(User).filter(
        User.type == "producer",
        User.created_at >= first_day_of_month,
        User.deleted_at.is_(None)
    ).count()
    
    return {
        "success": True,
        "data": {
            "total": total,
            "active": active,
            "inactive": inactive,
            "new_this_month": new_this_month
        }
    }


@router.get("/stats/consumers")
async def get_consumer_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê người tiêu dùng
    """
    check_dashboard_access(current_user)

    from app.models.user import User
    
    total = db.query(User).filter(
        User.type == "consumer",
        User.deleted_at.is_(None)
    ).count()
    
    active = db.query(User).filter(
        User.type == "consumer",
        User.activated == 1,
        User.deleted_at.is_(None)
    ).count()
    
    # Mới trong tháng này
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = db.query(User).filter(
        User.type == "consumer",
        User.created_at >= first_day_of_month,
        User.deleted_at.is_(None)
    ).count()
    
    return {
        "success": True,
        "data": {
            "total": total,
            "active": active,
            "new_this_month": new_this_month
        }
    }


@router.get("/stats/trending")
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sản phẩm trending (được đặt hàng nhiều nhất)
    TODO: Implement khi có Order model
    """
    check_dashboard_access(current_user)

    from app.models.product import Product, ProductStatus
    
    # Lấy sản phẩm đã duyệt mới nhất (tạm thời, sau này sẽ sort theo order count)
    products = db.query(Product).filter(
        Product.status == ProductStatus.APPROVED
    ).order_by(Product.created_at.desc()).limit(limit).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "label": p.label,
                "order_count": 0,  # TODO: Tính từ Order model
                "rating": 0.0  # TODO: Tính từ Review model
            }
            for p in products
        ],
        "message": "Trending based on newest approved products. Will be sorted by order count when Order model is ready."
    }


@router.get("/stats/regions")
async def get_region_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê sản phẩm theo vùng miền
    TODO: Implement khi có Region model
    """
    check_dashboard_access(current_user)

    return {
        "success": True,
        "data": {
            "regions": []
        },
        "message": "Region stats - will be implemented with Region model"
    }


@router.get("/stats/categories")
async def get_category_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thống kê sản phẩm theo danh mục
    TODO: Implement khi có Category model
    """
    check_dashboard_access(current_user)

    return {
        "success": True,
        "data": {
            "categories": []
        },
        "message": "Category stats - will be implemented with Category model"
    }


# ==============================================================================
# DEPRECATED ENDPOINTS - Comment out, giữ lại để tham khảo
# ==============================================================================

# @router.get("/stats/tvc-quality")
# async def get_tvc_quality_status(
#     meta: Optional[dict] = None,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get TVC quality status - DEPRECATED: Không phù hợp với hệ thống nông sản"""
#     return {
#         "data": {
#             "total": 0,
#             "passed": 0,
#             "failed": 0
#         }
#     }

# @router.get("/stats/tvc-quality-daily")
# async def get_tvc_quality_daily(
#     meta: Optional[dict] = None,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get TVC quality daily chart data - DEPRECATED: Không phù hợp với hệ thống nông sản"""
#     return {
#         "data": []
#     }

# @router.get("/stats/tvc-quality-by-cid")
# async def get_tvc_quality_by_cid(
#     meta: Optional[dict] = None,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get TVC quality by CID table data - DEPRECATED: Không phù hợp với hệ thống nông sản"""
#     return {
#         "data": []
#     }
