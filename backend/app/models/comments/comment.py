from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Integer, Index, and_, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base


class Comment(Base):
    """Model for comments."""
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    thread_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("comment_threads.id", ondelete="SET NULL"),
        nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("comments.id", ondelete="CASCADE"), 
        nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="comments",
        passive_deletes=True
    )
    thread: Mapped[Optional["CommentThread"]] = relationship(
        "CommentThread",
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
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        primaryjoin="and_(foreign(Comment.entity_type) == 'report', foreign(Comment.entity_id) == Report.id)",
        back_populates="comments",
        passive_deletes=True
    )
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity",
        primaryjoin="and_(foreign(UserActivity.entity_type) == 'comment', foreign(UserActivity.entity_id) == Comment.id)",
        back_populates="comment",
        passive_deletes=True,
        overlaps="activities,report"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        primaryjoin="and_(foreign(AuditLog.entity_type) == 'comment', foreign(AuditLog.entity_id) == Comment.id)",
        back_populates="comment",
        passive_deletes=True,
        overlaps="audit_logs,report"
    )
    mentions: Mapped[List["User"]] = relationship(
        "User",
        secondary="comment_mentions",
        back_populates="mentioned_in_comments",
        passive_deletes=True,
        foreign_keys="[CommentMention.comment_id, CommentMention.user_id]"
    )

    # Indexes
    __table_args__ = (
        Index("ix_comments_user_id", "user_id"),
        Index("ix_comments_entity_type", "entity_type"),
        Index("ix_comments_entity_id", "entity_id"),
        Index("ix_comments_parent_id", "parent_id"),
        Index("ix_comments_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Comment(user_id={self.user_id}, entity_type='{self.entity_type}')>"


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