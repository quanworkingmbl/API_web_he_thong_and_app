from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.media import Media
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from pydantic import BaseModel
import os
import uuid
import boto3
from botocore.client import Config

router = APIRouter()

# ==============================================================================
# AWS S3 Storage config
# ==============================================================================

AWS_ACCESS_KEY_ID     = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_REGION            = settings.AWS_REGION
AWS_S3_BUCKET         = settings.AWS_S3_BUCKET

# Public URL base: https://<bucket>.s3.<region>.amazonaws.com/<key>
AWS_S3_PUBLIC_URL_BASE = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/"

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "video/quicktime"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_s3_client():
    """Trả về boto3 S3 client kết nối AWS S3"""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        config=Config(signature_version="s3v4"),
    )



# ==============================================================================
# SCHEMAS
# ==============================================================================

class MediaResponse(BaseModel):
    id: int
    filename: str
    file_path: str          # public URL trên Supabase Storage
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
    Upload file (image/video) lên AWS S3.
    Trả về public URL để dùng trong trường `images` của content/product.
    """
    # Validate MIME type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Loại file không được hỗ trợ: {file.content_type}. Chỉ chấp nhận: {', '.join(ALLOWED_TYPES)}",
        )

    content = await file.read()

    # Validate size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File quá lớn. Tối đa {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    # Tạo tên file duy nhất
    ext           = os.path.splitext(file.filename or "file")[1].lower() or ".bin"
    unique_key    = f"{uuid.uuid4()}{ext}"

    # Xác định loại
    if file.content_type and file.content_type.startswith("image/"):
        file_type = "image"
    elif file.content_type and file.content_type.startswith("video/"):
        file_type = "video"
    else:
        file_type = "document"

    # Upload lên AWS S3
    try:
        s3 = get_s3_client()
        s3.put_object(
            Bucket=AWS_S3_BUCKET,
            Key=unique_key,
            Body=content,
            ContentType=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload thất bại: {str(e)}")

    public_url = AWS_S3_PUBLIC_URL_BASE + unique_key

    # Lưu record vào DB
    new_media = Media(
        filename=file.filename,
        file_path=public_url,        # lưu public URL thay cho local path
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
        "url": public_url,           # ← dùng URL này cho trường images/videos
        "file_type": file_type,
        "file_size": len(content),
    }


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa media (cả trên AWS S3 và DB)"""
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # Xóa trên AWS S3
    try:
        # Lấy key từ URL
        key = media.file_path.split(f".amazonaws.com/")[-1]
        s3  = get_s3_client()
        s3.delete_object(Bucket=AWS_S3_BUCKET, Key=key)
    except Exception:
        pass  # không chặn nếu file không tồn tại trên storage

    db.delete(media)
    db.commit()

    return {"success": True, "message": "Media deleted successfully"}
