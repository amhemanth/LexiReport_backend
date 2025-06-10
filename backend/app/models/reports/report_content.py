"""Report content model for storing report content data and versions."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Index, Integer, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base

class ReportContent(Base):
    """Report content model for storing report content data and versions."""
    __tablename__ = "report_contents"
    
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    comment: Mapped[Optional[str]] = mapped_column(String)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_content_report', 'report_id'),
        Index('idx_report_content_version', 'version_number'),
        Index('idx_report_content_created', 'created_at'),
        Index('idx_report_content_creator', 'created_by'),
        UniqueConstraint('report_id', 'version_number', name='uq_report_content_version'),
    )
    
    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="contents")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<ReportContent {self.report_id}:v{self.version_number}>" 