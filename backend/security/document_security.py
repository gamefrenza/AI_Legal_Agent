from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from datetime import datetime
from ..models.document import Document, DocumentAccess
from ..models.audit import AuditLog
from .encryption import EncryptionService

class DocumentSecurityManager:
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.access_manager = DocumentAccessManager()
        self.version_manager = DocumentVersionManager()
        self.audit_logger = SecurityAuditLogger()
    
    async def secure_document(
        self,
        document: Document,
        access_policy: Dict[str, Any]
    ) -> Document:
        """Apply security measures to document"""
        try:
            # 1. Encrypt document content
            encrypted_content = await self.encryption_service.encrypt_document(
                document.content,
                document.metadata
            )
            
            # 2. Apply access controls
            access_controls = await self.access_manager.apply_access_policy(
                document.id,
                access_policy
            )
            
            # 3. Create version record
            version_info = await self.version_manager.create_version(document)
            
            # 4. Update document with security measures
            secured_document = Document(
                **document.dict(),
                content=encrypted_content,
                access_controls=access_controls,
                version_info=version_info,
                security_metadata={
                    'encryption_timestamp': datetime.utcnow(),
                    'encryption_method': self.encryption_service.method,
                    'access_policy': access_policy
                }
            )
            
            # 5. Log security action
            await self.audit_logger.log_security_action(
                action='document_secured',
                document_id=document.id,
                user_id=access_policy.get('owner_id'),
                details={
                    'version': version_info.version,
                    'access_policy': access_policy
                }
            )
            
            return secured_document
            
        except Exception as e:
            await self.audit_logger.log_security_error(
                error=e,
                document_id=document.id
            )
            raise 