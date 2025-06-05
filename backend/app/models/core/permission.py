from typing import Optional, List
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class Permission(Base):
    """Permission model for role-based access control"""
    
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    user_permissions: Mapped[List["UserPermission"]] = relationship(
        "UserPermission",
        back_populates="permission",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>" 