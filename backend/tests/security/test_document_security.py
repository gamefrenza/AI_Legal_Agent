import pytest
import json
from unittest.mock import AsyncMock, patch
from document_service.document_processor import DocumentProcessor
from security.access_control import AccessControlManager
from security.encryption import EncryptionService
from audit_service.audit_logger import AuditLogger
from models.document import Document
from models.user import User, Role

class TestDocumentSecurity:
    @pytest.fixture
    async def security_components(self):
        document_processor = DocumentProcessor()
        access_control = AccessControlManager()
        encryption_service = EncryptionService()
        audit_logger = AuditLogger()
        return document_processor, access_control, encryption_service, audit_logger
    
    @pytest.fixture
    def users(self):
        admin_user = User(
            id="admin123",
            name="Admin User",
            email="admin@example.com",
            roles=[Role.ADMIN, Role.LEGAL]
        )
        
        legal_user = User(
            id="legal123",
            name="Legal User",
            email="legal@example.com",
            roles=[Role.LEGAL]
        )
        
        basic_user = User(
            id="basic123",
            name="Basic User",
            email="user@example.com",
            roles=[Role.USER]
        )
        
        return admin_user, legal_user, basic_user
    
    @pytest.mark.asyncio
    async def test_document_access_control(self, security_components, users):
        document_processor, access_control, encryption_service, audit_logger = security_components
        admin_user, legal_user, basic_user = users
        
        # 1. Create document with admin user
        document = await document_processor.process_document(
            document_id=None,
            template_id="confidential-agreement",
            variables={"party1": "Company A", "party2": "Company B"},
            format="docx",
            user_id=admin_user.id,
            context={"classification": "confidential"}
        )
        
        # 2. Set access permissions
        await access_control.set_document_permissions(
            document_id=document.id,
            owner_id=admin_user.id,
            read_roles=[Role.ADMIN, Role.LEGAL],
            write_roles=[Role.ADMIN],
            delete_roles=[Role.ADMIN]
        )
        
        # 3. Test access for different users
        # Admin should have full access
        assert await access_control.can_read(admin_user.id, document.id) is True
        assert await access_control.can_write(admin_user.id, document.id) is True
        assert await access_control.can_delete(admin_user.id, document.id) is True
        
        # Legal should have read-only access
        assert await access_control.can_read(legal_user.id, document.id) is True
        assert await access_control.can_write(legal_user.id, document.id) is False
        assert await access_control.can_delete(legal_user.id, document.id) is False
        
        # Basic user should have no access
        assert await access_control.can_read(basic_user.id, document.id) is False
        assert await access_control.can_write(basic_user.id, document.id) is False
        assert await access_control.can_delete(basic_user.id, document.id) is False
        
        # 4. Verify audit logs were created
        audit_logs = await audit_logger.get_logs_for_document(document.id)
        assert len(audit_logs) >= 2  # At least creation and permission setting
        
        # Verify creation log
        creation_log = next((log for log in audit_logs if log.action == "CREATE"), None)
        assert creation_log is not None
        assert creation_log.user_id == admin_user.id
        
        # Verify permission log
        permission_log = next((log for log in audit_logs if log.action == "SET_PERMISSIONS"), None)
        assert permission_log is not None
    
    @pytest.mark.asyncio
    async def test_document_encryption(self, security_components, users):
        document_processor, access_control, encryption_service, audit_logger = security_components
        admin_user, _, _ = users
        
        # 1. Create document with sensitive data
        document = await document_processor.process_document(
            document_id=None,
            template_id="contract-with-pii",
            variables={
                "client_name": "John Smith",
                "ssn": "123-45-6789",
                "address": "123 Main St, Anytown, USA"
            },
            format="docx",
            user_id=admin_user.id,
            context={"classification": "sensitive"}
        )
        
        # 2. Verify document is encrypted at rest
        stored_document = await document_processor._load_document(document.id)
        
        # Content should be encrypted
        assert stored_document.is_encrypted is True
        
        # 3. Decrypt document for authorized user
        decrypted_content = await encryption_service.decrypt_document(
            document_id=document.id,
            user_id=admin_user.id
        )
        
        # Verify decryption worked
        assert decrypted_content is not None
        assert b"John Smith" in decrypted_content
        
        # 4. Verify PII is properly masked in logs
        audit_logs = await audit_logger.get_logs_for_document(document.id)
        for log in audit_logs:
            log_data = json.loads(log.data) if isinstance(log.data, str) else log.data
            # SSN should be masked in logs
            assert "123-45-6789" not in json.dumps(log_data)
            # Check for masked SSN format (e.g., ***-**-6789)
            if "ssn" in json.dumps(log_data):
                assert "***-**-" in json.dumps(log_data)
    
    @pytest.mark.asyncio
    async def test_unauthorized_access_attempts(self, security_components, users):
        document_processor, access_control, encryption_service, audit_logger = security_components
        admin_user, _, basic_user = users
        
        # 1. Create confidential document
        document = await document_processor.process_document(
            document_id=None,
            template_id="merger-agreement",
            variables={"company1": "Acme Inc", "company2": "Widget Corp"},
            format="docx",
            user_id=admin_user.id,
            context={"classification": "confidential"}
        )
        
        # 2. Set strict permissions
        await access_control.set_document_permissions(
            document_id=document.id,
            owner_id=admin_user.id,
            read_roles=[Role.ADMIN],
            write_roles=[Role.ADMIN],
            delete_roles=[Role.ADMIN]
        )
        
        # 3. Mock document access method to test security
        original_load = document_processor._load_document
        
        async def mock_load_with_security(doc_id):
            # Check permissions before loading
            user_id = basic_user.id  # Unauthorized user
            if not await access_control.can_read(user_id, doc_id):
                # Log unauthorized attempt
                await audit_logger.log_security_event(
                    user_id=user_id,
                    document_id=doc_id,
                    action="UNAUTHORIZED_ACCESS",
                    status="DENIED",
                    data={"reason": "Insufficient permissions"}
                )
                raise PermissionError(f"User {user_id} does not have permission to access document {doc_id}")
            return await original_load(doc_id)
        
        document_processor._load_document = mock_load_with_security
        
        # 4. Attempt unauthorized access
        with pytest.raises(PermissionError):
            await document_processor._load_document(document.id)
        
        # 5. Verify security event was logged
        security_logs = await audit_logger.get_security_logs()
        unauthorized_log = next((log for log in security_logs if log.action == "UNAUTHORIZED_ACCESS"), None)
        
        assert unauthorized_log is not None
        assert unauthorized_log.user_id == basic_user.id
        assert unauthorized_log.document_id == document.id
        assert unauthorized_log.status == "DENIED" 