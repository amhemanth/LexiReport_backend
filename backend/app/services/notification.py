from sqlalchemy.orm import Session
from app.repositories.notification import notification_repository, notification_preference_repository, notification_template_repository
from app.models.notifications.notification import Notification, NotificationPreference, NotificationTemplate
from app.models.notifications.enums import NotificationType, NotificationStatus, NotificationPriority
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate,
    NotificationTemplateCreate, NotificationTemplateUpdate,
    NotificationPreferenceUpdate
)
from typing import List, Optional
import uuid

class NotificationService:
    def get_notifications(
        self, 
        db: Session, 
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        notification_type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Notification]:
        """Get notifications for user with filters."""
        return notification_repository.get_by_user(
            db, 
            user_id=user_id,
            skip=skip,
            limit=limit,
            notification_type=notification_type,
            status=status,
            priority=priority
        )

    def count_notifications(self, db: Session, user_id: uuid.UUID) -> int:
        """Count notifications for user."""
        return notification_repository.count_by_user(db, user_id)

    def create_notification(
        self, 
        db: Session, 
        user_id: uuid.UUID, 
        obj_in: NotificationCreate
    ) -> Notification:
        """Create a new notification."""
        return notification_repository.create(db, user_id, obj_in)

    def update_notification(
        self,
        db: Session,
        notification_id: uuid.UUID,
        obj_in: NotificationUpdate
    ) -> Optional[Notification]:
        """Update a notification."""
        return notification_repository.update(db, notification_id, obj_in)

    def mark_as_read(
        self, 
        db: Session, 
        notification_id: uuid.UUID
    ) -> Optional[Notification]:
        """Mark notification as read."""
        return notification_repository.mark_as_read(db, notification_id)

    def get_preferences(
        self, 
        db: Session, 
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[NotificationPreference]:
        """Get notification preferences for user."""
        return notification_preference_repository.get_by_user(
            db, 
            user_id=user_id,
            skip=skip,
            limit=limit
        )

    def count_preferences(self, db: Session, user_id: uuid.UUID) -> int:
        """Count notification preferences for user."""
        return notification_preference_repository.count_by_user(db, user_id)

    def update_preference(
        self, 
        db: Session, 
        user_id: uuid.UUID, 
        obj_in: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        """Update notification preferences."""
        return notification_preference_repository.update(db, user_id, obj_in)

    def get_templates(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        template_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[NotificationTemplate]:
        """Get notification templates with filters."""
        return notification_template_repository.get_multi(
            db,
            skip=skip,
            limit=limit,
            template_type=template_type,
            is_active=is_active
        )

    def count_templates(self, db: Session) -> int:
        """Count notification templates."""
        return notification_template_repository.count(db)

    def create_template(
        self,
        db: Session,
        obj_in: NotificationTemplateCreate
    ) -> NotificationTemplate:
        """Create a new notification template."""
        return notification_template_repository.create(db, obj_in)

notification_service = NotificationService() 