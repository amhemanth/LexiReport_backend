from typing import Optional, Dict, Any
from datetime import time
from sqlalchemy import String, ForeignKey, JSON, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class UserPreferences(Base):
    """User preferences model including notification settings."""
    
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    theme: Mapped[str] = mapped_column(String, default="light")
    language: Mapped[str] = mapped_column(String, default="en")
    timezone: Mapped[str] = mapped_column(String, default="UTC")
    notification_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    display_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    accessibility_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Notification settings
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_frequency: Mapped[str] = mapped_column(String(50), default="immediate")
    quiet_hours_start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    quiet_hours_end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferences {self.user_id}>" 