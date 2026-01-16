from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class PublisherResponse(BaseModel):
    id: int
    email: str
    name: str
    type: Optional[str]
    activated: int

    class Config:
        from_attributes = True

class AdvertiserPrivateResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class FlightResponse(BaseModel):
    id: int
    name: str
    running: int
    status: str

    class Config:
        from_attributes = True

@router.get("/accounts")
async def get_accounts(
    model: Optional[str] = Query(None),
    activated: Optional[int] = Query(None),
    limit: int = Query(500, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accounts (publishers, advertisers, etc.)"""
    from app.models.user import User
    
    query = db.query(User).filter(User.deleted_at.is_(None))
    
    if model:
        query = query.filter(User.type == model)
    if activated is not None:
        query = query.filter(User.activated == activated)
    
    users = query.limit(limit).all()
    
    return {
        "data": [PublisherResponse(
            id=u.id,
            email=u.email,
            name=u.name,
            type=u.type,
            activated=u.activated
        ) for u in users]
    }

@router.get("/advertiser-private")
async def get_advertiser_private(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get private advertisers"""
    from app.models.user import User
    
    advertisers = db.query(User).filter(
        User.type == "advertiser",
        User.activated == 1,
        User.deleted_at.is_(None)
    ).all()
    
    return {
        "data": [AdvertiserPrivateResponse(
            id=a.id,
            name=a.name,
            email=a.email
        ) for a in advertisers]
    }

@router.get("/flights")
async def get_flights(
    running: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get flights (placeholder - adjust based on your flight model)"""
    # This is a placeholder - you may need to create a Flight model
    # For now, returning empty data
    return {
        "data": [],
        "message": "Flight model not implemented yet"
    }

@router.get("/report/flights/realtime")
async def get_flight_realtime(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get realtime flight reports"""
    # Placeholder for flight realtime data
    return {
        "data": [],
        "message": "Flight realtime report not implemented yet"
    }

