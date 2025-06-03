from sqlalchemy import Boolean, Column, String, Integer
from app.db.base_class import Base
from app.models.base import TimestampMixin

class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True) 