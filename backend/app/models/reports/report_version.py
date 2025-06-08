from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, JSON, Column, DateTime, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base
from app.models.core.user import User
from app.models.reports.report import Report

class ReportVersion(Base):
    """Model for tracking report versions."""
    
    __tablename__ = "report_versions"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    content: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_by: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    comment: Mapped[Optional[str]] = mapped_column(String)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_version_report', 'report_id'),
        Index('idx_report_version_number', 'version_number'),
        Index('idx_report_version_created', 'created_at'),
    )

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="versions")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<ReportVersion {self.report_id}:v{self.version_number}>" 