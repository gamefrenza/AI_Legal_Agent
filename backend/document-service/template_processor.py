from typing import Dict, List, Optional
from pydantic import BaseModel, validator
import re
from jinja2 import Environment, meta

class TemplateValidator(BaseModel):
    content: str
    variables: List[str]
    conditions: List[str]
    sections: List[str]
    
    @validator('content')
    def validate_template_syntax(cls, v):
        """Validate Jinja2 template syntax"""
        env = Environment()
        try:
            env.parse(v)
        except Exception as e:
            raise ValueError(f"Invalid template syntax: {str(e)}")
        return v
    
    @validator('variables')
    def validate_variables(cls, v, values):
        """Ensure all referenced variables are declared"""
        if 'content' not in values:
            return v
            
        env = Environment()
        ast = env.parse(values['content'])
        variables = meta.find_undeclared_variables(ast)
        
        if not all(var in variables for var in v):
            raise ValueError("Template references undeclared variables")
        return v

class TemplateProcessor:
    def __init__(self):
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    async def process_template(
        self,
        template: str,
        variables: Dict,
        sections: Optional[List[str]] = None
    ) -> str:
        """Process template with variables and optional sections"""
        
        # Validate template
        validator = TemplateValidator(
            content=template,
            variables=list(variables.keys()),
            conditions=self._extract_conditions(template),
            sections=sections or []
        )
        
        # Process conditional sections
        if sections:
            template = self._process_sections(template, sections)
        
        # Render template
        template_obj = self.env.from_string(template)
        return template_obj.render(**variables)
    
    def _extract_conditions(self, template: str) -> List[str]:
        """Extract conditional statements from template"""
        pattern = r'{%\s*if\s+(.*?)\s*%}'
        return re.findall(pattern, template)
    
    def _process_sections(self, template: str, sections: List[str]) -> str:
        """Process template sections based on inclusion list"""
        lines = template.split('\n')
        result = []
        current_section = None
        include_line = True
        
        for line in lines:
            section_start = re.match(r'{%\s*section\s+([^\s%]+)\s*%}', line)
            if section_start:
                current_section = section_start.group(1)
                include_line = current_section in sections
                continue
                
            if re.match(r'{%\s*endsection\s*%}', line):
                current_section = None
                include_line = True
                continue
                
            if include_line:
                result.append(line)
        
        return '\n'.join(result) 