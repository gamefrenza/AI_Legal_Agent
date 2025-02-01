from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
from datetime import datetime

# Template inheritance association table
template_inheritance = Table('template_inheritance', Base.metadata,
    Column('parent_id', Integer, ForeignKey('templates.id')),
    Column('child_id', Integer, ForeignKey('templates.id'))
)

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content = Column(String, nullable=False)
    jurisdiction = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    
    # Template inheritance
    parent_templates = relationship(
        "Template",
        secondary=template_inheritance,
        primaryjoin=id==template_inheritance.c.child_id,
        secondaryjoin=id==template_inheritance.c.parent_id,
        backref="child_templates"
    )
    
    # Variables and placeholders
    variables = Column(JSONB, nullable=False, default=[])
    
    # Metadata
    metadata = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Access control
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    access_level = Column(String(50), nullable=False, default='private') 