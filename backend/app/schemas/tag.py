from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
import uuid

class TagBase(BaseSchema):
    """Base tag schema with common attributes."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, max_length=7)  # Hex color code

class TagCreate(TagBase):
    """Schema for tag creation."""
    pass

class TagUpdate(TagBase):
    """Schema for tag updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)

class TagInDB(TagBase, TimestampSchema):
    """Schema for tag in database."""
    id: uuid.UUID
    created_by: uuid.UUID

class TagResponse(TagInDB):
    """Schema for tag response."""
    pass

class EntityTagBase(BaseSchema):
    """Base entity tag schema."""
    entity_type: str
    entity_id: uuid.UUID
    tag_id: uuid.UUID

class EntityTagCreate(EntityTagBase):
    """Schema for entity tag creation."""
    pass

class EntityTagInDB(EntityTagBase, TimestampSchema):
    """Schema for entity tag in database."""
    id: uuid.UUID
    user_id: uuid.UUID

class EntityTagResponse(EntityTagInDB):
    """Schema for entity tag response."""
    tag: TagResponse

class TagList(BaseSchema):
    """Schema for paginated tag list."""
    items: List[TagResponse]
    total: int
    page: int
    size: int
    pages: int 