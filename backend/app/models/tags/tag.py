from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, Text, JSON, Boolean, DateTime, Integer, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class Tag(Base):
    """Tag model"""
    
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color code
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    entities: Mapped[List["EntityTag"]] = relationship(
        "EntityTag",
        back_populates="tag",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class EntityTag(Base):
    """Model for entity tags."""
    __tablename__ = "entity_tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tag: Mapped["Tag"] = relationship("Tag", back_populates="entity_tags")

    # Indexes
    __table_args__ = (
        Index("ix_entity_tags_entity_type", "entity_type"),
        Index("ix_entity_tags_entity_id", "entity_id"),
        Index("ix_entity_tags_tag_id", "tag_id"),
        UniqueConstraint("entity_type", "entity_id", "tag_id", name="uq_entity_tags_entity_tag"),
    )

    def __repr__(self) -> str:
        return f"<EntityTag(entity_type='{self.entity_type}', entity_id={self.entity_id}, tag_id={self.tag_id})>" 