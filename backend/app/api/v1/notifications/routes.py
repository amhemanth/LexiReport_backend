from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationPreferenceUpdate, NotificationPreferenceResponse
from app.services.notification import notification_service
import uuid

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [NotificationResponse.from_orm(n) for n in notification_service.get_notifications(db, current_user.id)]

@router.post("/", response_model=NotificationResponse)
def create_notification(
    obj_in: NotificationCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return NotificationResponse.from_orm(notification_service.create_notification(db, current_user.id, obj_in))

@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = notification_service.mark_as_read(db, notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notif)

@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return [NotificationPreferenceResponse.from_orm(p) for p in notification_service.get_preferences(db, current_user.id)]

@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_notification_preference(
    obj_in: NotificationPreferenceUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return NotificationPreferenceResponse.from_orm(notification_service.update_preference(db, current_user.id, obj_in)) 