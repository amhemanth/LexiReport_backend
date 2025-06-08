from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Integer, Boolean, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class FileType(str, PyEnum):
    """File type enum"""
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    OTHER = "other"


class FileStatus(str, PyEnum):
    """File status enum"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


class FileStorage(Base):
    """File storage model"""
    
    __tablename__ = "file_storage"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[FileType] = mapped_column(SQLEnum(FileType), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)  # in bytes
    status: Mapped[FileStatus] = mapped_column(SQLEnum(FileStatus), default=FileStatus.UPLOADING)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_file_storage_user_type', 'user_id', 'file_type'),
        Index('idx_file_storage_status_created', 'status', 'created_at'),
        Index('idx_file_storage_expires', 'expires_at'),
        Index('idx_file_storage_entity', 'entity_type', 'entity_id'),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="files",
        passive_deletes=True
    )
    versions: Mapped[List["FileVersion"]] = relationship(
        "FileVersion",
        back_populates="file",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    access_logs: Mapped[List["FileAccessLog"]] = relationship(
        "FileAccessLog",
        back_populates="file",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        primaryjoin="and_(foreign(FileStorage.entity_type) == 'report', foreign(FileStorage.entity_id) == remote(Report.id))",
        back_populates="attachments",
        passive_deletes=True
    )
    report_exports: Mapped[List["ReportExport"]] = relationship(
        "ReportExport",
        back_populates="file",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<FileStorage {self.filename}>"


class FileVersion(Base):
    """File version model"""
    
    __tablename__ = "file_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("file_storage.id", ondelete="CASCADE"), 
        nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)  # in bytes
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True
    )
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_file_version_file_current', 'file_id', 'is_current'),
        Index('idx_file_version_created', 'created_at'),
    )

    # Relationships
    file: Mapped["FileStorage"] = relationship(
        "FileStorage", 
        back_populates="versions",
        passive_deletes=True
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[created_by],
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<FileVersion {self.file_id}:v{self.version_number}>"


class FileAccessLog(Base):
    """File access log model"""
    
    __tablename__ = "file_access_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("file_storage.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # view, download, share, etc.
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    additional_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_file_access_log_file', 'file_id'),
        Index('idx_file_access_log_user', 'user_id'),
        Index('idx_file_access_log_created', 'created_at'),
    )

    # Relationships
    file: Mapped["FileStorage"] = relationship(
        "FileStorage", 
        back_populates="access_logs",
        passive_deletes=True
    )
    user: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[user_id],
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<FileAccessLog {self.file_id}:{self.action}>" 