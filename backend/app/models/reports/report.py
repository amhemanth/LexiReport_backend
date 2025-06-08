from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Index, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from enum import Enum as PyEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base
from app.models.core.user import User
from app.models.reports.enums import ReportType, ReportStatus, ReportTypeCategory, AnalysisType, MetadataType


class Report(Base):
    """Model for reports."""
    __tablename__ = "reports"
    
    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ReportStatus] = mapped_column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.DRAFT)
    type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType), nullable=False, default=ReportType.STANDARD)
    category: Mapped[ReportTypeCategory] = mapped_column(SQLEnum(ReportTypeCategory), nullable=False, default=ReportTypeCategory.ANALYTICAL)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Analysis fields
    analysis_type: Mapped[Optional[AnalysisType]] = mapped_column(SQLEnum(AnalysisType))
    analysis_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Metadata fields
    metadata_type: Mapped[Optional[MetadataType]] = mapped_column(SQLEnum(MetadataType))
    metadata_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Common fields
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("report_templates.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[created_by], 
        back_populates="created_reports",
        passive_deletes=True
    )
    updater: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[updated_by], 
        back_populates="updated_reports",
        passive_deletes=True
    )
    content_obj: Mapped[Optional["ReportContent"]] = relationship(
        "ReportContent",
        back_populates="report",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    insights: Mapped[List["ReportInsight"]] = relationship(
        "ReportInsight",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    queries: Mapped[List["ReportQuery"]] = relationship(
        "ReportQuery",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    versions: Mapped[List["ReportVersion"]] = relationship(
        "ReportVersion",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="desc(ReportVersion.version_number)"
    )
    comments: Mapped[List["ReportComment"]] = relationship(
        "ReportComment",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True,
        primaryjoin="and_(Report.id == ReportComment.report_id, ReportComment.parent_id == None)"
    )
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity",
        primaryjoin="and_(foreign(UserActivity.entity_type) == 'report', foreign(UserActivity.entity_id) == Report.id)",
        back_populates="report",
        passive_deletes=True,
        overlaps="comment"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        primaryjoin="and_(foreign(AuditLog.entity_type) == 'report', foreign(AuditLog.entity_id) == Report.id)",
        back_populates="report",
        passive_deletes=True,
        overlaps="comment"
    )
    tags: Mapped[List["EntityTag"]] = relationship(
        "EntityTag",
        primaryjoin="and_(foreign(EntityTag.entity_type) == 'report', foreign(EntityTag.entity_id) == Report.id)",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    bi_integrations: Mapped[List["BIIntegration"]] = relationship(
        "BIIntegration",
        primaryjoin="and_(foreign(BIIntegration.entity_type) == 'report', foreign(BIIntegration.entity_id) == Report.id)",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    shares: Mapped[List["ReportShare"]] = relationship(
        "ReportShare",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    template: Mapped[Optional["ReportTemplate"]] = relationship(
        "ReportTemplate",
        back_populates="reports",
        passive_deletes=True
    )
    schedules: Mapped[List["ReportSchedule"]] = relationship(
        "ReportSchedule",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    exports: Mapped[List["ReportExport"]] = relationship(
        "ReportExport",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        primaryjoin="and_(foreign(Notification.entity_type) == 'report', foreign(Notification.entity_id) == Report.id)",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    attachments: Mapped[List["FileStorage"]] = relationship(
        "FileStorage",
        primaryjoin="and_(foreign(FileStorage.entity_type) == 'report', foreign(FileStorage.entity_id) == Report.id)",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    voice_commands: Mapped[List["VoiceCommand"]] = relationship(
        "VoiceCommand",
        primaryjoin="and_(foreign(VoiceCommand.entity_type) == 'report', foreign(VoiceCommand.entity_id) == Report.id)",
        back_populates="report",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Indexes
    __table_args__ = (
        Index("ix_reports_created_by", "created_by"),
        Index("ix_reports_updated_by", "updated_by"),
        Index("ix_reports_status", "status"),
        Index("ix_reports_type", "type"),
        Index("ix_reports_category", "category"),
        Index("ix_reports_created", "created_at"),
        Index("ix_reports_updated", "updated_at"),
        Index("ix_reports_template", "template_id"),
        Index("ix_reports_analysis_type", "analysis_type"),
        Index("ix_reports_metadata_type", "metadata_type"),
    )

    def __repr__(self) -> str:
        return f"<Report(title='{self.title}', status='{self.status}')>"


class ReportShare(Base):
    """Model for report sharing."""
    __tablename__ = "report_shares"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    shared_by: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shared_with: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission: Mapped[str] = mapped_column(String(50), default="view")
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="shares", passive_deletes=True)
    sharer: Mapped["User"] = relationship("User", foreign_keys=[shared_by], back_populates="shared_reports", passive_deletes=True)
    sharee: Mapped["User"] = relationship("User", foreign_keys=[shared_with], back_populates="received_reports", passive_deletes=True)

    # Indexes
    __table_args__ = (
        Index("ix_report_shares_report_id", "report_id"),
        Index("ix_report_shares_shared_by", "shared_by"),
        Index("ix_report_shares_shared_with", "shared_with"),
        Index("ix_report_shares_created", "created_at"),
        Index("ix_report_shares_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<ReportShare(report_id={self.report_id}, shared_with={self.shared_with})>" 