from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ContractStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class PartnerContract(Base):
    __tablename__ = "partner_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(100), unique=True, nullable=False)
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Producer
    contract_type = Column(String(50), nullable=False)  # ADVERTISING, PARTNERSHIP
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    amount = Column(Numeric(10, 2), nullable=True)
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT)
    terms = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    partner = relationship("User", foreign_keys=[partner_id])
    creator = relationship("User", foreign_keys=[created_by])

