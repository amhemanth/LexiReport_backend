from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
from .base import BaseSchema, TimestampSchema
import uuid

class BIConnectionBase(BaseSchema):
    """Base BI connection schema."""
    platform_type: str = Field(..., description="Type of BI platform (e.g., 'powerbi', 'tableau')")
    credentials: Dict[str, Any] = Field(..., description="Connection credentials")
    name: Optional[str] = Field(None, description="Optional connection name")

class BIConnectionCreate(BIConnectionBase):
    """Schema for BI connection creation."""
    pass

class BIConnectionUpdate(BaseSchema):
    """Schema for BI connection updates."""
    credentials: Optional[Dict[str, Any]] = None
    name: Optional[str] = None

class BIConnectionInDB(BIConnectionBase, TimestampSchema):
    """Schema for BI connection in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class BIConnectionResponse(BIConnectionInDB):
    """Schema for BI connection response."""
    pass

class BIDashboardBase(BaseSchema):
    """Base BI dashboard schema."""
    connection_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=200)
    metadata: Optional[Dict[str, Any]] = None

class BIDashboardCreate(BIDashboardBase):
    """Schema for BI dashboard creation."""
    pass

class BIDashboardUpdate(BaseSchema):
    """Schema for BI dashboard updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    metadata: Optional[Dict[str, Any]] = None

class BIDashboardInDB(BIDashboardBase, TimestampSchema):
    """Schema for BI dashboard in database."""
    id: uuid.UUID

class BIDashboardResponse(BIDashboardInDB):
    """Schema for BI dashboard response."""
    pass

class BIReportBase(BaseSchema):
    """Base BI report schema."""
    dashboard_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=200)
    metadata: Optional[Dict[str, Any]] = None

class BIReportCreate(BIReportBase):
    """Schema for BI report creation."""
    pass

class BIReportUpdate(BaseSchema):
    """Schema for BI report updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    metadata: Optional[Dict[str, Any]] = None

class BIReportInDB(BIReportBase, TimestampSchema):
    """Schema for BI report in database."""
    id: uuid.UUID

class BIReportResponse(BIReportInDB):
    """Schema for BI report response."""
    pass

class SyncJobBase(BaseSchema):
    """Base sync job schema."""
    connection_id: uuid.UUID
    job_type: str = Field(..., description="Type of sync job (e.g., 'dashboard', 'report')")
    parameters: Optional[Dict[str, Any]] = None

class SyncJobCreate(SyncJobBase):
    """Schema for sync job creation."""
    pass

class SyncJobUpdate(BaseSchema):
    """Schema for sync job updates."""
    status: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None

class SyncJobInDB(SyncJobBase, TimestampSchema):
    """Schema for sync job in database."""
    id: uuid.UUID
    status: str = "pending"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    details: Optional[Dict[str, Any]] = None

class SyncJobResponse(SyncJobInDB):
    """Schema for sync job response."""
    pass

class BIConnectionList(BaseSchema):
    """Schema for paginated BI connection list."""
    items: List[BIConnectionResponse]
    total: int
    page: int
    size: int
    pages: int

class BIDashboardList(BaseSchema):
    """Schema for paginated BI dashboard list."""
    items: List[BIDashboardResponse]
    total: int
    page: int
    size: int
    pages: int

class BIReportList(BaseSchema):
    """Schema for paginated BI report list."""
    items: List[BIReportResponse]
    total: int
    page: int
    size: int
    pages: int

class SyncJobList(BaseSchema):
    """Schema for paginated sync job list."""
    items: List[SyncJobResponse]
    total: int
    page: int
    size: int
    pages: int

class BIIntegrationBase(BaseSchema):
    """Base BI integration schema."""
    name: str = Field(..., min_length=1, max_length=100)
    platform_type: str = Field(..., description="Type of BI platform (e.g., 'power_bi', 'tableau')")
    api_key: str = Field(..., min_length=1, max_length=255)
    api_secret: str = Field(..., min_length=1, max_length=255)
    base_url: str = Field(..., min_length=1, max_length=255)
    workspace_id: Optional[str] = Field(None, max_length=100)
    meta_data: Optional[Dict[str, Any]] = None
    is_active: bool = Field(default=True)
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[uuid.UUID] = None

class BIIntegrationCreate(BIIntegrationBase):
    """Schema for BI integration creation."""
    pass

class BIIntegrationUpdate(BaseSchema):
    """Schema for BI integration updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, min_length=1, max_length=255)
    api_secret: Optional[str] = Field(None, min_length=1, max_length=255)
    base_url: Optional[str] = Field(None, min_length=1, max_length=255)
    workspace_id: Optional[str] = Field(None, max_length=100)
    meta_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[uuid.UUID] = None

class BIIntegrationInDB(BIIntegrationBase, TimestampSchema):
    """Schema for BI integration in database."""
    id: uuid.UUID
    created_by: Optional[uuid.UUID] = None

class BIIntegrationResponse(BIIntegrationInDB):
    """Schema for BI integration response."""
    pass

class BIIntegrationList(BaseSchema):
    """Schema for paginated BI integration list."""
    items: List[BIIntegrationResponse]
    total: int
    page: int
    size: int
    pages: int 