from sqlalchemy import Boolean, Column, String, Integer, DateTime
from app.db.base_class import Base
from app.models.base import TimestampMixin
from datetime import datetime, timezone

class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    password_updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False) 