from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
from datetime import datetime

class AuditRecord(Base):
    __tablename__ = "audit_records"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Action details
    action = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=False)
    
    # Change tracking
    changes = Column(JSONB, nullable=False)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    metadata = Column(JSONB, nullable=False, default={}) 