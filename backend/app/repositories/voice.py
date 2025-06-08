from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.media.voice import VoiceProfile, AudioCache
from app.schemas.voice import (
    VoiceProfileCreate, VoiceProfileUpdate,
    AudioCacheCreate, AudioCacheUpdate
)
from .base import BaseRepository

class VoiceProfileRepository(
    BaseRepository[VoiceProfile, VoiceProfileCreate, VoiceProfileUpdate]
):
    """Repository for VoiceProfile model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfile]:
        """Get voice profiles by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_active(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfile]:
        """Get active voice profiles."""
        return self.get_multi_by_field(
            db, field="is_active", value=True, skip=skip, limit=limit
        )

    def get_by_language(
        self, db: Session, *, language: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfile]:
        """Get voice profiles by language."""
        return self.get_multi_by_field(
            db, field="language", value=language, skip=skip, limit=limit
        )

class AudioCacheRepository(
    BaseRepository[AudioCache, AudioCacheCreate, AudioCacheUpdate]
):
    """Repository for AudioCache model."""

    def get_by_voice_profile(
        self, db: Session, *, voice_profile_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[AudioCache]:
        """Get audio cache entries by voice profile."""
        return self.get_multi_by_field(
            db, field="voice_profile_id", value=voice_profile_id,
            skip=skip, limit=limit
        )

    def get_by_hash(
        self, db: Session, *, content_hash: str
    ) -> Optional[AudioCache]:
        """Get audio cache entry by content hash."""
        return self.get_by_field(db, field="content_hash", value=content_hash)

# Create repository instances
voice_profile_repository = VoiceProfileRepository(VoiceProfile)
audio_cache_repository = AudioCacheRepository(AudioCache) 