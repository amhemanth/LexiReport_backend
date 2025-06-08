from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
import uuid

class CommentCreate(BaseModel):
    report_id: uuid.UUID
    content: str
    parent_id: Optional[uuid.UUID] = None
    mentions: Optional[List[uuid.UUID]] = None

class CommentResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    parent_id: Optional[uuid.UUID]
    mentions: Optional[List[uuid.UUID]]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CommentThreadResponse(BaseModel):
    thread_id: uuid.UUID
    comments: List[CommentResponse]

class TagCreate(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 