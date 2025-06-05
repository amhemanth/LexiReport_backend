from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class Comment(Base):
    """Comment model"""
    
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    thread_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("comment_threads.id", ondelete="CASCADE"), nullable=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_comment_thread_created', 'thread_id', 'created_at'),
        Index('idx_comment_user_created', 'user_id', 'created_at'),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="comments")
    thread: Mapped[Optional["CommentThread"]] = relationship("CommentThread", back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        remote_side=[id],
        backref="replies"
    )
    mentions: Mapped[List["User"]] = relationship(
        "User",
        secondary="comment_mentions",
        back_populates="mentioned_in_comments"
    )

    def __repr__(self) -> str:
        return f"<Comment {self.id}>"


class CommentThread(Base):
    """Comment thread model"""
    
    __tablename__ = "comment_threads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # report, file, etc.
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
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
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CommentThread {self.entity_type}:{self.entity_id}>"


class CommentMention(Base):
    """Comment mention association model"""
    
    __tablename__ = "comment_mentions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<CommentMention {self.comment_id}:{self.user_id}>" 