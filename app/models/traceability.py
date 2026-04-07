from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class CertificateStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chờ xác minh
    VERIFIED = "VERIFIED"         # Đã xác minh
    REJECTED = "REJECTED"         # Từ chối
    EXPIRED = "EXPIRED"           # Hết hạn


class OriginStatus(str, enum.Enum):
    PENDING = "PENDING"           # Chờ xác minh
    VERIFIED = "VERIFIED"         # Đã xác minh
    REJECTED = "REJECTED"         # Từ chối


class ProductCertificate(Base):
    """Chứng nhận sản phẩm (VietGAP, OCOP, ISO...)"""
    __tablename__ = "product_certificates"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    certificate_name = Column(String(255), nullable=False)      # VietGAP, OCOP 4 sao, ISO 22000...
    certificate_number = Column(String(100), nullable=True)     # Số chứng nhận
    issued_by = Column(String(255), nullable=True)              # Cơ quan cấp
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    document_url = Column(Text, nullable=True)                  # Link file minh chứng

    verification_status = Column(
        SQLEnum(CertificateStatus), default=CertificateStatus.PENDING
    )
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    verifier = relationship("User", foreign_keys=[verified_by])


class ProductOrigin(Base):
    """Truy xuất nguồn gốc sản phẩm"""
    __tablename__ = "product_origins"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Thông tin nơi sản xuất
    village_name = Column(String(255), nullable=True)           # Tên làng nghề / vùng sản xuất
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    producer_name = Column(String(255), nullable=True)          # Tên hộ / HTX sản xuất

    # Lô sản xuất
    batch_number = Column(String(100), nullable=True)           # Mã lô
    production_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)

    # Thành phần & quy trình
    ingredients = Column(Text, nullable=True)                   # Nguyên liệu / thành phần
    process_summary = Column(Text, nullable=True)               # Mô tả quy trình sản xuất

    verification_status = Column(
        SQLEnum(OriginStatus), default=OriginStatus.PENDING
    )
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", foreign_keys=[product_id])
    region = relationship("Region", foreign_keys=[region_id])
    verifier = relationship("User", foreign_keys=[verified_by])
