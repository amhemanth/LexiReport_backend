from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseSchema, TimestampSchema
import uuid

class ReportCommentBase(BaseSchema):
    """Base report comment schema."""
    content: str
    report_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    meta_data: Optional[Dict[str, Any]] = None

class ReportCommentCreate(ReportCommentBase):
    """Schema for creating a report comment."""
    pass

class ReportCommentUpdate(BaseSchema):
    """Schema for updating a report comment."""
    content: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_resolved: Optional[bool] = None

class ReportCommentInDB(ReportCommentBase, TimestampSchema):
    """Schema for report comment in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    is_resolved: bool = False

    model_config = ConfigDict(from_attributes=True)

class ReportCommentResponse(ReportCommentInDB):
    """Schema for report comment response."""
    user: Optional[Dict[str, Any]] = None
    replies_count: int = 0

class ReportCommentList(BaseSchema):
    """Schema for paginated report comment list."""
    items: List[ReportCommentResponse]
    total: int
    page: int
    size: int
    pages: int 