from pydantic import BaseModel, field_validator
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime

class ReportParameter(BaseModel):
    name: str
    type: Literal["string", "date", "number", "boolean"]
    required: bool = False
    default: Optional[str] = None\

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if not value.strip():
            raise ValueError("El nombre del parámetro es obligatorio.")
        return value

class ReportCreate(BaseModel):
    #id: str
    name: str
    description: str
    sql_template: str
    parameters: List[ReportParameter]
    created_by: str
    #created_at: datetime

    @field_validator("name", "sql_template", "created_by")
    @classmethod
    def validate_required_fields(cls, value: str):
        if not value.strip():
            raise ValueError("Este campo es obligatorio.")
        return value

class ReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sql_template: Optional[str] = None
    parameters: Optional[List[ReportParameter]] = None
    created_by: Optional[str] = None

    @field_validator("name", "sql_template")
    @classmethod
    def validate_optional_fields(cls, value):
        if value is None:
            return value

        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")

        return value

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