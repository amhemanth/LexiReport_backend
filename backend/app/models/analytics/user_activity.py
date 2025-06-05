from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.models.core.user import User


class EventType(str, PyEnum):
    """Event type enum"""
    LOGIN = "login"
    LOGOUT = "logout"
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SHARE = "share"
    EXPORT = "export"
    OTHER = "other"


class UserActivity(Base):
    """User activity model"""
    
    __tablename__ = "user_activities"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('idx_user_activity_user', 'user_id'),
        Index('idx_user_activity_type', 'event_type'),
        Index('idx_user_activity_entity', 'entity_type', 'entity_id'),
        Index('idx_user_activity_created', 'created_at'),
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="activities")
    
    def __repr__(self) -> str:
        return f"<UserActivity {self.user_id}:{self.event_type}>" 