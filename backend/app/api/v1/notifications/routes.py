from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.schemas.notification import (
    NotificationCreate, NotificationResponse, NotificationUpdate,
    NotificationPreferenceUpdate, NotificationPreferenceResponse,
    NotificationTemplateCreate, NotificationTemplateResponse,
    NotificationList, NotificationPreferenceList, NotificationTemplateList
)
from app.services.notification import notification_service
import uuid

router = APIRouter()

@router.get("/", response_model=NotificationList)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    notification_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    """List notifications for the current user."""
    notifications = notification_service.get_notifications(
        db, 
        current_user.id,
        skip=skip,
        limit=limit,
        notification_type=notification_type,
        status=status,
        priority=priority
    )
    total = notification_service.count_notifications(db, current_user.id)
    return NotificationList(
        items=[NotificationResponse.from_orm(n) for n in notifications],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=NotificationResponse)
def create_notification(
    obj_in: NotificationCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification."""
    return NotificationResponse.from_orm(
        notification_service.create_notification(db, current_user.id, obj_in)
    )

@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: uuid.UUID,
    obj_in: NotificationUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a notification."""
    notification = notification_service.update_notification(db, notification_id, obj_in)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)

@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    notification = notification_service.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)

@router.get("/preferences", response_model=NotificationPreferenceList)
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get notification preferences for the current user."""
    preferences = notification_service.get_preferences(
        db, 
        current_user.id,
        skip=skip,
        limit=limit
    )
    total = notification_service.count_preferences(db, current_user.id)
    return NotificationPreferenceList(
        items=[NotificationPreferenceResponse.from_orm(p) for p in preferences],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_notification_preference(
    obj_in: NotificationPreferenceUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences for the current user."""
    return NotificationPreferenceResponse.from_orm(
        notification_service.update_preference(db, current_user.id, obj_in)
    )

@router.get("/templates", response_model=NotificationTemplateList)
def list_notification_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    template_type: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """List notification templates."""
    templates = notification_service.get_templates(
        db,
        skip=skip,
        limit=limit,
        template_type=template_type,
        is_active=is_active
    )
    total = notification_service.count_templates(db)
    return NotificationTemplateList(
        items=[NotificationTemplateResponse.from_orm(t) for t in templates],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/templates", response_model=NotificationTemplateResponse)
def create_notification_template(
    obj_in: NotificationTemplateCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification template."""
    return NotificationTemplateResponse.from_orm(
        notification_service.create_template(db, obj_in)
    ) 