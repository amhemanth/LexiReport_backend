from sqlalchemy.orm import Session
from app.repositories.voice import voice_profile_repository, audio_cache_repository
from app.models.media.voice import VoiceProfile, AudioCache
from app.schemas.voice_profile import VoiceProfileCreate, VoiceProfileUpdate
from typing import Optional
import uuid

class VoiceService:
    def get_profile(self, db: Session, user_id: uuid.UUID) -> Optional[VoiceProfile]:
        return voice_profile_repository.get_by_user(db, user_id)

    def create_profile(self, db: Session, user_id: uuid.UUID, obj_in: VoiceProfileCreate) -> VoiceProfile:
        return voice_profile_repository.create(db, user_id, obj_in.voice_id, obj_in.voice_settings)

    def update_profile(self, db: Session, profile_id: int, obj_in: VoiceProfileUpdate) -> Optional[VoiceProfile]:
        profile = voice_profile_repository.get(db, profile_id)
        if not profile:
            return None
        return voice_profile_repository.update(db, profile, obj_in.dict(exclude_unset=True))

    def delete_profile(self, db: Session, profile_id: int) -> None:
        profile = voice_profile_repository.get(db, profile_id)
        if profile:
            voice_profile_repository.delete(db, profile)

    # AudioCache methods and TTS fallback logic can be added here

voice_service = VoiceService() 