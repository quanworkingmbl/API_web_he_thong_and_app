from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.partner_contract import PartnerContract, ContractStatus
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

router = APIRouter()

class ContractResponse(BaseModel):
    id: int
    contract_number: str
    partner_id: int
    contract_type: str
    start_date: datetime
    end_date: Optional[datetime]
    amount: Optional[Decimal]
    status: str
    terms: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedContractResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[ContractResponse]

@router.get("", response_model=PaginatedContractResponse)
async def get_contracts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    partner_id: Optional[int] = Query(None),
    contract_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get partner contracts (advertising contracts with producers) with pagination"""
    query = db.query(PartnerContract)
    
    if status:
        query = query.filter(PartnerContract.status == status)
    if partner_id:
        query = query.filter(PartnerContract.partner_id == partner_id)
    if contract_type:
        query = query.filter(PartnerContract.contract_type == contract_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    skip = (page - 1) * limit
    contracts = query.offset(skip).limit(limit).all()
    
    return PaginatedContractResponse(
        total=total,
        page=page,
        limit=limit,
        data=[ContractResponse.from_orm(c) for c in contracts]
    )

@router.post("")
async def create_contract(
    contract_number: str,
    partner_id: int,
    contract_type: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    amount: Optional[Decimal] = None,
    terms: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a partner contract"""
    new_contract = PartnerContract(
        contract_number=contract_number,
        partner_id=partner_id,
        contract_type=contract_type,
        start_date=start_date,
        end_date=end_date,
        amount=amount,
        status=ContractStatus.DRAFT,
        terms=terms,
        created_by=current_user.id
    )
    
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    
    return ContractResponse.from_orm(new_contract)

