from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Integer, Index, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base
from enum import Enum as PyEnum

class ActivityType(str, PyEnum):
    """Activity type enum"""
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SHARE = "share"
    EXPORT = "export"
    COMMENT = "comment"
    TAG = "tag"
    OTHER = "other"


class UserActivity(Base):
    """Model for tracking user activities."""
    __tablename__ = "user_activities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    session_id: Mapped[Optional[str]] = mapped_column(String(100))
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
        primaryjoin="and_(foreign(UserActivity.entity_type) == 'report', foreign(UserActivity.entity_id) == Report.id)",
        back_populates="activities",
        passive_deletes=True,
        overlaps="comment"
    )
    comment: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        primaryjoin="and_(foreign(UserActivity.entity_type) == 'comment', foreign(UserActivity.entity_id) == Comment.id)",
        back_populates="activities",
        passive_deletes=True,
        overlaps="report"
    )

    # Indexes
    __table_args__ = (
        Index("ix_user_activities_user_id", "user_id"),
        Index("ix_user_activities_type", "activity_type"),
        Index("ix_user_activities_entity_type", "entity_type"),
        Index("ix_user_activities_entity_id", "entity_id"),
        Index("ix_user_activities_created", "created_at"),
        Index("ix_user_activities_session", "session_id"),
        Index('idx_user_activity_user', 'user_id'),
        Index('idx_user_activity_type', 'activity_type'),
        Index('idx_user_activity_entity', 'entity_type', 'entity_id'),
        Index('idx_user_activity_created', 'created_at'),
        Index('idx_user_activity_user_type', 'user_id', 'activity_type'),
        Index('idx_user_activity_user_created', 'user_id', 'created_at'),
        Index('idx_user_activity_entity_created', 'entity_type', 'entity_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<UserActivity(user_id={self.user_id}, type='{self.activity_type}', entity_type='{self.entity_type}')>" 