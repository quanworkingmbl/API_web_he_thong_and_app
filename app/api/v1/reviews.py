"""
Reviews API – Đánh giá sản phẩm

Endpoints:
- POST /reviews              – Tạo đánh giá (phải là đơn DELIVERED)
- GET  /reviews/product/{id} – Lấy reviews của sản phẩm (public)
- PUT  /reviews/{id}         – Cập nhật đánh giá của mình
- DELETE /reviews/{id}       – Xóa đánh giá của mình
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.complaint import Review
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CreateReviewRequest(BaseModel):
    product_id: int
    order_id: int  # Phải cung cấp order_id để verify đã mua
    rating: int = Field(..., ge=1, le=5, description="Đánh giá từ 1–5 sao")
    comment: Optional[str] = Field(None, max_length=2000)


class UpdateReviewRequest(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.post("", summary="Tạo đánh giá sản phẩm")
async def create_review(
    review_data: CreateReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo đánh giá sản phẩm.
    Yêu cầu: phải có đơn hàng ở trạng thái DELIVERED chứa sản phẩm đó.
    """
    # Kiểm tra sản phẩm tồn tại
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    # Verify đã mua sản phẩm trong đơn hàng đã giao
    order = db.query(Order).filter(
        Order.id == review_data.order_id,
        Order.customer_id == current_user.id,
        Order.status == OrderStatus.DELIVERED
    ).first()
    if not order:
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể đánh giá sản phẩm sau khi đơn hàng đã được giao thành công"
        )

    # Kiểm tra đã đánh giá sản phẩm này chưa
    existing = db.query(Review).filter(
        Review.product_id == review_data.product_id,
        Review.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bạn đã đánh giá sản phẩm này rồi. Dùng PUT /reviews/{id} để cập nhật."
        )

    review = Review(
        product_id=review_data.product_id,
        user_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "success": True,
        "message": "Đánh giá đã được tạo thành công",
        "data": {
            "id": review.id,
            "product_id": review.product_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat()
        }
    }


@router.get("/product/{product_id}", summary="Lấy đánh giá của sản phẩm (public)")
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách đánh giá của sản phẩm – public, không cần đăng nhập.
    Bao gồm thống kê: tổng số review, điểm trung bình.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    # Thống kê
    stats = db.query(
        sql_func.count(Review.id).label("total"),
        sql_func.avg(Review.rating).label("avg_rating")
    ).filter(Review.product_id == product_id).first()

    total = stats.total or 0
    avg_rating = round(float(stats.avg_rating), 1) if stats.avg_rating else 0.0

    # Phân trang
    skip = (page - 1) * limit
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

    review_list = []
    for r in reviews:
        user = db.query(User).filter(User.id == r.user_id).first()
        # Ẩn một phần tên người dùng để bảo vệ privacy
        name = user.name if user else "Người dùng ẩn danh"
        if len(name) > 2:
            name = name[0] + "*" * (len(name) - 2) + name[-1]
        review_list.append({
            "id": r.id,
            "reviewer_name": name,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    # Phân bố rating
    rating_distribution = {}
    for star in range(1, 6):
        count = db.query(Review).filter(
            Review.product_id == product_id,
            Review.rating == star
        ).count()
        rating_distribution[f"{star}_star"] = count

    return {
        "success": True,
        "data": {
            "product_id": product_id,
            "product_name": product.name,
            "stats": {
                "total_reviews": total,
                "avg_rating": avg_rating,
                "rating_distribution": rating_distribution
            },
            "reviews": review_list
        },
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }
    }


@router.put("/{review_id}", summary="Cập nhật đánh giá của mình")
async def update_review(
    review_id: int,
    review_data: UpdateReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật đánh giá của người dùng đang đăng nhập."""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Đánh giá không tồn tại hoặc không có quyền sửa")

    if review_data.rating is not None:
        review.rating = review_data.rating
    if review_data.comment is not None:
        review.comment = review_data.comment

    db.commit()

    return {
        "success": True,
        "message": "Đánh giá đã được cập nhật",
        "data": {
            "id": review.id,
            "rating": review.rating,
            "comment": review.comment
        }
    }


@router.delete("/{review_id}", summary="Xóa đánh giá của mình")
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa đánh giá của người dùng đang đăng nhập."""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Đánh giá không tồn tại hoặc không có quyền xóa")

    db.delete(review)
    db.commit()

    return {
        "success": True,
        "message": "Đánh giá đã được xóa thành công"
    }
