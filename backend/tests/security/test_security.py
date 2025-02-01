import pytest
import jwt
from datetime import datetime, timedelta
from security.auth_manager import AuthManager
from security.encryption import EncryptionService

class TestSecurity:
    @pytest.fixture
    def security_components(self):
        auth_manager = AuthManager()
        encryption_service = EncryptionService()
        return auth_manager, encryption_service
    
    def test_jwt_token_validation(self, security_components):
        auth_manager, _ = security_components
        
        # Create token
        token = auth_manager.create_token({"user_id": "test-user"})
        
        # Validate token
        payload = auth_manager.validate_token(token)
        assert payload["user_id"] == "test-user"
    
    def test_data_encryption(self, security_components):
        _, encryption_service = security_components
        
        # Test data
        sensitive_data = "confidential information"
        
        # Encrypt
        encrypted = encryption_service.encrypt(sensitive_data)
        
        # Decrypt
        decrypted = encryption_service.decrypt(encrypted)
        
        assert decrypted == sensitive_data
        assert encrypted != sensitive_data
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, security_components):
        auth_manager, _ = security_components
        
        # Test rate limiting
        for _ in range(100):  # Below limit
            await auth_manager.check_rate_limit("test-user")
        
        # Should raise exception
        with pytest.raises(Exception):
            for _ in range(50):  # Exceeds limit
                await auth_manager.check_rate_limit("test-user") 