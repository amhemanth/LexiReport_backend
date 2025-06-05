from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ErrorLog(Base):
    """Error log model"""
    __tablename__ = "error_logs"
    
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[str] = mapped_column(Text, nullable=True)
    context_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ErrorLog {self.error_type}>" 