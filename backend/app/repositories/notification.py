from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.notifications import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationStatus, NotificationPriority
)
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate,
    NotificationTemplateCreate, NotificationTemplateUpdate,
    NotificationPreferenceCreate, NotificationPreferenceUpdate
)
from .base import BaseRepository

class NotificationRepository(BaseRepository[Notification, NotificationCreate, NotificationUpdate]):
    """Repository for Notification model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications for user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_type(
        self, db: Session, *, notification_type: NotificationType,
        skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications by type."""
        return self.get_multi_by_field(
            db, field="notification_type", value=notification_type,
            skip=skip, limit=limit
        )

    def get_by_status(
        self, db: Session, *, status: NotificationStatus,
        skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications by status."""
        return self.get_multi_by_field(
            db, field="status", value=status, skip=skip, limit=limit
        )

    def get_by_priority(
        self, db: Session, *, priority: NotificationPriority,
        skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications by priority."""
        return self.get_multi_by_field(
            db, field="priority", value=priority, skip=skip, limit=limit
        )

class NotificationTemplateRepository(
    BaseRepository[NotificationTemplate, NotificationTemplateCreate, NotificationTemplateUpdate]
):
    """Repository for NotificationTemplate model."""

    def get_by_type(
        self, db: Session, *, template_type: NotificationType,
        skip: int = 0, limit: int = 100
    ) -> List[NotificationTemplate]:
        """Get templates by type."""
        return self.get_multi_by_field(
            db, field="template_type", value=template_type,
            skip=skip, limit=limit
        )

    def get_active_templates(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[NotificationTemplate]:
        """Get active templates."""
        return self.get_multi_by_field(
            db, field="is_active", value=True, skip=skip, limit=limit
        )

class NotificationPreferenceRepository(
    BaseRepository[NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate]
):
    """Repository for NotificationPreference model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[NotificationPreference]:
        """Get preferences for user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_type(
        self, db: Session, *, notification_type: NotificationType,
        skip: int = 0, limit: int = 100
    ) -> List[NotificationPreference]:
        """Get preferences by notification type."""
        return self.get_multi_by_field(
            db, field="notification_type", value=notification_type,
            skip=skip, limit=limit
        )

    def get_enabled_preferences(
        self, db: Session, *, user_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[NotificationPreference]:
        """Get enabled preferences for user."""
        return db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.email_enabled == True,
            NotificationPreference.push_enabled == True,
            NotificationPreference.in_app_enabled == True
        ).offset(skip).limit(limit).all()

# Create repository instances
notification_repository = NotificationRepository(Notification)
notification_template_repository = NotificationTemplateRepository(NotificationTemplate)
notification_preference_repository = NotificationPreferenceRepository(NotificationPreference) 