from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.comments import Comment, CommentThread, CommentMention
from app.schemas.comment import (
    CommentCreate, CommentUpdate,
    CommentThreadCreate, CommentThreadUpdate,
    CommentMentionCreate
)
from .base import BaseRepository

class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    """Repository for Comment model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get comments by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_thread(
        self, db: Session, *, thread_id: str, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get comments in thread."""
        return self.get_multi_by_field(
            db, field="thread_id", value=thread_id, skip=skip, limit=limit
        )

    def get_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get comments for entity."""
        return db.query(Comment).join(
            CommentThread, Comment.thread_id == CommentThread.id
        ).filter(
            CommentThread.entity_type == entity_type,
            CommentThread.entity_id == entity_id
        ).offset(skip).limit(limit).all()

    def get_replies(
        self, db: Session, *, comment_id: str, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get replies to comment."""
        return self.get_multi_by_field(
            db, field="parent_id", value=comment_id, skip=skip, limit=limit
        )

class CommentThreadRepository(
    BaseRepository[CommentThread, CommentThreadCreate, CommentThreadUpdate]
):
    """Repository for CommentThread model."""

    def get_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[CommentThread]:
        """Get threads for entity."""
        return db.query(CommentThread).filter(
            CommentThread.entity_type == entity_type,
            CommentThread.entity_id == entity_id
        ).offset(skip).limit(limit).all()

    def get_by_creator(
        self, db: Session, *, created_by: str,
        skip: int = 0, limit: int = 100
    ) -> List[CommentThread]:
        """Get threads created by user."""
        return self.get_multi_by_field(
            db, field="created_by", value=created_by, skip=skip, limit=limit
        )

    def get_locked_threads(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CommentThread]:
        """Get locked threads."""
        return self.get_multi_by_field(
            db, field="is_locked", value=True, skip=skip, limit=limit
        )

class CommentMentionRepository(
    BaseRepository[CommentMention, CommentMentionCreate, CommentMentionCreate]
):
    """Repository for CommentMention model."""

    def get_by_comment(
        self, db: Session, *, comment_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[CommentMention]:
        """Get mentions in comment."""
        return self.get_multi_by_field(
            db, field="comment_id", value=comment_id, skip=skip, limit=limit
        )

    def get_by_user(
        self, db: Session, *, user_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[CommentMention]:
        """Get mentions of user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

# Create repository instances
comment_repository = CommentRepository(Comment)
comment_thread_repository = CommentThreadRepository(CommentThread)
comment_mention_repository = CommentMentionRepository(CommentMention) 