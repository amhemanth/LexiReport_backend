from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
import uuid

class NotificationCreate(BaseModel):
    type: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    message: str
    metadata: Optional[Dict[str, Any]]
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NotificationPreferenceUpdate(BaseModel):
    type: str
    enabled: bool

class NotificationPreferenceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    enabled: bool
    model_config = ConfigDict(from_attributes=True) 