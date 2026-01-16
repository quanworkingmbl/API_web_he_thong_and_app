from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.organization import Organization
from app.api.v1.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True

@router.get("", response_model=List[OrganizationResponse])
async def get_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of organizations"""
    organizations = db.query(Organization).all()
    return [OrganizationResponse.from_orm(org) for org in organizations]

