from sqlalchemy import String, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base_class import Base


class SystemMetrics(Base):
    """System metrics model"""
    __tablename__ = "system_metrics"
    
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(nullable=False)
    metric_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_system_metrics_name', 'metric_name'),
        Index('idx_system_metrics_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<SystemMetrics {self.metric_name}:{self.metric_value}>" 