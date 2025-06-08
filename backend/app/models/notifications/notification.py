from datetime import datetime, time
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean, DateTime, Index, UniqueConstraint, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.models.notifications.enums import NotificationType, NotificationStatus


class Notification(Base):
    """Notification model"""
    
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notification_templates.id", ondelete="SET NULL"),
        nullable=True
    )
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), default=NotificationStatus.UNREAD)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_notification_user_status', 'user_id', 'status'),
        Index('idx_notification_type_created', 'type', 'created_at'),
        Index('idx_notification_expires', 'expires_at'),
        Index('idx_notification_important', 'is_important'),
        Index('idx_notification_template', 'template_id'),
        Index('idx_notification_entity', 'entity_type', 'entity_id'),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="notifications",
        passive_deletes=True
    )
    template: Mapped[Optional["NotificationTemplate"]] = relationship(
        "NotificationTemplate",
        back_populates="notifications",
        passive_deletes=True
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        primaryjoin="and_(foreign(Notification.entity_type) == 'report', foreign(Notification.entity_id) == remote(Report.id))",
        back_populates="notifications",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Notification {self.title}>"


class NotificationTemplate(Base):
    """Notification template model"""
    
    __tablename__ = "notification_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    subject_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_notification_template_type', 'type'),
        Index('idx_notification_template_active', 'is_active'),
        UniqueConstraint('type', 'name', name='uq_notification_template_type_name'),
    )

    # Relationships
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="template",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<NotificationTemplate {self.name}>"


class NotificationPreference(Base):
    """User notification preferences model"""
    
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
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
        Index('idx_notification_preference_user', 'user_id'),
        Index('idx_notification_preference_type', 'type'),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="notification_preferences",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<NotificationPreference {self.user_id}:{self.type}>" 