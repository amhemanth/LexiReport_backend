from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid

class ReportCreate(BaseModel):
    title: str
    description: Optional[str] = None
    report_type_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ReportResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    file_path: str
    file_type: str
    file_size: int
    report_type_id: Optional[uuid.UUID]
    status_id: Optional[uuid.UUID]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportTypeResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    supported_formats: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportStatusResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportVersionResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    version_number: int
    file_path: str
    changes_description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportInsightResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    insight_type: str
    content: str
    confidence_score: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportShareResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    shared_with: uuid.UUID
    permission: str
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 