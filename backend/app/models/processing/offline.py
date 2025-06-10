from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base
from app.models.core.user import User
from app.models.processing.enums import ContentType, ProcessingStatus, SyncAction


class OfflineContent(Base):
    """Offline content model"""
    
    __tablename__ = "offline_content"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    sync_status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_offline_content_type', 'content_type'),
        Index('idx_offline_content_status', 'sync_status'),
        Index('idx_offline_content_created', 'created_at'),
        Index('idx_offline_content_creator', 'created_by'),
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by], passive_deletes=True)
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


class OfflineProcessing(Base):
    """Model for offline processing tasks."""
    __tablename__ = "offline_processing"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    sync_action: Mapped[Optional[str]] = mapped_column(String(50))
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_offline_processing_type', 'content_type'),
        Index('idx_offline_processing_status', 'status'),
        Index('idx_offline_processing_created', 'created_at'),
    ) 