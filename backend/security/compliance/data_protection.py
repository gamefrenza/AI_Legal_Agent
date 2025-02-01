from typing import Dict, Any, List
from datetime import datetime
from ..models.document import Document
from ..models.compliance import PrivacyPolicy, DataRetentionPolicy
from .encryption import EncryptionService

class DataProtectionManager:
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.privacy_manager = PrivacyManager()
        self.retention_manager = RetentionManager()
        self.audit_logger = ComplianceAuditLogger()
    
    async def protect_sensitive_data(
        self,
        document: Document,
        policy: PrivacyPolicy
    ) -> Document:
        """Apply data protection measures"""
        try:
            # 1. Identify sensitive data
            sensitive_data = await self.privacy_manager.identify_sensitive_data(
                document.content
            )
            
            # 2. Apply privacy controls
            protected_content = await self.privacy_manager.apply_privacy_controls(
                document.content,
                sensitive_data,
                policy
            )
            
            # 3. Apply encryption
            encrypted_content = await self.encryption_service.encrypt_sensitive_data(
                protected_content,
                sensitive_data.keys()
            )
            
            # 4. Update document metadata
            protected_document = Document(
                **document.dict(),
                content=encrypted_content,
                privacy_metadata={
                    'protection_level': policy.protection_level,
                    'sensitive_fields': list(sensitive_data.keys()),
                    'applied_at': datetime.utcnow()
                }
            )
            
            # 5. Log protection action
            await self.audit_logger.log_data_protection(
                document_id=document.id,
                protection_details=protected_document.privacy_metadata
            )
            
            return protected_document
            
        except Exception as e:
            await self.audit_logger.log_protection_error(
                document_id=document.id,
                error=str(e)
            )
            raise 