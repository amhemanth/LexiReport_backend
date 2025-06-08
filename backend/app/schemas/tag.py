from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseSchema, TimestampSchema
import uuid

class TagBase(BaseSchema):
    """Base tag schema with common attributes."""
    name: str = Field(..., min_length=1, max_length=50, description="Name of the tag")
    description: Optional[str] = Field(None, max_length=200, description="Description of the tag")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code for the tag")
    category: Optional[str] = Field(None, max_length=50, description="Category of the tag")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class TagCreate(TagBase):
    """Schema for tag creation."""
    pass

class TagUpdate(BaseSchema):
    """Schema for tag updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, max_length=7)
    category: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class TagInDB(TagBase, TimestampSchema):
    """Schema for tag in database."""
    id: uuid.UUID
    created_by: uuid.UUID
    is_active: bool = Field(default=True, description="Whether the tag is active")
    usage_count: int = Field(default=0, description="Number of times the tag is used")

class TagResponse(TagInDB):
    """Schema for tag response."""
    pass

class EntityTagBase(BaseSchema):
    """Base entity tag schema."""
    entity_type: str = Field(..., description="Type of entity being tagged")
    entity_id: uuid.UUID = Field(..., description="ID of the entity being tagged")
    tag_id: uuid.UUID = Field(..., description="ID of the tag")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class EntityTagCreate(EntityTagBase):
    """Schema for entity tag creation."""
    pass

class EntityTagUpdate(BaseSchema):
    """Schema for entity tag updates."""
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class EntityTagInDB(EntityTagBase, TimestampSchema):
    """Schema for entity tag in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool = Field(default=True, description="Whether the entity tag is active")

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

class EntityTagList(BaseSchema):
    """Schema for paginated entity tag list."""
    items: List[EntityTagResponse]
    total: int
    page: int
    size: int
    pages: int 