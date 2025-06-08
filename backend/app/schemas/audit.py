from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseSchema, TimestampSchema
from app.models.audit import AuditAction
import uuid

# Audit Log Schemas
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

class AuditLogUpdate(BaseSchema):
    """Schema for audit log updates."""
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

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

# User Activity Schemas
class UserActivityBase(BaseSchema):
    """Base user activity schema."""
    activity_type: str = Field(..., description="Type of user activity")
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserActivityCreate(UserActivityBase):
    """Schema for user activity creation."""
    user_id: uuid.UUID

class UserActivityUpdate(BaseSchema):
    """Schema for user activity updates."""
    details: Optional[Dict[str, Any]] = None

class UserActivityInDB(UserActivityBase, TimestampSchema):
    """Schema for user activity in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class UserActivityResponse(UserActivityInDB):
    """Schema for user activity response."""
    user: Optional[Dict[str, Any]] = None

class UserActivityList(BaseSchema):
    """Schema for paginated user activity list."""
    items: List[UserActivityResponse]
    total: int
    page: int
    size: int
    pages: int

# System Metrics Schemas
class SystemMetricsBase(BaseSchema):
    """Base system metrics schema."""
    metric_name: str = Field(..., description="Name of the metric")
    metric_value: float = Field(..., description="Metric value")
    metric_data: Optional[Dict[str, Any]] = None

class SystemMetricsCreate(SystemMetricsBase):
    """Schema for system metrics creation."""
    pass

class SystemMetricsUpdate(BaseSchema):
    """Schema for system metrics updates."""
    metric_value: Optional[float] = None
    metric_data: Optional[Dict[str, Any]] = None

class SystemMetricsInDB(SystemMetricsBase, TimestampSchema):
    """Schema for system metrics in database."""
    id: uuid.UUID

class SystemMetricsResponse(SystemMetricsInDB):
    """Schema for system metrics response."""
    pass

class SystemMetricsList(BaseSchema):
    """Schema for paginated system metrics list."""
    items: List[SystemMetricsResponse]
    total: int
    page: int
    size: int
    pages: int

# Error Log Schemas
class ErrorLogBase(BaseSchema):
    """Base error log schema."""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class ErrorLogCreate(ErrorLogBase):
    """Schema for error log creation."""
    pass

class ErrorLogUpdate(BaseSchema):
    """Schema for error log updates."""
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class ErrorLogInDB(ErrorLogBase, TimestampSchema):
    """Schema for error log in database."""
    id: uuid.UUID

class ErrorLogResponse(ErrorLogInDB):
    """Schema for error log response."""
    pass

class ErrorLogList(BaseSchema):
    """Schema for paginated error log list."""
    items: List[ErrorLogResponse]
    total: int
    page: int
    size: int
    pages: int 