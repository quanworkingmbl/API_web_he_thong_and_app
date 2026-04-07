"""
Mobile App API - Dành cho ứng dụng di động
Bao gồm các API cho:
- Posts: Producer đăng bài giới thiệu sản phẩm
- Products: Người dùng xem danh sách sản phẩm
- Shopping: Giỏ hàng và thanh toán
- Profile: Quản lý thông tin cá nhân
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.content import Content, ContentStatus, ContentAuditLog, ContentAuditAction
from app.models.product import Product, ProductStatus
from app.models.traceability import ProductOrigin, ProductCertificate, OriginStatus, CertificateStatus
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.core.permissions import check_seller_kyc_verified
from app.services.order_state import (
    check_order_ownership,
    validate_status_transition,
    log_status_change,
    resolve_payment_status,
)
from app.services.inventory import validate_line_for_sale, decrement_stock, increment_stock
from pydantic import BaseModel, Field
from decimal import Decimal
import uuid
import os
import boto3
import json
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

# Supabase S3 config (dùng chung với media.py)
_S3_ENDPOINT  = os.getenv("SUPABASE_S3_ENDPOINT", "")
_S3_KEY       = os.getenv("SUPABASE_S3_ACCESS_KEY", "")
_S3_SECRET    = os.getenv("SUPABASE_S3_SECRET_KEY", "")
_S3_REGION    = os.getenv("SUPABASE_S3_REGION", "ap-south-1")
_PROJECT_ID   = os.getenv("SUPABASE_PROJECT_ID", "")
_BUCKET       = os.getenv("SUPABASE_STORAGE_BUCKET", "file_test00")
_PUBLIC_BASE  = f"https://{_PROJECT_ID}.supabase.co/storage/v1/object/public/{_BUCKET}/"
_ALLOWED_IMG  = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_ALLOWED_VID  = {"video/mp4", "video/quicktime", "video/avi", "video/x-msvideo", "video/x-ms-wmv"}
_ALLOWED_MEDIA = _ALLOWED_IMG | _ALLOWED_VID

def _upload_to_supabase(content: bytes, filename: str, mime: str) -> str:
    """Upload bytes lên Supabase Storage, trả về public URL"""
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    key = f"{uuid.uuid4()}{ext}"
    s3  = boto3.client(
        "s3",
        endpoint_url=_S3_ENDPOINT,
        aws_access_key_id=_S3_KEY,
        aws_secret_access_key=_S3_SECRET,
        region_name=_S3_REGION,
        config=Config(signature_version="s3v4"),
    )
    s3.put_object(Bucket=_BUCKET, Key=key, Body=content, ContentType=mime)
    return _PUBLIC_BASE + key

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class MobilePostResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    author_id: int
    author_name: str
    author_type: Optional[str]
    images: Optional[str]
    videos: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MobileProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    producer_id: int
    producer_name: str
    label: Optional[str]
    images: Optional[str]
    status: str

    class Config:
        from_attributes = True


class CreatePostRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: Optional[str] = None
    product_id: Optional[int] = None
    images: Optional[str] = None
    videos: Optional[str] = None


class UpdatePostRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = None
    images: Optional[str] = None
    videos: Optional[str] = None


class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)
    variant_id: Optional[int] = None


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=255)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    customer_email: Optional[str] = None
    shipping_address: str = Field(..., min_length=10)
    shipping_province: Optional[str] = None
    shipping_district: Optional[str] = None
    shipping_ward: Optional[str] = None
    payment_method: str = Field(default="COD", pattern="^(COD|BANK_TRANSFER|MOMO|VNPAY|ZALOPAY)$")
    customer_note: Optional[str] = None
    items: List[CartItemRequest]


# ==============================================================================
# POSTS API - Cho Producer đăng bài giới thiệu sản phẩm
# ==============================================================================

@router.get("/posts")
async def get_public_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    author_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách bài viết công khai (đã duyệt + is_active)
    Public endpoint - không cần đăng nhập
    """
    query = db.query(Content).filter(
        Content.status == ContentStatus.APPROVED,
        Content.is_active == True
    )
    
    if author_id:
        query = query.filter(Content.author_id == author_id)
    
    total = query.count()
    skip = (page - 1) * limit
    posts = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()
    
    post_list = []
    for p in posts:
        author = db.query(User).filter(User.id == p.author_id).first()
        post_list.append({
            "id": p.id,
            "title": p.title,
            "content": p.content[:200] + "..." if p.content and len(p.content) > 200 else p.content,
            "author_id": p.author_id,
            "author_name": author.name if author else "Unknown",
            "author_type": author.type if author else None,
            "images": p.images,
            "videos": p.videos,
            "created_at": p.created_at.isoformat()
        })
    
    return {
        "success": True,
        "data": post_list,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


# --- /posts/my routes MUST be before /posts/{post_id} to avoid conflict ---

@router.get("/posts/my")
async def get_my_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    status: Optional[str] = Query(None),
    include_inactive: bool = Query(False, description="Include deleted posts"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách bài viết của producer đang đăng nhập"""
    query = db.query(Content).filter(Content.author_id == current_user.id)
    
    if not include_inactive:
        query = query.filter(Content.is_active == True)
    
    if status:
        query = query.filter(Content.status == status)
    
    total = query.count()
    skip = (page - 1) * limit
    posts = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status.value if hasattr(p.status, 'value') else str(p.status),
                "is_active": p.is_active,
                "created_at": p.created_at.isoformat()
            }
            for p in posts
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit
        }
    }


@router.post("/posts/my")
async def create_my_post(
    # --- Text fields qua Form (multipart) ---
    title: str = Form(..., min_length=2, max_length=255),
    content: Optional[str] = Form(None),
    product_id: Optional[int] = Form(None),
    images: Optional[str] = Form(None),   # URL nếu đã upload riêng
    videos: Optional[str] = Form(None),
    # --- File ảnh hoặc video (tùy chọn) --- 
    media_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Producer tạo bài viết mới (multipart/form-data).
    - KYC Required: Producer/seller phải được xác minh trước khi tạo bài viết.
    - Nếu gửi kèm `media_file` (ảnh hoặc video): tự upload lên Supabase rồi lưu URL.
    - Nếu chỉ gửi `images`/`videos` (URL text): dùng trực tiếp.
    - Bài viết tạo xong ở trạng thái PENDING chờ admin duyệt.
    """
    # KYC check for seller/producer
    if current_user.type in ("producer", "seller"):
        check_seller_kyc_verified(current_user, db)
    
    final_image_url = images
    final_video_url = videos

    # Nếu có file đính kèm, upload lên Supabase trước
    if media_file and media_file.filename:
        mime = media_file.content_type or ""
        if mime not in _ALLOWED_MEDIA:
            raise HTTPException(
                status_code=400,
                detail=f"Chỉ chấp nhận ảnh (JPEG/PNG/GIF/WEBP) hoặc video (MP4/MOV/AVI). Nhận được: {mime}"
            )
        file_bytes = await media_file.read()
        max_size = 50 * 1024 * 1024 if mime in _ALLOWED_VID else 10 * 1024 * 1024
        if len(file_bytes) > max_size:
            raise HTTPException(status_code=400, detail=f"File quá lớn, tối đa {'50MB' if mime in _ALLOWED_VID else '10MB'}")
        try:
            url = _upload_to_supabase(file_bytes, media_file.filename, mime)
            if mime in _ALLOWED_VID:
                final_video_url = url   # video → lưu vào field videos
            else:
                final_image_url = url   # ảnh  → lưu vào field images
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload thất bại: {str(e)}")

    # Validate: require at least one media
    has_media = bool(final_image_url or final_video_url)
    if not has_media:
        raise HTTPException(status_code=400, detail="Bài viết phải có ít nhất 1 ảnh hoặc video")
    
    # Validate: require content with minimum length
    MIN_CONTENT_LENGTH = 30
    if not content or len(content.strip()) < MIN_CONTENT_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Nội dung bài viết phải có ít nhất {MIN_CONTENT_LENGTH} ký tự"
        )

    new_post = Content(
        title=title,
        content=content,
        content_type="POST",
        author_id=current_user.id,
        product_id=product_id,
        status=ContentStatus.PENDING,
        images=final_image_url,
        videos=final_video_url,
        is_active=True
    )

    db.add(new_post)
    db.flush()
    
    # Log audit
    audit_log = ContentAuditLog(
        content_id=new_post.id,
        action=ContentAuditAction.CREATE,
        user_id=current_user.id,
        new_status="PENDING",
        notes=f"Post created via mobile app by {current_user.email}"
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(new_post)

    return {
        "success": True,
        "message": "Post created successfully. Waiting for approval.",
        "data": {
            "id": new_post.id,
            "title": new_post.title,
            "status": "PENDING",
            "images": final_image_url,
            "videos": final_video_url
        }
    }


# --- Dynamic path /posts/{post_id} AFTER static /posts/my ---

@router.get("/posts/{post_id}")
async def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Xem chi tiết bài viết - Public (chỉ hiện bài APPROVED & is_active)"""
    post = db.query(Content).filter(
        Content.id == post_id,
        Content.status == ContentStatus.APPROVED,
        Content.is_active == True
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    author = db.query(User).filter(User.id == post.author_id).first()
    
    return {
        "success": True,
        "data": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "author_name": author.name if author else "Unknown",
            "author_type": author.type if author else None,
            "images": post.images,
            "videos": post.videos,
            "product_id": post.product_id,
            "created_at": post.created_at.isoformat()
        }
    }


@router.put("/posts/my/{post_id}")
async def update_my_post(
    post_id: int,
    post_data: UpdatePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Producer cập nhật bài viết của mình (ownership check)"""
    post = db.query(Content).filter(
        Content.id == post_id,
        Content.author_id == current_user.id,
        Content.is_active == True
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or not authorized")
    
    old_status = post.status.value if hasattr(post.status, 'value') else str(post.status)
    
    update_data = post_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)
    
    # Reset to pending if content is updated
    if update_data:
        post.status = ContentStatus.PENDING
    
    post.updated_at = datetime.utcnow()
    
    # Log audit
    audit_log = ContentAuditLog(
        content_id=post.id,
        action=ContentAuditAction.UPDATE,
        user_id=current_user.id,
        old_status=old_status,
        new_status="PENDING",
        notes=f"Post updated via mobile app by {current_user.email}"
    )
    db.add(audit_log)
    
    db.commit()
    
    return {
        "success": True,
        "message": "Post updated. Waiting for re-approval.",
        "data": {"id": post.id, "status": "PENDING"}
    }


@router.delete("/posts/my/{post_id}")
async def delete_my_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Producer soft-delete bài viết của mình (ownership check)"""
    post = db.query(Content).filter(
        Content.id == post_id,
        Content.author_id == current_user.id,
        Content.is_active == True
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or not authorized")
    
    # Soft delete instead of hard delete
    post.is_active = False
    post.deleted_at = datetime.utcnow()
    post.deleted_by = current_user.id
    
    # Log audit
    audit_log = ContentAuditLog(
        content_id=post.id,
        action=ContentAuditAction.DELETE,
        user_id=current_user.id,
        notes=f"Post soft-deleted via mobile app by {current_user.email}"
    )
    db.add(audit_log)
    
    db.commit()
    
    return {"success": True, "message": "Post deleted successfully"}


# ==============================================================================
# PRODUCTS API - Cho người dùng xem sản phẩm
# ==============================================================================

@router.get("/products")
async def get_public_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    producer_id: Optional[int] = Query(None),
    label: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[Decimal] = Query(None),
    max_price: Optional[Decimal] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách sản phẩm đã duyệt
    Public endpoint - không cần đăng nhập
    """
    query = db.query(Product).filter(Product.status == ProductStatus.APPROVED)
    
    if producer_id:
        query = query.filter(Product.producer_id == producer_id)
    if label:
        query = query.filter(Product.label == label)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    total = query.count()
    skip = (page - 1) * limit
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    product_list = []
    for p in products:
        producer = db.query(User).filter(User.id == p.producer_id).first()
        product_list.append({
            "id": p.id,
            "name": p.name,
            "description": p.description[:100] + "..." if p.description and len(p.description) > 100 else p.description,
            "price": str(p.price),
            "producer_id": p.producer_id,
            "producer_name": producer.name if producer else "Unknown",
            "label": p.label,
            "images": p.images
        })
    
    return {
        "success": True,
        "data": product_list,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/products/{product_id}")
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Xem chi tiết sản phẩm - Public"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.status == ProductStatus.APPROVED
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    producer = db.query(User).filter(User.id == product.producer_id).first()
    origin = db.query(ProductOrigin).filter(
        ProductOrigin.product_id == product.id,
        ProductOrigin.verification_status == OriginStatus.VERIFIED,
    ).first()
    certificates = db.query(ProductCertificate).filter(
        ProductCertificate.product_id == product.id,
        ProductCertificate.verification_status == CertificateStatus.VERIFIED,
    ).all()

    origin_payload = None
    if origin:
        origin_payload = {
            "village_name": origin.village_name,
            "region_id": origin.region_id,
            "producer_name": origin.producer_name,
            "batch_number": origin.batch_number,
            "production_date": origin.production_date.isoformat() if origin.production_date else None,
            "expiry_date": origin.expiry_date.isoformat() if origin.expiry_date else None,
            "ingredients": origin.ingredients,
            "process_summary": origin.process_summary,
        }

    certificates_payload = [
        {
            "certificate_name": cert.certificate_name,
            "certificate_number": cert.certificate_number,
            "issued_by": cert.issued_by,
            "issue_date": cert.issue_date.isoformat() if cert.issue_date else None,
            "expiry_date": cert.expiry_date.isoformat() if cert.expiry_date else None,
            "document_url": cert.document_url,
        }
        for cert in certificates
    ]
    
    return {
        "success": True,
        "data": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
            "producer_id": product.producer_id,
            "producer_name": producer.name if producer else "Unknown",
            "producer_type": producer.type if producer else None,
            "label": product.label,
            "images": product.images,
            "traceability": {
                "origin": origin_payload,
                "certificates": certificates_payload,
            },
            "created_at": product.created_at.isoformat() if product.created_at else None
        }
    }


# ==============================================================================
# SHOPPING API - Giỏ hàng và Thanh toán
# ==============================================================================

@router.post("/checkout")
async def create_order(
    checkout_data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo đơn hàng từ giỏ hàng.
    """
    if not checkout_data.items or len(checkout_data.items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # ── Bước 1: Khóa Product + ProductVariant (FOR UPDATE), validate SKU/tồn ──
    sellers_map: dict = {}

    product_ids = sorted({item.product_id for item in checkout_data.items})
    variant_ids = sorted({item.variant_id for item in checkout_data.items if item.variant_id})

    locked_products = (
        db.query(Product)
        .filter(
            Product.id.in_(product_ids),
            Product.status == ProductStatus.APPROVED,
            Product.is_active == True,
        )
        .order_by(Product.id)
        .with_for_update()
        .all()
    )
    locked_map = {p.id: p for p in locked_products}

    if len(locked_map) != len(product_ids):
        raise HTTPException(
            status_code=400,
            detail="Một hoặc nhiều sản phẩm không tồn tại hoặc chưa được duyệt",
        )

    if variant_ids:
        locked_variants = (
            db.query(ProductVariant)
            .filter(ProductVariant.id.in_(variant_ids))
            .order_by(ProductVariant.id)
            .with_for_update()
            .all()
        )
        if len(locked_variants) != len(variant_ids):
            raise HTTPException(
                status_code=400,
                detail="Biến thể không tồn tại hoặc không khả dụng",
            )

    for item in checkout_data.items:
        product = locked_map[item.product_id]
        _, unit_price = validate_line_for_sale(db, product, item.quantity, item.variant_id)
        total_price = unit_price * item.quantity
        sid = product.producer_id
        if sid not in sellers_map:
            sellers_map[sid] = []
        sellers_map[sid].append(
            {
                "product": product,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "variant_id": item.variant_id,
            }
        )

    # ── Bước 2: Tạo đơn hàng – tách theo từng người bán (FIX 3) ───────────────
    platform_fee_percentage = Decimal("5.0")
    created_orders = []

    for seller_id, items_of_seller in sellers_map.items():
        subtotal = sum(i["total_price"] for i in items_of_seller)
        shipping_fee = Decimal("30000")          # 30.000 VND flat rate / đơn
        discount_amount = Decimal("0")
        total_amount = subtotal + shipping_fee - discount_amount
        platform_fee_amount = subtotal * platform_fee_percentage / Decimal("100")
        seller_amount = subtotal - platform_fee_amount

        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        new_order = Order(
            order_number=order_number,
            customer_id=current_user.id,
            customer_name=checkout_data.customer_name,
            customer_phone=checkout_data.customer_phone,
            customer_email=checkout_data.customer_email,
            shipping_address=checkout_data.shipping_address,
            shipping_province=checkout_data.shipping_province,
            shipping_district=checkout_data.shipping_district,
            shipping_ward=checkout_data.shipping_ward,
            seller_id=seller_id,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            discount_amount=discount_amount,
            total_amount=total_amount,
            platform_fee_percentage=platform_fee_percentage,
            platform_fee_amount=platform_fee_amount,
            seller_amount=seller_amount,
            status=OrderStatus.PENDING,
            payment_method=checkout_data.payment_method,
            payment_status="UNPAID",
            customer_note=checkout_data.customer_note,
        )
        db.add(new_order)
        db.flush()  # lấy new_order.id trước khi tạo items

        for item_data in items_of_seller:
            p = item_data["product"]
            db.add(
                OrderItem(
                    order_id=new_order.id,
                    product_id=p.id,
                    seller_id=p.producer_id,
                    variant_id=item_data["variant_id"],
                    product_name=p.name,
                    product_image=p.images,
                    unit_price=item_data["unit_price"],
                    quantity=item_data["quantity"],
                    total_price=item_data["total_price"],
                )
            )
            decrement_stock(db, p, item_data["quantity"], item_data["variant_id"])

        # [AUDIT] Ghi log trạng thái khởi tạo
        log_status_change(
            db=db,
            order_id=new_order.id,
            old_status=None,
            new_status=OrderStatus.PENDING.value,
            actor_id=current_user.id,
            role="consumer",
            note=f"Đặt hàng qua mobile app. Phương thức: {checkout_data.payment_method}",
            auto_flush=True,
        )

        created_orders.append({
            "order_id": new_order.id,
            "order_number": new_order.order_number,
            "seller_id": seller_id,
            "total_amount": str(total_amount),
        })

    db.commit()

    # Trả về 1 đơn nếu chỉ có 1 seller, trả về danh sách nếu nhiều seller
    if len(created_orders) == 1:
        order = created_orders[0]
        return {
            "success": True,
            "message": "Đặt hàng thành công",
            "data": {
                "order_id": order["order_id"],
                "order_number": order["order_number"],
                "total_amount": order["total_amount"],
                "status": "PENDING",
                "payment_method": checkout_data.payment_method,
            },
        }
    else:
        return {
            "success": True,
            "message": f"Đặt hàng thành công. Giỏ hàng được tách thành {len(created_orders)} đơn theo từng người bán.",
            "data": {
                "orders": created_orders,
                "payment_method": checkout_data.payment_method,
            },
        }


@router.get("/orders/my")
async def get_my_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách đơn hàng của người dùng đang đăng nhập"""
    query = db.query(Order).filter(Order.customer_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    skip = (page - 1) * limit
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    order_list = []
    for o in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        order_list.append({
            "id": o.id,
            "order_number": o.order_number,
            "total_amount": str(o.total_amount),
            "status": o.status.value if hasattr(o.status, 'value') else str(o.status),
            "payment_status": o.payment_status,
            "item_count": len(items),
            "created_at": o.created_at.isoformat()
        })
    
    return {
        "success": True,
        "data": order_list,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit
        }
    }


@router.get("/orders/my/{order_id}")
async def get_my_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xem chi tiết đơn hàng của người dùng"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    seller = db.query(User).filter(User.id == order.seller_id).first()
    
    return {
        "success": True,
        "data": {
            "id": order.id,
            "order_number": order.order_number,
            "seller_name": seller.name if seller else None,
            "subtotal": str(order.subtotal),
            "shipping_fee": str(order.shipping_fee),
            "discount_amount": str(order.discount_amount),
            "total_amount": str(order.total_amount),
            "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
            "payment_method": order.payment_method.value if hasattr(order.payment_method, 'value') else str(order.payment_method),
            "payment_status": order.payment_status,
            "shipping_address": order.shipping_address,
            "customer_note": order.customer_note,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "product_name": item.product_name,
                    "product_image": item.product_image,
                    "unit_price": str(item.unit_price),
                    "quantity": item.quantity,
                    "total_price": str(item.total_price)
                }
                for item in items
            ]
        }
    }


# ==============================================================================
# CANCEL ORDER – Consumer tự hủy đơn hàng của mình
# ==============================================================================

class CancelOrderRequest(BaseModel):
    cancel_reason: Optional[str] = Field(None, max_length=500, description="Lý do hủy đơn")


@router.put("/orders/my/{order_id}/cancel")
async def cancel_my_order(
    order_id: int,
    cancel_data: CancelOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Consumer tự hủy đơn hàng của mình.
    - Cho phép hủy khi đơn đang ở PENDING hoặc CONFIRMED.
    - Trạng thái PROCESSING/SHIPPING/DELIVERED không thể hủy.
    - Ghi audit log và trả về tồn kho nếu đơn đã CONFIRMED.
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id,  # ownership check trực tiếp
        Order.is_active == True
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    old_status = order.status

    # [STATE MACHINE] Chỉ cho phép hủy từ PENDING hoặc CONFIRMED
    validate_status_transition(old_status, OrderStatus.CANCELLED, role="consumer")

    # Hoàn tồn: đã trừ khi đặt hàng (PENDING/CONFIRMED trước khi hủy)
    if old_status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                increment_stock(db, product, item.quantity, item.variant_id)

    # Cập nhật đơn
    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()
    if cancel_data.cancel_reason:
        order.cancel_reason = cancel_data.cancel_reason

    # [AUDIT] Ghi log
    log_status_change(
        db=db,
        order_id=order_id,
        old_status=old_status.value if hasattr(old_status, "value") else str(old_status),
        new_status=OrderStatus.CANCELLED.value,
        actor_id=current_user.id,
        role="consumer",
        note=cancel_data.cancel_reason or "Consumer tự hủy đơn",
        auto_flush=True,
    )

    db.commit()

    return {
        "success": True,
        "message": "Đơn hàng đã được hủy thành công",
        "order_id": order_id,
        "old_status": old_status.value if hasattr(old_status, "value") else str(old_status),
        "new_status": "CANCELLED",
    }


# ==============================================================================
# PROFILE API - Quản lý thông tin cá nhân
# ==============================================================================

@router.get("/profile")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin profile của người dùng đăng nhập"""
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "type": current_user.type,
            "gender": current_user.gender,
            "activated": current_user.activated,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
    }


@router.put("/profile")
async def update_my_profile(
    name: Optional[str] = None,
    gender: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin profile"""
    if name:
        current_user.name = name
    if gender:
        current_user.gender = gender
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "gender": current_user.gender
        }
    }
