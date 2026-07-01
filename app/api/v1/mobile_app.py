"""
Mobile App API - Dành cho ứng dụng di động
Bao gồm các API cho:
- Home: Trang chủ aggregated
- Posts: Producer đăng bài giới thiệu sản phẩm
- Products: Người dùng xem danh sách sản phẩm
- Shops: Trang cửa hàng
- Shopping: Giỏ hàng và thanh toán
- Orders: Theo dõi đơn hàng + timeline
- Addresses: Sổ địa chỉ
- Promotions: Áp mã giảm giá
- Profile: Quản lý thông tin cá nhân
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.models.content import Content, ContentStatus, ContentAuditLog, ContentAuditAction
from app.models.product import Product, ProductStatus
from app.models.traceability import ProductOrigin, ProductCertificate, OriginStatus, CertificateStatus
from app.models.region import Region
from app.models.product_variant import ProductVariant
from app.models.product_media import ProductMedia
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, OrderStatusLog, PaymentMethod
from app.models.category import Category
from app.models.store import Store
from app.models.address import Address, Province, District, Ward
from app.models.promotion import Promotion, PromotionStatus
from app.models.promotion_usage import PromotionUsage
from app.models.complaint import Review
from app.models.review_image import ReviewImage
from app.models.shipment import Shipment
from app.models.return_request import ReturnRequest, ReturnStatus
from app.models.seller_profile import SellerProfile, VerificationStatus
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.core.permissions import check_seller_kyc_verified
from app.services.order_state import (
    check_order_ownership,
    validate_status_transition,
    log_status_change,
    resolve_payment_status,
)
from app.services.inventory import validate_line_for_sale, decrement_stock, increment_stock, get_unit_price
from app.services.inventory import get_available_stock
from app.services.notification import (
    notify_new_order_to_seller,
    notify_order_placed_to_buyer,
    notify_order_delivered_to_seller,
    notify_order_cancelled_to_seller,
)
from app.services.wallet import credit_seller_wallet
from pydantic import BaseModel, Field
from decimal import Decimal
from google.cloud import storage as gcs
import uuid
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Google Cloud Storage config
_GCS_BUCKET   = os.getenv("GCS_BUCKET_NAME", "mbl-cms-media-bucket")
_PUBLIC_BASE  = f"https://storage.googleapis.com/{_GCS_BUCKET}/"
_ALLOWED_IMG  = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_ALLOWED_VID  = {"video/mp4", "video/quicktime", "video/avi", "video/x-msvideo", "video/x-ms-wmv"}
_ALLOWED_MEDIA = _ALLOWED_IMG | _ALLOWED_VID

def _upload_to_supabase(content: bytes, filename: str, mime: str) -> str:
    """Upload bytes lên GCS (thầy Supabase đã migrate sang GCS), trả về public URL"""
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    key = f"posts/{uuid.uuid4()}{ext}"
    client = gcs.Client()
    bucket = client.bucket(_GCS_BUCKET)
    blob   = bucket.blob(key)
    blob.upload_from_string(content, content_type=mime)
    return _PUBLIC_BASE + key

import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _sanitize_search(term: str) -> str:
    """Escape wildcard chars trong LIKE/ILIKE để tránh unintended full-scan.

    '%' và '_' là ký tự đặc biệt trong SQL LIKE.
    Nếu user gõ '%' thì khớp toàn bộ DB — không phải SQL injection
    nhưng là logic bypass. Ta escape chúng trước khi truyền vào ilike().
    """
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


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
    seller_id: int
    seller_name: str
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


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., ge=1)


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=255)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    customer_email: Optional[str] = None
    shipping_address: str = Field(..., min_length=10)
    shipping_province: Optional[str] = None
    shipping_district: Optional[str] = None
    shipping_ward: Optional[str] = None
    payment_method: str = Field(default="COD", pattern="^(COD|BANK_TRANSFER|MOMO|VNPAY|ZALOPAY|PLATFORM_CREDITS)$")
    customer_note: Optional[str] = None
    coupon_code: Optional[str] = None
    seller_id: Optional[int] = None
    items: List[CartItemRequest]


class AddressRequest(BaseModel):
    recipient_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    province_code: Optional[str] = Field(None, max_length=20)
    district_code: Optional[str] = Field(None, max_length=20)
    ward_code: Optional[str] = Field(None, max_length=20)
    address_line: str = Field(..., min_length=5)
    is_default: bool = False


class ApplyPromotionRequest(BaseModel):
    coupon_code: str = Field(..., min_length=3, max_length=50)
    subtotal: Decimal = Field(..., ge=0)
    seller_id: Optional[int] = None
    product_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None


class ConfirmReceivedRequest(BaseModel):
    note: Optional[str] = Field(None, max_length=500)


# ==============================================================================
# HELPERS
# ==============================================================================

def _get_product_review_stats(db: Session, product_id: int) -> dict:
    """Lấy thống kê review cho sản phẩm."""
    stats = db.query(
        sql_func.count(Review.id).label("total"),
        sql_func.avg(Review.rating).label("avg_rating")
    ).filter(Review.product_id == product_id).first()
    return {
        "total_reviews": stats.total or 0,
        "avg_rating": round(float(stats.avg_rating), 1) if stats.avg_rating else 0.0,
    }


def _extract_first_media_url(raw_value: Optional[str]) -> Optional[str]:
    """Lấy URL đầu tiên từ chuỗi URL đơn hoặc JSON array URL."""
    if raw_value is None:
        return None

    text = str(raw_value).strip()
    if not text:
        return None

    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except Exception:
            return text

        if isinstance(parsed, list):
            for item in parsed:
                if item is None:
                    continue
                candidate = str(item).strip()
                if candidate:
                    return candidate
            return None

    return text


def _promotion_type(promo: Promotion) -> str:
    return promo.promotion_type.value if hasattr(promo.promotion_type, "value") else str(promo.promotion_type)


def _promotion_scope(promo: Promotion) -> str:
    return str(getattr(promo, "applicable_to", "ALL") or "ALL").upper()


def _parse_scope_ids(raw: Optional[str]) -> set:
    if not raw:
        return set()
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return set()
    if not isinstance(parsed, list):
        return set()

    values = set()
    for item in parsed:
        try:
            values.add(int(item))
        except (TypeError, ValueError):
            continue
    return values


def _calculate_discount(promo: Promotion, eligible_subtotal: Decimal) -> Decimal:
    if eligible_subtotal <= 0:
        return Decimal("0")

    promo_type = _promotion_type(promo)
    if promo_type == "PERCENTAGE":
        discount = eligible_subtotal * promo.discount_value / Decimal("100")
    else:
        discount = promo.discount_value

    if promo.max_discount_amount and discount > promo.max_discount_amount:
        discount = promo.max_discount_amount

    if discount < 0:
        return Decimal("0")
    if discount > eligible_subtotal:
        return eligible_subtotal
    return discount


def _can_user_use_promotion(db: Session, promo: Promotion, user_id: int) -> tuple[bool, str]:
    if promo.usage_limit and promo.used_count >= promo.usage_limit:
        return False, "Mã khuyến mãi đã hết lượt sử dụng"

    user_used_count = db.query(sql_func.count(PromotionUsage.id)).filter(
        PromotionUsage.promotion_id == promo.id,
        PromotionUsage.user_id == user_id,
    ).scalar() or 0

    if promo.usage_limit_per_user:
        if user_used_count >= promo.usage_limit_per_user:
            return False, "Bạn đã dùng hết lượt cho mã khuyến mãi này"
    elif user_used_count > 0:
        return False, "Bạn đã sử dụng mã này rồi"

    return True, ""


def _promotion_matches_cart_scope(promo: Promotion, cart_lines: List[Dict[str, Any]]) -> bool:
    if not cart_lines:
        return False

    seller_ids = {line["product"].seller_id for line in cart_lines}
    if len(seller_ids) != 1:
        return False
    cart_seller_id = next(iter(seller_ids))

    if promo.seller_id and promo.seller_id != cart_seller_id:
        return False

    scope = _promotion_scope(promo)
    if scope == "ALL":
        return True
    if scope == "SELLER":
        return bool(promo.seller_id and promo.seller_id == cart_seller_id)

    product_ids = {line["product"].id for line in cart_lines}
    category_ids = {line["product"].category_id for line in cart_lines if line["product"].category_id is not None}

    if scope == "PRODUCT":
        scoped_product_ids = _parse_scope_ids(promo.applicable_product_ids)
        return bool(scoped_product_ids.intersection(product_ids))

    if scope == "CATEGORY":
        scoped_category_ids = _parse_scope_ids(promo.applicable_category_ids)
        return bool(scoped_category_ids.intersection(category_ids))

    return False


def _eligible_subtotal_for_cart_promotion(promo: Promotion, cart_lines: List[Dict[str, Any]]) -> Decimal:
    scope = _promotion_scope(promo)
    if scope in {"ALL", "SELLER"}:
        return sum((line["total_price"] for line in cart_lines), Decimal("0"))

    if scope == "PRODUCT":
        scoped_product_ids = _parse_scope_ids(promo.applicable_product_ids)
        return sum((line["total_price"] for line in cart_lines if line["product"].id in scoped_product_ids), Decimal("0"))

    if scope == "CATEGORY":
        scoped_category_ids = _parse_scope_ids(promo.applicable_category_ids)
        return sum(
            (
                line["total_price"]
                for line in cart_lines
                if line["product"].category_id is not None and line["product"].category_id in scoped_category_ids
            ),
            Decimal("0"),
        )

    return Decimal("0")


def _promotion_matches_product_scope(promo: Promotion, product: Product) -> bool:
    if promo.seller_id and promo.seller_id != product.seller_id:
        return False

    scope = _promotion_scope(promo)
    if scope == "ALL":
        return True
    if scope == "SELLER":
        return bool(promo.seller_id and promo.seller_id == product.seller_id)
    if scope == "PRODUCT":
        return product.id in _parse_scope_ids(promo.applicable_product_ids)
    if scope == "CATEGORY":
        return product.category_id is not None and product.category_id in _parse_scope_ids(promo.applicable_category_ids)
    return False


def _build_flash_sale_info(product: Product, active_promotions: List[Promotion], now_utc) -> Dict[str, Any]:
    """Trả dict flash-sale cho 1 sản phẩm.  Không có flash sale → tất cả None / False."""
    from decimal import Decimal as _Dec
    for promo in active_promotions:
        if not promo.is_flash_sale:
            continue
        if not _promotion_matches_product_scope(promo, product):
            continue
        ends_in = None
        if promo.end_date:
            end_aware = promo.end_date
            if end_aware.tzinfo is None:
                from datetime import timezone as _tz
                end_aware = end_aware.replace(tzinfo=_tz.utc)
            delta = end_aware - now_utc
            ends_in = max(0, int(delta.total_seconds()))
        ptype = promo.promotion_type.value if hasattr(promo.promotion_type, "value") else str(promo.promotion_type)
        dv = float(promo.discount_value or 0)
        if ptype == "PERCENTAGE":
            label = f"-{int(dv)}%"
        else:
            label = f"-{int(dv):,}đ".replace(",", ".")
        return {
            "is_flash_sale": True,
            "flash_sale_code": promo.code,
            "flash_sale_ends_in_seconds": ends_in,
            "flash_sale_discount": label,
        }
    return {
        "is_flash_sale": False,
        "flash_sale_code": None,
        "flash_sale_ends_in_seconds": None,
        "flash_sale_discount": None,
    }


def _build_product_pricing(product: Product, active_promotions: List[Promotion]) -> Dict[str, Any]:
    base_price = Decimal(str(product.price or 0))
    best_promo: Optional[Promotion] = None
    best_discount = Decimal("0")

    for promo in active_promotions:
        if not _promotion_matches_product_scope(promo, product):
            continue

        if base_price < (promo.min_order_amount or Decimal("0")):
            continue

        discount = _calculate_discount(promo, base_price)
        if discount > best_discount:
            best_discount = discount
            best_promo = promo

    final_price = base_price - best_discount
    if final_price < 0:
        final_price = Decimal("0")

    promo_payload = None
    if best_promo and best_discount > 0:
        promo_payload = {
            "id": best_promo.id,
            "code": best_promo.code,
            "name": best_promo.name,
            "promotion_type": _promotion_type(best_promo),
            "discount_amount": str(best_discount),
        }

    return {
        "price": str(final_price),
        "original_price": str(base_price),
        "discount_amount": str(best_discount),
        "auto_promotion": promo_payload,
    }


def _build_address_response(addr: Address, db: Session) -> dict:
    """Build address dict với tên tỉnh/quận/phường."""
    province = (
        db.query(Province).filter(Province.code == addr.province_code).first()
        if addr.province_code
        else None
    )
    district = (
        db.query(District).filter(District.code == addr.district_code).first()
        if addr.district_code
        else None
    )
    ward = (
        db.query(Ward).filter(Ward.code == addr.ward_code).first()
        if addr.ward_code
        else None
    )

    province_name = province.name if province else addr.province_code
    district_name = district.name if district else addr.district_code
    ward_name = ward.name if ward else addr.ward_code
    full_address = ", ".join(
        part for part in [addr.address_line, ward_name, district_name, province_name] if part
    )

    return {
        "id": addr.id,
        "recipient_name": addr.recipient_name,
        "phone": addr.phone,
        "province_code": addr.province_code,
        "province_name": province_name,
        "district_code": addr.district_code,
        "district_name": district_name,
        "ward_code": addr.ward_code,
        "ward_name": ward_name,
        "address_line": addr.address_line,
        "full_address": full_address,
        "is_default": addr.is_default,
    }


def _normalize_region_code(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = value.strip()
    return text if text else None


def _resolve_region_codes(
    db: Session,
    province_code: Optional[str],
    district_code: Optional[str],
    ward_code: Optional[str],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    normalized_province = _normalize_region_code(province_code)
    normalized_district = _normalize_region_code(district_code)
    normalized_ward = _normalize_region_code(ward_code)

    provided_count = sum(
        1 for code in [normalized_province, normalized_district, normalized_ward] if code is not None
    )
    if provided_count == 0:
        return None, None, None

    if provided_count != 3:
        raise HTTPException(
            status_code=400,
            detail="Nếu chọn khu vực, vui lòng chọn đầy đủ Tỉnh/Thành phố, Quận/Huyện và Phường/Xã",
        )

    assert normalized_province is not None
    assert normalized_district is not None
    assert normalized_ward is not None
    _validate_address_codes(db, normalized_province, normalized_district, normalized_ward)
    return normalized_province, normalized_district, normalized_ward


def _validate_address_codes(db: Session, province_code: str, district_code: str, ward_code: str) -> None:
    province = db.query(Province).filter(Province.code == province_code).first()
    if not province:
        raise HTTPException(status_code=400, detail="province_code không hợp lệ")

    district = db.query(District).filter(District.code == district_code).first()
    if not district:
        raise HTTPException(status_code=400, detail="district_code không hợp lệ")
    if district.province_code != province.code:
        raise HTTPException(status_code=400, detail="district_code không thuộc province_code đã chọn")

    ward = db.query(Ward).filter(Ward.code == ward_code).first()
    if not ward:
        raise HTTPException(status_code=400, detail="ward_code không hợp lệ")
    if ward.district_code != district.code:
        raise HTTPException(status_code=400, detail="ward_code không thuộc district_code đã chọn")


def _extract_primary_image(raw_images: Any) -> Optional[str]:
    if raw_images is None:
        return None

    if isinstance(raw_images, list):
        for item in raw_images:
            text = str(item).strip()
            if text and text.lower() != "null":
                return text
        return None

    if isinstance(raw_images, dict):
        text = str(raw_images.get("url", "")).strip()
        return text if text else None

    text = str(raw_images).strip()
    if not text or text.lower() == "null":
        return None

    if text.startswith("[") or text.startswith("{"):
        try:
            parsed = json.loads(text)
            return _extract_primary_image(parsed)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None

    return text


def _get_or_create_mobile_cart(user_id: int, db: Session) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _mobile_cart_line_filter(db: Session, cart_id: int, product_id: int, variant_id: Optional[int]):
    query = db.query(CartItem).filter(
        CartItem.cart_id == cart_id,
        CartItem.product_id == product_id,
    )
    if variant_id is not None:
        query = query.filter(CartItem.variant_id == variant_id)
    else:
        query = query.filter(CartItem.variant_id.is_(None))
    return query


def _build_mobile_cart_response(cart: Cart, db: Session) -> dict:
    items_data = []
    subtotal = Decimal("0")

    # Lấy tất cả promotions đang active (flash sale + thường) để tránh query N+1
    from datetime import datetime, timezone as dt_timezone
    now_utc = datetime.now(dt_timezone.utc)
    active_promos = db.query(Promotion).filter(
        Promotion.status == "ACTIVE",
        Promotion.start_date <= now_utc,
        Promotion.end_date >= now_utc,
    ).all()

    # Sắp xếp theo item.id để đảm bảo thứ tự ổn định, không đổi vị trí sau mỗi update
    for item in sorted(cart.items, key=lambda x: x.id):
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue

        seller = db.query(User).filter(User.id == product.seller_id).first()
        category = db.query(Category).filter(Category.id == product.category_id).first() if product.category_id else None

        stock_quantity = get_available_stock(db, product, item.variant_id)

        variant = None
        if item.variant_id is not None:
            variant = db.query(ProductVariant).filter(
                ProductVariant.id == item.variant_id,
                ProductVariant.product_id == product.id,
            ).first()

        current_unit_price = get_unit_price(product, variant, db=db)
        line_subtotal = current_unit_price * item.quantity
        subtotal += line_subtotal

        # ── Xác định Flash Sale áp dụng cho sản phẩm này ─────────────────────
        flash_promo = None
        for promo in active_promos:
            if promo.is_flash_sale and _promotion_matches_product_scope(promo, product):
                flash_promo = promo
                break

        is_flash_sale = flash_promo is not None
        flash_sale_code = flash_promo.code if flash_promo else None
        flash_sale_ends_in_seconds: Optional[int] = None
        if flash_promo and flash_promo.end_date:
            end_aware = flash_promo.end_date
            if end_aware.tzinfo is None:
                from datetime import timezone as tz
                end_aware = end_aware.replace(tzinfo=tz.utc)
            delta = end_aware - now_utc
            flash_sale_ends_in_seconds = max(0, int(delta.total_seconds()))

        items_data.append(
            {
                "id": item.id,
                "product_id": product.id,
                "variant_id": item.variant_id,
                "seller_id": product.seller_id,
                "seller_name": seller.name if seller else "Cửa hàng Agrarian",
                "product_name": product.name,
                "product_image": _extract_primary_image(product.images),
                "unit_label": product.unit if hasattr(product, "unit") and product.unit else "1 sản phẩm",
                "location_label": category.name if category else "Nông trại Việt",
                "unit_price": str(current_unit_price),
                "original_price": str(product.price),  # Giá gốc trước khuyến mãi
                "quantity": item.quantity,
                "subtotal": str(line_subtotal),
                "stock_quantity": stock_quantity,
                "is_active": bool(product.is_active),
                # ── Flash Sale fields ──────────────────────────────────────────
                "is_flash_sale": is_flash_sale,
                "flash_sale_code": flash_sale_code,
                "flash_sale_ends_in_seconds": flash_sale_ends_in_seconds,
                # ── Category (dùng validate coupon scope CATEGORY) ─────────────
                "category_id": product.category_id,
            }
        )

    shipping_fee = Decimal("30000")
    discount_amount = Decimal("0")
    total_amount = subtotal + shipping_fee - discount_amount

    return {
        "items": items_data,
        "total_items": len(items_data),
        "subtotal": str(subtotal),
        "shipping_fee": str(shipping_fee),
        "discount_amount": str(discount_amount),
        "total_amount": str(total_amount),
        "updated_at": cart.updated_at.isoformat() if cart.updated_at else None,
    }



def _order_status_label(status: str) -> str:
    mapping = {
        "PENDING": "Chờ xác nhận",
        "CONFIRMED": "Đã xác nhận",
        "PROCESSING": "Đang xử lý",
        "SHIPPING": "Đang giao",
        "DELIVERED": "Đã giao",
        "CANCELLED": "Đã hủy",
    }
    return mapping.get(str(status or "").upper(), str(status or "Đang cập nhật"))



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

        # Lấy thông tin sản phẩm liên kết nếu có
        linked_product = None
        if p.product_id:
            prod = db.query(Product).filter(
                Product.id == p.product_id,
                Product.is_active == True
            ).first()
            if prod:
                linked_product = {
                    "id": prod.id,
                    "name": prod.name,
                    "price": str(prod.price),
                    "image": _extract_primary_image(prod.images),
                }

        post_list.append({
            "id": p.id,
            "title": p.title,
            "content": p.content[:200] + "..." if p.content and len(p.content) > 200 else p.content,
            "author_id": p.author_id,
            "author_name": author.name if author else "Unknown",
            "author_type": author.type if author else None,
            "images": p.images,
            "videos": p.videos,
            "product_id": p.product_id,
            "linked_product": linked_product,
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
# HOME API – Trang chủ aggregated (1 call)
# ==============================================================================

@router.get("/home", summary="Trang chủ aggregated")
async def get_mobile_home(
    db: Session = Depends(get_db)
):
    """
    Trả về toàn bộ data cần cho trang chủ mobile trong 1 request:
    - Danh mục
    - Sản phẩm nổi bật (featured)
    - Sản phẩm mới
    - Mã khuyến mãi đang hoạt động
    """
    # Categories
    categories = db.query(Category).filter(Category.is_active == True).all()
    cat_list = []
    for c in categories:
        product_count = db.query(Product).filter(
            Product.category_id == c.id,
            Product.status == ProductStatus.APPROVED,
            Product.is_active == True,
        ).count()
        cat_list.append({
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "image_url": c.image_url if hasattr(c, 'image_url') else None,
            "product_count": product_count,
        })

    # Featured products (OCOP or CLEAN_AGRICULTURE label, limit 10)
    featured_q = db.query(Product).filter(
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
        Product.label.in_(["OCOP", "CLEAN_AGRICULTURE"]),
    ).order_by(Product.created_at.desc()).limit(10).all()

    # New products (limit 20)
    new_q = db.query(Product).filter(
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    ).order_by(Product.created_at.desc()).limit(20).all()

    now = datetime.utcnow()
    active_promotions = db.query(Promotion).filter(
        Promotion.is_public == True,
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
    ).all()

    from datetime import timezone as _tz_home
    now_utc_home = now.replace(tzinfo=_tz_home.utc)

    def _build_product_card(p):
        producer = db.query(User).filter(User.id == p.seller_id).first()
        category = db.query(Category).filter(Category.id == p.category_id).first() if p.category_id else None
        review_stats = _get_product_review_stats(db, p.id)
        pricing = _build_product_pricing(p, active_promotions)
        flash = _build_flash_sale_info(p, active_promotions, now_utc_home)
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description[:150] + "..." if p.description and len(p.description) > 150 else p.description,
            "price": pricing["price"],
            "original_price": pricing["original_price"],
            "discount_amount": pricing["discount_amount"],
            "auto_promotion": pricing["auto_promotion"],
            "seller_id": p.seller_id,
            "seller_name": producer.name if producer else "Unknown",
            "category_id": p.category_id,
            "category_name": category.name if category else None,
            "label": p.label,
            "images": p.images,
            "stock_quantity": p.stock_quantity,
            "avg_rating": review_stats["avg_rating"],
            "review_count": review_stats["total_reviews"],
            # Chính sách đổi trả — App dùng để hiển thị badge
            "return_days": p.return_days,
            "return_fee_paid": p.return_fee_paid,
            # Flash Sale per-product
            "is_flash_sale": flash["is_flash_sale"],
            "flash_sale_code": flash["flash_sale_code"],
            "flash_sale_ends_in_seconds": flash["flash_sale_ends_in_seconds"],
            "flash_sale_discount": flash["flash_sale_discount"],
        }

    # Promotions (active, public)
    promos = sorted(active_promotions, key=lambda p: p.end_date)[:5]

    promo_list = [
        {
            "id": pr.id,
            "code": pr.code,
            "name": pr.name,
            "description": pr.description,
            "promotion_type": pr.promotion_type.value if hasattr(pr.promotion_type, 'value') else str(pr.promotion_type),
            "discount_value": str(pr.discount_value),
            "min_order_amount": str(pr.min_order_amount),
            "end_date": pr.end_date.isoformat(),
        }
        for pr in promos
    ]

    return {
        "success": True,
        "data": {
            "categories": cat_list,
            "featured_products": [_build_product_card(p) for p in featured_q],
            "new_products": [_build_product_card(p) for p in new_q],
            "promotions": promo_list,
        }
    }


# ==============================================================================
# PRODUCTS API - Cho người dùng xem sản phẩm (ENRICHED)
# ==============================================================================

@router.get("/products")
async def get_public_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    seller_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    label: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[Decimal] = Query(None),
    max_price: Optional[Decimal] = Query(None),
    sort_by: Optional[str] = Query(None, description="price_asc, price_desc, newest, rating"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách sản phẩm đã duyệt — ENRICHED cho mobile
    Public endpoint - không cần đăng nhập
    """
    query = db.query(Product).filter(
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    )

    if seller_id:
        query = query.filter(Product.seller_id == seller_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if label:
        query = query.filter(Product.label == label)
    if search:
        _s = _sanitize_search(search)
        query = query.filter(Product.name.ilike(f"%{_s}%"))
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    total = query.count()
    skip = (page - 1) * limit
    products = query.offset(skip).limit(limit).all()

    now = datetime.utcnow()
    active_promotions = db.query(Promotion).filter(
        Promotion.is_public == True,
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
    ).all()

    from datetime import timezone as _tz_products
    now_utc_products = now.replace(tzinfo=_tz_products.utc)

    product_list = []
    for p in products:
        producer = db.query(User).filter(User.id == p.seller_id).first()
        category = db.query(Category).filter(Category.id == p.category_id).first() if p.category_id else None
        review_stats = _get_product_review_stats(db, p.id)
        pricing = _build_product_pricing(p, active_promotions)
        flash = _build_flash_sale_info(p, active_promotions, now_utc_products)
        product_list.append({
            "id": p.id,
            "name": p.name,
            "description": p.description[:150] + "..." if p.description and len(p.description) > 150 else p.description,
            "price": pricing["price"],
            "original_price": pricing["original_price"],
            "discount_amount": pricing["discount_amount"],
            "auto_promotion": pricing["auto_promotion"],
            "seller_id": p.seller_id,
            "seller_name": producer.name if producer else "Unknown",
            "category_id": p.category_id,
            "category_name": category.name if category else None,
            "label": p.label,
            "images": p.images,
            "stock_quantity": p.stock_quantity,
            "avg_rating": review_stats["avg_rating"],
            "review_count": review_stats["total_reviews"],
            # Flash Sale per-product
            "is_flash_sale": flash["is_flash_sale"],
            "flash_sale_code": flash["flash_sale_code"],
            "flash_sale_ends_in_seconds": flash["flash_sale_ends_in_seconds"],
            "flash_sale_discount": flash["flash_sale_discount"],
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
    """Xem chi tiết sản phẩm — ENRICHED: store, variants, stock, VAT, reviews, media"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    producer = db.query(User).filter(User.id == product.seller_id).first()
    category = db.query(Category).filter(Category.id == product.category_id).first() if product.category_id else None

    # Store info
    store = db.query(Store).filter(
        Store.seller_id == product.seller_id, Store.is_active == True
    ).first()
    store_payload = None
    if store:
        store_payload = {
            "id": store.id,
            "store_name": store.store_name,
            "slug": store.slug,
            "logo_url": store.logo_url,
            "description": store.description,
        }

    # Variants
    variants = db.query(ProductVariant).filter(
        ProductVariant.product_id == product.id,
        ProductVariant.is_active == True,
    ).all()
    variants_payload = [
        {
            "id": v.id,
            "sku": v.sku,
            "variant_name": v.variant_name,
            "price": str(v.price),
            "stock_quantity": v.stock_quantity,
            "image_url": v.image_url,
        }
        for v in variants
    ]

    # Media
    media_items = db.query(ProductMedia).filter(
        ProductMedia.product_id == product.id
    ).order_by(ProductMedia.sort_order).all()
    media_payload = [
        {
            "id": m.id,
            "media_type": m.media_type.value if hasattr(m.media_type, 'value') else str(m.media_type),
            "url": m.url,
            "alt_text": m.alt_text,
            "is_primary": m.is_primary,
        }
        for m in media_items
    ]

    # Reviews summary
    review_stats = _get_product_review_stats(db, product.id)

    now = datetime.utcnow()
    active_promotions = db.query(Promotion).filter(
        Promotion.is_public == True,
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
    ).all()
    pricing = _build_product_pricing(product, active_promotions)
    from datetime import timezone as _tz_detail
    flash = _build_flash_sale_info(product, active_promotions, now.replace(tzinfo=_tz_detail.utc))

    # Traceability
    origin = db.query(ProductOrigin).filter(
        ProductOrigin.product_id == product.id,
        ProductOrigin.verification_status == OriginStatus.VERIFIED,
    ).first()
    # Lấy tất cả certificates trừ REJECTED để mobile hiển thị cả PENDING
    # với badge "Đang xác minh" — tránh user nhầm tưởng SP không có chứng nhận
    certificates = db.query(ProductCertificate).filter(
        ProductCertificate.product_id == product.id,
        ProductCertificate.verification_status != CertificateStatus.REJECTED,
    ).order_by(
        # VERIFIED lên trước, PENDING xuống sau
        ProductCertificate.verification_status.asc(),
        ProductCertificate.id.asc(),
    ).all()

    origin_payload = None
    if origin:
        origin_payload = {
            "village_name": origin.village_name,
            "facility_name": origin.facility_name,
            "region_id": origin.region_id,
            "region_name": None,
            "seller_name": origin.seller_name,
            "batch_number": origin.batch_number,
            "production_date": origin.production_date.isoformat() if origin.production_date else None,
            "expiry_date": origin.expiry_date.isoformat() if origin.expiry_date else None,
            "ingredients": origin.ingredients,
            "process_summary": origin.process_summary,
            "images": origin.images,
            "usage_instructions": origin.usage_instructions,
            "storage_instructions": origin.storage_instructions,
            "warnings": origin.warnings,
        }
        if origin.region_id:
            region = db.query(Region).filter(Region.id == origin.region_id).first()
            origin_payload["region_name"] = region.name if region else None

    certificates_payload = [
        {
            "certificate_name": cert.certificate_name,
            "certificate_number": cert.certificate_number,
            "issued_by": cert.issued_by,
            "issue_date": cert.issue_date.isoformat() if cert.issue_date else None,
            "expiry_date": cert.expiry_date.isoformat() if cert.expiry_date else None,
            "document_url": cert.document_url,
            # Mobile app dùng field này để hiện badge "Đã xác minh" / "Đang xác minh"
            "verification_status": cert.verification_status.value
            if hasattr(cert.verification_status, "value")
            else str(cert.verification_status),
        }
        for cert in certificates
    ]

    return {
        "success": True,
        "data": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": pricing["price"],
            "original_price": pricing["original_price"],
            "discount_amount": pricing["discount_amount"],
            "auto_promotion": pricing["auto_promotion"],
            "stock_quantity": product.stock_quantity,
            "vat_rate": str(product.vat_rate) if product.vat_rate else "10.00",
            "unit": product.unit if hasattr(product, 'unit') and product.unit else None,
            "weight": str(product.weight) if hasattr(product, 'weight') and product.weight else None,
            "sku": product.sku if hasattr(product, 'sku') and product.sku else None,
            "category_id": product.category_id,
            "category_name": category.name if category else None,
            "seller_id": product.seller_id,
            "seller_name": producer.name if producer else "Unknown",
            "producer_type": producer.type if producer else None,
            "store": store_payload,
            "label": product.label,
            "images": product.images,
            "media": media_payload,
            "variants": variants_payload,
            "reviews_summary": review_stats,
            "traceability": {
                "origin": origin_payload,
                "certificates": certificates_payload,
            },
            # Chính sách đổi trả — App hiển thị badge dưới tên sản phẩm
            "return_days": product.return_days,
            "return_fee_paid": product.return_fee_paid,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            # Flash Sale per-product
            "is_flash_sale": flash["is_flash_sale"],
            "flash_sale_code": flash["flash_sale_code"],
            "flash_sale_ends_in_seconds": flash["flash_sale_ends_in_seconds"],
            "flash_sale_discount": flash["flash_sale_discount"],
        }
    }


# ==============================================================================
# SHOPS API – Trang cửa hàng
# ==============================================================================

@router.get("/shops/{seller_id}", summary="Trang cửa hàng")
async def get_shop_page(
    seller_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lấy thông tin cửa hàng + sản phẩm của seller."""
    seller = db.query(User).filter(User.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Cửa hàng không tồn tại")

    store = db.query(Store).filter(
        Store.seller_id == seller_id, Store.is_active == True
    ).first()

    # Tổng sản phẩm
    total_products = db.query(Product).filter(
        Product.seller_id == seller_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    ).count()

    # Avg rating từ tất cả product reviews
    all_product_ids = [
        pid for (pid,) in db.query(Product.id).filter(
            Product.seller_id == seller_id,
            Product.status == ProductStatus.APPROVED,
        ).all()
    ]
    shop_stats = {"avg_rating": 0.0, "total_reviews": 0}
    if all_product_ids:
        stats = db.query(
            sql_func.count(Review.id).label("total"),
            sql_func.avg(Review.rating).label("avg"),
        ).filter(Review.product_id.in_(all_product_ids)).first()
        shop_stats = {
            "avg_rating": round(float(stats.avg), 1) if stats.avg else 0.0,
            "total_reviews": stats.total or 0,
        }

    # Shop info
    shop_info = {
        "seller_id": seller_id,
        "seller_name": seller.name,
        "store_name": store.store_name if store else seller.name,
        "slug": store.slug if store else None,
        "logo_url": store.logo_url if store else None,
        "description": store.description if store else None,
        "contact_phone": store.contact_phone if store else None,
        "total_products": total_products,
        "avg_rating": shop_stats["avg_rating"],
        "total_reviews": shop_stats["total_reviews"],
        "member_since": seller.created_at.isoformat() if seller.created_at else None,
    }

    # Products
    product_q = db.query(Product).filter(
        Product.seller_id == seller_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    )
    if search:
        _s = _sanitize_search(search)
        product_q = product_q.filter(Product.name.ilike(f"%{_s}%"))

    total = product_q.count()
    skip = (page - 1) * limit
    products = product_q.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    now = datetime.utcnow()
    active_promotions = db.query(Promotion).filter(
        Promotion.is_public == True,
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
    ).all()

    from datetime import timezone as _tz_shop
    now_utc_shop = now.replace(tzinfo=_tz_shop.utc)

    product_list = []
    for p in products:
        r_stats = _get_product_review_stats(db, p.id)
        pricing = _build_product_pricing(p, active_promotions)
        flash = _build_flash_sale_info(p, active_promotions, now_utc_shop)
        product_list.append({
            "id": p.id,
            "name": p.name,
            "price": pricing["price"],
            "original_price": pricing["original_price"],
            "discount_amount": pricing["discount_amount"],
            "auto_promotion": pricing["auto_promotion"],
            "images": p.images,
            "label": p.label,
            "stock_quantity": p.stock_quantity,
            "avg_rating": r_stats["avg_rating"],
            "review_count": r_stats["total_reviews"],
            # Flash Sale per-product
            "is_flash_sale": flash["is_flash_sale"],
            "flash_sale_code": flash["flash_sale_code"],
            "flash_sale_ends_in_seconds": flash["flash_sale_ends_in_seconds"],
            "flash_sale_discount": flash["flash_sale_discount"],
        })

    return {
        "success": True,
        "data": {
            "shop": shop_info,
            "products": product_list,
        },
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }


# ==============================================================================
# PROMOTIONS API – Áp mã giảm giá
# ==============================================================================

@router.post("/promotions/apply", summary="Áp mã giảm giá")
async def apply_promotion(
    promo_data: ApplyPromotionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate & tính discount cho coupon code tại bước checkout."""
    now = datetime.utcnow()
    promo = db.query(Promotion).filter(
        Promotion.code == promo_data.coupon_code.upper(),
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now,
    ).first()

    if not promo:
        return {"success": True, "data": {"valid": False, "message": "Mã khuyến mãi không tồn tại hoặc đã hết hạn"}}

    can_use, reason = _can_user_use_promotion(db, promo, current_user.id)
    if not can_use:
        return {"success": True, "data": {"valid": False, "message": reason}}

    scope = _promotion_scope(promo)
    if scope == "SELLER":
        if promo_data.seller_id is None:
            return {"success": True, "data": {"valid": False, "message": "Mã này cần thông tin seller để kiểm tra"}}
        if not promo.seller_id or promo_data.seller_id != promo.seller_id:
            return {"success": True, "data": {"valid": False, "message": "Mã không áp dụng cho cửa hàng này"}}

    if scope == "PRODUCT":
        if not promo_data.product_ids:
            return {"success": True, "data": {"valid": False, "message": "Mã này cần danh sách sản phẩm để kiểm tra"}}
        scoped_product_ids = _parse_scope_ids(promo.applicable_product_ids)
        request_product_ids = {int(pid) for pid in promo_data.product_ids}
        if not scoped_product_ids.intersection(request_product_ids):
            return {"success": True, "data": {"valid": False, "message": "Mã không áp dụng cho sản phẩm đã chọn"}}

    if scope == "CATEGORY":
        if not promo_data.category_ids:
            return {"success": True, "data": {"valid": False, "message": "Mã này cần danh mục sản phẩm để kiểm tra"}}
        scoped_category_ids = _parse_scope_ids(promo.applicable_category_ids)
        request_category_ids = {int(cid) for cid in promo_data.category_ids}
        if not scoped_category_ids.intersection(request_category_ids):
            return {"success": True, "data": {"valid": False, "message": "Mã không áp dụng cho danh mục đã chọn"}}

    if promo.seller_id and promo_data.seller_id and promo_data.seller_id != promo.seller_id:
        return {"success": True, "data": {"valid": False, "message": "Mã không áp dụng cho cửa hàng này"}}

    # Check min order
    if promo_data.subtotal < promo.min_order_amount:
        return {
            "success": True,
            "data": {
                "valid": False,
                "message": f"Đơn hàng tối thiểu {promo.min_order_amount:,.0f}đ để áp mã này",
            }
        }

    # Calculate discount
    ptype = _promotion_type(promo)
    discount = _calculate_discount(promo, promo_data.subtotal)

    new_subtotal = promo_data.subtotal - discount

    return {
        "success": True,
        "data": {
            "valid": True,
            "promotion_id": promo.id,
            "promotion_name": promo.name,
            "promotion_type": ptype,
            "applicable_to": scope,
            "discount_amount": str(discount),
            "new_subtotal": str(new_subtotal),
            "message": f"Áp mã thành công: Giảm {discount:,.0f}đ",
        }
    }


# ==============================================================================
# SHOPPING API - Giỏ hàng và Thanh toán (ENRICHED)
# ==============================================================================

@router.get("/cart", summary="Lấy giỏ hàng mobile")
async def get_mobile_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = _get_or_create_mobile_cart(current_user.id, db)
    return {
        "success": True,
        "data": _build_mobile_cart_response(cart, db),
    }


@router.post("/cart/items", summary="Thêm sản phẩm vào giỏ hàng mobile")
async def add_mobile_cart_item(
    item_data: CartItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == item_data.product_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại hoặc chưa được duyệt")

    _, unit_price = validate_line_for_sale(db, product, item_data.quantity, item_data.variant_id)

    cart = _get_or_create_mobile_cart(current_user.id, db)

    existing_item = _mobile_cart_line_filter(db, cart.id, item_data.product_id, item_data.variant_id).first()

    if existing_item:
        new_quantity = existing_item.quantity + item_data.quantity
        validate_line_for_sale(db, product, new_quantity, item_data.variant_id)
        existing_item.quantity = new_quantity
        existing_item.unit_price = unit_price
        if item_data.variant_id is not None:
            existing_item.variant_id = item_data.variant_id
    else:
        db.add(
            CartItem(
                cart_id=cart.id,
                product_id=item_data.product_id,
                variant_id=item_data.variant_id,
                quantity=item_data.quantity,
                unit_price=unit_price,
            )
        )

    db.commit()
    db.refresh(cart)

    return {
        "success": True,
        "message": "Đã thêm vào giỏ hàng",
        "data": _build_mobile_cart_response(cart, db),
    }


@router.put("/cart/items/{item_id}", summary="Cập nhật số lượng item giỏ hàng mobile")
async def update_mobile_cart_item(
    item_id: int,
    item_data: UpdateCartItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = _get_or_create_mobile_cart(current_user.id, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item không tồn tại trong giỏ hàng")

    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.status == ProductStatus.APPROVED,
        Product.is_active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không còn khả dụng")

    _, unit_price = validate_line_for_sale(db, product, item_data.quantity, item.variant_id)
    item.quantity = item_data.quantity
    item.unit_price = unit_price

    db.commit()
    db.refresh(cart)

    return {
        "success": True,
        "message": "Đã cập nhật giỏ hàng",
        "data": _build_mobile_cart_response(cart, db),
    }


@router.delete("/cart/items/{item_id}", summary="Xóa item giỏ hàng mobile")
async def remove_mobile_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = _get_or_create_mobile_cart(current_user.id, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item không tồn tại trong giỏ hàng")

    db.delete(item)
    db.commit()
    db.refresh(cart)

    return {
        "success": True,
        "message": "Đã xóa sản phẩm khỏi giỏ hàng",
        "data": _build_mobile_cart_response(cart, db),
    }


@router.delete("/cart", summary="Xóa toàn bộ giỏ hàng mobile")
async def clear_mobile_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()

    return {
        "success": True,
        "message": "Đã xóa toàn bộ giỏ hàng",
    }

@router.post("/checkout")
async def create_order(
    checkout_data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo đơn hàng từ giỏ hàng.
    Hỗ trợ: coupon_code, BANK_TRANSFER (giả lập auto-paid), PLATFORM_CREDITS payment method.
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
        sid = product.seller_id
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

    seller_ids = list(sellers_map.keys())
    if len(seller_ids) != 1:
        raise HTTPException(
            status_code=400,
            detail="Kiểu A: Giỏ hàng chỉ được chứa sản phẩm của một người bán",
        )

    detected_seller_id = seller_ids[0]
    if checkout_data.seller_id is not None and checkout_data.seller_id != detected_seller_id:
        raise HTTPException(
            status_code=400,
            detail="seller_id không khớp với sản phẩm trong giỏ hàng",
        )

    items_of_seller = sellers_map[detected_seller_id]

    # ── Bước 1.5: Validate coupon user nhập ────────────────────────────────
    # Lưu ý: unit_price ở items_of_seller đã là giá bán sau flash sale/auto product promo
    # từ validate_line_for_sale(). Không auto-apply thêm promotion ở checkout,
    # nếu không VNPay/COD sẽ bị giảm giá lần 2 trên subtotal đã giảm.
    coupon_discount = Decimal("0")
    applied_promo = None

    if checkout_data.coupon_code:
        now = datetime.utcnow()
        promo = db.query(Promotion).filter(
            Promotion.code == checkout_data.coupon_code.upper(),
            Promotion.status == PromotionStatus.ACTIVE,
            Promotion.start_date <= now,
            Promotion.end_date >= now,
        ).first()

        if not promo:
            raise HTTPException(status_code=400, detail="Mã khuyến mãi không tồn tại hoặc đã hết hạn")

        # FOR UPDATE: khóa row promotion để tránh concurrent overuse
        promo = db.query(Promotion).filter(Promotion.id == promo.id).with_for_update().first()

        can_use, reason = _can_user_use_promotion(db, promo, current_user.id)
        if not can_use:
            raise HTTPException(status_code=400, detail=reason)

        if not _promotion_matches_cart_scope(promo, items_of_seller):
            raise HTTPException(status_code=400, detail="Mã khuyến mãi không áp dụng cho giỏ hàng này")

        eligible_subtotal = _eligible_subtotal_for_cart_promotion(promo, items_of_seller)
        if eligible_subtotal < promo.min_order_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Đơn hàng tối thiểu {promo.min_order_amount:,.0f}đ để áp mã này",
            )

        coupon_discount = _calculate_discount(promo, eligible_subtotal)
        if coupon_discount <= 0:
            raise HTTPException(status_code=400, detail="Mã khuyến mãi không mang lại giảm giá cho giỏ hàng")

        applied_promo = promo

    # ── Bước 2: Tạo 1 đơn hàng duy nhất cho 1 seller (Kiểu A) ───────────────
    platform_fee_percentage = Decimal("10.0")  # Phí nền tảng 10% trên subtotal
    subtotal = sum(i["total_price"] for i in items_of_seller)
    shipping_fee = Decimal("30000")
    discount_amount = coupon_discount
    total_amount = subtotal + shipping_fee - discount_amount
    platform_fee_amount = subtotal * platform_fee_percentage / Decimal("100")

    # ── Tính VAT từng sản phẩm (VAT included trong giá niêm yết) ─────────────
    # Công thức: VAT = giá_bán × rate / (100 + rate)  [VAT đã gộp trong giá]
    # Mặc định hệ thống: 10% nếu sản phẩm chưa khai báo vat_rate
    # Nền tảng giữ VAT và nộp thuế thay seller.
    DEFAULT_VAT_RATE = Decimal("10.0")   # mặc định 10%
    tax_detail = []
    total_vat_amount = Decimal("0")
    for item_data in items_of_seller:
        p = item_data["product"]
        # Dùng vat_rate của sản phẩm; fallback về 10% nếu chưa khai báo
        vat_rate = Decimal(str(p.vat_rate)) if p.vat_rate is not None else DEFAULT_VAT_RATE
        item_price = item_data["total_price"]
        if vat_rate > 0:
            item_vat = (item_price * vat_rate / (Decimal("100") + vat_rate)).quantize(Decimal("0.01"))
        else:
            item_vat = Decimal("0")
        item_data["_tax_amount"] = item_vat  # dùng khi tạo OrderItem
        total_vat_amount += item_vat
        tax_detail.append({
            "product_id":   p.id,
            "product_name": p.name,
            "vat_rate":     float(vat_rate),
            "item_total":   float(item_price),
            "vat_amount":   float(item_vat),
        })
    total_vat_amount = total_vat_amount.quantize(Decimal("0.01"))

    # Seller nhận = subtotal − phí nền tảng 10% − VAT đã tách ra
    seller_amount = subtotal - platform_fee_amount - total_vat_amount

    import json as _json
    tax_breakdown_json = _json.dumps({
        "total_vat": float(total_vat_amount),
        "items": tax_detail,
    }, ensure_ascii=False)

    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # Payment status: giả lập chuyển khoản + credits được auto PAID.
    auto_paid_methods = {"PLATFORM_CREDITS", "BANK_TRANSFER"}
    payment_status = "PAID" if checkout_data.payment_method in auto_paid_methods else "UNPAID"

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
        seller_id=detected_seller_id,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        total_amount=total_amount,
        vat_amount=total_vat_amount,
        platform_fee_percentage=platform_fee_percentage,
        platform_fee_amount=platform_fee_amount,
        seller_amount=seller_amount,
        status=OrderStatus.PENDING,
        payment_method=checkout_data.payment_method,
        payment_status=payment_status,
        customer_note=checkout_data.customer_note,
        coupon_code=checkout_data.coupon_code or (applied_promo.code if applied_promo else None),
        tax_breakdown=tax_breakdown_json,
    )
    db.add(new_order)
    db.flush()

    for item_data in items_of_seller:
        p = item_data["product"]
        db.add(
            OrderItem(
                order_id=new_order.id,
                product_id=p.id,
                seller_id=p.seller_id,
                variant_id=item_data["variant_id"],
                product_name=p.name,
                product_image=p.images,
                unit_price=item_data["unit_price"],
                quantity=item_data["quantity"],
                total_price=item_data["total_price"],
                tax_amount=item_data.get("_tax_amount", Decimal("0")),
            )
        )
        decrement_stock(db, p, item_data["quantity"], item_data["variant_id"])

    # Ghi promo usage — dùng atomic SQL UPDATE để tránh race condition used_count
    if applied_promo:
        db.add(PromotionUsage(
            promotion_id=applied_promo.id,
            user_id=current_user.id,
            order_id=new_order.id,
            discount_amount=discount_amount,
        ))
        # Atomic increment — an toàn với concurrent requests
        db.query(Promotion).filter(Promotion.id == applied_promo.id).update(
            {"used_count": Promotion.used_count + 1},
            synchronize_session=False,
        )

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

    # [NOTIFICATION O1] Thông báo cho Seller: có đơn hàng mới
    customer_name_val = checkout_data.customer_name or current_user.name or "Khách hàng"
    notify_new_order_to_seller(
        db=db,
        seller_id=detected_seller_id,
        order_id=new_order.id,
        order_number=order_number,
        customer_name=customer_name_val,
        total_amount=total_amount,
    )

    # [NOTIFICATION O2] Thông báo cho Buyer: đặt hàng thành công
    notify_order_placed_to_buyer(
        db=db,
        buyer_id=current_user.id,
        order_id=new_order.id,
        order_number=order_number,
        total_amount=total_amount,
    )

    # [CHAT] Ghi thông báo đơn hàng vào Firestore — chỉ seller thấy trong tab Chat
    try:
        from app.services.firebase_service import send_order_notification_to_chat
        # Tóm tắt danh sách sản phẩm (tối đa 3 dòng)
        item_lines = [
            f"{d['product'].name} x{d['quantity']}"
            for d in items_of_seller[:3]
        ]
        if len(items_of_seller) > 3:
            item_lines.append(f"... và {len(items_of_seller) - 3} sản phẩm khác")
        items_summary = ", ".join(item_lines)

        # Lấy shop_name từ Store hoặc User
        seller_user = db.query(User).filter(User.id == detected_seller_id).first()
        shop_name = seller_user.name if seller_user else f"Shop #{detected_seller_id}"

        send_order_notification_to_chat(
            buyer_id=current_user.id,
            seller_id=detected_seller_id,
            buyer_name=customer_name_val,
            shop_name=shop_name,
            order_number=order_number,
            total_amount=f"{int(total_amount):,}đ",
            items_summary=items_summary,
        )
    except Exception as _chat_err:
        # Không để lỗi chat ảnh hưởng đến đơn hàng
        import logging as _log
        _log.getLogger(__name__).warning(
            "[Checkout] Chat notification failed (non-critical): %s", _chat_err
        )

    # ── Bước 4: Xóa các cart items đã checkout thành công ──────────────────
    # Chỉ xóa đúng các items user vừa đặt (theo product_id + variant_id)
    # để không ảnh hưởng các sản phẩm còn lại trong giỏ (nếu có)
    try:
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
        if cart:
            checked_out_product_ids = {item.product_id for item in checkout_data.items}
            checked_out_variant_ids = {
                (item.product_id, item.variant_id) for item in checkout_data.items
            }
            cart_items_to_remove = db.query(CartItem).filter(
                CartItem.cart_id == cart.id,
                CartItem.product_id.in_(checked_out_product_ids),
            ).all()
            for cart_item in cart_items_to_remove:
                if (cart_item.product_id, cart_item.variant_id) in checked_out_variant_ids:
                    db.delete(cart_item)
    except Exception as e:
        import logging as _logging
        _logging.getLogger(__name__).warning("[Checkout] Không thể clear cart: %s", e)

    db.commit()

    return {
        "success": True,
        "message": "Đặt hàng thành công",
        "data": {
            "order_id": new_order.id,
            "order_number": new_order.order_number,
            "seller_id": detected_seller_id,
            "total_amount": str(total_amount),
            "discount_amount": str(discount_amount),
            "applied_promotion": (
                {
                    "id": applied_promo.id,
                    "code": applied_promo.code,
                    "name": applied_promo.name,
                    "auto_applied": checkout_data.coupon_code is None,
                }
                if applied_promo
                else None
            ),
            "status": "PENDING",
            "payment_method": checkout_data.payment_method,
        },
    }


# ==============================================================================
# ORDERS API – Enriched (items, seller, timeline)
# ==============================================================================

_RETURN_TERMINAL_STATUSES = {ReturnStatus.CANCELLED, ReturnStatus.REJECTED}


def _serialize_return_request_mobile(r: ReturnRequest) -> dict:
    """Serialize return request cho mobile app (đơn hàng + yêu cầu của tôi)."""
    return {
        "id": r.id,
        "order_id": r.order_id,
        "return_type": r.return_type.value if hasattr(r.return_type, "value") else str(r.return_type),
        "reason": r.reason,
        "status": r.status.value if hasattr(r.status, "value") else str(r.status),
        "seller_note": r.seller_note,
        "seller_handled_at": r.seller_handled_at.isoformat() if r.seller_handled_at else None,
        "admin_note": r.admin_note,
        "handled_at": r.handled_at.isoformat() if r.handled_at else None,
        "refund_amount": r.refund_amount,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def _is_active_return_status(status) -> bool:
    if hasattr(status, "value"):
        status = status.value
    return str(status).upper() not in {s.value for s in _RETURN_TERMINAL_STATUSES}


def _get_latest_returns_for_orders(db: Session, user_id: int, order_ids: list) -> dict:
    """Lấy yêu cầu đổi/trả mới nhất theo order_id (một đơn một bản ghi hiển thị)."""
    if not order_ids:
        return {}
    returns = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.user_id == user_id,
            ReturnRequest.order_id.in_(order_ids),
        )
        .order_by(ReturnRequest.created_at.desc())
        .all()
    )
    result: dict = {}
    for r in returns:
        if r.order_id not in result:
            result[r.order_id] = r
    return result


@router.get("/orders/my")
async def get_my_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách đơn hàng — ENRICHED: trả thêm items, seller_name, first_item_image"""
    query = db.query(Order).filter(Order.customer_id == current_user.id, Order.is_active == True)

    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    skip = (page - 1) * limit
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    order_list = []

    # Dùng raw SQL để tránh SQLAlchemy Enum load lỗi khi DB có giá trị enum không hợp lệ
    from sqlalchemy import text as _sql_text
    _rev_result = db.execute(
        _sql_text(
            "SELECT DISTINCT order_item_id FROM reviews "
            "WHERE user_id = :uid AND order_item_id IS NOT NULL"
        ),
        {"uid": current_user.id}
    )
    # Dùng order_item_id thay vì product_id để tránh false positive:
    # nếu user đã review SP X từ đơn cũ, đơn mới cũng chứa SP X
    # → product_id match → has_reviewed sai.
    # order_item_id gắn với đơn cụ thể nên chính xác hơn.
    reviewed_order_item_ids = {row[0] for row in _rev_result.fetchall()}

    return_map = _get_latest_returns_for_orders(db, current_user.id, [o.id for o in orders])

    for o in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        seller = db.query(User).filter(User.id == o.seller_id).first()
        first_image = _extract_first_media_url(items[0].product_image) if items else None

        # Kiểm tra đơn này đã có ít nhất 1 order_item được review chưa
        raw_status = o.status.value if hasattr(o.status, 'value') else str(o.status)
        is_delivered = raw_status.upper() == "DELIVERED"
        order_item_ids_in_order = [i.id for i in items if i.id is not None]
        has_reviewed = (
            is_delivered
            and len(order_item_ids_in_order) > 0
            and bool(set(order_item_ids_in_order) & reviewed_order_item_ids)
        )

        ret_req = return_map.get(o.id)
        return_payload = _serialize_return_request_mobile(ret_req) if ret_req else None
        has_return_request = ret_req is not None and _is_active_return_status(ret_req.status)

        order_list.append({
            "id": o.id,
            "order_number": o.order_number,
            "seller_name": seller.name if seller else None,
            "total_amount": str(o.total_amount),
            "status": raw_status,
            "payment_method": o.payment_method.value if hasattr(o.payment_method, 'value') else str(o.payment_method),
            "payment_status": o.payment_status,
            "item_count": len(items),
            "first_item_image": first_image,
            "has_reviewed": has_reviewed,  # ← Flutter dùng field này để hiển thị nút
            "has_return_request": has_return_request,
            "return_request": return_payload,
            # delivered_at — Flutter dùng để tính deadline đánh giá (30 ngày) và đổi trả (7 ngày)
            "delivered_at": o.delivered_at.isoformat() if o.delivered_at else None,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "product_image": _extract_first_media_url(item.product_image),
                    "unit_price": str(item.unit_price),
                    "quantity": item.quantity,
                    "total_price": str(item.total_price),
                }
                for item in items
            ],
            "created_at": o.created_at.isoformat()
        })

    return {
        "success": True,
        "data": order_list,
        "meta": {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
    }

REVIEW_DEADLINE_DAYS = 5  # Số ngày được phép đánh giá sau khi nhận hàng


# ==============================================================================
# PENDING REVIEWS — phải đặt TRƯỚC route /orders/my/{order_id} để tránh conflict
# ==============================================================================

@router.get("/orders/my/pending-reviews", summary="Danh sách sản phẩm cần đánh giá")
async def get_pending_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trả về danh sách ORDER ITEM của các đơn DELIVERED mà user chưa đánh giá.
    - Chỉ hiển thị trong vòng REVIEW_DEADLINE_DAYS ngày kể từ delivered_at.
    - Mỗi item có đủ thông tin để render card đánh giá.
    """
    deadline_cutoff = datetime.utcnow() - timedelta(days=REVIEW_DEADLINE_DAYS)

    # Lấy tất cả đơn DELIVERED của user, còn trong deadline
    delivered_orders = db.query(Order).filter(
        Order.customer_id == current_user.id,
        Order.status == OrderStatus.DELIVERED,
        Order.delivered_at >= deadline_cutoff,
    ).all()

    if not delivered_orders:
        return {"success": True, "data": [], "meta": {"total": 0}}

    order_ids = [o.id for o in delivered_orders]
    order_map = {o.id: o for o in delivered_orders}

    # Lấy tất cả order items trong các đơn đó
    all_items = db.query(OrderItem).filter(
        OrderItem.order_id.in_(order_ids)
    ).all()

    if not all_items:
        return {"success": True, "data": [], "meta": {"total": 0}}

    # Lấy tập product_id đã được review bởi user này
    reviewed_product_ids = set(
        r.product_id for r in db.query(Review.product_id).filter(
            Review.user_id == current_user.id,
            Review.product_id.in_([i.product_id for i in all_items]),
        ).all()
    )

    pending_list = []
    for item in all_items:
        if item.product_id in reviewed_product_ids:
            continue  # Đã đánh giá sản phẩm này rồi

        order = order_map.get(item.order_id)
        if not order or not order.delivered_at:
            continue

        delivered_at = order.delivered_at
        if delivered_at.tzinfo is not None:
            from datetime import timezone
            deadline_cutoff_aware = datetime.now(timezone.utc) - timedelta(days=REVIEW_DEADLINE_DAYS)
            if delivered_at < deadline_cutoff_aware:
                continue
        else:
            if delivered_at < deadline_cutoff:
                continue

        days_left = REVIEW_DEADLINE_DAYS - (
            datetime.utcnow() - (delivered_at.replace(tzinfo=None) if delivered_at.tzinfo else delivered_at)
        ).days
        days_left = max(0, days_left)

        pending_list.append({
            "order_id": item.order_id,
            "order_number": order.order_number,
            "order_item_id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "product_image": _extract_first_media_url(item.product_image),
            "unit_price": str(item.unit_price),
            "quantity": item.quantity,
            "delivered_at": delivered_at.isoformat(),
            "days_left": days_left,
        })

    # Sắp xếp: ít ngày còn lại nhất lên đầu (sắp hết hạn)
    pending_list.sort(key=lambda x: x["days_left"])

    return {
        "success": True,
        "data": pending_list,
        "meta": {"total": len(pending_list)},
    }


@router.get("/orders/my/{order_id}")
async def get_my_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xem chi tiết đơn hàng — ENRICHED: timeline, shipment, can_cancel, can_review"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    seller = db.query(User).filter(User.id == order.seller_id).first()

    # Timeline
    logs = db.query(OrderStatusLog).filter(
        OrderStatusLog.order_id == order.id
    ).order_by(OrderStatusLog.timestamp.asc()).all()
    timeline = [
        {
            "status": log.new_status,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "actor_role": log.role,
            "note": log.note,
        }
        for log in logs
    ]

    # Shipment info
    shipment = db.query(Shipment).filter(Shipment.order_id == order.id).first()
    shipment_info = None
    if shipment:
        shipment_info = {
            "tracking_code": shipment.tracking_code,
            "provider": shipment.provider.value if hasattr(shipment.provider, 'value') else str(shipment.provider) if shipment.provider else None,
            "status": shipment.status.value if hasattr(shipment.status, 'value') else str(shipment.status) if shipment.status else None,
            "fee": str(shipment.fee) if shipment.fee else None,
        }

    # Capabilities
    current_status = order.status if hasattr(order.status, 'value') else order.status
    can_cancel = current_status in (OrderStatus.PENDING, OrderStatus.CONFIRMED)
    can_review = current_status == OrderStatus.DELIVERED

    # Kiểm tra user đã review TẤT CẢ sản phẩm trong đơn chưa
    has_reviewed = False
    if can_review and items:
        product_ids_in_order = [i.product_id for i in items if i.product_id]
        if product_ids_in_order:
            reviewed_ids = {
                r.product_id
                for r in db.query(Review.product_id).filter(
                    Review.user_id == current_user.id,
                    Review.product_id.in_(product_ids_in_order),
                ).all()
            }
            # Coi là "đã review" nếu ít nhất 1 sản phẩm đã được review
            has_reviewed = len(reviewed_ids) > 0

    ret_req = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.order_id == order.id,
            ReturnRequest.user_id == current_user.id,
        )
        .order_by(ReturnRequest.created_at.desc())
        .first()
    )
    return_payload = _serialize_return_request_mobile(ret_req) if ret_req else None
    has_return_request = ret_req is not None and _is_active_return_status(ret_req.status)

    return {
        "success": True,
        "data": {
            "id": order.id,
            "order_number": order.order_number,
            "seller_id": order.seller_id,
            "seller_name": seller.name if seller else None,
            # ✅ Thêm customer_name và customer_phone để app hiển thị đúng
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "subtotal": str(order.subtotal),
            "shipping_fee": str(order.shipping_fee),
            "discount_amount": str(order.discount_amount),
            "total_amount": str(order.total_amount),
            "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
            "payment_method": order.payment_method.value if hasattr(order.payment_method, 'value') else str(order.payment_method),
            "payment_status": order.payment_status,
            "shipping_address": order.shipping_address,
            "customer_note": order.customer_note,
            "coupon_code": order.coupon_code,
            "can_cancel": can_cancel,
            "can_review": can_review,
            "has_reviewed": has_reviewed,
            "has_return_request": has_return_request,
            "return_request": return_payload,
            "created_at": order.created_at.isoformat(),
            "confirmed_at": order.confirmed_at.isoformat() if order.confirmed_at else None,
            "shipped_at": order.shipped_at.isoformat() if order.shipped_at else None,
            "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "product_image": _extract_first_media_url(item.product_image),
                    "unit_price": str(item.unit_price),
                    "quantity": item.quantity,
                    "total_price": str(item.total_price)
                }
                for item in items
            ],
            "timeline": timeline,
            "shipment": shipment_info,
        }
    }


# ==============================================================================
# ORDER TIMELINE
# ==============================================================================

@router.get("/orders/my/{order_id}/timeline", summary="Timeline đơn hàng")
async def get_order_timeline(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử thay đổi trạng thái đơn hàng."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    logs = db.query(OrderStatusLog).filter(
        OrderStatusLog.order_id == order_id
    ).order_by(OrderStatusLog.timestamp.asc()).all()

    shipment = db.query(Shipment).filter(Shipment.order_id == order_id).first()
    shipment_info = None
    if shipment:
        shipment_info = {
            "tracking_code": shipment.tracking_code,
            "provider": shipment.provider.value if hasattr(shipment.provider, 'value') else str(shipment.provider) if shipment.provider else None,
            "status": shipment.status.value if hasattr(shipment.status, 'value') else str(shipment.status) if shipment.status else None,
        }

    return {
        "success": True,
        "data": {
            "order_id": order_id,
            "order_number": order.order_number,
            "current_status": order.status.value if hasattr(order.status, 'value') else str(order.status),
            "timeline": [
                {
                    "status": log.new_status,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "actor_role": log.role,
                    "note": log.note,
                }
                for log in logs
            ],
            "shipment": shipment_info,
        }
    }


# ==============================================================================
# NOTIFICATIONS API – User notifications (order-centric)
# ==============================================================================

@router.get("/notifications", summary="Lấy danh sách thông báo cho user")
async def get_my_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(OrderStatusLog, Order)
        .join(Order, Order.id == OrderStatusLog.order_id)
        .filter(
            Order.customer_id == current_user.id,
            Order.is_active == True,
        )
    )

    total = query.count()
    skip = (page - 1) * limit
    rows = query.order_by(OrderStatusLog.timestamp.desc()).offset(skip).limit(limit).all()

    notifications = []
    for status_log, order in rows:
        status = status_log.new_status or (order.status.value if hasattr(order.status, "value") else str(order.status))
        status_label = _order_status_label(status)
        note = (status_log.note or "").strip()

        notifications.append(
            {
                "id": status_log.id,
                "category": "ORDER",
                "title": f"Đơn {order.order_number}",
                "message": note or f"Đơn hàng đã chuyển trạng thái: {status_label}",
                "order_id": order.id,
                "order_number": order.order_number,
                "status": str(status).upper(),
                "status_label": status_label,
                "created_at": status_log.timestamp.isoformat() if status_log.timestamp else None,
                "unread": False,
            }
        )

    return {
        "success": True,
        "data": notifications,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        },
    }


# ==============================================================================
# CONFIRM RECEIVED — Consumer xác nhận nhận hàng
# ==============================================================================

@router.post("/orders/my/{order_id}/confirm-received", summary="Xác nhận nhận hàng")
async def confirm_order_received(
    order_id: int,
    body: Optional[ConfirmReceivedRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Consumer xác nhận đã nhận hàng → DELIVERED + payment_status=PAID.
    Chỉ thực hiện được khi đơn ở trạng thái SHIPPING.
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id,
        Order.is_active == True,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    if order.status != OrderStatus.SHIPPING:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ xác nhận nhận hàng khi đơn đang giao. Trạng thái hiện tại: {order.status.value if hasattr(order.status, 'value') else order.status}"
        )

    old_status = order.status.value if hasattr(order.status, 'value') else str(order.status)
    order.status = OrderStatus.DELIVERED
    order.delivered_at = datetime.utcnow()

    # Auto PAID
    new_pay = resolve_payment_status(order, OrderStatus.DELIVERED)
    if new_pay is not None:
        order.payment_status = new_pay
    else:
        order.payment_status = "PAID"

    note = body.note if body and body.note else "Consumer xác nhận đã nhận hàng"
    log_status_change(
        db=db,
        order_id=order_id,
        old_status=old_status,
        new_status=OrderStatus.DELIVERED.value,
        actor_id=current_user.id,
        role="consumer",
        note=note,
        auto_flush=True,
    )

    # [WALLET] Cộng tiền vào ví seller khi user xác nhận nhận hàng
    # Chỉ thực hiện tại đây – KHÔNG cộng khi seller/admin set DELIVERED
    credit_seller_wallet(db=db, order=order)

    # [NOTIFICATION O7] Thông báo cho Seller: khách đã nhận hàng
    notify_order_delivered_to_seller(
        db=db,
        seller_id=order.seller_id,
        order_id=order_id,
        order_number=order.order_number,
        seller_amount=order.seller_amount or 0,
    )

    db.commit()

    return {
        "success": True,
        "message": "Đã xác nhận nhận hàng. Cảm ơn bạn!",
        "order_id": order_id,
        "new_status": "DELIVERED",
        "payment_status": order.payment_status,
        "can_review": True,
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
        Order.customer_id == current_user.id,
        Order.is_active == True
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    old_status = order.status

    validate_status_transition(old_status, OrderStatus.CANCELLED, role="consumer")

    if old_status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                increment_stock(db, product, item.quantity, item.variant_id)

    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()
    if cancel_data.cancel_reason:
        order.cancel_reason = cancel_data.cancel_reason

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

    # [NOTIFICATION O8] Thông báo cho Seller khi buyer hủy đơn
    try:
        notify_order_cancelled_to_seller(
            db=db,
            seller_id=order.seller_id,
            order_id=order_id,
            order_number=order.order_number,
            reason=cancel_data.cancel_reason or "Khách hàng tự hủy đơn",
        )
    except Exception as e:
        import logging as _logging
        _logging.getLogger(__name__).warning("[Cancel] Không thể gửi notification cho seller: %s", e)

    db.commit()

    return {
        "success": True,
        "message": "Đơn hàng đã được hủy thành công",
        "order_id": order_id,
        "old_status": old_status.value if hasattr(old_status, "value") else str(old_status),
        "new_status": "CANCELLED",
    }


# ==============================================================================
# ADDRESSES API – Sổ địa chỉ
# ==============================================================================

@router.get("/regions/provinces", summary="Danh sách tỉnh/thành cho mobile")
async def get_mobile_provinces(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Province)
    if search:
        query = query.filter(
            Province.name.ilike(f"%{search}%") |
            Province.code.ilike(f"%{search}%")
        )

    rows = query.order_by(Province.name.asc()).all()
    return {
        "success": True,
        "data": [
            {
                "code": p.code,
                "name": p.name,
            }
            for p in rows
        ],
    }


@router.get("/regions/districts", summary="Danh sách quận/huyện theo tỉnh cho mobile")
async def get_mobile_districts(
    province_code: str = Query(..., min_length=1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(District).filter(District.province_code == province_code)
    if search:
        query = query.filter(
            District.name.ilike(f"%{search}%") |
            District.code.ilike(f"%{search}%")
        )

    rows = query.order_by(District.name.asc()).all()
    return {
        "success": True,
        "data": [
            {
                "code": d.code,
                "name": d.name,
                "province_code": d.province_code,
            }
            for d in rows
        ],
    }


@router.get("/regions/wards", summary="Danh sách phường/xã theo quận cho mobile")
async def get_mobile_wards(
    district_code: str = Query(..., min_length=1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Ward).filter(Ward.district_code == district_code)
    if search:
        query = query.filter(
            Ward.name.ilike(f"%{search}%") |
            Ward.code.ilike(f"%{search}%")
        )

    rows = query.order_by(Ward.name.asc()).all()
    return {
        "success": True,
        "data": [
            {
                "code": w.code,
                "name": w.name,
                "district_code": w.district_code,
            }
            for w in rows
        ],
    }

@router.get("/addresses", summary="Lấy sổ địa chỉ")
async def get_my_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách địa chỉ của người dùng."""
    addresses = db.query(Address).filter(
        Address.user_id == current_user.id
    ).order_by(Address.is_default.desc(), Address.created_at.desc()).all()

    return {
        "success": True,
        "data": [_build_address_response(a, db) for a in addresses]
    }


@router.post("/addresses", summary="Thêm địa chỉ")
async def create_address(
    addr_data: AddressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Thêm địa chỉ mới vào sổ."""
    province_code, district_code, ward_code = _resolve_region_codes(
        db,
        addr_data.province_code,
        addr_data.district_code,
        addr_data.ward_code,
    )

    # Nếu set default → reset các addr cũ
    if addr_data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id, Address.is_default == True
        ).update({"is_default": False})

    new_addr = Address(
        user_id=current_user.id,
        recipient_name=addr_data.recipient_name,
        phone=addr_data.phone,
        province_code=province_code,
        district_code=district_code,
        ward_code=ward_code,
        address_line=addr_data.address_line,
        is_default=addr_data.is_default,
    )
    db.add(new_addr)
    db.commit()
    db.refresh(new_addr)

    return {
        "success": True,
        "message": "Đã thêm địa chỉ",
        "data": _build_address_response(new_addr, db)
    }


@router.put("/addresses/{address_id}", summary="Sửa địa chỉ")
async def update_address(
    address_id: int,
    addr_data: AddressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật địa chỉ trong sổ."""
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Địa chỉ không tồn tại")

    province_code, district_code, ward_code = _resolve_region_codes(
        db,
        addr_data.province_code,
        addr_data.district_code,
        addr_data.ward_code,
    )

    if addr_data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id, Address.is_default == True
        ).update({"is_default": False})

    addr.recipient_name = addr_data.recipient_name
    addr.phone = addr_data.phone
    addr.province_code = province_code
    addr.district_code = district_code
    addr.ward_code = ward_code
    addr.address_line = addr_data.address_line
    addr.is_default = addr_data.is_default

    db.commit()
    db.refresh(addr)

    return {
        "success": True,
        "message": "Đã cập nhật địa chỉ",
        "data": _build_address_response(addr, db)
    }


@router.delete("/addresses/{address_id}", summary="Xóa địa chỉ")
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa địa chỉ khỏi sổ."""
    addr = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Địa chỉ không tồn tại")

    db.delete(addr)
    db.commit()

    return {"success": True, "message": "Đã xóa địa chỉ"}


# ==============================================================================
# PROFILE API - Quản lý thông tin cá nhân (ENRICHED)
# ==============================================================================

@router.get("/profile")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin profile — ENRICHED: addresses, order_stats"""
    # Auto-heal dữ liệu cũ: user đã VERIFIED KYC nhưng type vẫn là customer/consumer.
    current_type = (current_user.type or "").strip().lower()
    if current_type not in {"seller", "producer"}:
        seller_profile = db.query(SellerProfile).filter(SellerProfile.user_id == current_user.id).first()
        if seller_profile and seller_profile.verification_status == VerificationStatus.VERIFIED:
            current_user.type = "seller"
            db.commit()
            db.refresh(current_user)

    # Addresses
    addresses = db.query(Address).filter(
        Address.user_id == current_user.id
    ).order_by(Address.is_default.desc()).all()
    primary_address = addresses[0] if addresses else None
    primary_address_data = _build_address_response(primary_address, db) if primary_address else None

    # Order stats
    total_orders = db.query(Order).filter(Order.customer_id == current_user.id).count()
    pending_orders = db.query(Order).filter(
        Order.customer_id == current_user.id, Order.status == OrderStatus.PENDING
    ).count()
    delivered_orders = db.query(Order).filter(
        Order.customer_id == current_user.id, Order.status == OrderStatus.DELIVERED
    ).count()

    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "type": current_user.type,
            "gender": current_user.gender,
            "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
            "activated": current_user.activated,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "avatar_url": current_user.avatar_url,
            "phone": primary_address_data.get("phone") if primary_address_data else None,
            "recipient_name": primary_address_data.get("recipient_name") if primary_address_data else current_user.name,
            "address": primary_address_data.get("address_line") if primary_address_data else None,
            "address_line": primary_address_data.get("address_line") if primary_address_data else None,
            "province": primary_address_data.get("province_name") if primary_address_data else None,
            "province_name": primary_address_data.get("province_name") if primary_address_data else None,
            "province_code": primary_address_data.get("province_code") if primary_address_data else None,
            "district": primary_address_data.get("district_name") if primary_address_data else None,
            "district_name": primary_address_data.get("district_name") if primary_address_data else None,
            "district_code": primary_address_data.get("district_code") if primary_address_data else None,
            "ward": primary_address_data.get("ward_name") if primary_address_data else None,
            "ward_name": primary_address_data.get("ward_name") if primary_address_data else None,
            "ward_code": primary_address_data.get("ward_code") if primary_address_data else None,
            "full_address": primary_address_data.get("full_address") if primary_address_data else None,
            "primary_address": primary_address_data,
            "addresses": [_build_address_response(a, db) for a in addresses],
            "order_stats": {
                "total": total_orders,
                "pending": pending_orders,
                "delivered": delivered_orders,
            }
        }
    }


@router.put("/profile")
async def update_my_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin profile"""
    if profile_data.name:
        current_user.name = profile_data.name
    if profile_data.gender is not None:
        current_user.gender = profile_data.gender
    if profile_data.date_of_birth is not None:
        current_user.date_of_birth = profile_data.date_of_birth

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "gender": current_user.gender,
            "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
            "avatar_url": current_user.avatar_url,
        }
    }


@router.post("/profile/avatar")
async def upload_profile_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload ảnh đại diện (avatar) cho user hiện tại.
    - Accepts: multipart/form-data, field name = 'file'
    - Max: 5 MB, chỉ ảnh (JPEG/PNG/GIF/WebP)
    - Returns: { success, data: { avatar_url } }
    """
    mime = file.content_type or ""
    if mime not in _ALLOWED_IMG:
        raise HTTPException(
            status_code=400,
            detail="Loại file không hợp lệ. Chỉ chấp nhận: JPEG, PNG, GIF, WebP."
        )

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Ảnh quá lớn. Giới hạn tối đa 5MB.")

    try:
        avatar_url = _upload_to_supabase(
            content=content,
            filename=file.filename or "avatar.jpg",
            mime=mime,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Upload Storage thất bại: {exc}")

    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Avatar uploaded successfully",
        "data": {"avatar_url": avatar_url}
    }


# ==============================================================================
# REVIEWS – Đánh giá sản phẩm (Mobile)
# ==============================================================================
# NOTE: GET /orders/my/pending-reviews đã được di chuyển lên TRƯỚC route
# /orders/my/{order_id} để tránh FastAPI route conflict (422 error).
# Xem phần "PENDING REVIEWS" bên trên.
# ==============================================================================


@router.post("/reviews", summary="Gửi đánh giá sản phẩm")
async def submit_review(
    product_id: int = Form(...),
    order_id: int = Form(...),
    order_item_id: Optional[int] = Form(None),
    rating: int = Form(..., ge=1, le=5),
    comment: Optional[str] = Form(None, max_length=2000),
    is_anonymous: Optional[bool] = Form(None),   # Optional để tránh Pydantic v2 strict bool
    images: List[UploadFile] = File(default=[]),  # default=[] thay vì Optional[List]
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tạo đánh giá sản phẩm (multipart/form-data).
    - Yêu cầu: đơn hàng ở trạng thái DELIVERED và còn trong REVIEW_DEADLINE_DAYS.
    - Upload tối đa 5 ảnh kèm đánh giá (JPEG/PNG/WebP, tối đa 10MB mỗi ảnh).
    """
    # Kiểm tra sản phẩm tồn tại
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    # Verify đơn hàng DELIVERED, thuộc user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id,
        Order.status == OrderStatus.DELIVERED,
    ).first()
    if not order:
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể đánh giá sau khi đơn hàng đã được giao thành công",
        )

    # Kiểm tra deadline 5 ngày
    if order.delivered_at:
        delivered_naive = order.delivered_at.replace(tzinfo=None) if order.delivered_at.tzinfo else order.delivered_at
        if (datetime.utcnow() - delivered_naive).days > REVIEW_DEADLINE_DAYS:
            raise HTTPException(
                status_code=400,
                detail=f"Đã quá {REVIEW_DEADLINE_DAYS} ngày kể từ khi nhận hàng, không thể đánh giá",
            )

    # Kiểm tra đã đánh giá cho đơn hàng này chưa (KHÔNG check toàn cục theo product_id)
    # → cho phép user mua cùng sản phẩm ở đơn khác vẫn review được
    if order_item_id:
        # Ưu tiên check theo order_item_id (chính xác nhất)
        existing = db.query(Review).filter(
            Review.order_item_id == order_item_id,
            Review.user_id == current_user.id,
        ).first()
    else:
        # Fallback: check theo order_id + product_id (vẫn cho phép review ở đơn khác)
        existing = db.query(Review).filter(
            Review.order_id == order_id,
            Review.product_id == product_id,
            Review.user_id == current_user.id,
        ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bạn đã đánh giá sản phẩm này rồi",
        )

    # Validate và upload ảnh
    uploaded_urls: List[str] = []
    if images:
        valid_images = [f for f in images if f and f.filename]
        if len(valid_images) > 5:
            raise HTTPException(status_code=400, detail="Tối đa 5 ảnh mỗi đánh giá")

        for img_file in valid_images:
            mime = img_file.content_type or ""
            if mime not in _ALLOWED_IMG:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ảnh '{img_file.filename}' không hợp lệ. Chỉ chấp nhận JPEG, PNG, WebP.",
                )
            img_bytes = await img_file.read()
            if len(img_bytes) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ảnh '{img_file.filename}' quá lớn. Tối đa 10MB.",
                )
            try:
                url = _upload_to_supabase(img_bytes, img_file.filename or "review.jpg", mime)
                uploaded_urls.append(url)
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Upload ảnh thất bại: {e}")

    # Tạo review
    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        order_item_id=order_item_id,
        rating=rating,
        comment=comment,
    )
    db.add(review)
    db.flush()  # lấy review.id

    # Lưu ảnh kèm theo
    for idx, url in enumerate(uploaded_urls):
        db.add(ReviewImage(
            review_id=review.id,
            image_url=url,
            sort_order=idx,
        ))

    db.commit()
    db.refresh(review)

    return {
        "success": True,
        "message": "Đánh giá đã được gửi thành công. Cảm ơn bạn!",
        "data": {
            "id": review.id,
            "product_id": review.product_id,
            "rating": review.rating,
            "comment": review.comment,
            "image_count": len(uploaded_urls),
            "created_at": review.created_at.isoformat() if review.created_at else None,
        },
    }


@router.get("/reviews/product/{product_id}", summary="Đánh giá của sản phẩm (public)")
async def get_product_reviews_mobile(
    product_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    rating_filter: Optional[int] = Query(None, ge=1, le=5, description="Lọc theo số sao"),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách đánh giá của sản phẩm – public (không cần đăng nhập).
    Trả về: thống kê tổng hợp + danh sách review kèm ảnh.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    # Thống kê
    stats = db.query(
        sql_func.count(Review.id).label("total"),
        sql_func.avg(Review.rating).label("avg_rating"),
    ).filter(Review.product_id == product_id).first()

    total_reviews = stats.total or 0
    avg_rating = round(float(stats.avg_rating), 1) if stats.avg_rating else 0.0

    # Phân bố sao
    rating_distribution = {}
    for star in range(1, 6):
        count = db.query(sql_func.count(Review.id)).filter(
            Review.product_id == product_id,
            Review.rating == star,
        ).scalar() or 0
        rating_distribution[str(star)] = count

    # Query reviews
    q = db.query(Review).filter(Review.product_id == product_id)
    if rating_filter:
        q = q.filter(Review.rating == rating_filter)
    total_filtered = q.count()
    skip = (page - 1) * limit
    reviews = q.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

    review_list = []
    for r in reviews:
        user = db.query(User).filter(User.id == r.user_id).first()
        name = (user.name or "Người dùng") if user else "Người dùng ẩn danh"
        # Che tên để bảo vệ privacy: A***n
        if len(name) > 2:
            name = name[0] + "*" * (len(name) - 2) + name[-1]

        # Ảnh kèm review
        review_images = [
            img.image_url
            for img in sorted(r.images, key=lambda x: x.sort_order)
        ] if r.images else []

        review_list.append({
            "id": r.id,
            "reviewer_name": name,
            "rating": r.rating,
            "comment": r.comment,
            "images": review_images,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "success": True,
        "data": {
            "product_id": product_id,
            "product_name": product.name,
            "stats": {
                "total_reviews": total_reviews,
                "avg_rating": avg_rating,
                "rating_distribution": rating_distribution,
            },
            "reviews": review_list,
        },
        "meta": {
            "total": total_filtered,
            "page": page,
            "limit": limit,
            "total_pages": (total_filtered + limit - 1) // limit if total_filtered > 0 else 1,
        },
    }


# ==============================================================================
# REVIEWS – Xem đánh giá của tôi cho đơn hàng
# ==============================================================================

@router.get("/reviews/my/order/{order_id}", summary="Xem đánh giá của tôi cho đơn hàng")
async def get_my_order_reviews(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách đánh giá mà user hiện tại đã gửi
    cho các sản phẩm trong đơn hàng order_id.
    """
    from app.models.order import OrderItem  # tránh circular import ở top-level

    # Xác nhận đơn hàng thuộc user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    # Lấy product_id từ các items của đơn
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    product_ids = [item.product_id for item in order_items if item.product_id]

    if not product_ids:
        return {"success": True, "data": []}

    # Lấy review của user cho các sản phẩm trong đơn
    reviews = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id.in_(product_ids),
    ).order_by(Review.created_at.desc()).all()

    review_list = []
    for r in reviews:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        # Tìm product_image từ order item
        order_item = next(
            (oi for oi in order_items if oi.product_id == r.product_id), None
        )
        product_image = order_item.product_image if order_item else (
            product.images if product else None
        )

        review_images = [
            img.image_url
            for img in sorted(r.images, key=lambda x: x.sort_order)
        ] if r.images else []

        review_list.append({
            "id": r.id,
            "product_id": r.product_id,
            "product_name": product.name if product else (
                order_item.product_name if order_item else "Sản phẩm"
            ),
            "product_image": product_image,
            "rating": r.rating,
            "comment": r.comment,
            "images": review_images,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {"success": True, "data": review_list}


# ==============================================================================
# REVIEWS – Kiểm tra & lấy đánh giá của tôi cho sản phẩm cụ thể
# ==============================================================================

@router.get("/reviews/my/product/{product_id}", summary="Đánh giá của tôi cho sản phẩm")
async def get_my_product_review(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kiểm tra user hiện tại đã đánh giá sản phẩm product_id chưa.
    Trả về:
      - has_reviewed: bool
      - review: object (id, rating, comment, images, created_at) nếu đã review, null nếu chưa
    Dùng để Flutter hiển thị bình luận của mình lên đầu danh sách đánh giá sản phẩm.
    """
    review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id == product_id,
    ).order_by(Review.created_at.desc()).first()

    if not review:
        return {
            "success": True,
            "data": {
                "has_reviewed": False,
                "review": None,
            }
        }

    review_images = [
        img.image_url
        for img in sorted(review.images, key=lambda x: x.sort_order)
    ] if review.images else []

    return {
        "success": True,
        "data": {
            "has_reviewed": True,
            "review": {
                "id": review.id,
                "product_id": review.product_id,
                "rating": review.rating,
                "comment": review.comment,
                "images": review_images,
                "created_at": review.created_at.isoformat() if review.created_at else None,
            }
        }
    }
