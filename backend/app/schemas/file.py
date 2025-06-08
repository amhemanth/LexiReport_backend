from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
from app.models.files import FileType, FileStatus, StorageType
import uuid

class FileBase(BaseSchema):
    """Base file schema."""
    filename: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_type: FileType
    storage_type: StorageType
    file_size: int
    mime_type: str
    status: FileStatus = FileStatus.PENDING
    metadata: Optional[Dict[str, Any]] = None
    is_public: bool = False

class FileCreate(FileBase):
    """Schema for file creation."""
    pass

class FileUpdate(FileBase):
    """Schema for file updates."""
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    file_type: Optional[FileType] = None
    status: Optional[FileStatus] = None
    is_public: Optional[bool] = None

class FileInDB(FileBase, TimestampSchema):
    """Schema for file in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    file_path: str
    storage_path: str
    checksum: Optional[str] = None

class FileResponse(FileInDB):
    """Schema for file response."""
    user: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None

class FileList(BaseSchema):
    """Schema for paginated file list."""
    items: List[FileResponse]
    total: int
    page: int
    size: int
    pages: int

class FileUploadResponse(BaseSchema):
    """Schema for file upload response."""
    file_id: uuid.UUID
    upload_url: str
    fields: Dict[str, str]
    expires_in: int

class FileDownloadResponse(BaseSchema):
    """Schema for file download response."""
    file_id: uuid.UUID
    download_url: str
    expires_in: int

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