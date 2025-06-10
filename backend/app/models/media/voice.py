from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from sqlalchemy import String, ForeignKey, Float, JSON, Column, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class VoiceProfile(Base):
    """Voice profile model"""
    
    __tablename__ = "voice_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    voice_id: Mapped[str] = mapped_column(String, nullable=False)
    voice_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="voice_profile")
    audio_cache: Mapped[List["AudioCache"]] = relationship(
        "AudioCache",
        back_populates="voice_profile",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<VoiceProfile {self.voice_id}>"


class AudioCache(Base):
    """Audio cache model"""
    
    __tablename__ = "audio_cache"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    voice_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("voice_profiles.id", ondelete="CASCADE"), nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    audio_path: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    voice_profile: Mapped["VoiceProfile"] = relationship("VoiceProfile", back_populates="audio_cache")
    
    def __repr__(self) -> str:
        return f"<AudioCache {self.content_hash}>" 