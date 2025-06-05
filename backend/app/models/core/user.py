from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid

from sqlalchemy import String, Boolean, Enum as SQLEnum, Index, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class UserRole(str, PyEnum):
    """User role enum"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class User(Base):
    """User model"""
    
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships with cascade rules
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="user_permission",
        back_populates="users"
    )
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    voice_profile: Mapped[Optional["VoiceProfile"]] = relationship(
        "VoiceProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    password: Mapped[Optional["Password"]] = relationship(
        "Password",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # New relationships
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notification_preferences: Mapped[List["NotificationPreference"]] = relationship(
        "NotificationPreference",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    files: Mapped[List["FileStorage"]] = relationship(
        "FileStorage",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    mentioned_in_comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        secondary="comment_mentions",
        back_populates="mentions"
    )
    entity_tags: Mapped[List["EntityTag"]] = relationship(
        "EntityTag",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Add composite index for common queries
    __table_args__ = (
        Index('idx_user_email_username', 'email', 'username'),
        Index('idx_user_role', 'role'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>" 