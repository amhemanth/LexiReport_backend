from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class ReportStatus(str, PyEnum):
    """Report status enum"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ReportType(str, PyEnum):
    """Report type enum"""
    STANDARD = "standard"
    CUSTOM = "custom"
    TEMPLATE = "template"


class ReportTypeCategory(str, PyEnum):
    """Report category enum"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class Report(Base):
    """Report model"""
    
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ReportStatus] = mapped_column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT)
    type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType), nullable=False)
    category: Mapped[ReportTypeCategory] = mapped_column(SQLEnum(ReportTypeCategory), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_status', 'status'),
        Index('idx_report_type', 'type'),
        Index('idx_report_category', 'category'),
        Index('idx_report_created', 'created_at'),
        Index('idx_report_creator', 'created_by'),
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="reports")
    shares: Mapped[List["ReportShare"]] = relationship(
        "ReportShare",
        back_populates="report",
        cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="report",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Report {self.title}>"


class ReportShare(Base):
    """Report share model"""
    
    __tablename__ = "report_shares"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    shared_with: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission: Mapped[str] = mapped_column(String(50), nullable=False)  # view, edit, admin
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_share_report', 'report_id'),
        Index('idx_report_share_user', 'shared_with'),
        Index('idx_report_share_expires', 'expires_at'),
    )

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="shares")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ReportShare {self.report_id}:{self.shared_with}>" 