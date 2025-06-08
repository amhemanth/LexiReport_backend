from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.voice import (
    voice_profile_repository,
    audio_cache_repository,
    voice_command_repository
)
from app.models.media.voice import VoiceProfile, AudioCache
from app.models.analytics.voice_command import VoiceCommand
from app.schemas.voice import (
    VoiceProfileCreate, VoiceProfileUpdate, VoiceProfileResponse,
    AudioCacheCreate, AudioCacheUpdate, AudioCacheResponse,
    TextToSpeechRequest, TextToSpeechResponse,
    VoiceCommandCreate, VoiceCommandUpdate, VoiceCommandResponse
)
from app.core.exceptions import NotFoundException, PermissionException
import uuid
import hashlib
import os
from datetime import datetime

class VoiceService:
    """Service for managing voice profiles, audio caching, and voice commands."""

    def get_voice_profiles_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfileResponse]:
        """Get voice profiles by user."""
        profiles = voice_profile_repository.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )
        return [VoiceProfileResponse.model_validate(p) for p in profiles]

    def get_active_voice_profiles(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfileResponse]:
        """Get active voice profiles."""
        profiles = voice_profile_repository.get_active(db, skip=skip, limit=limit)
        return [VoiceProfileResponse.model_validate(p) for p in profiles]

    def get_voice_profiles_by_language(
        self, db: Session, *, language: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceProfileResponse]:
        """Get voice profiles by language."""
        profiles = voice_profile_repository.get_by_language(
            db, language=language, skip=skip, limit=limit
        )
        return [VoiceProfileResponse.model_validate(p) for p in profiles]

    def create_voice_profile(
        self, db: Session, *, user_id: uuid.UUID, obj_in: VoiceProfileCreate
    ) -> VoiceProfileResponse:
        """Create a new voice profile."""
        profile = voice_profile_repository.create(
            db, obj_in=VoiceProfileCreate(**obj_in.dict(), user_id=user_id)
        )
        return VoiceProfileResponse.model_validate(profile)

    def update_voice_profile(
        self, db: Session, *, profile_id: uuid.UUID, obj_in: VoiceProfileUpdate
    ) -> VoiceProfileResponse:
        """Update a voice profile."""
        profile = voice_profile_repository.get(db, id=profile_id)
        if not profile:
            raise NotFoundException("Voice profile not found")
        updated = voice_profile_repository.update(db, db_obj=profile, obj_in=obj_in)
        return VoiceProfileResponse.model_validate(updated)

    def delete_voice_profile(self, db: Session, *, profile_id: uuid.UUID) -> None:
        """Delete a voice profile."""
        profile = voice_profile_repository.get(db, id=profile_id)
        if not profile:
            raise NotFoundException("Voice profile not found")
        voice_profile_repository.remove(db, id=profile_id)

    def get_audio_cache_by_profile(
        self, db: Session, *, voice_profile_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[AudioCacheResponse]:
        """Get audio cache entries by voice profile."""
        cache_entries = audio_cache_repository.get_by_voice_profile(
            db, voice_profile_id=voice_profile_id,
            skip=skip, limit=limit
        )
        return [AudioCacheResponse.model_validate(c) for c in cache_entries]

    def get_audio_cache_by_hash(
        self, db: Session, *, content_hash: str
    ) -> Optional[AudioCacheResponse]:
        """Get audio cache entry by content hash."""
        cache = audio_cache_repository.get_by_hash(db, content_hash=content_hash)
        return AudioCacheResponse.model_validate(cache) if cache else None

    def create_audio_cache(
        self, db: Session, *, obj_in: AudioCacheCreate
    ) -> AudioCacheResponse:
        """Create a new audio cache entry."""
        cache = audio_cache_repository.create(db, obj_in=obj_in)
        return AudioCacheResponse.model_validate(cache)

    def update_audio_cache(
        self, db: Session, *, cache_id: uuid.UUID, obj_in: AudioCacheUpdate
    ) -> AudioCacheResponse:
        """Update an audio cache entry."""
        cache = audio_cache_repository.get(db, id=cache_id)
        if not cache:
            raise NotFoundException("Audio cache entry not found")
        updated = audio_cache_repository.update(db, db_obj=cache, obj_in=obj_in)
        return AudioCacheResponse.model_validate(updated)

    def delete_audio_cache(self, db: Session, *, cache_id: uuid.UUID) -> None:
        """Delete an audio cache entry."""
        cache = audio_cache_repository.get(db, id=cache_id)
        if not cache:
            raise NotFoundException("Audio cache entry not found")
        audio_cache_repository.remove(db, id=cache_id)

    def create_voice_command(
        self, db: Session, *, user_id: uuid.UUID, obj_in: VoiceCommandCreate
    ) -> VoiceCommandResponse:
        """Create a new voice command."""
        command = voice_command_repository.create(
            db, obj_in=VoiceCommandCreate(**obj_in.dict(), user_id=user_id)
        )
        return VoiceCommandResponse.model_validate(command)

    def get_voice_commands_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[VoiceCommandResponse]:
        """Get voice commands by user."""
        commands = voice_command_repository.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )
        return [VoiceCommandResponse.model_validate(c) for c in commands]

    def get_voice_commands_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceCommandResponse]:
        """Get voice commands by status."""
        commands = voice_command_repository.get_by_status(
            db, status=status, skip=skip, limit=limit
        )
        return [VoiceCommandResponse.model_validate(c) for c in commands]

    def get_voice_commands_by_action_type(
        self, db: Session, *, action_type: str, skip: int = 0, limit: int = 100
    ) -> List[VoiceCommandResponse]:
        """Get voice commands by action type."""
        commands = voice_command_repository.get_by_action_type(
            db, action_type=action_type, skip=skip, limit=limit
        )
        return [VoiceCommandResponse.model_validate(c) for c in commands]

    async def text_to_speech(
        self, db: Session, *, request: TextToSpeechRequest
    ) -> TextToSpeechResponse:
        """Convert text to speech using the specified voice profile."""
        # Get voice profile
        profile = voice_profile_repository.get(db, id=request.voice_profile_id)
        if not profile:
            raise NotFoundException("Voice profile not found")

        # Generate content hash
        content_hash = hashlib.sha256(
            f"{request.text}:{request.voice_id}:{request.language}".encode()
        ).hexdigest()

        # Check if we have a cached version
        cache = audio_cache_repository.get_by_hash(db, content_hash=content_hash)
        if cache:
            return TextToSpeechResponse(
                audio_url=cache.file_path,
                duration=cache.duration,
                metadata={
                    "cached": True,
                    "cache_id": str(cache.id),
                    "generated_at": cache.created_at.isoformat()
                }
            )

        # TODO: Implement actual text-to-speech conversion
        # This would typically involve calling an external TTS service
        # and storing the result in the audio cache

        raise NotImplementedError("Text-to-speech conversion not implemented")

# Create service instance
voice_service = VoiceService() 