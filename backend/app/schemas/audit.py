from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
from app.models.audit import AuditAction
import uuid

class AuditLogBase(BaseSchema):
    """Base audit log schema."""
    action: AuditAction
    entity_type: str
    entity_id: uuid.UUID
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    """Schema for audit log creation."""
    user_id: uuid.UUID

class AuditLogInDB(AuditLogBase, TimestampSchema):
    """Schema for audit log in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class AuditLogResponse(AuditLogInDB):
    """Schema for audit log response."""
    user: Optional[Dict[str, Any]] = None

class AuditLogList(BaseSchema):
    """Schema for paginated audit log list."""
    items: List[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int

class AuditLogFilter(BaseSchema):
    """Schema for audit log filtering."""
    action: Optional[AuditAction] = None
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

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