from typing import Optional, List, Dict, Any
from pydantic import Field
from .base import BaseSchema, TimestampSchema
import uuid

class VoiceProfileBase(BaseSchema):
    """Base voice profile schema."""
    language: str = Field(..., description="Preferred language for voice interactions")
    voice_id: Optional[str] = Field(None, description="Selected voice ID for text-to-speech")
    settings: Optional[Dict[str, Any]] = Field(None, description="Voice profile settings")

class VoiceProfileCreate(VoiceProfileBase):
    """Schema for voice profile creation."""
    pass

class VoiceProfileUpdate(VoiceProfileBase):
    """Schema for voice profile updates."""
    language: Optional[str] = None
    voice_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class VoiceProfileInDB(VoiceProfileBase, TimestampSchema):
    """Schema for voice profile in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class VoiceProfileResponse(VoiceProfileInDB):
    """Schema for voice profile response."""
    pass

class AudioCacheBase(BaseSchema):
    """Base audio cache schema."""
    content_hash: str
    audio_format: str
    duration: float
    file_path: str

class AudioCacheCreate(AudioCacheBase):
    """Schema for audio cache creation."""
    pass

class AudioCacheUpdate(BaseSchema):
    """Schema for audio cache updates."""
    audio_format: Optional[str] = None
    duration: Optional[float] = None
    file_path: Optional[str] = None

class AudioCacheInDB(AudioCacheBase, TimestampSchema):
    """Schema for audio cache in database."""
    id: uuid.UUID

class AudioCacheResponse(AudioCacheInDB):
    """Schema for audio cache response."""
    pass

class TextToSpeechRequest(BaseSchema):
    """Schema for text-to-speech request."""
    text: str
    voice_id: Optional[str] = None
    language: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class TextToSpeechResponse(BaseSchema):
    """Schema for text-to-speech response."""
    audio_url: str
    duration: float
    metadata: Optional[Dict[str, Any]] = None

class VoiceCommandBase(BaseSchema):
    """Base voice command schema."""
    command_text: str = Field(..., description="The voice command text")
    action_type: str = Field(..., description="Type of action to perform")
    status: str = Field(..., description="Current status of the command")
    entity_type: Optional[str] = Field(None, description="Type of entity this command is related to")
    entity_id: Optional[uuid.UUID] = Field(None, description="ID of the related entity")
    meta_data: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class VoiceCommandCreate(VoiceCommandBase):
    """Schema for voice command creation."""
    pass

class VoiceCommandUpdate(BaseSchema):
    """Schema for voice command updates."""
    command_text: Optional[str] = None
    action_type: Optional[str] = None
    status: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    meta_data: Optional[Dict[str, Any]] = None

class VoiceCommandInDB(VoiceCommandBase, TimestampSchema):
    """Schema for voice command in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class VoiceCommandResponse(VoiceCommandInDB):
    """Schema for voice command response."""
    pass

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

class VoiceCommandList(BaseSchema):
    """Schema for paginated voice command list."""
    items: List[VoiceCommandResponse]
    total: int
    page: int
    size: int
    pages: int 