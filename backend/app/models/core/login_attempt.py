from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid

from app.db.base_class import Base

class LoginAttempt(Base):
    """Model for tracking login attempts."""
    __tablename__ = "login_attempts"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="login_attempts",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<LoginAttempt(user_id={self.user_id}, success={self.success})>" 