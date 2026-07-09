from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime

class ReportParameter(BaseModel):
    name: str
    type: Literal["string", "date", "number", "boolean"]
    required: bool = False
    default: Optional[str] = None

class ReportCreate(BaseModel):
    #id: str
    name: str
    description: str
    sql_template: str
    parameters: List[ReportParameter]
    created_by: str
    #created_at: datetime

class ReportResponse(ReportCreate):
    id: str
    created_at:datetime

class ExecuteReportRequest(BaseModel):
    parameters: Dict[str, Any]

class ReportList(BaseModel):
    id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    parameters_count: int