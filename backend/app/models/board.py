from datetime import datetime
from typing import Optional
import uuid
from app.core.database_client import Base
from sqlalchemy import Column, Text, DateTime, func, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

class BoardModel(Base):
    __tablename__ = "boards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    powerbi_report_id = Column(String(255), nullable=False)
    workspace_id = Column(String(255), nullable=False)
    embed_url = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

class UserBoardPermission(Base):
    __tablename__ = "user_board_permissions"

    user_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True
    )
    granted_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    board = relationship("BoardModel")

class PositionBoardPermission(Base):
    __tablename__ = "position_board_permissions"

    position_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    board = relationship("BoardModel")

class PowerBITokenModel(Base):
    __tablename__ = "powerbi_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())