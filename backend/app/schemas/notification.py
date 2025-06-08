from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
from app.models.notifications.enums import NotificationType, NotificationStatus, NotificationPriority
import uuid

class NotificationBase(BaseSchema):
    """Base notification schema."""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    status: NotificationStatus = NotificationStatus.UNREAD
    metadata: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None

class NotificationCreate(NotificationBase):
    """Schema for notification creation."""
    user_id: uuid.UUID

class NotificationUpdate(NotificationBase):
    """Schema for notification updates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    status: Optional[NotificationStatus] = None

class NotificationInDB(NotificationBase, TimestampSchema):
    """Schema for notification in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool = False
    read_at: Optional[datetime] = None

class NotificationResponse(NotificationInDB):
    """Schema for notification response."""
    user: Optional[Dict[str, Any]] = None

class NotificationTemplateBase(BaseSchema):
    """Base notification template schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_type: NotificationType
    subject_template: str
    body_template: str
    metadata_schema: Optional[Dict[str, Any]] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema for notification template creation."""
    pass

class NotificationTemplateUpdate(NotificationTemplateBase):
    """Schema for notification template updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    template_type: Optional[NotificationType] = None
    is_active: Optional[bool] = None

class NotificationTemplateInDB(NotificationTemplateBase, TimestampSchema):
    """Schema for notification template in database."""
    id: uuid.UUID

class NotificationTemplateResponse(NotificationTemplateInDB):
    """Schema for notification template response."""
    pass

class NotificationPreferenceBase(BaseSchema):
    """Base notification preference schema."""
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    notification_types: Dict[str, bool] = Field(default_factory=dict)

class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for notification preference creation."""
    pass

class NotificationPreferenceUpdate(NotificationPreferenceBase):
    """Schema for notification preference updates."""
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    notification_types: Optional[Dict[str, bool]] = None

class NotificationPreferenceInDB(NotificationPreferenceBase, TimestampSchema):
    """Schema for notification preference in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class NotificationPreferenceResponse(NotificationPreferenceInDB):
    """Schema for notification preference response."""
    user: Optional[Dict[str, Any]] = None

class NotificationList(BaseSchema):
    """Schema for paginated notification list."""
    items: List[NotificationResponse]
    total: int
    page: int
    size: int
    pages: int

class NotificationTemplateList(BaseSchema):
    """Schema for paginated notification template list."""
    items: List[NotificationTemplateResponse]
    total: int
    page: int
    size: int
    pages: int

class NotificationPreferenceList(BaseSchema):
    """Schema for paginated notification preference list."""
    items: List[NotificationPreferenceResponse]
    total: int
    page: int
    size: int
    pages: int 