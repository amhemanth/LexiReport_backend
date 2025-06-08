"""Report content model for storing report content data."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base

class ReportContent(Base):
    """Report content model for storing report content data."""
    __tablename__ = "report_contents"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    report: Mapped["Report"] = relationship(
        "Report",
        back_populates="content_obj",
        passive_deletes=True,
        primaryjoin="ReportContent.report_id==Report.id"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_report_content_report", "report_id"),
        Index("idx_report_content_type", "content_type"),
        Index("idx_report_content_version", "version"),
        Index("idx_report_content_created", "created_at"),
        Index("idx_report_content_updated", "updated_at"),
    )

    def __repr__(self):
        return f"<ReportContent {self.content_type}>" 