from fastapi import FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Dict
import uuid
from datetime import datetime

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Template(BaseModel):
    id: str
    name: str
    content: str
    jurisdiction: str
    variables: List[str]
    metadata: Dict
    version: int
    created_at: datetime
    updated_at: datetime

class TemplateService:
    def __init__(self):
        self.templates = {}
        
    async def create_template(self, template_data: dict) -> Template:
        template_id = str(uuid.uuid4())
        template = Template(
            id=template_id,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **template_data
        )
        self.templates[template_id] = template
        return template

template_service = TemplateService()

@app.post("/templates/", response_model=Template)
async def create_template(template_data: dict, token: str = Security(oauth2_scheme)):
    return await template_service.create_template(template_data) 