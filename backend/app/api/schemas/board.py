from typing import Optional, List
from pydantic import BaseModel, UUID4
from datetime import datetime

class BoardCreate(BaseModel):
    name: str
    description: Optional[str] = None
    powerbi_report_id: str
    workspace_id: str
    embed_url: str
    created_by: UUID4

class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    powerbi_report_id: Optional[str] = None
    workspace_id: Optional[str] = None
    embed_url: Optional[str] = None
    updated_by: UUID4

class BoardResponse(BaseModel):
    id: UUID4
    name: str
    description: Optional[str] = None
    powerbi_report_id: str
    workspace_id: str
    embed_url: str
    created_by: UUID4
    created_at: datetime

    class Config:
        from_attributes = True