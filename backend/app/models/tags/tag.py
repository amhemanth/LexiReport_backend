from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Integer, Index, UniqueConstraint, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign, remote
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base_class import Base


class Tag(Base):
    """Tag model for managing tags."""
    __tablename__ = "tags"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color code
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_tag_name', 'name'),
        Index('idx_tag_system', 'is_system'),
        Index('idx_tag_created', 'created_at'),
    )

    # Relationships
    entities: Mapped[List["EntityTag"]] = relationship(
        "EntityTag",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class EntityTag(Base):
    """Model for entity tags."""
    __tablename__ = "entity_tags"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    tag_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("tags.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True
    )
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tag: Mapped["Tag"] = relationship(
        "Tag", 
        back_populates="entities",
        passive_deletes=True
    )
    user: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="entity_tags",
        passive_deletes=True
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        primaryjoin="and_(foreign(EntityTag.entity_type) == 'report', foreign(EntityTag.entity_id) == Report.id)",
        back_populates="tags",
        passive_deletes=True
    )

    # Indexes
    __table_args__ = (
        Index("ix_entity_tags_entity_type", "entity_type"),
        Index("ix_entity_tags_entity_id", "entity_id"),
        Index("ix_entity_tags_tag_id", "tag_id"),
        Index("ix_entity_tags_user_id", "user_id"),
        Index("ix_entity_tags_created", "created_at"),
        UniqueConstraint("entity_type", "entity_id", "tag_id", name="uq_entity_tags_entity_tag"),
    )

    def __repr__(self) -> str:
        return f"<EntityTag(entity_type='{self.entity_type}', entity_id={self.entity_id}, tag_id={self.tag_id})>" 