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
    command_text: str = Field(..., description="The voice command text")
    action_type: str = Field(..., description="Type of action to perform")
    status: str = Field(..., description="Status of the command execution")
    entity_type: Optional[str] = Field(None, description="Type of entity this command relates to")
    entity_id: Optional[uuid.UUID] = Field(None, description="ID of the entity this command relates to")
    meta_data: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class VoiceCommandCreate(VoiceCommandBase):
    """Schema for voice command creation."""
    user_id: uuid.UUID = Field(..., description="ID of the user who issued the command")

class VoiceCommandUpdate(BaseSchema):
    """Schema for voice command updates."""
    status: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class VoiceCommandInDB(VoiceCommandBase, TimestampSchema):
    """Schema for voice command in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class VoiceCommandResponse(VoiceCommandInDB):
    """Schema for voice command response."""
    user: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None

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

class VoiceCommandFilter(BaseSchema):
    """Schema for voice command filtering."""
    user_id: Optional[uuid.UUID] = None
    action_type: Optional[str] = None
    status: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TimeRangeQuery(BaseModel):
    start_date: datetime = Field(..., description="Start date for analytics")
    end_date: datetime = Field(..., description="End date for analytics")

class MetricValue(BaseModel):
    value: float = Field(..., description="Metric value")
    change: float = Field(0, description="Change from previous period")
    trend: str = Field("neutral", description="Trend direction (up, down, neutral)")

class UserActivityMetrics(BaseModel):
    total_users: int = Field(0, description="Total number of users")
    active_users: int = Field(0, description="Number of active users")
    new_users: int = Field(0, description="Number of new users")
    returning_users: int = Field(0, description="Number of returning users")
    average_session_duration: float = Field(0, description="Average session duration in seconds")
    top_actions: List[Dict[str, Any]] = Field([], description="Top user actions")

class ContentMetrics(BaseModel):
    total_views: int = Field(0, description="Total number of views")
    unique_views: int = Field(0, description="Number of unique views")
    average_time_spent: float = Field(0, description="Average time spent in seconds")
    engagement_rate: float = Field(0, description="Engagement rate as percentage")
    top_content: List[Dict[str, Any]] = Field([], description="Top performing content")

class AnalyticsResponse(BaseModel):
    user_metrics: UserActivityMetrics
    content_metrics: ContentMetrics
    time_period: str
    last_updated: datetime

class UserActivityResponse(BaseModel):
    user_id: int
    username: str
    activity_count: int
    last_active: datetime
    top_actions: List[Dict[str, Any]]
    session_duration: float

class ContentAnalyticsResponse(BaseModel):
    content_type: Optional[str]
    total_items: int
    total_views: int
    total_engagement: int
    average_time_spent: float
    top_performers: List[Dict[str, Any]]
    trends: Dict[str, List[Dict[str, Any]]] 