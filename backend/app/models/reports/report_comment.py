from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, JSON, Column, DateTime, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base
from app.models.core.user import User
from app.models.reports.report import Report

class ReportComment(Base):
    """Model for report comments."""
    
    __tablename__ = "report_comments"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("report_comments.id", ondelete="SET NULL"))
    content: Mapped[str] = mapped_column(String, nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_comment_report', 'report_id'),
        Index('idx_report_comment_user', 'user_id'),
        Index('idx_report_comment_parent', 'parent_id'),
        Index('idx_report_comment_created', 'created_at'),
    )

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="comments")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    parent: Mapped[Optional["ReportComment"]] = relationship(
        "ReportComment",
        remote_side=[id],
        backref="replies"
    )

    def __repr__(self) -> str:
        return f"<ReportComment {self.id}:{self.content[:50]}>" 