from typing import Optional, List
from sqlalchemy import String, ForeignKey, Text, Table, Index, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.base_class import Base


class Permission(Base):
    """Model for system permissions."""
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    user_permissions: Mapped[List["UserPermission"]] = relationship(
        "UserPermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        viewonly=True,
        foreign_keys="[RolePermission.role_id, RolePermission.permission_id]"
    )
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_permissions",
        back_populates="permissions",
        viewonly=True,
        foreign_keys="[UserPermission.user_id, UserPermission.permission_id]"
    )

    # Indexes
    __table_args__ = (
        UniqueConstraint('name', name='uq_permission_name'),
        Index("ix_permissions_name", "name"),
        Index("ix_permissions_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


class Role(Base):
    """Model for user roles."""
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        viewonly=True,
        foreign_keys="[RolePermission.role_id, RolePermission.permission_id]"
    )
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        viewonly=True,
        foreign_keys="[UserRole.user_id, UserRole.role_id]"
    )

    # Indexes
    __table_args__ = (
        UniqueConstraint('name', name='uq_role_name'),
        Index("ix_roles_name", "name"),
        Index("ix_roles_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class RolePermission(Base):
    """Model for role-permission relationships."""
    __tablename__ = "role_permissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="role_permissions",
        passive_deletes=True
    )
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="role_permissions",
        passive_deletes=True
    )

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
        Index('ix_role_permissions_role', 'role_id'),
        Index('ix_role_permissions_permission', 'permission_id'),
    )

    def __repr__(self) -> str:
        return f"<RolePermission {self.role_id}:{self.permission_id}>" 