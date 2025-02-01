from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EncryptedType
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
import enum
from datetime import datetime

class DocumentStatus(enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False, default=1)
    title = Column(String(255), nullable=False)
    content = Column(EncryptedType, nullable=False)  # Encrypted storage
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    jurisdiction = Column(String(100), nullable=False)
    metadata = Column(JSONB, nullable=False, default={})
    
    # Version control
    parent_version_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    versions = relationship("Document", backref="parent_version")
    
    # Ownership and permissions
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('templates.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Compliance tracking
    compliance_status = Column(JSONB, nullable=False, default={})
    last_compliance_check = Column(DateTime, nullable=True)
    
    __table_args__ = (
        # Ensure version numbers are unique per document lineage
        UniqueConstraint('parent_version_id', 'version', name='uq_document_version'),
    ) 