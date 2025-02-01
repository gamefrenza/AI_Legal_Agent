from typing import Union
import mammoth
from docx import Document
from pypdf import PdfReader, PdfWriter
import markdown
import html2docx
import io

class FormatConverter:
    async def convert(
        self,
        content: Union[str, bytes],
        source_format: str,
        target_format: str
    ) -> bytes:
        """Convert content between different formats"""
        
        # First convert to HTML as intermediate format
        html_content = await self._to_html(content, source_format)
        
        # Then convert HTML to target format
        if target_format == "docx":
            return await self._html_to_docx(html_content)
        elif target_format == "pdf":
            return await self._html_to_pdf(html_content)
        elif target_format == "markdown":
            return await self._html_to_markdown(html_content)
        else:
            return html_content.encode('utf-8')
    
    async def _to_html(self, content: Union[str, bytes], source_format: str) -> str:
        """Convert source content to HTML"""
        if source_format == "markdown":
            return markdown.markdown(content)
        elif source_format == "docx":
            result = mammoth.convert_to_html(content)
            return result.value
        elif source_format == "pdf":
            # Extract text from PDF and convert to HTML
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return f"<pre>{text}</pre>"
        else:
            return content
    
    async def _html_to_docx(self, html: str) -> bytes:
        """Convert HTML to DOCX"""
        doc = html2docx.html2docx(html)
        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()
    
    async def _html_to_pdf(self, html: str) -> bytes:
        """Convert HTML to PDF"""
        # Implementation using WeasyPrint or similar library
        pass 