from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Index, UniqueConstraint, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base

class UserRole(Base):
    """Model for user-role relationships."""
    __tablename__ = "user_roles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="user_roles",
        passive_deletes=True
    )
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="user_roles",
        passive_deletes=True
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_user_roles",
        passive_deletes=True
    )

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
        Index('ix_user_roles_user', 'user_id'),
        Index('ix_user_roles_role', 'role_id'),
        Index('ix_user_roles_primary', 'is_primary'),
    )

    def __repr__(self) -> str:
        return f"<UserRole {self.user_id}:{self.role_id}>" 