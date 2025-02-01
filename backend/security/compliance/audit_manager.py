from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.audit import ComplianceAudit, AuditEvent
from ..utils.hash import calculate_hash

class ComplianceAuditManager:
    def __init__(self):
        self.audit_store = AuditStore()
        self.event_validator = AuditEventValidator()
        self.report_generator = AuditReportGenerator()
    
    async def log_compliance_event(
        self,
        event_type: str,
        document_id: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AuditEvent:
        """Log compliance-related event"""
        event = AuditEvent(
            event_type=event_type,
            document_id=document_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            details=details,
            event_hash=await self._generate_event_hash(details)
        )
        
        # Validate event
        await self.event_validator.validate_event(event)
        
        # Store event
        await self.audit_store.store_event(event)
        
        return event
    
    async def create_audit_trail(
        self,
        document_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> ComplianceAudit:
        """Create audit trail for document"""
        # Get events
        events = await self.audit_store.get_document_events(
            document_id,
            start_time,
            end_time
        )
        
        # Create audit trail
        audit_trail = ComplianceAudit(
            document_id=document_id,
            events=events,
            generated_at=datetime.utcnow(),
            hash_chain=await self._generate_hash_chain(events)
        )
        
        # Store audit trail
        await self.audit_store.store_audit_trail(audit_trail)
        
        return audit_trail
    
    async def _generate_hash_chain(
        self,
        events: List[AuditEvent]
    ) -> str:
        """Generate hash chain for events"""
        if not events:
            return ""
            
        current_hash = events[0].event_hash
        for event in events[1:]:
            current_hash = await calculate_hash(
                f"{current_hash}:{event.event_hash}"
            )
            
        return current_hash 