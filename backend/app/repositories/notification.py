from sqlalchemy.orm import Session
from app.models.notifications.notification import Notification, NotificationPreference
from app.schemas.notification import NotificationCreate, NotificationPreferenceUpdate
from typing import Optional, List
import uuid

class NotificationRepository:
    def get_by_user(self, db: Session, user_id: uuid.UUID) -> List[Notification]:
        return db.query(Notification).filter(Notification.user_id == user_id).all()

    def create(self, db: Session, user_id: uuid.UUID, obj_in: NotificationCreate) -> Notification:
        db_obj = Notification(user_id=user_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_as_read(self, db: Session, notification_id: uuid.UUID) -> Optional[Notification]:
        notif = db.query(Notification).filter(Notification.id == notification_id).first()
        if notif:
            notif.is_read = True
            db.add(notif)
            db.commit()
            db.refresh(notif)
        return notif

class NotificationPreferenceRepository:
    def get_by_user(self, db: Session, user_id: uuid.UUID) -> List[NotificationPreference]:
        return db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).all()

    def update(self, db: Session, user_id: uuid.UUID, obj_in: NotificationPreferenceUpdate) -> NotificationPreference:
        pref = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id, NotificationPreference.type == obj_in.type).first()
        if pref:
            pref.enabled = obj_in.enabled
        else:
            pref = NotificationPreference(user_id=user_id, type=obj_in.type, enabled=obj_in.enabled)
            db.add(pref)
        db.commit()
        db.refresh(pref)
        return pref

notification_repository = NotificationRepository()
notification_preference_repository = NotificationPreferenceRepository() 