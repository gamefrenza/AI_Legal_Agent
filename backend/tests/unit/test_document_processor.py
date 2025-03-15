import pytest
from unittest.mock import Mock, patch, AsyncMock
from document_service.document_processor import DocumentProcessor
from document_service.document_generator import DocumentGenerator
from document_service.template_processor import TemplateProcessor
from document_service.nlp_processor import NLPProcessor
from document_service.format_converter import FormatConverter
from models.document import Document
from models.audit import AuditRecord

class TestDocumentProcessor:
    @pytest.fixture
    def document_processor(self):
        # Create mocks for dependencies
        document_processor = DocumentProcessor()
        document_processor.generator = AsyncMock(spec=DocumentGenerator)
        document_processor.template_processor = AsyncMock(spec=TemplateProcessor)
        document_processor.nlp_processor = AsyncMock(spec=NLPProcessor)
        document_processor.format_converter = AsyncMock(spec=FormatConverter)
        
        # Mock internal methods
        document_processor._load_document = AsyncMock()
        document_processor._save_document = AsyncMock()
        document_processor._save_audit_record = AsyncMock()
        
        return document_processor
    
    @pytest.mark.asyncio
    async def test_process_document_new(self, document_processor):
        # Arrange
        document_id = None
        template_id = "contract-template"
        variables = {"client": "Test Corp"}
        format = "docx"
        user_id = "user123"
        context = {"jurisdiction": "US-CA"}
        
        # Mock _generate_content to return sample content
        sample_content = b"Sample document content"
        document_processor._generate_content = AsyncMock(return_value=sample_content)
        
        # Mock _create_version to return a new document
        new_doc = Document(id="doc123", content=sample_content)
        document_processor._create_version = AsyncMock(return_value=new_doc)
        
        # Mock _track_changes
        document_processor._track_changes = AsyncMock()
        
        # Act
        result = await document_processor.process_document(
            document_id=document_id,
            template_id=template_id,
            variables=variables,
            format=format,
            user_id=user_id,
            context=context
        )
        
        # Assert
        assert result == new_doc
        document_processor._generate_content.assert_called_once_with(
            template_id=template_id,
            variables=variables,
            format=format,
            context=context
        )
        document_processor._create_version.assert_called_once_with(
            content=sample_content,
            parent_doc=None,
            user_id=user_id,
            context=context
        )
        document_processor._track_changes.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_document_update(self, document_processor):
        # Arrange
        document_id = "existing-doc-123"
        template_id = "contract-template"
        variables = {"client": "Test Corp"}
        format = "docx"
        user_id = "user123"
        context = {"jurisdiction": "US-CA"}
        
        # Mock existing document
        existing_doc = Document(id=document_id, content=b"Old content")
        document_processor._load_document.return_value = existing_doc
        
        # Mock _generate_content to return sample content
        sample_content = b"Updated document content"
        document_processor._generate_content = AsyncMock(return_value=sample_content)
        
        # Mock _create_version to return a new document
        new_doc = Document(id="doc123-v2", content=sample_content)
        document_processor._create_version = AsyncMock(return_value=new_doc)
        
        # Mock _track_changes
        document_processor._track_changes = AsyncMock()
        
        # Act
        result = await document_processor.process_document(
            document_id=document_id,
            template_id=template_id,
            variables=variables,
            format=format,
            user_id=user_id,
            context=context
        )
        
        # Assert
        assert result == new_doc
        document_processor._load_document.assert_called_once_with(document_id)
        document_processor._generate_content.assert_called_once()
        document_processor._create_version.assert_called_once_with(
            content=sample_content,
            parent_doc=existing_doc,
            user_id=user_id,
            context=context
        )
        document_processor._track_changes.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_content(self, document_processor):
        # Arrange
        template_id = "contract-template"
        variables = {"client": "Test Corp"}
        format = "docx"
        context = {"jurisdiction": "US-CA"}
        
        # Mock template processor
        template_content = b"Template content with {{client}}"
        document_processor.template_processor.process_template.return_value = template_content
        
        # Mock generator
        generated_content = b"Template content with Test Corp"
        document_processor.generator.generate.return_value = generated_content
        
        # Mock format converter
        final_content = b"Converted content"
        document_processor.format_converter.convert.return_value = final_content
        
        # Restore original method for testing
        document_processor._generate_content = DocumentProcessor._generate_content
        
        # Act
        result = await document_processor._generate_content(
            template_id=template_id,
            variables=variables,
            format=format,
            context=context
        )
        
        # Assert
        assert result == final_content
        document_processor.template_processor.process_template.assert_called_once_with(
            template_id=template_id,
            variables=variables
        )
        document_processor.generator.generate.assert_called_once()
        document_processor.format_converter.convert.assert_called_once_with(
            content=generated_content,
            target_format=format
        ) 