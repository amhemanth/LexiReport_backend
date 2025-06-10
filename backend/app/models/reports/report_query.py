from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, JSON, Column, DateTime, Index, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base
from app.models.core.user import User
from app.models.reports.report import Report

class ReportQuery(Base):
    """Model for storing report queries and their responses."""
    __tablename__ = "report_queries"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query_text: Mapped[str] = mapped_column(String, nullable=False)
    response_text: Mapped[Optional[str]] = mapped_column(String)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_query_report', 'report_id'),
        Index('idx_report_query_user', 'user_id'),
        Index('idx_report_query_created', 'created_at'),
    )

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="queries")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<ReportQuery {self.id}:{self.query_text[:50]}>" 