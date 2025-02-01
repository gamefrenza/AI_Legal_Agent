import pytest
from unittest.mock import Mock, patch
from document_service.document_engine import DocumentEngine
from document_service.models import Template, Document

class TestDocumentEngine:
    @pytest.fixture
    def document_engine(self):
        return DocumentEngine()
    
    @pytest.mark.asyncio
    async def test_generate_document(self, document_engine):
        # Arrange
        template_id = "test-template-1"
        variables = {"client_name": "Test Corp", "date": "2024-01-01"}
        
        # Act
        result = await document_engine.generate_document(
            template_id=template_id,
            variables=variables
        )
        
        # Assert
        assert result is not None
        assert isinstance(result, bytes)
    
    @pytest.mark.asyncio
    async def test_template_validation(self, document_engine):
        # Arrange
        invalid_template_id = "non-existent"
        
        # Act & Assert
        with pytest.raises(ValueError):
            await document_engine.generate_document(
                template_id=invalid_template_id,
                variables={}
            ) 