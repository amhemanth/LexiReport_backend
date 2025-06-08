from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

class FileMetadataResponse(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    key: str
    value: Any
    model_config = ConfigDict(from_attributes=True)

class FileVersionResponse(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    version: int
    file_path: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 