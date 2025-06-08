from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseSchema, TimestampSchema
from app.models.files import FileType, FileStatus, StorageType
import uuid

class FileBase(BaseSchema):
    """Base file schema."""
    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: FileType = Field(..., description="Type of file")
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None
    storage_type: StorageType = Field(default=StorageType.LOCAL, description="Storage type for the file")

class FileCreate(FileBase):
    """Schema for file creation."""
    pass

class FileUpdate(BaseSchema):
    """Schema for file updates."""
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[FileStatus] = None

class FileInDB(FileBase, TimestampSchema):
    """Schema for file in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    file_path: str
    file_size: int
    mime_type: str
    status: FileStatus = FileStatus.PENDING
    version: int = 1
    storage_path: Optional[str] = None

class FileResponse(FileInDB):
    """Schema for file response."""
    download_url: Optional[str] = None
    preview_url: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class FileList(BaseSchema):
    """Schema for paginated file list."""
    items: List[FileResponse]
    total: int
    page: int
    size: int
    pages: int

class FileUpload(BaseSchema):
    """Schema for file upload."""
    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: FileType
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None

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

class FileMetadataBase(BaseSchema):
    """Base file metadata schema."""
    key: str = Field(..., min_length=1, max_length=100)
    value: Any

class FileMetadataCreate(FileMetadataBase):
    """Schema for file metadata creation."""
    file_id: uuid.UUID

class FileMetadataUpdate(BaseSchema):
    """Schema for file metadata updates."""
    value: Any

class FileMetadataInDB(FileMetadataBase, TimestampSchema):
    """Schema for file metadata in database."""
    id: uuid.UUID
    file_id: uuid.UUID

class FileMetadataResponse(FileMetadataInDB):
    """Schema for file metadata response."""
    pass

class FileVersionBase(BaseSchema):
    """Base file version schema."""
    version: int = Field(..., ge=1)
    file_path: str
    file_size: int
    mime_type: str

class FileVersionCreate(FileVersionBase):
    """Schema for file version creation."""
    file_id: uuid.UUID

class FileVersionInDB(FileVersionBase, TimestampSchema):
    """Schema for file version in database."""
    id: uuid.UUID
    file_id: uuid.UUID

class FileVersionResponse(FileVersionInDB):
    """Schema for file version response."""
    pass

class FileVersionList(BaseSchema):
    """Schema for paginated file version list."""
    items: List[FileVersionResponse]
    total: int
    page: int
    size: int
    pages: int 