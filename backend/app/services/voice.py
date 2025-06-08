from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.voice import voice_profile_repository, audio_cache_repository
from app.models.media.voice import VoiceProfile, AudioCache
from app.schemas.voice import (
    VoiceProfileCreate, VoiceProfileUpdate,
    AudioCacheCreate, AudioCacheUpdate,
    TextToSpeechRequest, TextToSpeechResponse
)
from app.core.exceptions import NotFoundException, PermissionException

class VoiceService:
    """Service for managing voice profiles and audio caching."""

    def get_voice_profiles_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfile]:
        """Get voice profiles by user."""
        return voice_profile_repository.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

    def get_active_voice_profiles(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfile]:
        """Get active voice profiles."""
        return voice_profile_repository.get_active(db, skip=skip, limit=limit)

    def get_voice_profiles_by_language(
        self, db: Session, *, language: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfile]:
        """Get voice profiles by language."""
        return voice_profile_repository.get_by_language(
            db, language=language, skip=skip, limit=limit
        )

    def create_voice_profile(
        self, db: Session, *, obj_in: VoiceProfileCreate
    ) -> VoiceProfile:
        """Create a new voice profile."""
        return voice_profile_repository.create(db, obj_in=obj_in)

    def update_voice_profile(
        self, db: Session, *, profile_id: str, obj_in: VoiceProfileUpdate
    ) -> VoiceProfile:
        """Update a voice profile."""
        profile = voice_profile_repository.get(db, id=profile_id)
        if not profile:
            raise NotFoundException("Voice profile not found")
        return voice_profile_repository.update(db, db_obj=profile, obj_in=obj_in)

    def delete_voice_profile(self, db: Session, *, profile_id: str) -> None:
        """Delete a voice profile."""
        profile = voice_profile_repository.get(db, id=profile_id)
        if not profile:
            raise NotFoundException("Voice profile not found")
        voice_profile_repository.remove(db, id=profile_id)

    def get_audio_cache_by_profile(
        self, db: Session, *, voice_profile_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[AudioCache]:
        """Get audio cache entries by voice profile."""
        return audio_cache_repository.get_by_voice_profile(
            db, voice_profile_id=voice_profile_id,
            skip=skip, limit=limit
        )

    def get_audio_cache_by_hash(
        self, db: Session, *, content_hash: str
    ) -> Optional[AudioCache]:
        """Get audio cache entry by content hash."""
        return audio_cache_repository.get_by_hash(
            db, content_hash=content_hash
        )

    def create_audio_cache(
        self, db: Session, *, obj_in: AudioCacheCreate
    ) -> AudioCache:
        """Create a new audio cache entry."""
        return audio_cache_repository.create(db, obj_in=obj_in)

    def update_audio_cache(
        self, db: Session, *, cache_id: str, obj_in: AudioCacheUpdate
    ) -> AudioCache:
        """Update an audio cache entry."""
        cache = audio_cache_repository.get(db, id=cache_id)
        if not cache:
            raise NotFoundException("Audio cache entry not found")
        return audio_cache_repository.update(db, db_obj=cache, obj_in=obj_in)

    def delete_audio_cache(self, db: Session, *, cache_id: str) -> None:
        """Delete an audio cache entry."""
        cache = audio_cache_repository.get(db, id=cache_id)
        if not cache:
            raise NotFoundException("Audio cache entry not found")
        audio_cache_repository.remove(db, id=cache_id)

    async def text_to_speech(
        self, db: Session, *, request: TextToSpeechRequest
    ) -> TextToSpeechResponse:
        """Convert text to speech using the specified voice profile."""
        # Get voice profile
        profile = voice_profile_repository.get(db, id=request.voice_profile_id)
        if not profile:
            raise NotFoundException("Voice profile not found")

        # Check if we have a cached version
        cache = audio_cache_repository.get_by_hash(
            db, content_hash=request.content_hash
        )
        if cache:
            return TextToSpeechResponse(
                audio_url=cache.audio_url,
                duration=cache.duration,
                size=cache.size,
                format=cache.format
            )

        # TODO: Implement actual text-to-speech conversion
        # This would typically involve calling an external TTS service
        # and storing the result in the audio cache

        raise NotImplementedError("Text-to-speech conversion not implemented")

# Create service instance
voice_service = VoiceService() 