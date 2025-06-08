from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base

class ReportSchedule(Base):
    """Model for report schedules."""
    __tablename__ = "report_schedules"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    schedule: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)  # Cron expression or schedule details
    recipients: Mapped[list[str]] = mapped_column(JSON, nullable=False)  # List of recipient emails
    format: Mapped[str] = mapped_column(String(20), nullable=False)  # PDF, Excel, etc.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report: Mapped["Report"] = relationship(
        "Report",
        back_populates="schedules",
        passive_deletes=True
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="report_schedules",
        passive_deletes=True
    )
    updater: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_schedules",
        passive_deletes=True
    )

    # Indexes
    __table_args__ = (
        Index("ix_report_schedules_name", "name"),
        Index("ix_report_schedules_active", "is_active"),
        Index("ix_report_schedules_next_run", "next_run"),
        Index("ix_report_schedules_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ReportSchedule {self.name}>" 