import uuid
from app.core.database_client import Base
from sqlalchemy import Column, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB

class ReportModel(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    sql_template = Column(Text, nullable=False)
    parameters = Column(JSONB, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)