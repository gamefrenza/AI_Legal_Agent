from typing import Dict, Optional, List
from datetime import datetime
from .document_generator import DocumentGenerator
from .template_processor import TemplateProcessor
from .nlp_processor import NLPProcessor
from .format_converter import FormatConverter
from ..models.document import Document
from ..models.audit import AuditRecord

class DocumentProcessor:
    def __init__(self):
        self.generator = DocumentGenerator()
        self.template_processor = TemplateProcessor()
        self.nlp_processor = NLPProcessor()
        self.format_converter = FormatConverter()
    
    async def process_document(
        self,
        document_id: str,
        template_id: Optional[str] = None,
        variables: Optional[Dict] = None,
        format: str = "docx",
        user_id: str = None,
        context: Optional[Dict] = None
    ) -> Document:
        """Process document with version control and change tracking"""
        
        # Load existing document if updating
        existing_doc = None
        if document_id:
            existing_doc = await self._load_document(document_id)
        
        # Generate new content
        content = await self._generate_content(
            template_id=template_id,
            variables=variables,
            format=format,
            context=context
        )
        
        # Create new version
        new_doc = await self._create_version(
            content=content,
            parent_doc=existing_doc,
            user_id=user_id,
            context=context
        )
        
        # Track changes
        await self._track_changes(
            new_doc=new_doc,
            old_doc=existing_doc,
            user_id=user_id
        )
        
        return new_doc
    
    async def _generate_content(
        self,
        template_id: Optional[str],
        variables: Optional[Dict],
        format: str,
        context: Optional[Dict]
    ) -> bytes:
        """Generate document content using existing components"""
        
        if template_id:
            # Use document generator for template-based generation
            content = await self.generator.generate_document(
                template_id=template_id,
                variables=variables or {},
                format=format,
                context=context
            )
        else:
            # Process raw content
            content = variables.get('content', '')
            if isinstance(content, str) and len(content) > 50:
                content = await self.nlp_processor.enhance_content(content, context)
            content = await self.format_converter.convert(
                content=content,
                source_format="text",
                target_format=format
            )
        
        return content
    
    async def _create_version(
        self,
        content: bytes,
        parent_doc: Optional[Document],
        user_id: str,
        context: Optional[Dict]
    ) -> Document:
        """Create new document version"""
        
        version = 1
        if parent_doc:
            version = parent_doc.version + 1
        
        # Create new document version
        new_doc = Document(
            content=content,
            version=version,
            parent_version_id=parent_doc.id if parent_doc else None,
            created_by=user_id,
            jurisdiction=context.get('jurisdiction') if context else None,
            metadata={
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Save to database
        await self._save_document(new_doc)
        
        return new_doc
    
    async def _track_changes(
        self,
        new_doc: Document,
        old_doc: Optional[Document],
        user_id: str
    ) -> None:
        """Track document changes in audit log"""
        
        changes = {
            'version': new_doc.version,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'changes': await self._compute_diff(old_doc, new_doc) if old_doc else None
        }
        
        # Create audit record
        audit_record = AuditRecord(
            action='document_update' if old_doc else 'document_create',
            user_id=user_id,
            resource_type='document',
            resource_id=new_doc.id,
            changes=changes
        )
        
        # Save audit record
        await self._save_audit_record(audit_record)
    
    async def _compute_diff(self, old_doc: Document, new_doc: Document) -> Dict:
        """Compute differences between document versions"""
        # Implementation of diff logic here
        # Could use libraries like difflib for text comparison
        pass
    
    async def _load_document(self, document_id: str) -> Optional[Document]:
        """Load document from database"""
        # Database access implementation
        pass
    
    async def _save_document(self, document: Document) -> None:
        """Save document to database"""
        # Database access implementation
        pass
    
    async def _save_audit_record(self, record: AuditRecord) -> None:
        """Save audit record to database"""
        # Database access implementation
        pass 