from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Integer, Index, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base
from enum import Enum as PyEnum

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
    """Model for audit logging."""
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    session_id: Mapped[Optional[str]] = mapped_column(String(100))
    is_successful: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="audit_logs",
        passive_deletes=True
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        primaryjoin="and_(foreign(AuditLog.entity_type) == 'report', foreign(AuditLog.entity_id) == Report.id)",
        back_populates="audit_logs",
        passive_deletes=True,
        overlaps="comment"
    )
    comment: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        primaryjoin="and_(foreign(AuditLog.entity_type) == 'comment', foreign(AuditLog.entity_id) == Comment.id)",
        back_populates="audit_logs",
        passive_deletes=True,
        overlaps="report"
    )
    change_history: Mapped[List["ChangeHistory"]] = relationship(
        "ChangeHistory",
        back_populates="audit_log",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Indexes
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_entity_type", "entity_type"),
        Index("ix_audit_logs_entity_id", "entity_id"),
        Index("ix_audit_logs_created", "created_at"),
        Index("ix_audit_logs_session", "session_id"),
        Index("ix_audit_logs_success", "is_successful"),
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_log_created', 'created_at'),
        Index('idx_audit_log_user_action', 'user_id', 'action'),
        Index('idx_audit_log_user_created', 'user_id', 'created_at'),
        Index('idx_audit_log_entity_created', 'entity_type', 'entity_id', 'created_at'),
        Index('idx_audit_log_success', 'is_successful'),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(user_id={self.user_id}, action='{self.action}', entity_type='{self.entity_type}')>"


class ChangeHistory(Base):
    """Model for tracking changes to entities."""
    __tablename__ = "change_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_log_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("audit_logs.id", ondelete="CASCADE"), 
        nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_log: Mapped["AuditLog"] = relationship(
        "AuditLog", 
        back_populates="change_history",
        passive_deletes=True
    )

    # Indexes
    __table_args__ = (
        Index("ix_change_history_audit_log_id", "audit_log_id"),
        Index("ix_change_history_field", "field_name"),
        Index("ix_change_history_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ChangeHistory(audit_log_id={self.audit_log_id}, field='{self.field_name}')>" 