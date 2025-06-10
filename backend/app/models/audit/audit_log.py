from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base

class AuditLog(Base):
    """Model for audit logs."""
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    report_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"))
    comment_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_report', 'report_id'),
        Index('idx_audit_log_comment', 'comment_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_created', 'created_at'),
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="audit_logs",
        passive_deletes=True
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        foreign_keys=[report_id],
        back_populates="audit_logs",
        passive_deletes=True
    )
    comment: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        foreign_keys=[comment_id],
        back_populates="audit_logs",
        passive_deletes=True
    )
    change_history: Mapped[List["ChangeHistory"]] = relationship(
        "ChangeHistory",
        back_populates="audit_log",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog(user_id={self.user_id}, action='{self.action}')>"


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