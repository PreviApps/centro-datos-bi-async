import uuid

from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database_client import Base


class ReportJobModel(Base):

    __tablename__ = "report_jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    report_id = Column(
        UUID(as_uuid=True)
    )

    status = Column(
        String,
        nullable=False,
        default="queued"
    )

    job_type = Column(
        String,
        nullable=False,
        default="exec"
    )

    parameters = Column(
        JSONB,
        nullable=False
    )

    result_path = Column(Text)

    preview_results = Column(JSONB, nullable=True)

    error = Column(Text)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    started_at = Column(DateTime)

    finished_at = Column(DateTime)