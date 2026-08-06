from datetime import datetime
from typing import Optional
import uuid
from app.core.database_client import Base
from sqlalchemy import Column, Text, DateTime, func, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
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


# --- PERMISOS DIRECTOS POR USUARIO ---
class UserReportPermission(Base):
    __tablename__ = "user_report_permissions"

    user_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True
    )
    granted_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relación opcional para cargar los datos del reporte directamente
    report = relationship("ReportModel")


# --- PERMISOS POR CARGO ---
class PositionReportPermission(Base):
    __tablename__ = "position_report_permissions"

    position_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    report = relationship("ReportModel")