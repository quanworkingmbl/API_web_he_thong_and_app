from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.content import Content, ContentStatus
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.core.permissions import check_content_approve_access
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================

class ContentResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    content_type: str
    author_id: int
    author_name: Optional[str] = None
    product_id: Optional[int]
    status: str
    images: Optional[str]
    videos: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedContentResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[ContentResponse]


class CreateContentRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: Optional[str] = None
    content_type: str = Field(..., pattern="^(POST|PRODUCT_DESCRIPTION|NEWS|ANNOUNCEMENT)$")
    author_id: int
    product_id: Optional[int] = None
    images: Optional[str] = None
    videos: Optional[str] = None


class UpdateContentRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = None
    content_type: Optional[str] = None
    images: Optional[str] = None
    videos: Optional[str] = None


class ContentApprovalRequest(BaseModel):
    content_id: int
    status: str  # APPROVED, REJECTED
    notes: Optional[str] = None


# ==============================================================================
# LIST & GET ENDPOINTS
# ==============================================================================

@router.get("", response_model=PaginatedContentResponse)
async def get_contents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    author_id: Optional[int] = Query(None),
    content_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get list of contents (posts from producers and cooperatives) with pagination"""
    query = db.query(Content)
    
    if status:
        query = query.filter(Content.status == status)
    if author_id:
        query = query.filter(Content.author_id == author_id)
    if content_type:
        query = query.filter(Content.content_type == content_type)
    if search:
        query = query.filter(Content.title.ilike(f"%{search}%"))
    
    total = query.count()
    skip = (page - 1) * limit
    contents = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()
    
    content_list = []
    for c in contents:
        author = db.query(User).filter(User.id == c.author_id).first()
        content_list.append(ContentResponse(
            id=c.id,
            title=c.title,
            content=c.content,
            content_type=c.content_type,
            author_id=c.author_id,
            author_name=author.name if author else None,
            product_id=c.product_id,
            status=c.status.value if hasattr(c.status, 'value') else str(c.status),
            images=c.images,
            videos=c.videos,
            approved_by=c.approved_by,
            approved_at=c.approved_at,
            created_at=c.created_at,
            updated_at=c.updated_at
        ))
    
    return PaginatedContentResponse(
        total=total,
        page=page,
        limit=limit,
        data=content_list
    )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_by_id(
    content_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get content by ID"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    author = db.query(User).filter(User.id == content.author_id).first()
    
    return ContentResponse(
        id=content.id,
        title=content.title,
        content=content.content,
        content_type=content.content_type,
        author_id=content.author_id,
        author_name=author.name if author else None,
        product_id=content.product_id,
        status=content.status.value if hasattr(content.status, 'value') else str(content.status),
        images=content.images,
        videos=content.videos,
        approved_by=content.approved_by,
        approved_at=content.approved_at,
        created_at=content.created_at,
        updated_at=content.updated_at
    )


# ==============================================================================
# CREATE, UPDATE, DELETE ENDPOINTS
# ==============================================================================

@router.post("", response_model=ContentResponse)
async def create_content(
    content_data: CreateContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    [WEB endpoint] Tạo nội dung/bài viết mới thông qua WEB.
    Route: POST /api/content  (file: app/api/v1/content.py)
    - Đây là endpoint web cho phép tạo bất kỳ loại nội dung (POST, ARTICLE, v.v.).
    - Seller đăng bài trên web sử dụng endpoint này.
    - Tương đương mobile: POST /api/mobile/posts/my (app/api/v1/mobile_app.py).
    """
    # Validate author
    author = db.query(User).filter(User.id == content_data.author_id).first()
    if not author:
        raise HTTPException(status_code=400, detail="Author not found")
    
    new_content = Content(
        title=content_data.title,
        content=content_data.content,
        content_type=content_data.content_type,
        author_id=content_data.author_id,
        product_id=content_data.product_id,
        status=ContentStatus.PENDING,
        images=content_data.images,
        videos=content_data.videos
    )
    
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    
    return ContentResponse(
        id=new_content.id,
        title=new_content.title,
        content=new_content.content,
        content_type=new_content.content_type,
        author_id=new_content.author_id,
        author_name=author.name,
        product_id=new_content.product_id,
        status=new_content.status.value if hasattr(new_content.status, 'value') else str(new_content.status),
        images=new_content.images,
        videos=new_content.videos,
        approved_by=None,
        approved_at=None,
        created_at=new_content.created_at,
        updated_at=None
    )


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_data: UpdateContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update content"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    update_data = content_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(content, key, value)
    
    db.commit()
    db.refresh(content)
    
    author = db.query(User).filter(User.id == content.author_id).first()
    
    return ContentResponse(
        id=content.id,
        title=content.title,
        content=content.content,
        content_type=content.content_type,
        author_id=content.author_id,
        author_name=author.name if author else None,
        product_id=content.product_id,
        status=content.status.value if hasattr(content.status, 'value') else str(content.status),
        images=content.images,
        videos=content.videos,
        approved_by=content.approved_by,
        approved_at=content.approved_at,
        created_at=content.created_at,
        updated_at=content.updated_at
    )


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete content"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(content)
    db.commit()
    
    return {"success": True, "message": "Content deleted successfully"}


# ==============================================================================
# APPROVAL ENDPOINT
# ==============================================================================

@router.post("/{content_id}/approve")
async def approve_content(
    content_id: int,
    approval_data: ContentApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject content"""
    # Permission check
    if not check_content_approve_access(current_user, db):
        raise HTTPException(status_code=403, detail="Không có quyền duyệt content. Yêu cầu role: admin hoặc content_manager")
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = approval_data.status
    content.approved_by = current_user.id
    content.approved_at = datetime.utcnow()
    
    db.commit()
    
    return {"success": True, "message": f"Content {approval_data.status.lower()} successfully"}
