from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import uuid

class BIConnectionCreate(BaseModel):
    platform_type: str
    credentials: Dict[str, Any]
    name: Optional[str] = None

class BIConnectionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    platform_type: str
    credentials: Dict[str, Any]
    name: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class BIDashboardResponse(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    name: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    class Config:
        orm_mode = True

class BIReportResponse(BaseModel):
    id: uuid.UUID
    dashboard_id: uuid.UUID
    name: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    class Config:
        orm_mode = True

class SyncJobResponse(BaseModel):
    id: uuid.UUID
    connection_id: uuid.UUID
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    details: Optional[Dict[str, Any]]
    class Config:
        orm_mode = True 