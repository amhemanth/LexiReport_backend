from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uuid

class FileUpload(BaseModel):
    file_name: str
    file_type: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class FileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    file_type: str
    file_path: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class FileMetadataResponse(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    key: str
    value: Any
    class Config:
        orm_mode = True

class FileVersionResponse(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    version: int
    file_path: str
    created_at: datetime
    class Config:
        orm_mode = True 