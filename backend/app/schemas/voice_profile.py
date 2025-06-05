from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import uuid

class VoiceProfileCreate(BaseModel):
    voice_id: str
    voice_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = True

class VoiceProfileUpdate(BaseModel):
    voice_id: Optional[str] = None
    voice_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class VoiceProfileResponse(BaseModel):
    id: int
    user_id: uuid.UUID
    voice_id: str
    voice_settings: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class AudioCacheResponse(BaseModel):
    id: int
    voice_profile_id: int
    content_hash: str
    audio_path: str
    created_at: datetime
    class Config:
        orm_mode = True 