from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.media import Media
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
import os
import uuid
from datetime import datetime

router = APIRouter()


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


@router.get("", response_model=MediaListResponse)
async def get_media_list(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    file_type: Optional[str] = Query(None, description="Filter by file type: image, video, document"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of media files"""
    query = db.query(Media)
    
    if file_type:
        query = query.filter(Media.file_type == file_type)
    
    total = query.count()
    offset = (page - 1) * limit
    medias = query.order_by(Media.id.desc()).offset(offset).limit(limit).all()
    
    return MediaListResponse(
        data=[MediaResponse.from_orm(media) for media in medias],
        meta={
            "total": total,
            "limit": limit,
            "current_page": page,
            "total_pages": (total + limit - 1) // limit
        }
    )


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media_by_id(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get media by ID"""
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return MediaResponse.from_orm(media)


@router.post("")
async def create_media(
    filename: str,
    file_path: str,
    file_type: Optional[str] = None,
    file_size: Optional[int] = None,
    mime_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create media record"""
    new_media = Media(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        mime_type=mime_type,
        uploaded_by=current_user.id
    )
    
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    
    return MediaResponse.from_orm(new_media)


@router.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file"""
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file size
        file_size = len(content)
        
        # Determine file type
        file_type = "image" if file.content_type and file.content_type.startswith("image/") else "document"
        if file.content_type and file.content_type.startswith("video/"):
            file_type = "video"
        
        # Create media record
        new_media = Media(
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            mime_type=file.content_type,
            uploaded_by=current_user.id
        )
        
        db.add(new_media)
        db.commit()
        db.refresh(new_media)
        
        return {
            "success": True,
            "id": new_media.id,
            "filename": new_media.filename,
            "file_path": new_media.file_path,
            "url": f"/{file_path}"  # Adjust based on your static file serving
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a media file"""
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Delete physical file if exists
    if media.file_path and os.path.exists(media.file_path):
        try:
            os.remove(media.file_path)
        except Exception:
            pass  # Continue even if file deletion fails
    
    # Delete database record
    db.delete(media)
    db.commit()
    
    return {"success": True, "message": "Media deleted successfully"}
