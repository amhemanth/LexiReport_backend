from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class AuditAction(str, PyEnum):
    """Audit action enum"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    SHARE = "share"
    LOGIN = "login"
    LOGOUT = "logout"
    OTHER = "other"


class AuditLog(Base):
    """Audit log model"""
    
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[AuditAction] = mapped_column(SQLEnum(AuditAction), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_created', 'created_at'),
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
    changes: Mapped[list["ChangeHistory"]] = relationship(
        "ChangeHistory",
        back_populates="audit_log",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} {self.entity_type}:{self.entity_id}>"


class ChangeHistory(Base):
    """Change history model for tracking detailed changes"""
    
    __tablename__ = "change_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_log_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_logs.id", ondelete="CASCADE"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_change_history_audit', 'audit_log_id'),
        Index('idx_change_history_field', 'field_name'),
    )

    # Relationships
    audit_log: Mapped["AuditLog"] = relationship("AuditLog", back_populates="changes")

    def __repr__(self) -> str:
        return f"<ChangeHistory {self.field_name}>" 