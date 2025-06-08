from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
import uuid

class OfflineContentBase(BaseSchema):
    """Base offline content schema."""
    content_type: str
    content_id: uuid.UUID
    sync_status: str = "pending"
    metadata: Optional[Dict[str, Any]] = None

class OfflineContentCreate(OfflineContentBase):
    """Schema for offline content creation."""
    pass

class OfflineContentUpdate(BaseSchema):
    """Schema for offline content updates."""
    sync_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    last_synced_at: Optional[datetime] = None
    sync_error: Optional[str] = None

class OfflineContentInDB(OfflineContentBase, TimestampSchema):
    """Schema for offline content in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    last_synced_at: Optional[datetime] = None
    sync_error: Optional[str] = None

class OfflineContentResponse(OfflineContentInDB):
    """Schema for offline content response."""
    pass

class SyncQueueBase(BaseSchema):
    """Base sync queue schema."""
    content_type: str
    content_id: uuid.UUID
    priority: int = 0
    metadata: Optional[Dict[str, Any]] = None

class SyncQueueCreate(SyncQueueBase):
    """Schema for sync queue creation."""
    pass

class SyncQueueUpdate(BaseSchema):
    """Schema for sync queue updates."""
    priority: Optional[int] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None
    last_attempt: Optional[datetime] = None
    error: Optional[str] = None

class SyncQueueInDB(SyncQueueBase, TimestampSchema):
    """Schema for sync queue in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    status: str = "pending"
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    error: Optional[str] = None

class SyncQueueResponse(SyncQueueInDB):
    """Schema for sync queue response."""
    pass

class ProcessingJobBase(BaseSchema):
    """Base processing job schema."""
    job_type: str
    content_id: uuid.UUID
    priority: int = 0
    parameters: Optional[Dict[str, Any]] = None

class ProcessingJobCreate(ProcessingJobBase):
    """Schema for processing job creation."""
    pass

class ProcessingJobUpdate(BaseSchema):
    """Schema for processing job updates."""
    priority: Optional[int] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ProcessingJobInDB(ProcessingJobBase, TimestampSchema):
    """Schema for processing job in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    status: str = "pending"
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ProcessingJobResponse(ProcessingJobInDB):
    """Schema for processing job response."""
    pass 