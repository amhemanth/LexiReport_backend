from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, Boolean, DateTime, Integer, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base
from app.models.reports.enums import ReportExportStatus

class ReportExport(Base):
    """Model for report exports."""
    __tablename__ = "report_exports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    file_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("file_storage.id", ondelete="SET NULL"), nullable=True)
    template_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("report_templates.id", ondelete="SET NULL"), nullable=True)
    format: Mapped[str] = mapped_column(String(20), nullable=False)  # PDF, Excel, etc.
    status: Mapped[ReportExportStatus] = mapped_column(SQLEnum(ReportExportStatus), nullable=False, default=ReportExportStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_export_report', 'report_id'),
        Index('idx_report_export_status', 'status'),
        Index('idx_report_export_created', 'created_at'),
        Index('idx_report_export_format', 'format'),
    )

    # Relationships
    report: Mapped["Report"] = relationship(
        "Report",
        back_populates="exports",
        passive_deletes=True
    )
    file: Mapped[Optional["FileStorage"]] = relationship(
        "FileStorage",
        back_populates="report_exports",
        passive_deletes=True
    )
    template: Mapped[Optional["ReportTemplate"]] = relationship(
        "ReportTemplate",
        back_populates="created_exports",
        passive_deletes=True
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_exports",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<ReportExport {self.id}>" 