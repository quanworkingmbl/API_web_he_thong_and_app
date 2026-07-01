from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.media import Media
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from app.core.permissions import check_ownership
from pydantic import BaseModel
from google.cloud import storage as gcs
import os
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ==============================================================================
# Google Cloud Storage config
# ==============================================================================
GCS_BUCKET_NAME    = settings.GCS_BUCKET_NAME
GCS_PUBLIC_URL_BASE = settings.GCS_PUBLIC_URL_BASE.rstrip("/")

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "video/quicktime"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_gcs_client() -> gcs.Client:
    """Trả về GCS client — trên Cloud Run dùng Workload Identity, không cần key file."""
    return gcs.Client()


def upload_to_gcs(content: bytes, key: str, content_type: str) -> str:
    """Upload file lên GCS, trả về public URL."""
    client = get_gcs_client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob   = bucket.blob(key)
    blob.upload_from_string(content, content_type=content_type)
    # Bucket cần được cấu hình public read hoặc dùng signed URL
    return f"{GCS_PUBLIC_URL_BASE}/{GCS_BUCKET_NAME}/{key}"


def delete_from_gcs(file_url: str) -> None:
    """Xóa file trên GCS từ public URL."""
    try:
        # Lấy key từ URL: https://storage.googleapis.com/<bucket>/<key>
        prefix = f"{GCS_PUBLIC_URL_BASE}/{GCS_BUCKET_NAME}/"
        key = file_url.replace(prefix, "")
        client = get_gcs_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(key)
        blob.delete()
    except Exception as e:
        logger.warning(f"Không thể xóa file GCS '{file_url}': {e}")


# ==============================================================================
# SCHEMAS
# ==============================================================================

class MediaResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    file_type: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_by: Optional[int]
    created_at: str

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    data: List[MediaResponse]
    meta: dict


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("", response_model=MediaListResponse)
async def get_media_list(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    file_type: Optional[str] = Query(None, description="image | video | document"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy danh sách media đã upload"""
    query = db.query(Media)
    if file_type:
        query = query.filter(Media.file_type == file_type)

    total  = query.count()
    offset = (page - 1) * limit
    medias = query.order_by(Media.id.desc()).offset(offset).limit(limit).all()

    return MediaListResponse(
        data=[MediaResponse.from_orm(m) for m in medias],
        meta={
            "total": total,
            "limit": limit,
            "current_page": page,
            "total_pages": (total + limit - 1) // limit,
        },
    )


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media_by_id(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy media theo ID"""
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return MediaResponse.from_orm(media)


@router.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload file (image/video) lên Google Cloud Storage.
    Trả về public URL để dùng trong trường `images` của content/product.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Loại file không được hỗ trợ: {file.content_type}. Chỉ chấp nhận: {', '.join(ALLOWED_TYPES)}",
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File quá lớn. Tối đa {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    ext        = os.path.splitext(file.filename or "file")[1].lower() or ".bin"
    unique_key = f"uploads/{uuid.uuid4()}{ext}"

    if file.content_type and file.content_type.startswith("image/"):
        file_type = "image"
    elif file.content_type and file.content_type.startswith("video/"):
        file_type = "video"
    else:
        file_type = "document"

    try:
        public_url = upload_to_gcs(content, unique_key, file.content_type or "application/octet-stream")
    except Exception as e:
        logger.error(f"GCS upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload thất bại: {str(e)}")

    new_media = Media(
        filename=file.filename,
        file_path=public_url,
        file_type=file_type,
        file_size=len(content),
        mime_type=file.content_type,
        uploaded_by=current_user.id,
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)

    return {
        "success": True,
        "id": new_media.id,
        "filename": file.filename,
        "url": public_url,
        "file_type": file_type,
        "file_size": len(content),
    }


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa media (cả trên GCS và DB)"""
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    check_ownership(media.uploaded_by, current_user, allow_admin=True)

    delete_from_gcs(media.file_path)

    db.delete(media)
    db.commit()

    return {"success": True, "message": "Media deleted successfully"}
