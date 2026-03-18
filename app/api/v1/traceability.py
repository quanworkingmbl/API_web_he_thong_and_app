"""
Traceability API – Truy xuất nguồn gốc & Chứng nhận sản phẩm

Endpoints:
- POST /traceability/certificates                  – Seller thêm chứng nhận
- GET  /traceability/certificates/product/{id}      – Xem chứng nhận (public)
- PUT  /traceability/certificates/{id}/verify       – Admin xác minh
- POST /traceability/origins                        – Seller khai báo nguồn gốc
- GET  /traceability/origins/product/{id}           – Xem nguồn gốc (public)
- GET  /traceability/product/{id}                   – Xem tất cả (public)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
from app.core.database import get_db
from app.models.traceability import ProductCertificate, CertificateStatus, ProductOrigin
from app.models.product import Product
from app.models.user import User
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
    producer_name: Optional[str] = None
    batch_number: Optional[str] = None
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    ingredients: Optional[str] = None
    process_summary: Optional[str] = None


# ==============================================================================
# HELPERS
# ==============================================================================

def _require_seller(user: User):
    if user.type not in {"producer", "seller", "admin"}:
        raise HTTPException(status_code=403, detail="Chỉ người bán mới có quyền")


def _require_admin(user: User):
    if user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền")


def _check_product_owner(product_id: int, user: User, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    if user.type != "admin" and product.producer_id != user.id:
        raise HTTPException(status_code=403, detail="Bạn không sở hữu sản phẩm này")
    return product


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

    cert.verification_status = data.status
    cert.verified_by = current_user.id
    cert.verified_at = datetime.utcnow()
    if data.status == "REJECTED":
        cert.rejection_reason = data.rejection_reason

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

    # Kiểm tra đã có chưa (1 product → 1 origin)
    existing = db.query(ProductOrigin).filter(
        ProductOrigin.product_id == data.product_id
    ).first()

    if existing:
        # Cập nhật
        for key, value in data.dict(exclude_unset=True).items():
            if key != "product_id":
                setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        origin = existing
        msg = "Đã cập nhật thông tin nguồn gốc"
    else:
        origin = ProductOrigin(**data.dict())
        db.add(origin)
        db.commit()
        db.refresh(origin)
        msg = "Đã khai báo nguồn gốc sản phẩm"

    return {
        "success": True,
        "message": msg,
        "data": {
            "id": origin.id,
            "product_id": origin.product_id,
            "village_name": origin.village_name,
            "producer_name": origin.producer_name,
            "batch_number": origin.batch_number
        }
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
        ProductOrigin.product_id == product_id
    ).first()

    if not origin:
        return {"success": True, "data": None, "message": "Chưa có thông tin nguồn gốc"}

    return {
        "success": True,
        "data": {
            "id": origin.id,
            "village_name": origin.village_name,
            "region_id": origin.region_id,
            "producer_name": origin.producer_name,
            "batch_number": origin.batch_number,
            "production_date": origin.production_date.isoformat() if origin.production_date else None,
            "expiry_date": origin.expiry_date.isoformat() if origin.expiry_date else None,
            "ingredients": origin.ingredients,
            "process_summary": origin.process_summary
        }
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

    origin = db.query(ProductOrigin).filter(ProductOrigin.product_id == product_id).first()
    certs = db.query(ProductCertificate).filter(
        ProductCertificate.product_id == product_id,
        ProductCertificate.verification_status == CertificateStatus.VERIFIED
    ).all()

    return {
        "success": True,
        "data": {
            "product": {
                "id": product.id,
                "name": product.name,
                "label": product.label,
                "producer_id": product.producer_id
            },
            "origin": {
                "village_name": origin.village_name if origin else None,
                "producer_name": origin.producer_name if origin else None,
                "batch_number": origin.batch_number if origin else None,
                "production_date": origin.production_date.isoformat() if origin and origin.production_date else None,
                "ingredients": origin.ingredients if origin else None,
                "process_summary": origin.process_summary if origin else None
            } if origin else None,
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
