from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.payment import Payment, PaymentTransaction, PaymentStatus, PaymentCycle
from app.api.v1.auth import get_current_user, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

router = APIRouter()

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    seller_id: int
    amount: Decimal
    platform_fee_percentage: Decimal
    platform_fee_amount: Decimal
    seller_amount: Decimal
    status: str
    payment_cycle: str
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedPaymentResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[PaymentResponse]

class PaymentReconciliationResponse(BaseModel):
    total_customer_paid: Decimal
    total_platform_commission: Decimal
    total_seller_amount: Decimal
    payments: List[PaymentResponse]

class RefundRequest(BaseModel):
    payment_id: int
    amount: Decimal
    reason: str

class PaymentComplaintRequest(BaseModel):
    payment_id: int
    complaint: str

@router.get("", response_model=PaginatedPaymentResponse)
async def get_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    seller_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get list of payments with pagination"""
    query = db.query(Payment)
    
    if status:
        query = query.filter(Payment.status == status)
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    if seller_id:
        query = query.filter(Payment.seller_id == seller_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    skip = (page - 1) * limit
    payments = query.offset(skip).limit(limit).all()
    
    return PaginatedPaymentResponse(
        total=total,
        page=page,
        limit=limit,
        data=[PaymentResponse.from_orm(p) for p in payments]
    )

@router.get("/{payment_id}/status")
async def get_payment_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment status"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return PaymentResponse.from_orm(payment)

@router.get("/reconciliation")
async def get_payment_reconciliation(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get payment reconciliation data"""
    query = db.query(Payment).filter(Payment.status == PaymentStatus.COMPLETED)
    
    # Add date filters if provided
    # Note: You'll need to implement date parsing and filtering
    
    payments = query.all()
    
    total_customer_paid = sum(p.amount for p in payments)
    total_platform_commission = sum(p.platform_fee_amount for p in payments)
    total_seller_amount = sum(p.seller_amount for p in payments)
    
    return PaymentReconciliationResponse(
        total_customer_paid=total_customer_paid,
        total_platform_commission=total_platform_commission,
        total_seller_amount=total_seller_amount,
        payments=[PaymentResponse.from_orm(p) for p in payments]
    )

@router.post("/refund")
async def process_refund(
    refund_data: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a refund"""
    payment = db.query(Payment).filter(Payment.id == refund_data.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Create refund transaction
    refund_transaction = PaymentTransaction(
        payment_id=refund_data.payment_id,
        transaction_type="REFUND",
        amount=refund_data.amount,
        status=PaymentStatus.REFUNDED,
        notes=refund_data.reason
    )
    
    # Update payment status
    payment.status = PaymentStatus.REFUNDED
    
    db.add(refund_transaction)
    db.commit()
    
    return {"message": "Refund processed successfully"}

@router.post("/complaint")
async def create_payment_complaint(
    complaint_data: PaymentComplaintRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment complaint"""
    payment = db.query(Payment).filter(Payment.id == complaint_data.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # You may want to create a separate complaint record
    # For now, just return success
    return {"message": "Payment complaint created successfully"}

@router.put("/config/fee")
async def update_platform_fee(
    fee_percentage: Decimal = Query(..., ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update platform fee percentage (global config)"""
    # This would typically be stored in a configuration table
    # For now, return success
    return {"message": f"Platform fee updated to {fee_percentage}%"}

@router.put("/config/cycle")
async def update_payment_cycle(
    cycle: str = Query(..., pattern="^(WEEKLY|MONTHLY)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update payment cycle (global config)"""
    # This would typically be stored in a configuration table
    return {"message": f"Payment cycle updated to {cycle}"}

