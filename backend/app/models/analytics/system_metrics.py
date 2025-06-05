from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class SystemMetrics(Base):
    """System metrics model"""
    __tablename__ = "system_metrics"
    
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(nullable=False)
    metric_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<SystemMetrics {self.metric_name}:{self.metric_value}>" 