from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from sqlalchemy import String, ForeignKey, Float, JSON, Column, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.models.core.user import User


class VoiceProfile(Base):
    """Voice profile model"""
    
    __tablename__ = "voice_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    voice_id: Mapped[str] = mapped_column(String, nullable=False)
    voice_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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

    id = Column(Integer, primary_key=True, index=True)
    voice_profile_id: Mapped[int] = mapped_column(ForeignKey("voice_profiles.id", ondelete="CASCADE"), nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    audio_path: Mapped[str] = mapped_column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    voice_profile: Mapped["VoiceProfile"] = relationship("VoiceProfile", back_populates="audio_cache")
    
    def __repr__(self) -> str:
        return f"<AudioCache {self.content_hash}>" 