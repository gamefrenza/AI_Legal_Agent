from typing import Dict, Any, List
from datetime import datetime
from ..models.document import Document, DocumentVersion
from ..utils.hash import calculate_hash

class DocumentVersionManager:
    def __init__(self):
        self.version_store = VersionStore()
        self.hash_validator = HashValidator()
    
    async def create_version(
        self,
        document: Document
    ) -> DocumentVersion:
        """Create new document version"""
        # Calculate document hash
        content_hash = await calculate_hash(document.content)
        
        # Create version record
        version = DocumentVersion(
            document_id=document.id,
            version_number=await self._get_next_version(document.id),
            content_hash=content_hash,
            created_at=datetime.utcnow(),
            created_by=document.metadata.get('modified_by'),
            changes=document.metadata.get('changes'),
            parent_version=document.version_info.version_number if document.version_info else None
        )
        
        # Store version
        await self.version_store.store_version(version)
        
        return version
    
    async def verify_version(
        self,
        document: Document,
        version: DocumentVersion
    ) -> bool:
        """Verify document version integrity"""
        # Calculate current hash
        current_hash = await calculate_hash(document.content)
        
        # Compare with stored hash
        return current_hash == version.content_hash
    
    async def get_version_history(
        self,
        document_id: str
    ) -> List[DocumentVersion]:
        """Get document version history"""
        return await self.version_store.get_versions(document_id) 