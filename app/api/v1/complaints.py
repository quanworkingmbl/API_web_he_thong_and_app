from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.complaint import Complaint, Review, ComplaintStatus
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

class ComplaintResponse(BaseModel):
    id: int
    product_id: Optional[int]
    order_id: Optional[int]
    user_id: int
    complaint_type: str
    title: str
    description: str
    status: str
    handled_by: Optional[int]
    resolution: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

@router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    product_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get product reviews"""
    query = db.query(Review)
    
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)
    
    reviews = query.all()
    return [ReviewResponse.from_orm(r) for r in reviews]

@router.get("/complaints", response_model=List[ComplaintResponse])
async def get_complaints(
    status: Optional[str] = Query(None),
    complaint_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get product complaints"""
    query = db.query(Complaint)
    
    if status:
        query = query.filter(Complaint.status == status)
    if complaint_type:
        query = query.filter(Complaint.complaint_type == complaint_type)
    
    complaints = query.all()
    return [ComplaintResponse.from_orm(c) for c in complaints]

@router.put("/complaints/{complaint_id}/handle")
async def handle_complaint(
    complaint_id: int,
    status: str,
    resolution: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle a complaint"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = status
    complaint.handled_by = current_user.id
    if resolution:
        complaint.resolution = resolution
    
    db.commit()
    
    return {"message": "Complaint handled successfully"}

