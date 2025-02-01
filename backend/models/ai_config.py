from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
from datetime import datetime

class AIAgent(Base):
    __tablename__ = "ai_agents"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)
    
    # Configuration
    config = Column(JSONB, nullable=False)
    active = Column(Boolean, default=True)
    
    # Performance tracking
    metrics = Column(JSONB, nullable=False, default={})
    last_execution = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AITask(Base):
    __tablename__ = "ai_tasks"
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('ai_agents.id'), nullable=False)
    
    # Task details
    status = Column(String(50), nullable=False)
    input_data = Column(JSONB, nullable=False)
    output_data = Column(JSONB, nullable=True)
    
    # Execution tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_log = Column(JSONB, nullable=True) 