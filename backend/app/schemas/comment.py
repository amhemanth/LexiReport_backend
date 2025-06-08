from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, TimestampSchema
import uuid

class CommentBase(BaseSchema):
    """Base comment schema."""
    content: str = Field(..., min_length=1, max_length=1000)
    entity_type: str
    entity_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None

class CommentCreate(CommentBase):
    """Schema for comment creation."""
    pass

class CommentUpdate(CommentBase):
    """Schema for comment updates."""
    content: Optional[str] = Field(None, min_length=1, max_length=1000)

class CommentInDB(CommentBase, TimestampSchema):
    """Schema for comment in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    thread_id: uuid.UUID

class CommentResponse(CommentInDB):
    """Schema for comment response."""
    user: Optional[Dict[str, Any]] = None
    mentions: List[Dict[str, Any]] = []
    replies: List["CommentResponse"] = []

class CommentThreadBase(BaseSchema):
    """Base comment thread schema."""
    entity_type: str
    entity_id: uuid.UUID
    is_locked: bool = False
    metadata: Optional[Dict[str, Any]] = None

class CommentThreadCreate(CommentThreadBase):
    """Schema for comment thread creation."""
    pass

class CommentThreadUpdate(CommentThreadBase):
    """Schema for comment thread updates."""
    is_locked: Optional[bool] = None

class CommentThreadInDB(CommentThreadBase, TimestampSchema):
    """Schema for comment thread in database."""
    id: uuid.UUID
    created_by: uuid.UUID

class CommentThreadResponse(CommentThreadInDB):
    """Schema for comment thread response."""
    creator: Optional[Dict[str, Any]] = None
    comments: List[CommentResponse] = []

class CommentMentionBase(BaseSchema):
    """Base comment mention schema."""
    comment_id: uuid.UUID
    user_id: uuid.UUID

class CommentMentionCreate(CommentMentionBase):
    """Schema for comment mention creation."""
    pass

class CommentMentionInDB(CommentMentionBase, TimestampSchema):
    """Schema for comment mention in database."""
    id: uuid.UUID

class CommentMentionResponse(CommentMentionInDB):
    """Schema for comment mention response."""
    user: Optional[Dict[str, Any]] = None
    comment: Optional[CommentResponse] = None

class CommentList(BaseSchema):
    """Schema for paginated comment list."""
    items: List[CommentResponse]
    total: int
    page: int
    size: int
    pages: int

class CommentThreadList(BaseSchema):
    """Schema for paginated comment thread list."""
    items: List[CommentThreadResponse]
    total: int
    page: int
    size: int
    pages: int

class TagCreate(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 