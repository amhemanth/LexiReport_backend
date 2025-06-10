from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, Boolean, DateTime, Index, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base


class Comment(Base):
    """Model for comments."""
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    report_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    thread_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("comment_threads.id", ondelete="CASCADE"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_comment_user', 'user_id'),
        Index('idx_comment_report', 'report_id'),
        Index('idx_comment_parent', 'parent_id'),
        Index('idx_comment_thread', 'thread_id'),
        Index('idx_comment_created', 'created_at'),
        Index('idx_comment_deleted', 'is_deleted'),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="comments",
        passive_deletes=True
    )
    report: Mapped["Report"] = relationship(
        "Report",
        foreign_keys=[report_id],
        back_populates="comments",
        passive_deletes=True
    )
    thread: Mapped[Optional["CommentThread"]] = relationship(
        "CommentThread",
        foreign_keys=[thread_id],
        back_populates="comments",
        passive_deletes=True
    )
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        foreign_keys=[parent_id],
        back_populates="replies",
        remote_side=[id],
        passive_deletes=True
    )
    replies: Mapped[List["Comment"]] = relationship(
        "Comment",
        foreign_keys=[parent_id],
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity",
        back_populates="comment",
        primaryjoin="and_(foreign(UserActivity.entity_type) == 'comment', foreign(UserActivity.entity_id) == remote(Comment.id))",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="report"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="comment",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    mentions: Mapped[List["User"]] = relationship(
        "User",
        secondary="comment_mentions",
        back_populates="mentioned_in_comments",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Comment(user_id={self.user_id}, report_id={self.report_id})>"


class CommentThread(Base):
    """Comment thread model"""
    
    __tablename__ = "comment_threads"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # report, file, etc.
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_comment_thread_entity', 'entity_type', 'entity_id'),
        Index('idx_comment_thread_resolved', 'is_resolved', 'created_at'),
    )

    # Relationships
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="thread",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<CommentThread {self.entity_type}:{self.entity_id}>"


class CommentMention(Base):
    """Comment mention association model"""
    
    __tablename__ = "comment_mentions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    comment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("comments.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_comment_mention_comment', 'comment_id'),
        Index('idx_comment_mention_user', 'user_id'),
        UniqueConstraint('comment_id', 'user_id', name='uq_comment_mention'),
    )

    def __repr__(self) -> str:
        return f"<CommentMention(comment_id={self.comment_id}, user_id={self.user_id})>" 