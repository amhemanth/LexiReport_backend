from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class AISettings(BaseSettings):
    """AI service settings."""
    
    # Model settings
    MODEL_PATH: str = Field(
        default="models/whisper-base",
        description="Path to the Whisper model"
    )
    CACHE_DIR: str = Field(
        default=".cache",
        description="Directory for caching model files"
    )
    
    # Processing settings
    MAX_WORKERS: int = Field(
        default=4,
        description="Maximum number of worker processes"
    )
    BATCH_SIZE: int = Field(
        default=16,
        description="Batch size for processing"
    )
    
    # File settings
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["pdf", "docx", "xlsx", "csv", "txt"],
        description="Allowed file extensions for processing"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum file upload size in bytes"
    )
    
    # Voice settings
    DEFAULT_VOICE: str = Field(
        default="en-US-Neural2-F",
        description="Default voice for text-to-speech"
    )
    SUPPORTED_LANGUAGES: List[str] = Field(
        default=["en", "es", "fr", "de", "it"],
        description="Supported languages for voice generation"
    )
    
    # Cache settings
    CACHE_TTL: int = Field(
        default=3600,  # 1 hour
        description="Cache time-to-live in seconds"
    )
    
    model_config = ConfigDict(extra='allow', from_attributes=True, env_file='.env') 

def get_ai_settings() -> AISettings:
    return AISettings() 