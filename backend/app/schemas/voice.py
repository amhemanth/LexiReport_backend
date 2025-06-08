from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
import uuid

class VoiceProfileBase(BaseSchema):
    """Base voice profile schema."""
    user_id: uuid.UUID
    voice_id: str
    voice_name: str
    language: str
    accent: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True

class VoiceProfileCreate(VoiceProfileBase):
    """Schema for voice profile creation."""
    pass

class VoiceProfileUpdate(VoiceProfileBase):
    """Schema for voice profile updates."""
    voice_name: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None

class VoiceProfileInDB(VoiceProfileBase, TimestampSchema):
    """Schema for voice profile in database."""
    id: uuid.UUID

class VoiceProfileResponse(VoiceProfileInDB):
    """Schema for voice profile response."""
    user: Optional[Dict[str, Any]] = None

class AudioCacheBase(BaseSchema):
    """Base audio cache schema."""
    user_id: uuid.UUID
    text: str
    voice_id: str
    audio_format: str
    duration: float
    file_path: str
    file_size: int
    metadata: Optional[Dict[str, Any]] = None

class AudioCacheCreate(AudioCacheBase):
    """Schema for audio cache creation."""
    pass

class AudioCacheInDB(AudioCacheBase, TimestampSchema):
    """Schema for audio cache in database."""
    id: uuid.UUID

class AudioCacheResponse(AudioCacheInDB):
    """Schema for audio cache response."""
    user: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None

class VoiceProfileList(BaseSchema):
    """Schema for paginated voice profile list."""
    items: List[VoiceProfileResponse]
    total: int
    page: int
    size: int
    pages: int

class AudioCacheList(BaseSchema):
    """Schema for paginated audio cache list."""
    items: List[AudioCacheResponse]
    total: int
    page: int
    size: int
    pages: int

class TextToSpeechRequest(BaseSchema):
    """Schema for text to speech request."""
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str
    audio_format: str = Field(..., pattern="^(mp3|wav|ogg)$")
    speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    pitch: Optional[float] = Field(None, ge=0.5, le=2.0)
    metadata: Optional[Dict[str, Any]] = None

class TextToSpeechResponse(BaseSchema):
    """Schema for text to speech response."""
    audio_url: str
    duration: float
    file_size: int
    expires_in: int 