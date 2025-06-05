from sqlalchemy.orm import Session
from app.models.media.voice import VoiceProfile, AudioCache
from typing import Optional, List
import uuid

class VoiceProfileRepository:
    def get(self, db: Session, profile_id: int) -> Optional[VoiceProfile]:
        return db.query(VoiceProfile).filter(VoiceProfile.id == profile_id).first()

    def get_by_user(self, db: Session, user_id: uuid.UUID) -> Optional[VoiceProfile]:
        return db.query(VoiceProfile).filter(VoiceProfile.user_id == user_id, VoiceProfile.is_active == True).first()

    def create(self, db: Session, user_id: uuid.UUID, voice_id: str, voice_settings: dict) -> VoiceProfile:
        profile = VoiceProfile(user_id=user_id, voice_id=voice_id, voice_settings=voice_settings)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def update(self, db: Session, db_obj: VoiceProfile, update_data: dict) -> VoiceProfile:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: VoiceProfile) -> None:
        db.delete(db_obj)
        db.commit()

class AudioCacheRepository:
    def get_by_hash(self, db: Session, voice_profile_id: int, content_hash: str) -> Optional[AudioCache]:
        return db.query(AudioCache).filter(AudioCache.voice_profile_id == voice_profile_id, AudioCache.content_hash == content_hash).first()

    def create(self, db: Session, voice_profile_id: int, content_hash: str, audio_path: str) -> AudioCache:
        cache = AudioCache(voice_profile_id=voice_profile_id, content_hash=content_hash, audio_path=audio_path)
        db.add(cache)
        db.commit()
        db.refresh(cache)
        return cache

voice_profile_repository = VoiceProfileRepository()
audio_cache_repository = AudioCacheRepository() 