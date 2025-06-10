from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
from app.models.comments.comment import Comment
from app.schemas.report_comment import (
    ReportCommentCreate, ReportCommentUpdate
)
from .base import BaseRepository

class ReportCommentRepository(BaseRepository[Comment, ReportCommentCreate, ReportCommentUpdate]):
    """Repository for ReportComment model."""

    def get_by_report(
        self, db: Session, *, report_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get comments for a report."""
        return self.get_multi_by_field(
            db, field="report_id", value=report_id, skip=skip, limit=limit
        )

    def get_by_user(
        self, db: Session, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get comments by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_replies(
        self, db: Session, *, comment_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get replies to a comment."""
        return self.get_multi_by_field(
            db, field="parent_id", value=comment_id, skip=skip, limit=limit
        )

# Create repository instance
report_comment_repository = ReportCommentRepository(Comment) 