from sqlalchemy.orm import Session
from app.repositories.notification import notification_repository, notification_preference_repository
from app.models.notifications.notification import Notification, NotificationPreference
from app.schemas.notification import NotificationCreate, NotificationPreferenceUpdate
from typing import List
import uuid

class NotificationService:
    def get_notifications(self, db: Session, user_id: uuid.UUID) -> List[Notification]:
        return notification_repository.get_by_user(db, user_id)

    def create_notification(self, db: Session, user_id: uuid.UUID, obj_in: NotificationCreate) -> Notification:
        return notification_repository.create(db, user_id, obj_in)

    def mark_as_read(self, db: Session, notification_id: uuid.UUID) -> Notification:
        return notification_repository.mark_as_read(db, notification_id)

    def get_preferences(self, db: Session, user_id: uuid.UUID) -> List[NotificationPreference]:
        return notification_preference_repository.get_by_user(db, user_id)

    def update_preference(self, db: Session, user_id: uuid.UUID, obj_in: NotificationPreferenceUpdate) -> NotificationPreference:
        return notification_preference_repository.update(db, user_id, obj_in)

notification_service = NotificationService() 