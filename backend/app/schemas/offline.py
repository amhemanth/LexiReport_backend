from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
import uuid

class OfflineContentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content_type: str
    content_data: Dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SyncQueueResponse(BaseModel):
    id: uuid.UUID
    job_type: str
    status: str
    payload: Optional[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class ProcessingJobResponse(BaseModel):
    id: uuid.UUID
    job_type: str
    status: str
    details: Optional[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True) 