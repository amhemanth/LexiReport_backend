from sqlalchemy import String, ForeignKey, JSON, DateTime, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.analytics.enums import VoiceCommandStatus, VoiceCommandType

class VoiceCommand(Base):
    __tablename__ = "voice_commands"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    command_text: Mapped[str] = mapped_column(String, nullable=False)
    action_type: Mapped[VoiceCommandType] = mapped_column(SQLEnum(VoiceCommandType), nullable=False)
    status: Mapped[VoiceCommandStatus] = mapped_column(SQLEnum(VoiceCommandStatus), nullable=False, default=VoiceCommandStatus.PENDING)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    meta_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_voice_command_user', 'user_id'),
        Index('idx_voice_command_entity', 'entity_type', 'entity_id'),
        Index('idx_voice_command_created', 'created_at'),
        Index('idx_voice_command_status', 'status'),
        Index('idx_voice_command_type', 'action_type'),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="voice_commands",
        passive_deletes=True
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        primaryjoin="and_(foreign(VoiceCommand.entity_type) == 'report', foreign(VoiceCommand.entity_id) == Report.id)",
        back_populates="voice_commands",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<VoiceCommand {self.id} {self.command_text[:20]}>" 