from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Integer, Index, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base
from app.models.core.user import User
from app.models.processing.enums import ProcessingType, ProcessingStatus, ProcessingPriority


class DocumentProcessingQueue(Base):
    __tablename__ = "document_processing_queue"

    document_id: Mapped[str] = mapped_column(String, nullable=False)
    processing_type: Mapped[ProcessingType] = mapped_column(SQLEnum(ProcessingType), nullable=False)
    status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    priority: Mapped[ProcessingPriority] = mapped_column(SQLEnum(ProcessingPriority), default=ProcessingPriority.MEDIUM)

    # Relationships with cascade rules
    results: Mapped[List["DocumentProcessingResult"]] = relationship(
        "DocumentProcessingResult",
        back_populates="queue_item",
        cascade="all, delete-orphan"
    )

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_processing_queue_status', 'status', 'priority'),
        Index('idx_processing_queue_document', 'document_id', 'processing_type'),
    )

    def __repr__(self):
        return f"<DocumentProcessingQueue {self.document_id}>"


class DocumentProcessingResult(Base):
    """Model for document processing results."""
    __tablename__ = "document_processing_results"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    queue_item_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("document_processing_queue.id", ondelete="CASCADE"), nullable=False)
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(String)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_doc_processing_result_queue', 'queue_item_id'),
        Index('idx_doc_processing_result_created', 'created_at'),
    )

    # Relationships
    queue_item: Mapped["DocumentProcessingQueue"] = relationship(
        "DocumentProcessingQueue",
        back_populates="results",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<DocumentProcessingResult {self.id}>"


class DocumentProcessing(Base):
    """Model for document processing tasks."""
    __tablename__ = "document_processing"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    processing_type: Mapped[ProcessingType] = mapped_column(SQLEnum(ProcessingType), nullable=False)
    status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_doc_processing_document', 'document_id'),
        Index('idx_doc_processing_type', 'processing_type'),
        Index('idx_doc_processing_status', 'status'),
        Index('idx_doc_processing_created', 'created_at'),
        Index('idx_doc_processing_creator', 'created_by'),
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="processing_tasks")
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<DocumentProcessing {self.document_id}:{self.processing_type}>"


class ProcessingJob(Base):
    """Model for processing jobs."""
    __tablename__ = "processing_jobs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_processing_job_user', 'user_id'),
        Index('idx_processing_job_type', 'job_type'),
        Index('idx_processing_job_status', 'status'),
        Index('idx_processing_job_created', 'created_at'),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], passive_deletes=True)

    def __repr__(self) -> str:
        return f"<ProcessingJob {self.id}:{self.job_type}>" 