from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseSchema, TimestampSchema
import uuid

class CommentBase(BaseSchema):
    """Base comment schema."""
    content: str
    entity_type: str
    entity_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None

class CommentCreate(CommentBase):
    """Schema for comment creation."""
    pass

class CommentUpdate(BaseSchema):
    """Schema for comment updates."""
    content: str
    metadata: Optional[Dict[str, Any]] = None

class CommentInDB(CommentBase, TimestampSchema):
    """Schema for comment in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    is_edited: bool = False
    is_deleted: bool = False

class CommentResponse(CommentInDB):
    """Schema for comment response."""
    user: Optional[Dict[str, Any]] = None
    replies_count: int = 0

class CommentThreadBase(BaseSchema):
    """Base comment thread schema."""
    entity_type: str
    entity_id: uuid.UUID
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CommentThreadCreate(CommentThreadBase):
    """Schema for comment thread creation."""
    pass

class CommentThreadUpdate(CommentThreadBase):
    """Schema for comment thread updates."""
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CommentThreadInDB(CommentThreadBase, TimestampSchema):
    """Schema for comment thread in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    is_locked: bool = False
    is_archived: bool = False

class CommentThreadResponse(CommentThreadInDB):
    """Schema for comment thread response."""
    user: Optional[Dict[str, Any]] = None
    comments_count: int = 0
    last_comment_at: Optional[datetime] = None

class CommentMentionBase(BaseSchema):
    """Base comment mention schema."""
    comment_id: uuid.UUID
    mentioned_user_id: uuid.UUID

class CommentMentionCreate(CommentMentionBase):
    """Schema for comment mention creation."""
    pass

class CommentMentionUpdate(BaseSchema):
    """Schema for comment mention updates."""
    is_notified: Optional[bool] = None

class CommentMentionInDB(CommentMentionBase, TimestampSchema):
    """Schema for comment mention in database."""
    id: uuid.UUID
    is_notified: bool = False

class CommentMentionResponse(CommentMentionInDB):
    """Schema for comment mention response."""
    mentioned_user: Optional[Dict[str, Any]] = None

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
    color: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 