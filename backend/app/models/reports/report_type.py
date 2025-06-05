from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum

from app.db.base_class import Base
from app.models.reports.report import Report


class ReportTypeCategory(str, PyEnum):
    """Report type category enum"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class ReportType(Base):
    """Report type model"""
    
    __tablename__ = "report_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[ReportTypeCategory] = mapped_column(SQLEnum(ReportTypeCategory))
    template: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_report_type_category', 'category'),
        Index('idx_report_type_active', 'is_active'),
    )

    # Relationships
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="type")

    def __repr__(self) -> str:
        return f"<ReportType {self.name}>" 