from sqlalchemy.orm import Session
from app.repositories.notification import notification_repository, notification_preference_repository, notification_template_repository
from app.models.notifications.notification import Notification, NotificationPreference, NotificationTemplate
from app.models.notifications.enums import NotificationType, NotificationStatus, NotificationPriority
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate,
    NotificationTemplateCreate, NotificationTemplateUpdate,
    NotificationPreferenceUpdate
)
from typing import List, Optional, Dict
import uuid
from datetime import datetime
from app.config import settings
from app.core.logger import logger

class NotificationService:
    def __init__(self):
        self.batch_size = 100
        self.batch_timeout = 60  # seconds
        self.notification_batch = []
        self.last_batch_time = datetime.utcnow()

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
        # Add to batch
        self.notification_batch.append((user_id, obj_in))
        
        # Process batch if full or timeout reached
        if (len(self.notification_batch) >= self.batch_size or 
            (datetime.utcnow() - self.last_batch_time).total_seconds() >= self.batch_timeout):
            self._process_batch(db)
        
        return notification_repository.create(db, user_id, obj_in)

    def _process_batch(self, db: Session) -> None:
        """Process notification batch."""
        if not self.notification_batch:
            return
        
        try:
            # Sort by priority
            self.notification_batch.sort(key=lambda x: x[1].priority.value, reverse=True)
            
            # Create notifications
            for user_id, notification in self.notification_batch:
                notification_repository.create(db, user_id, notification)
            
            # Clear batch
            self.notification_batch = []
            self.last_batch_time = datetime.utcnow()
        except Exception as e:
            logger.error(f"Error processing notification batch: {str(e)}")
            # Retry failed notifications
            self._retry_failed_notifications(db)

    def _retry_failed_notifications(self, db: Session) -> None:
        """Retry failed notifications."""
        try:
            failed_notifications = notification_repository.get_by_status(
                db, status=NotificationStatus.FAILED
            )
            
            for notification in failed_notifications:
                if notification.retry_count < settings.MAX_NOTIFICATION_RETRIES:
                    notification.retry_count += 1
                    notification.status = NotificationStatus.PENDING
                    db.add(notification)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error retrying failed notifications: {str(e)}")

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

    def mark_all_as_read(
        self,
        db: Session,
        user_id: uuid.UUID
    ) -> int:
        """Mark all notifications as read for user."""
        return notification_repository.mark_all_as_read(db, user_id)

    def delete_old_notifications(
        self,
        db: Session,
        days: int = 30
    ) -> int:
        """Delete notifications older than specified days."""
        return notification_repository.delete_old_notifications(db, days)

    def get_notification_stats(
        self,
        db: Session,
        user_id: uuid.UUID
    ) -> Dict[str, int]:
        """Get notification statistics for user."""
        return {
            "total": notification_repository.count_by_user(db, user_id),
            "unread": notification_repository.count_by_user_and_status(
                db, user_id, NotificationStatus.UNREAD
            ),
            "read": notification_repository.count_by_user_and_status(
                db, user_id, NotificationStatus.READ
            ),
            "failed": notification_repository.count_by_user_and_status(
                db, user_id, NotificationStatus.FAILED
            )
        }

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

    def update_notification_preferences(
        self,
        db: Session,
        user_id: uuid.UUID,
        preferences: Dict[str, bool]
    ) -> NotificationPreference:
        """Update notification preferences."""
        return notification_preference_repository.update(
            db,
            user_id=user_id,
            obj_in=NotificationPreferenceUpdate(**preferences)
        )

    def get_notification_preferences(
        self,
        db: Session,
        user_id: uuid.UUID
    ) -> List[NotificationPreference]:
        """Get notification preferences for user."""
        return notification_preference_repository.get_by_user(db, user_id)

    def create_notification_template(
        self,
        db: Session,
        obj_in: NotificationTemplateCreate
    ) -> NotificationTemplate:
        """Create a new notification template."""
        return notification_template_repository.create(db, obj_in)

    def get_notification_templates(
        self,
        db: Session,
        template_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[NotificationTemplate]:
        """Get notification templates."""
        return notification_template_repository.get_multi(
            db,
            template_type=template_type,
            is_active=is_active
        )

notification_service = NotificationService() 