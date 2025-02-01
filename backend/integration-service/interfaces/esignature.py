from typing import Dict, Any, List, Optional
from .base_integration import BaseIntegration
from ..models.signature import SignatureRequest, SignatureStatus
from ..utils.document_preparer import DocumentPreparer

class ESignatureIntegration(BaseIntegration):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.document_preparer = DocumentPreparer()
    
    async def create_signature_request(
        self,
        document_id: str,
        signers: List[Dict[str, Any]],
        options: Optional[Dict] = None
    ) -> SignatureRequest:
        """Create new signature request"""
        # Prepare document for signing
        prepared_doc = await self.document_preparer.prepare_for_signing(
            document_id,
            signers
        )
        
        response = await self.execute_request(
            method="POST",
            endpoint="/api/v1/signature-requests",
            data={
                "document": prepared_doc,
                "signers": signers,
                "options": options
            }
        )
        
        return SignatureRequest(**response)
    
    async def get_signature_status(
        self,
        request_id: str
    ) -> SignatureStatus:
        """Get status of signature request"""
        response = await self.execute_request(
            method="GET",
            endpoint=f"/api/v1/signature-requests/{request_id}/status"
        )
        
        return SignatureStatus(**response)
    
    async def download_signed_document(
        self,
        request_id: str
    ) -> bytes:
        """Download signed document"""
        response = await self.execute_request(
            method="GET",
            endpoint=f"/api/v1/signature-requests/{request_id}/document"
        )
        
        return response['document_content'] 