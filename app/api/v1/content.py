from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.content import Content, ContentStatus, ContentAuditLog, ContentAuditAction
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.core.permissions import check_seller_kyc_verified
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json
from app.services.notification import (
    notify_content_pending_to_admin,
    notify_content_approved_to_author,
    notify_content_rejected_to_author,
)

router = APIRouter()

# ==============================================================================
# CONSTANTS FOR VALIDATION
# ==============================================================================

MIN_CONTENT_LENGTH = 30
MIN_MEDIA_COUNT = 1


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
    is_active: bool
    images: Optional[str]
    videos: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
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
    status: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    notes: Optional[str] = None


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def validate_content_media(content_text: Optional[str], images: Optional[str], videos: Optional[str], is_update: bool = False) -> List[str]:
    """Validate content quality - minimum description and media requirements"""
    errors = []
    
    # Validate content length
    if content_text:
        if len(content_text.strip()) < MIN_CONTENT_LENGTH:
            errors.append(f"Nội dung phải có ít nhất {MIN_CONTENT_LENGTH} ký tự (hiện tại: {len(content_text.strip())} ký tự)")
    elif not is_update:
        errors.append(f"Nội dung là bắt buộc và phải có ít nhất {MIN_CONTENT_LENGTH} ký tự")
    
    # Validate media count
    media_count = 0
    if images:
        try:
            images_list = json.loads(images)
            if isinstance(images_list, list):
                media_count += len(images_list)
            elif images_list:
                media_count += 1
        except json.JSONDecodeError:
            if images.strip():
                media_count += 1
    
    if videos:
        try:
            videos_list = json.loads(videos)
            if isinstance(videos_list, list):
                media_count += len(videos_list)
            elif videos_list:
                media_count += 1
        except json.JSONDecodeError:
            if videos.strip():
                media_count += 1
    
    if media_count < MIN_MEDIA_COUNT and not is_update:
        errors.append(f"Bài viết phải có ít nhất {MIN_MEDIA_COUNT} ảnh hoặc video")
    
    return errors


def log_content_audit(db: Session, content_id: int, action: ContentAuditAction, user_id: int, 
                      old_status: str = None, new_status: str = None, notes: str = None):
    """Log content action for audit purposes"""
    audit_log = ContentAuditLog(
        content_id=content_id,
        action=action,
        user_id=user_id,
        old_status=old_status,
        new_status=new_status,
        notes=notes
    )
    db.add(audit_log)


def check_content_ownership(content: Content, current_user: User) -> None:
    """
    Check if user can edit/delete content.
    Only author, admin, or content_manager can modify.
    """
    is_owner = content.author_id == current_user.id
    is_privileged = current_user.type in ("admin", "content_manager")
    
    if not (is_owner or is_privileged):
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền chỉnh sửa/xóa nội dung này. Chỉ tác giả hoặc admin/content_manager mới được phép."
        )


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
    include_inactive: bool = Query(False, description="Include inactive content (admin only)"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get list of contents with pagination.
    - Admin/content_manager: sees all content (with include_inactive=True)
    - Seller: sees own content + public APPROVED content
    - Consumer/Guest: only sees APPROVED & is_active content
    """
    query = db.query(Content)
    
    # Filter based on user role
    is_privileged = current_user and current_user.type in ("admin", "content_manager")
    
    if not is_privileged:
        # Non-admin: only active content
        query = query.filter(Content.is_active == True)
        
        if current_user and current_user.type in ("producer", "seller"):
            # Seller can see own content (any status) + public APPROVED
            query = query.filter(
                (Content.author_id == current_user.id) | 
                (Content.status == ContentStatus.APPROVED)
            )
        else:
            # Consumer/Guest: only APPROVED
            query = query.filter(Content.status == ContentStatus.APPROVED)
    elif not include_inactive:
        # Admin without include_inactive: only active
        query = query.filter(Content.is_active == True)
    
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
            is_active=c.is_active,
            images=c.images,
            videos=c.videos,
            approved_by=c.approved_by,
            approved_at=c.approved_at,
            rejection_reason=c.rejection_reason,
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
    
    # Check access permission
    is_privileged = current_user and current_user.type in ("admin", "content_manager")
    is_owner = current_user and content.author_id == current_user.id
    
    if not content.is_active and not (is_privileged or is_owner):
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status != ContentStatus.APPROVED and not (is_privileged or is_owner):
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
        is_active=content.is_active,
        images=content.images,
        videos=content.videos,
        approved_by=content.approved_by,
        approved_at=content.approved_at,
        rejection_reason=content.rejection_reason,
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
    Create new content.
    - Admin: can create for any author
    - Producer/Seller: must be KYC verified, author_id = current_user.id
    """
    is_admin = current_user.type == "admin"
    
    # KYC check for non-admin
    if not is_admin:
        check_seller_kyc_verified(current_user, db)
        actual_author_id = current_user.id
    else:
        actual_author_id = content_data.author_id
    
    # Validate author exists
    author = db.query(User).filter(User.id == actual_author_id).first()
    if not author:
        raise HTTPException(status_code=400, detail="Author not found")
    
    # Validate content quality
    validation_errors = validate_content_media(
        content_data.content, 
        content_data.images, 
        content_data.videos
    )
    if validation_errors:
        raise HTTPException(status_code=400, detail="; ".join(validation_errors))
    
    new_content = Content(
        title=content_data.title,
        content=content_data.content,
        content_type=content_data.content_type,
        author_id=actual_author_id,
        product_id=content_data.product_id,
        status=ContentStatus.PENDING,
        images=content_data.images,
        videos=content_data.videos,
        is_active=True
    )
    
    db.add(new_content)
    db.flush()  # Get ID before commit
    
    # Log audit
    log_content_audit(
        db=db,
        content_id=new_content.id,
        action=ContentAuditAction.CREATE,
        user_id=current_user.id,
        new_status="PENDING",
        notes=f"Content created by {current_user.email}"
    )
    
    db.commit()
    db.refresh(new_content)

    # [NOTIFICATION C1] Thông báo Admin/Content Manager: bài viết mới chờ duyệt
    try:
        admin_ids = [
            u.id for u in db.query(User).filter(
                User.type.in_(["admin", "content_manager"])
            ).all()
        ]
        if admin_ids:
            notify_content_pending_to_admin(
                db=db,
                admin_user_ids=admin_ids,
                content_id=new_content.id,
                content_title=new_content.title,
                author_name=author.name if author else "Tác giả",
            )
            db.commit()
    except Exception:
        pass

    return ContentResponse(
        id=new_content.id,
        title=new_content.title,
        content=new_content.content,
        content_type=new_content.content_type,
        author_id=new_content.author_id,
        author_name=author.name,
        product_id=new_content.product_id,
        status=new_content.status.value if hasattr(new_content.status, 'value') else str(new_content.status),
        is_active=new_content.is_active,
        images=new_content.images,
        videos=new_content.videos,
        approved_by=None,
        approved_at=None,
        rejection_reason=None,
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
    """
    Update content.
    - Only author, admin, or content_manager can update
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Ownership check
    check_content_ownership(content, current_user)
    
    old_status = content.status.value if hasattr(content.status, 'value') else str(content.status)
    
    # Validate content quality if updating content/media
    update_data = content_data.dict(exclude_unset=True)
    
    content_text = update_data.get('content', content.content)
    images = update_data.get('images', content.images)
    videos = update_data.get('videos', content.videos)
    
    validation_errors = validate_content_media(content_text, images, videos, is_update=True)
    if validation_errors:
        raise HTTPException(status_code=400, detail="; ".join(validation_errors))
    
    for key, value in update_data.items():
        setattr(content, key, value)
    
    # Reset to pending if content is updated (except by admin)
    if update_data and current_user.type != "admin":
        content.status = ContentStatus.PENDING
    
    content.updated_at = datetime.utcnow()
    
    # Log audit
    log_content_audit(
        db=db,
        content_id=content.id,
        action=ContentAuditAction.UPDATE,
        user_id=current_user.id,
        old_status=old_status,
        new_status=content.status.value if hasattr(content.status, 'value') else str(content.status),
        notes=f"Content updated by {current_user.email}"
    )
    
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
        is_active=content.is_active,
        images=content.images,
        videos=content.videos,
        approved_by=content.approved_by,
        approved_at=content.approved_at,
        rejection_reason=content.rejection_reason,
        created_at=content.created_at,
        updated_at=content.updated_at
    )


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete content (set is_active=False).
    - Only author, admin, or content_manager can delete
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Ownership check
    check_content_ownership(content, current_user)
    
    # Soft delete
    content.is_active = False
    content.deleted_at = datetime.utcnow()
    content.deleted_by = current_user.id
    
    # Log audit
    log_content_audit(
        db=db,
        content_id=content.id,
        action=ContentAuditAction.DELETE,
        user_id=current_user.id,
        notes=f"Content soft-deleted by {current_user.email}"
    )
    
    db.commit()
    
    return {"success": True, "message": "Content deleted successfully"}


@router.put("/{content_id}/restore")
async def restore_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Restore soft-deleted content (admin/content_manager only).
    """
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới có thể khôi phục nội dung")
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.is_active = True
    content.deleted_at = None
    content.deleted_by = None
    
    # Log audit
    log_content_audit(
        db=db,
        content_id=content.id,
        action=ContentAuditAction.RESTORE,
        user_id=current_user.id,
        notes=f"Content restored by {current_user.email}"
    )
    
    db.commit()
    
    return {"success": True, "message": "Content restored successfully"}


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
    """
    Approve or reject content.
    - Only admin or content_manager can approve/reject
    - Check author's KYC status before approving
    """
    # Permission check
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Không có quyền duyệt content. Yêu cầu role: admin hoặc content_manager")
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    old_status = content.status.value if hasattr(content.status, 'value') else str(content.status)
    
    # Check author's KYC before approving
    if approval_data.status == "APPROVED":
        from app.models.seller_profile import SellerProfile, VerificationStatus
        author = db.query(User).filter(User.id == content.author_id).first()
        
        if author and author.type in ("producer", "seller"):
            seller_profile = db.query(SellerProfile).filter(
                SellerProfile.user_id == content.author_id
            ).first()
            
            if not seller_profile or seller_profile.verification_status != VerificationStatus.VERIFIED:
                raise HTTPException(
                    status_code=400,
                    detail="Không thể duyệt nội dung: Tác giả chưa được xác minh hồ sơ kinh doanh (KYC)"
                )
    
    content.status = approval_data.status
    content.approved_by = current_user.id
    content.approved_at = datetime.utcnow()
    
    if approval_data.status == "REJECTED":
        content.rejection_reason = approval_data.notes
    
    # Log audit
    action = ContentAuditAction.APPROVE if approval_data.status == "APPROVED" else ContentAuditAction.REJECT
    log_content_audit(
        db=db,
        content_id=content.id,
        action=action,
        user_id=current_user.id,
        old_status=old_status,
        new_status=approval_data.status,
        notes=approval_data.notes
    )
    
    db.commit()

    # [NOTIFICATION C2/C3] Thông báo cho tác giả kết quả duyệt
    try:
        if approval_data.status == "APPROVED":
            notify_content_approved_to_author(
                db=db,
                author_id=content.author_id,
                content_id=content_id,
                content_title=content.title,
            )
        else:
            notify_content_rejected_to_author(
                db=db,
                author_id=content.author_id,
                content_id=content_id,
                content_title=content.title,
                notes=approval_data.notes,
            )
        db.commit()
    except Exception:
        pass

    return {"success": True, "message": f"Content {approval_data.status.lower()} successfully"}


# ==============================================================================
# AUDIT LOG ENDPOINT
# ==============================================================================

@router.get("/{content_id}/audit-logs")
async def get_content_audit_logs(
    content_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a content (admin/content_manager only).
    """
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới có thể xem audit logs")
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    query = db.query(ContentAuditLog).filter(ContentAuditLog.content_id == content_id)
    total = query.count()
    skip = (page - 1) * limit
    logs = query.order_by(ContentAuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": log.id,
                "action": log.action.value if hasattr(log.action, 'value') else str(log.action),
                "user_id": log.user_id,
                "old_status": log.old_status,
                "new_status": log.new_status,
                "notes": log.notes,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit
        }
    }
