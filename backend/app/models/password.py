from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import uuid

class Password(Base):
    __tablename__ = "passwords"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    hashed_password = Column(String, nullable=False)
    password_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="passwords") 