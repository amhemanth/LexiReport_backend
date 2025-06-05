from typing import Optional
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.core.user import User


class Password(Base):
    """Password model"""
    
    __tablename__ = "passwords"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="password")
    
    def __repr__(self) -> str:
        return f"<Password {self.user_id}>" 