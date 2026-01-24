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
    start_date: str
    end_date: Optional[str]
    amount: Optional[Decimal]
    status: str
    terms: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

@router.get("", response_model=List[ContractResponse])
async def get_contracts(
    status: Optional[str] = Query(None),
    partner_id: Optional[int] = Query(None),
    contract_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get partner contracts (advertising contracts with producers)"""
    query = db.query(PartnerContract)
    
    if status:
        query = query.filter(PartnerContract.status == status)
    if partner_id:
        query = query.filter(PartnerContract.partner_id == partner_id)
    if contract_type:
        query = query.filter(PartnerContract.contract_type == contract_type)
    
    contracts = query.all()
    return [ContractResponse.from_orm(c) for c in contracts]

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

