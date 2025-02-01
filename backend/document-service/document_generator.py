from jinja2 import Environment, BaseLoader, Template
from typing import Dict, List, Optional
import mammoth
from docx import Document
from pypdf import PdfReader, PdfWriter
import json
from datetime import datetime
from .nlp_processor import NLPProcessor

class DocumentGenerator:
    def __init__(self):
        self.env = Environment(
            loader=BaseLoader(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.nlp = NLPProcessor()
        
    async def generate_document(
        self,
        template_id: str,
        variables: Dict,
        format: str = "docx",
        context: Optional[Dict] = None
    ) -> bytes:
        """Generate document from template with variable substitution and NLP enhancement"""
        
        # Get template and its inheritance chain
        template = await self._get_template_chain(template_id)
        
        # Process variables and enhance content
        processed_vars = await self._process_variables(variables, context)
        
        # Generate content
        content = await self._render_template(template, processed_vars)
        
        # Convert to requested format
        return await self._convert_format(content, format)
    
    async def _get_template_chain(self, template_id: str) -> Template:
        """Resolve template inheritance chain"""
        template = await self._load_template(template_id)
        
        # Process inheritance
        if template.parent_templates:
            parent_content = ""
            for parent in template.parent_templates:
                parent_content += await self._load_template(parent.id)
            
            # Merge parent and child templates
            template.content = self._merge_templates(parent_content, template.content)
        
        return self.env.from_string(template.content)
    
    async def _process_variables(self, variables: Dict, context: Optional[Dict]) -> Dict:
        """Process and enhance variables with NLP"""
        processed = variables.copy()
        
        # Enhance content with NLP where appropriate
        for key, value in processed.items():
            if isinstance(value, str) and len(value) > 50:  # Only process longer text
                processed[key] = await self.nlp.enhance_content(value, context)
        
        return processed
    
    async def _convert_format(self, content: str, format: str) -> bytes:
        """Convert document to requested format"""
        if format == "docx":
            return await self._to_docx(content)
        elif format == "pdf":
            return await self._to_pdf(content)
        else:
            return content.encode('utf-8') 