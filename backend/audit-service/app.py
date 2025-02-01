from fastapi import FastAPI, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import uuid
import motor.motor_asyncio

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuditLog(BaseModel):
    id: str
    action: str
    user_id: str
    resource_type: str
    resource_id: str
    changes: Dict
    timestamp: datetime
    ip_address: Optional[str]
    metadata: Dict

class AuditService:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client.legal_automation
        self.audit_logs = self.db.audit_logs
    
    async def log_action(self, log_data: dict) -> AuditLog:
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            **log_data
        )
        await self.audit_logs.insert_one(audit_log.dict())
        return audit_log

audit_service = AuditService()

@app.post("/audit/log", response_model=AuditLog)
async def create_audit_log(log_data: dict, token: str = Security(oauth2_scheme)):
    return await audit_service.log_action(log_data) 