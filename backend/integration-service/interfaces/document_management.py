from typing import Dict, Any, BinaryIO, List, Optional
from .base_integration import BaseIntegration
from ..models.document import Document, DocumentMetadata
from ..utils.file_handler import FileHandler

class DocumentManagementIntegration(BaseIntegration):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_handler = FileHandler()
    
    async def upload_document(
        self,
        file: BinaryIO,
        metadata: DocumentMetadata,
        folder_path: Optional[str] = None
    ) -> Document:
        """Upload document to DMS"""
        # Prepare file for upload
        prepared_file = await self.file_handler.prepare_upload(file)
        
        # Upload file
        response = await self.execute_request(
            method="POST",
            endpoint="/api/v1/documents",
            data={
                "file": prepared_file,
                "metadata": metadata.dict(),
                "folder_path": folder_path
            }
        )
        
        return Document(**response)
    
    async def sync_documents(
        self,
        last_sync: Optional[datetime] = None
    ) -> SyncLog:
        """Synchronize documents with DMS"""
        response = await self.execute_request(
            method="POST",
            endpoint="/api/v1/sync",
            data={"last_sync": last_sync.isoformat() if last_sync else None}
        )
        
        # Process sync results
        sync_log = await self._process_sync_results(response['sync_results'])
        
        return sync_log
    
    async def get_document_versions(
        self,
        document_id: str
    ) -> List[DocumentMetadata]:
        """Get document version history"""
        response = await self.execute_request(
            method="GET",
            endpoint=f"/api/v1/documents/{document_id}/versions"
        )
        
        return [DocumentMetadata(**version) for version in response['versions']] 