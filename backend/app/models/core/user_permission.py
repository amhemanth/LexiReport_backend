from typing import Optional
from sqlalchemy import ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.base_class import Base


class UserPermission(Base):
    """Model for user-permission relationships."""
    
    __tablename__ = "user_permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="user_permissions",
        passive_deletes=True
    )
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="user_permissions",
        passive_deletes=True
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_user_permissions",
        passive_deletes=True
    )

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id', name='uq_user_permission'),
        Index('ix_user_permissions_user', 'user_id'),
        Index('ix_user_permissions_permission', 'permission_id'),
        Index('ix_user_permissions_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<UserPermission {self.user_id}:{self.permission_id}>" 