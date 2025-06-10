from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
import uuid

from sqlalchemy import String, ForeignKey, Text, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base
from app.models.audit.enums import ActivityType

class UserActivity(Base):
    """Model for tracking user activities."""
    __tablename__ = "user_activities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    report_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="activities",
        passive_deletes=True
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        back_populates="activities",
        passive_deletes=True,
        primaryjoin="or_(foreign(UserActivity.report_id) == remote(Report.id), and_(foreign(UserActivity.entity_type) == 'report', foreign(UserActivity.entity_id) == remote(Report.id)))"
    )
    comment: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        back_populates="activities",
        passive_deletes=True,
        primaryjoin="and_(foreign(UserActivity.entity_type) == 'comment', foreign(UserActivity.entity_id) == Comment.id)",
        overlaps="report"
    )

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_user_activity_user', 'user_id'),
        Index('idx_user_activity_type', 'activity_type'),
        Index('idx_user_activity_entity', 'entity_type', 'entity_id'),
        Index('idx_user_activity_report', 'report_id'),
        Index('idx_user_activity_created', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<UserActivity {self.activity_type}:{self.user_id}>" 