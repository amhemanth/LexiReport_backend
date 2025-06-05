from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum

from app.db.base_class import Base
from app.models.core.user import User


class ContentType(str, PyEnum):
    """Content type enum"""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"


class ProcessingStatus(str, PyEnum):
    """Processing status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncAction(str, PyEnum):
    """Sync action enum"""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    UPDATE = "update"
    SYNC = "sync"


class OfflineContent(Base):
    """Offline content model"""
    
    __tablename__ = "offline_content"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    sync_status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_offline_content_type', 'content_type'),
        Index('idx_offline_content_status', 'sync_status'),
        Index('idx_offline_content_created', 'created_at'),
        Index('idx_offline_content_creator', 'created_by'),
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User")
    sync_queue: Mapped[List["SyncQueue"]] = relationship(
        "SyncQueue",
        back_populates="content",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<OfflineContent {self.title}>"


class SyncQueue(Base):
    """Sync queue model"""
    
    __tablename__ = "sync_queue"

    content_id: Mapped[int] = mapped_column(ForeignKey("offline_content.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[SyncAction] = mapped_column(SQLEnum(SyncAction), nullable=False)
    status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(default=0)
    last_retry: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_sync_queue_content', 'content_id'),
        Index('idx_sync_queue_action', 'action'),
        Index('idx_sync_queue_status', 'status'),
        Index('idx_sync_queue_created', 'created_at'),
    )

    # Relationships
    content: Mapped["OfflineContent"] = relationship("OfflineContent", back_populates="sync_queue")

    def __repr__(self) -> str:
        return f"<SyncQueue {self.content_id}:{self.action}>" 