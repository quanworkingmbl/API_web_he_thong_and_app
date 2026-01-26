from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.content import Content, ContentStatus
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ContentResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    content_type: str
    author_id: int
    product_id: Optional[int]
    status: str
    images: Optional[str]
    videos: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedContentResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[ContentResponse]

class ContentApprovalRequest(BaseModel):
    content_id: int
    status: str  # APPROVED, REJECTED
    notes: Optional[str] = None

@router.get("", response_model=PaginatedContentResponse)
async def get_contents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    author_id: Optional[int] = Query(None),
    content_type: Optional[str] = Query(None),
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
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    skip = (page - 1) * limit
    contents = query.offset(skip).limit(limit).all()
    
    return PaginatedContentResponse(
        total=total,
        page=page,
        limit=limit,
        data=[ContentResponse.from_orm(c) for c in contents]
    )

@router.post("/{content_id}/approve")
async def approve_content(
    content_id: int,
    approval_data: ContentApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject content"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = approval_data.status
    content.approved_by = current_user.id
    from datetime import datetime
    content.approved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Content {approval_data.status.lower()} successfully"}

