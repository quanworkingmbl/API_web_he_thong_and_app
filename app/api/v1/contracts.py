from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.partner_contract import PartnerContract, ContractStatus
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.core.permissions import check_contract_manage_access
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

router = APIRouter()


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================

class ContractResponse(BaseModel):
    id: int
    contract_number: str
    partner_id: int
    partner_name: Optional[str] = None
    contract_type: str
    start_date: datetime
    end_date: Optional[datetime]
    amount: Optional[Decimal]
    status: str
    terms: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedContractResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[ContractResponse]


class CreateContractRequest(BaseModel):
    contract_number: str = Field(..., min_length=2, max_length=50)
    partner_id: int
    contract_type: str = Field(..., pattern="^(ADVERTISING|PARTNERSHIP|DISTRIBUTION|OTHER)$")
    start_date: datetime
    end_date: Optional[datetime] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    terms: Optional[str] = None


class UpdateContractRequest(BaseModel):
    contract_number: Optional[str] = Field(None, min_length=2, max_length=50)
    contract_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = None
    terms: Optional[str] = None


# ==============================================================================
# CRUD ENDPOINTS
# ==============================================================================

@router.get("", response_model=PaginatedContractResponse)
async def get_contracts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    partner_id: Optional[int] = Query(None),
    contract_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by contract number"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get partner contracts with pagination"""
    query = db.query(PartnerContract)
    
    if status:
        query = query.filter(PartnerContract.status == status)
    if partner_id:
        query = query.filter(PartnerContract.partner_id == partner_id)
    if contract_type:
        query = query.filter(PartnerContract.contract_type == contract_type)
    if search:
        query = query.filter(PartnerContract.contract_number.ilike(f"%{search}%"))
    
    total = query.count()
    skip = (page - 1) * limit
    contracts = query.order_by(PartnerContract.created_at.desc()).offset(skip).limit(limit).all()
    
    contract_list = []
    for c in contracts:
        partner = db.query(User).filter(User.id == c.partner_id).first()
        contract_list.append(ContractResponse(
            id=c.id,
            contract_number=c.contract_number,
            partner_id=c.partner_id,
            partner_name=partner.name if partner else None,
            contract_type=c.contract_type,
            start_date=c.start_date,
            end_date=c.end_date,
            amount=c.amount,
            status=c.status.value if hasattr(c.status, 'value') else str(c.status),
            terms=c.terms,
            created_by=c.created_by,
            created_at=c.created_at,
            updated_at=c.updated_at
        ))
    
    return PaginatedContractResponse(
        total=total,
        page=page,
        limit=limit,
        data=contract_list
    )


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract_by_id(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contract by ID"""
    contract = db.query(PartnerContract).filter(PartnerContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    partner = db.query(User).filter(User.id == contract.partner_id).first()
    
    return ContractResponse(
        id=contract.id,
        contract_number=contract.contract_number,
        partner_id=contract.partner_id,
        partner_name=partner.name if partner else None,
        contract_type=contract.contract_type,
        start_date=contract.start_date,
        end_date=contract.end_date,
        amount=contract.amount,
        status=contract.status.value if hasattr(contract.status, 'value') else str(contract.status),
        terms=contract.terms,
        created_by=contract.created_by,
        created_at=contract.created_at,
        updated_at=contract.updated_at
    )


@router.post("", response_model=ContractResponse)
async def create_contract(
    contract_data: CreateContractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a partner contract"""
    check_contract_manage_access(current_user)

    # Check if contract number already exists
    existing = db.query(PartnerContract).filter(
        PartnerContract.contract_number == contract_data.contract_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contract number already exists")
    
    # Validate partner exists
    partner = db.query(User).filter(User.id == contract_data.partner_id).first()
    if not partner:
        raise HTTPException(status_code=400, detail="Partner not found")
    
    new_contract = PartnerContract(
        contract_number=contract_data.contract_number,
        partner_id=contract_data.partner_id,
        contract_type=contract_data.contract_type,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        amount=contract_data.amount,
        status=ContractStatus.DRAFT,
        terms=contract_data.terms,
        created_by=current_user.id
    )
    
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    
    return ContractResponse(
        id=new_contract.id,
        contract_number=new_contract.contract_number,
        partner_id=new_contract.partner_id,
        partner_name=partner.name,
        contract_type=new_contract.contract_type,
        start_date=new_contract.start_date,
        end_date=new_contract.end_date,
        amount=new_contract.amount,
        status=new_contract.status.value if hasattr(new_contract.status, 'value') else str(new_contract.status),
        terms=new_contract.terms,
        created_by=new_contract.created_by,
        created_at=new_contract.created_at,
        updated_at=None
    )


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    contract_data: UpdateContractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a contract"""
    check_contract_manage_access(current_user)

    contract = db.query(PartnerContract).filter(PartnerContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    update_data = contract_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contract, key, value)
    
    db.commit()
    db.refresh(contract)
    
    partner = db.query(User).filter(User.id == contract.partner_id).first()
    
    return ContractResponse(
        id=contract.id,
        contract_number=contract.contract_number,
        partner_id=contract.partner_id,
        partner_name=partner.name if partner else None,
        contract_type=contract.contract_type,
        start_date=contract.start_date,
        end_date=contract.end_date,
        amount=contract.amount,
        status=contract.status.value if hasattr(contract.status, 'value') else str(contract.status),
        terms=contract.terms,
        created_by=contract.created_by,
        created_at=contract.created_at,
        updated_at=contract.updated_at
    )


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a contract"""
    check_contract_manage_access(current_user)

    contract = db.query(PartnerContract).filter(PartnerContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    db.delete(contract)
    db.commit()
    
    return {"success": True, "message": "Contract deleted successfully"}
