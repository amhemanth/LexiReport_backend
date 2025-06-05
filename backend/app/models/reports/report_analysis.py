from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ReportAnalysis(Base):
    __tablename__ = "report_analysis"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String, nullable=False)
    analysis_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="analysis")

    def __repr__(self):
        return f"<ReportAnalysis {self.analysis_type}>" 