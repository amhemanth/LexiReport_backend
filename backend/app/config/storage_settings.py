from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class StorageSettings(BaseSettings):
    """File storage settings."""
    
    # Upload settings
    UPLOAD_DIR: str = Field(
        default="uploads",
        description="Directory for storing uploaded files"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum file upload size in bytes"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["pdf", "docx", "xlsx", "csv", "txt"],
        description="Allowed file extensions for upload"
    )
    
    # Cache settings
    CACHE_DIR: str = Field(
        default=".cache",
        description="Directory for caching files"
    )
    CACHE_TTL: int = Field(
        default=3600,  # 1 hour
        description="Cache time-to-live in seconds"
    )
    
    model_config = ConfigDict(case_sensitive=True, extra="allow", from_attributes=True, env_file='.env')


def get_storage_settings() -> StorageSettings:
    return StorageSettings() 