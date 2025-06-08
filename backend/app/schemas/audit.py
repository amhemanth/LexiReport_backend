from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
import uuid

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    event_type: str
    event_data: Optional[Dict[str, Any]]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserActivityResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    activity_type: str
    details: Optional[Dict[str, Any]]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SystemMetricResponse(BaseModel):
    id: uuid.UUID
    metric_type: str
    value: float
    recorded_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ErrorLogResponse(BaseModel):
    id: uuid.UUID
    error_type: str
    message: str
    details: Optional[Dict[str, Any]]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 