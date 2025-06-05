from datetime import datetime, time
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Index, UniqueConstraint, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class NotificationType(str, PyEnum):
    """Notification type enum"""
    SYSTEM = "system"
    REPORT = "report"
    COMMENT = "comment"
    SHARE = "share"
    ALERT = "alert"


class NotificationStatus(str, PyEnum):
    """Notification status enum"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class Notification(Base):
    """Notification model"""
    
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), default=NotificationStatus.UNREAD)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_notification_user_status', 'user_id', 'status'),
        Index('idx_notification_type_created', 'type', 'created_at'),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    template: Mapped[Optional["NotificationTemplate"]] = relationship(
        "NotificationTemplate",
        back_populates="notifications"
    )

    def __repr__(self) -> str:
        return f"<Notification {self.title}>"


class NotificationTemplate(Base):
    """Notification template model"""
    
    __tablename__ = "notification_templates"

    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    subject_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="template"
    )

    def __repr__(self) -> str:
        return f"<NotificationTemplate {self.name}>"


class NotificationPreference(Base):
    """User notification preferences model"""
    
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    frequency: Mapped[str] = mapped_column(String(50), default="immediate")  # immediate, daily, weekly
    quiet_hours_start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    quiet_hours_end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add unique constraint for user and type
    __table_args__ = (
        UniqueConstraint('user_id', 'type', name='uq_notification_preference_user_type'),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notification_preferences")

    def __repr__(self) -> str:
        return f"<NotificationPreference {self.user_id}:{self.type}>" 