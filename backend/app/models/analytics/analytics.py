from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.analytics.enums import EventType
from app.models.analytics.user_activity import UserActivity
from app.models.analytics.system_metrics import SystemMetrics
from app.models.analytics.error_log import ErrorLog
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID

__all__ = [
    "UserActivity",
    "SystemMetrics",
    "ErrorLog",
    "EventType"
]

class EventType(str, PyEnum):
    """Event type enum"""
    PAGE_VIEW = "page_view"
    REPORT_VIEW = "report_view"
    REPORT_CREATE = "report_create"
    REPORT_UPDATE = "report_update"
    REPORT_DELETE = "report_delete"
    REPORT_SHARE = "report_share"
    REPORT_EXPORT = "report_export"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    OTHER = "other"

class UserActivity(Base):
    __tablename__ = "user_activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType), nullable=False)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<UserActivity {self.event_type}>"

class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    metric_name: Mapped[str] = mapped_column(String, nullable=False)
    metric_value: Mapped[Dict[str, Any]] = mapped_column(JSON)

    def __repr__(self):
        return f"<SystemMetrics {self.metric_name}>"

class ErrorLog(Base):
    __tablename__ = "error_logs"

    error_type: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)
    stack_trace: Mapped[Optional[str]] = mapped_column(String)

    def __repr__(self):
        return f"<ErrorLog {self.error_type}>"

class Analytics(Base):
    """Analytics model"""
    
    __tablename__ = "analytics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_analytics_user', 'user_id'),
        Index('idx_analytics_type', 'event_type'),
        Index('idx_analytics_entity', 'entity_type', 'entity_id'),
        Index('idx_analytics_created', 'created_at'),
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<Analytics {self.user_id}:{self.event_type}>" 