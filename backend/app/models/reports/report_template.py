from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base

class ReportTemplate(Base):
    """Model for report templates."""
    __tablename__ = "report_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="report_templates",
        passive_deletes=True
    )
    updater: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_templates",
        passive_deletes=True
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="template",
        passive_deletes=True
    )
    created_exports: Mapped[List["ReportExport"]] = relationship(
        "ReportExport",
        back_populates="template",
        passive_deletes=True
    )

    # Indexes
    __table_args__ = (
        Index("ix_report_templates_name", "name"),
        Index("ix_report_templates_type", "type"),
        Index("ix_report_templates_category", "category"),
        Index("ix_report_templates_created", "created_at"),
        Index("ix_report_templates_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<ReportTemplate {self.name}>" 