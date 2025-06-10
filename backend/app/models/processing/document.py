"""Document model for storing document information."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Index, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base
from app.models.core.user import User
from app.models.files.enums import FileType, FileStatus

class Document(Base):
    """Model for documents."""
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    file_type: Mapped[FileType] = mapped_column(SQLEnum(FileType), nullable=False)
    status: Mapped[FileStatus] = mapped_column(SQLEnum(FileStatus), default=FileStatus.PROCESSING)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # in bytes
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_document_type', 'file_type'),
        Index('idx_document_status', 'status'),
        Index('idx_document_created', 'created_at'),
        Index('idx_document_creator', 'created_by'),
        Index('idx_document_version', 'version'),
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[created_by],
        back_populates="created_documents",
        passive_deletes=True
    )
    updater: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[updated_by],
        back_populates="updated_documents",
        passive_deletes=True
    )
    processing_tasks: Mapped[List["DocumentProcessing"]] = relationship(
        "DocumentProcessing",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Document {self.title}>" 