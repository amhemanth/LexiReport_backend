from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid

from sqlalchemy import String, ForeignKey, Enum as SQLEnum, JSON, Column, Integer, DateTime, Index, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.models.core.user import User


class ProcessingType(str, PyEnum):
    """Processing type enum"""
    OCR = "ocr"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    TRANSLATION = "translation"
    OTHER = "other"


class ProcessingStatus(str, PyEnum):
    """Processing status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentProcessingQueue(Base):
    __tablename__ = "document_processing_queue"

    document_id: Mapped[str] = mapped_column(String, nullable=False)
    processing_type: Mapped[ProcessingType] = mapped_column(SQLEnum(ProcessingType), nullable=False)
    status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    priority: Mapped[int] = mapped_column(Integer, default=0)

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
    __tablename__ = "document_processing_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("document_processing_queue.id", ondelete="CASCADE"), nullable=False)
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    queue_item: Mapped["DocumentProcessingQueue"] = relationship("DocumentProcessingQueue", back_populates="results")

    def __repr__(self):
        return f"<DocumentProcessingResult {self.id}>"


class DocumentProcessing(Base):
    """Document processing model"""
    
    __tablename__ = "document_processing"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("file_storage.id", ondelete="CASCADE"), nullable=False)
    processing_type: Mapped[ProcessingType] = mapped_column(SQLEnum(ProcessingType), nullable=False)
    status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(String)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_doc_processing_document', 'document_id'),
        Index('idx_doc_processing_type', 'processing_type'),
        Index('idx_doc_processing_status', 'status'),
        Index('idx_doc_processing_created', 'created_at'),
    )

    # Relationships
    document: Mapped["FileStorage"] = relationship("FileStorage", foreign_keys=[document_id])

    def __repr__(self) -> str:
        return f"<DocumentProcessing {self.document_id}:{self.processing_type}>"


class ProcessingJob(Base):
    """Processing job model for background tasks"""
    
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    content_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_processing_job_user', 'user_id'),
        Index('idx_processing_job_type', 'job_type'),
        Index('idx_processing_job_status', 'status'),
        Index('idx_processing_job_priority', 'priority'),
        Index('idx_processing_job_created', 'created_at'),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<ProcessingJob {self.id}:{self.job_type}>" 