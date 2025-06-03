from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationship
    user_permissions = relationship("UserPermission", back_populates="permission", cascade="all, delete-orphan") 