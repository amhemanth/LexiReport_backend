from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
from app.models.reports import ReportType, ReportStatus, ReportTypeCategory, AnalysisType, MetadataType
import uuid

class ReportBase(BaseSchema):
    """Base report schema with common attributes."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    type: ReportType = ReportType.STANDARD
    category: ReportTypeCategory = ReportTypeCategory.ANALYTICAL
    status: ReportStatus = ReportStatus.DRAFT
    is_public: bool = False
    is_archived: bool = False
    analysis_type: Optional[AnalysisType] = None
    analysis_data: Optional[Dict[str, Any]] = None
    metadata_type: Optional[MetadataType] = None
    metadata_data: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    template_id: Optional[uuid.UUID] = None

class ReportCreate(ReportBase):
    """Schema for report creation."""
    pass

class ReportUpdate(ReportBase):
    """Schema for report updates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    report_type: Optional[ReportType] = None
    report_type_category: Optional[ReportTypeCategory] = None
    status: Optional[ReportStatus] = None

class ReportInDB(ReportBase, TimestampSchema):
    """Schema for report in database."""
    id: uuid.UUID
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID] = None

class ReportResponse(ReportInDB):
    """Schema for report response."""
    creator: Optional[Dict[str, Any]] = None
    updater: Optional[Dict[str, Any]] = None

class ReportShareBase(BaseSchema):
    """Base report share schema."""
    report_id: uuid.UUID
    shared_with: uuid.UUID
    permission: str = Field(..., pattern="^(view|edit|admin)$")
    expires_at: Optional[datetime] = None

class ReportShareCreate(ReportShareBase):
    """Schema for report share creation."""
    pass

class ReportShareUpdate(BaseSchema):
    """Schema for report share updates."""
    permission: Optional[str] = Field(None, pattern="^(view|edit|admin)$")
    expires_at: Optional[datetime] = None

class ReportShareInDB(ReportShareBase, TimestampSchema):
    """Schema for report share in database."""
    id: uuid.UUID
    shared_by: uuid.UUID

class ReportShareResponse(ReportShareInDB):
    """Schema for report share response."""
    report: Optional[ReportResponse] = None
    sharer: Optional[Dict[str, Any]] = None
    sharee: Optional[Dict[str, Any]] = None

class ReportTemplateBase(BaseSchema):
    """Base report template schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_data: Dict[str, Any]
    report_type: ReportType
    report_type_category: ReportTypeCategory
    is_public: bool = False

class ReportTemplateCreate(ReportTemplateBase):
    """Schema for report template creation."""
    pass

class ReportTemplateUpdate(ReportTemplateBase):
    """Schema for report template updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    report_type: Optional[ReportType] = None
    report_type_category: Optional[ReportTypeCategory] = None

class ReportTemplateInDB(ReportTemplateBase, TimestampSchema):
    """Schema for report template in database."""
    id: uuid.UUID
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID] = None

class ReportTemplateResponse(ReportTemplateInDB):
    """Schema for report template response."""
    creator: Optional[Dict[str, Any]] = None
    updater: Optional[Dict[str, Any]] = None

class ReportScheduleBase(BaseSchema):
    """Base report schedule schema."""
    report_id: uuid.UUID
    schedule_type: str = Field(..., pattern="^(daily|weekly|monthly|custom)$")
    schedule_config: Dict[str, Any]
    is_active: bool = True
    recipients: List[uuid.UUID]

class ReportScheduleCreate(ReportScheduleBase):
    """Schema for report schedule creation."""
    pass

class ReportScheduleUpdate(ReportScheduleBase):
    """Schema for report schedule updates."""
    schedule_type: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|custom)$")
    is_active: Optional[bool] = None

class ReportScheduleInDB(ReportScheduleBase, TimestampSchema):
    """Schema for report schedule in database."""
    id: uuid.UUID
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID] = None

class ReportScheduleResponse(ReportScheduleInDB):
    """Schema for report schedule response."""
    report: Optional[ReportResponse] = None
    creator: Optional[Dict[str, Any]] = None
    updater: Optional[Dict[str, Any]] = None

class ReportExportBase(BaseSchema):
    """Base report export schema."""
    report_id: uuid.UUID
    export_format: str = Field(..., pattern="^(pdf|excel|csv|json)$")
    export_config: Optional[Dict[str, Any]] = None

class ReportExportCreate(ReportExportBase):
    """Schema for report export creation."""
    pass

class ReportExportUpdate(BaseSchema):
    """Schema for report export updates."""
    export_format: Optional[str] = Field(None, pattern="^(pdf|excel|csv|json)$")
    export_config: Optional[Dict[str, Any]] = None

class ReportExportInDB(ReportExportBase, TimestampSchema):
    """Schema for report export in database."""
    id: uuid.UUID
    created_by: uuid.UUID
    file_path: Optional[str] = None
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$")

class ReportExportResponse(ReportExportInDB):
    """Schema for report export response."""
    report: Optional[ReportResponse] = None
    creator: Optional[Dict[str, Any]] = None

class ReportList(BaseSchema):
    """Schema for paginated report list."""
    items: List[ReportResponse]
    total: int
    page: int
    size: int
    pages: int

class ReportTemplateList(BaseSchema):
    """Schema for paginated report template list."""
    items: List[ReportTemplateResponse]
    total: int
    page: int
    size: int
    pages: int

class ReportScheduleList(BaseSchema):
    """Schema for paginated report schedule list."""
    items: List[ReportScheduleResponse]
    total: int
    page: int
    size: int
    pages: int

class ReportExportList(BaseSchema):
    """Schema for paginated report export list."""
    items: List[ReportExportResponse]
    total: int
    page: int
    size: int
    pages: int

class ReportTypeResponse(BaseSchema):
    """Schema for report type response."""
    name: str
    description: Optional[str] = None
    category: ReportTypeCategory

class ReportStatusResponse(BaseSchema):
    """Schema for report status response."""
    name: str
    description: Optional[str] = None 