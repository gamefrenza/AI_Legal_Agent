from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
from typing import Dict, Any

class EncryptionService:
    def __init__(self):
        self.master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        self.salt = os.urandom(16)
        self.method = 'AES-256-GCM'
    
    async def encrypt_document(
        self,
        content: bytes,
        metadata: Dict[str, Any]
    ) -> bytes:
        """Encrypt document content using AES-GCM"""
        try:
            # Generate document-specific key
            doc_key = await self._generate_document_key(metadata)
            
            # Create AESGCM instance
            aesgcm = AESGCM(doc_key)
            nonce = os.urandom(12)
            
            # Encrypt content
            encrypted_content = aesgcm.encrypt(
                nonce,
                content,
                metadata.get('additional_data', None)
            )
            
            # Combine nonce and encrypted content
            return nonce + encrypted_content
            
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    async def decrypt_document(
        self,
        encrypted_content: bytes,
        metadata: Dict[str, Any]
    ) -> bytes:
        """Decrypt document content"""
        try:
            # Generate document-specific key
            doc_key = await self._generate_document_key(metadata)
            
            # Extract nonce and ciphertext
            nonce = encrypted_content[:12]
            ciphertext = encrypted_content[12:]
            
            # Create AESGCM instance
            aesgcm = AESGCM(doc_key)
            
            # Decrypt content
            return aesgcm.decrypt(
                nonce,
                ciphertext,
                metadata.get('additional_data', None)
            )
            
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")
    
    async def _generate_document_key(
        self,
        metadata: Dict[str, Any]
    ) -> bytes:
        """Generate document-specific encryption key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000
        )
        
        # Combine master key with document metadata
        key_material = f"{self.master_key}:{metadata.get('doc_id')}:{metadata.get('version')}"
        return base64.urlsafe_b64encode(kdf.derive(key_material.encode())) 