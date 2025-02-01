from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
from datetime import datetime

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    jurisdiction = Column(String(100), nullable=False)
    
    # Rule definition
    rule_type = Column(String(50), nullable=False)
    rule_definition = Column(JSONB, nullable=False)
    severity = Column(String(20), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Versioning
    version = Column(Integer, nullable=False, default=1)
    active = Column(Boolean, default=True)

class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    rule_id = Column(Integer, ForeignKey('compliance_rules.id'), nullable=False)
    
    # Check results
    status = Column(String(50), nullable=False)
    details = Column(JSONB, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow) 