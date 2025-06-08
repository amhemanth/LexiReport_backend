from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
import uuid

class SystemMetricsBase(BaseSchema):
    """Base system metrics schema."""
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    labels: Optional[Dict[str, str]] = None

class SystemMetricsCreate(SystemMetricsBase):
    """Schema for system metrics creation."""
    pass

class SystemMetricsInDB(SystemMetricsBase, TimestampSchema):
    """Schema for system metrics in database."""
    id: uuid.UUID

class SystemMetricsResponse(SystemMetricsInDB):
    """Schema for system metrics response."""
    pass

class ErrorLogBase(BaseSchema):
    """Base error log schema."""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    severity: str = Field(..., pattern="^(critical|error|warning|info)$")

class ErrorLogCreate(ErrorLogBase):
    """Schema for error log creation."""
    pass

class ErrorLogInDB(ErrorLogBase, TimestampSchema):
    """Schema for error log in database."""
    id: uuid.UUID

class ErrorLogResponse(ErrorLogInDB):
    """Schema for error log response."""
    pass

class VoiceCommandBase(BaseSchema):
    """Base voice command schema."""
    command_text: str
    recognized_text: Optional[str] = None
    confidence: Optional[float] = None
    context: Optional[Dict[str, Any]] = None

class VoiceCommandCreate(VoiceCommandBase):
    """Schema for voice command creation."""
    pass

class VoiceCommandInDB(VoiceCommandBase, TimestampSchema):
    """Schema for voice command in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class VoiceCommandResponse(VoiceCommandInDB):
    """Schema for voice command response."""
    pass

class AnalyticsList(BaseSchema):
    """Schema for paginated analytics list."""
    items: List[SystemMetricsResponse]
    total: int
    page: int
    size: int
    pages: int

class ErrorLogList(BaseSchema):
    """Schema for paginated error log list."""
    items: List[ErrorLogResponse]
    total: int
    page: int
    size: int
    pages: int

class VoiceCommandList(BaseSchema):
    """Schema for paginated voice command list."""
    items: List[VoiceCommandResponse]
    total: int
    page: int
    size: int
    pages: int 