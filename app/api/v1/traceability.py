"""
Traceability API – Truy xuất nguồn gốc & Chứng nhận sản phẩm

Endpoints:
- POST /traceability/certificates                  – Seller thêm chứng nhận
- GET  /traceability/certificates/product/{id}      – Xem chứng nhận (public)
- PUT  /traceability/certificates/{id}/verify       – Admin xác minh
- POST /traceability/origins                        – Seller khai báo nguồn gốc
- GET  /traceability/origins/product/{id}/review    – Admin xem nguồn gốc để duyệt
- PUT  /traceability/origins/{id}/verify            – Admin duyệt/từ chối nguồn gốc
- GET  /traceability/origins/product/{id}           – Xem nguồn gốc (public)
- GET  /traceability/product/{id}                   – Xem tất cả (public)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date
from app.core.database import get_db
from app.models.traceability import ProductCertificate, CertificateStatus, ProductOrigin, OriginStatus
from app.models.product import Product
from app.models.user import User
from app.models.region import Region
from app.api.v1.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter()


# ==============================================================================
# SCHEMAS
# ==============================================================================

class CreateCertificateRequest(BaseModel):
    product_id: int
    certificate_name: str = Field(..., min_length=2, max_length=255)
    certificate_number: Optional[str] = None
    issued_by: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    document_url: Optional[str] = None


class VerifyCertificateRequest(BaseModel):
    status: str = Field(..., pattern="^(VERIFIED|REJECTED)$")
    rejection_reason: Optional[str] = None


class CreateOriginRequest(BaseModel):
    product_id: int
    village_name: Optional[str] = None
    region_id: Optional[int] = None
    seller_name: Optional[str] = None
    batch_number: Optional[str] = None
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    ingredients: Optional[str] = None
    process_summary: Optional[str] = None


class VerifyOriginRequest(BaseModel):
    status: str = Field(..., pattern="^(VERIFIED|REJECTED)$")
    rejection_reason: Optional[str] = None


# ==============================================================================
# HELPERS
# ==============================================================================

def _require_seller(user: User):
    if user.type not in {"producer", "seller", "admin"}:
        raise HTTPException(status_code=403, detail="Chỉ người bán mới có quyền")


def _require_admin(user: User):
    if user.type not in {"admin", "content_manager"}:
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới có quyền")


def _check_product_owner(product_id: int, user: User, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    if user.type != "admin" and product.seller_id != user.id:
        raise HTTPException(status_code=403, detail="Bạn không sở hữu sản phẩm này")
    return product


def _serialize_origin(origin: ProductOrigin, include_status: bool = False) -> dict:
    payload = {
        "id": origin.id,
        "product_id": origin.product_id,
        "village_name": origin.village_name,
        "region_id": origin.region_id,
        "seller_name": origin.seller_name,
        "batch_number": origin.batch_number,
        "production_date": origin.production_date.isoformat() if origin.production_date else None,
        "expiry_date": origin.expiry_date.isoformat() if origin.expiry_date else None,
        "ingredients": origin.ingredients,
        "process_summary": origin.process_summary,
    }
    if include_status:
        payload.update(
            {
                "verification_status": origin.verification_status.value
                if hasattr(origin.verification_status, "value")
                else str(origin.verification_status),
                "verified_by": origin.verified_by,
                "verified_at": origin.verified_at.isoformat() if origin.verified_at else None,
                "rejection_reason": origin.rejection_reason,
            }
        )
    return payload


# ==============================================================================
# CERTIFICATES
# ==============================================================================

@router.post("/certificates", summary="Seller thêm chứng nhận cho sản phẩm")
async def create_certificate(
    data: CreateCertificateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_seller(current_user)
    _check_product_owner(data.product_id, current_user, db)

    cert = ProductCertificate(
        product_id=data.product_id,
        certificate_name=data.certificate_name,
        certificate_number=data.certificate_number,
        issued_by=data.issued_by,
        issue_date=data.issue_date,
        expiry_date=data.expiry_date,
        document_url=data.document_url,
        verification_status=CertificateStatus.PENDING
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    return {
        "success": True,
        "message": "Đã thêm chứng nhận, chờ admin xác minh",
        "data": {
            "id": cert.id,
            "certificate_name": cert.certificate_name,
            "status": "PENDING"
        }
    }


@router.get("/certificates/product/{product_id}", summary="Xem chứng nhận sản phẩm (public)")
async def get_product_certificates(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Lấy danh sách chứng nhận đã xác minh của sản phẩm."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    certs = db.query(ProductCertificate).filter(
        ProductCertificate.product_id == product_id,
        ProductCertificate.verification_status == CertificateStatus.VERIFIED
    ).all()

    return {
        "success": True,
        "data": [
            {
                "id": c.id,
                "certificate_name": c.certificate_name,
                "certificate_number": c.certificate_number,
                "issued_by": c.issued_by,
                "issue_date": c.issue_date.isoformat() if c.issue_date else None,
                "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
                "document_url": c.document_url,
                "verified_at": c.verified_at.isoformat() if c.verified_at else None
            }
            for c in certs
        ]
    }


@router.put("/certificates/{cert_id}/verify", summary="Admin xác minh chứng nhận")
async def verify_certificate(
    cert_id: int,
    data: VerifyCertificateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_admin(current_user)

    cert = db.query(ProductCertificate).filter(ProductCertificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Chứng nhận không tồn tại")

    cert.verification_status = CertificateStatus(data.status)
    cert.verified_by = current_user.id
    cert.verified_at = datetime.utcnow()
    cert.rejection_reason = data.rejection_reason if data.status == "REJECTED" else None

    db.commit()

    return {
        "success": True,
        "message": f"Chứng nhận đã được {'xác minh' if data.status == 'VERIFIED' else 'từ chối'}",
        "data": {"id": cert.id, "status": data.status}
    }


# ==============================================================================
# ORIGINS (TRUY XUẤT NGUỒN GỐC)
# ==============================================================================

@router.post("/origins", summary="Seller khai báo nguồn gốc sản phẩm")
async def create_origin(
    data: CreateOriginRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_seller(current_user)
    _check_product_owner(data.product_id, current_user, db)

    if data.region_id is not None:
        region = db.query(Region).filter(Region.id == data.region_id).first()
        if not region:
            raise HTTPException(status_code=400, detail="Vùng miền không tồn tại")

    # Kiểm tra đã có chưa (1 product → 1 origin)
    existing = db.query(ProductOrigin).filter(
        ProductOrigin.product_id == data.product_id
    ).first()

    if existing:
        # Cập nhật
        for key, value in data.dict(exclude_unset=True).items():
            if key != "product_id":
                setattr(existing, key, value)
        existing.verification_status = OriginStatus.PENDING
        existing.verified_by = None
        existing.verified_at = None
        existing.rejection_reason = None
        db.commit()
        db.refresh(existing)
        origin = existing
        msg = "Đã cập nhật thông tin nguồn gốc, chờ admin duyệt lại"
    else:
        origin = ProductOrigin(**data.dict(), verification_status=OriginStatus.PENDING)
        db.add(origin)
        db.commit()
        db.refresh(origin)
        msg = "Đã khai báo nguồn gốc sản phẩm, chờ admin duyệt"

    return {
        "success": True,
        "message": msg,
        "data": _serialize_origin(origin, include_status=True)
    }


@router.get("/origins/product/{product_id}/owner", summary="Seller xem nguồn gốc sản phẩm của mình")
async def get_product_origin_for_owner(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_seller(current_user)
    _check_product_owner(product_id, current_user, db)

    origin = db.query(ProductOrigin).filter(ProductOrigin.product_id == product_id).first()
    if not origin:
        return {"success": True, "data": None, "message": "Sản phẩm chưa có thông tin nguồn gốc"}

    payload = _serialize_origin(origin, include_status=True)
    if origin.region_id:
        region = db.query(Region).filter(Region.id == origin.region_id).first()
        payload["region_name"] = region.name if region else None

    return {"success": True, "data": payload}


@router.get("/origins/product/{product_id}/review", summary="Admin xem nguồn gốc theo sản phẩm")
async def get_product_origin_for_review(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_admin(current_user)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    origin = db.query(ProductOrigin).filter(ProductOrigin.product_id == product_id).first()
    producer = db.query(User).filter(User.id == product.seller_id).first()

    if not origin:
        return {
            "success": True,
            "data": {
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "seller_id": product.seller_id,
                    "seller_name": producer.name if producer else None,
                },
                "origin": None,
            },
            "message": "Sản phẩm chưa có thông tin nguồn gốc",
        }

    payload = _serialize_origin(origin, include_status=True)
    if origin.region_id:
        region = db.query(Region).filter(Region.id == origin.region_id).first()
        payload["region_name"] = region.name if region else None

    return {
        "success": True,
        "data": {
            "product": {
                "id": product.id,
                "name": product.name,
                "seller_id": product.seller_id,
                "seller_name": producer.name if producer else None,
            },
            "origin": payload,
        },
    }


@router.put("/origins/{origin_id}/verify", summary="Admin duyệt/từ chối nguồn gốc")
async def verify_origin(
    origin_id: int,
    data: VerifyOriginRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_admin(current_user)

    origin = db.query(ProductOrigin).filter(ProductOrigin.id == origin_id).first()
    if not origin:
        raise HTTPException(status_code=404, detail="Nguồn gốc không tồn tại")

    origin.verification_status = OriginStatus(data.status)
    origin.verified_by = current_user.id
    origin.verified_at = datetime.utcnow()
    origin.rejection_reason = data.rejection_reason if data.status == "REJECTED" else None

    db.commit()
    db.refresh(origin)

    return {
        "success": True,
        "message": f"Nguồn gốc đã được {'xác minh' if data.status == 'VERIFIED' else 'từ chối'}",
        "data": _serialize_origin(origin, include_status=True),
    }


@router.get("/origins/product/{product_id}", summary="Xem nguồn gốc sản phẩm (public)")
async def get_product_origin(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    origin = db.query(ProductOrigin).filter(
        ProductOrigin.product_id == product_id,
        ProductOrigin.verification_status == OriginStatus.VERIFIED,
    ).first()

    if not origin:
        return {"success": True, "data": None, "message": "Nguồn gốc đang chờ duyệt hoặc chưa khai báo"}

    region = db.query(Region).filter(Region.id == origin.region_id).first() if origin.region_id else None
    payload = _serialize_origin(origin, include_status=False)
    payload["region_name"] = region.name if region else None

    return {
        "success": True,
        "data": payload,
    }


@router.get("/product/{product_id}", summary="Xem toàn bộ truy xuất nguồn gốc (public)")
async def get_product_traceability(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Trả về tất cả: nguồn gốc + chứng nhận + thông tin sản phẩm."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    origin = db.query(ProductOrigin).filter(
        ProductOrigin.product_id == product_id,
        ProductOrigin.verification_status == OriginStatus.VERIFIED,
    ).first()
    certs = db.query(ProductCertificate).filter(
        ProductCertificate.product_id == product_id,
        ProductCertificate.verification_status == CertificateStatus.VERIFIED
    ).all()
    producer = db.query(User).filter(User.id == product.seller_id).first()

    origin_payload = None
    if origin:
        origin_payload = _serialize_origin(origin, include_status=False)
        region = db.query(Region).filter(Region.id == origin.region_id).first() if origin.region_id else None
        origin_payload["region_name"] = region.name if region else None

    return {
        "success": True,
        "data": {
            "product": {
                "id": product.id,
                "name": product.name,
                "label": product.label,
                "seller_id": product.seller_id,
                "seller_name": producer.name if producer else None,
            },
            "origin": origin_payload,
            "certificates": [
                {
                    "certificate_name": c.certificate_name,
                    "certificate_number": c.certificate_number,
                    "issued_by": c.issued_by,
                    "issue_date": c.issue_date.isoformat() if c.issue_date else None,
                    "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
                    "document_url": c.document_url
                }
                for c in certs
            ]
        }
    }
