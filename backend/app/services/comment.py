from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.comment import (
    comment_repository,
    comment_thread_repository,
    comment_mention_repository
)
from app.models.comments import Comment, CommentThread, CommentMention
from app.schemas.comment import (
    CommentCreate, CommentUpdate,
    CommentThreadCreate, CommentThreadUpdate,
    CommentMentionCreate
)
from app.core.exceptions import NotFoundException, PermissionException

class CommentService:
    """Service for managing comments and related operations."""

    def get_comments_by_thread(
        self, db: Session, *, thread_id: str, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get comments in a thread."""
        return comment_repository.get_by_thread(db, thread_id=thread_id, skip=skip, limit=limit)

    def get_comments_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get comments for an entity."""
        return comment_repository.get_by_entity(
            db, entity_type=entity_type, entity_id=entity_id,
            skip=skip, limit=limit
        )

    def get_replies(
        self, db: Session, *, comment_id: str, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Get replies to a comment."""
        return comment_repository.get_replies(
            db, comment_id=comment_id, skip=skip, limit=limit
        )

    def create_comment(
        self, db: Session, *, user_id: str, obj_in: CommentCreate
    ) -> Comment:
        """Create a new comment."""
        return comment_repository.create(db, obj_in=obj_in)

    def update_comment(
        self, db: Session, *, comment_id: str, obj_in: CommentUpdate
    ) -> Comment:
        """Update a comment."""
        comment = comment_repository.get(db, id=comment_id)
        if not comment:
            raise NotFoundException("Comment not found")
        return comment_repository.update(db, db_obj=comment, obj_in=obj_in)

    def delete_comment(self, db: Session, *, comment_id: str) -> None:
        """Delete a comment."""
        comment = comment_repository.get(db, id=comment_id)
        if not comment:
            raise NotFoundException("Comment not found")
        comment_repository.remove(db, id=comment_id)

    def get_threads_by_entity(
        self, db: Session, *, entity_type: str, entity_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[CommentThread]:
        """Get threads for an entity."""
        return comment_thread_repository.get_by_entity(
            db, entity_type=entity_type, entity_id=entity_id,
            skip=skip, limit=limit
        )

    def create_thread(
        self, db: Session, *, obj_in: CommentThreadCreate
    ) -> CommentThread:
        """Create a new thread."""
        return comment_thread_repository.create(db, obj_in=obj_in)

    def update_thread(
        self, db: Session, *, thread_id: str, obj_in: CommentThreadUpdate
    ) -> CommentThread:
        """Update a thread."""
        thread = comment_thread_repository.get(db, id=thread_id)
        if not thread:
            raise NotFoundException("Thread not found")
        return comment_thread_repository.update(db, db_obj=thread, obj_in=obj_in)

    def get_mentions_by_comment(
        self, db: Session, *, comment_id: str,
        skip: int = 0, limit: int = 100
    ) -> List[CommentMention]:
        """Get mentions in a comment."""
        return comment_mention_repository.get_by_comment(
            db, comment_id=comment_id, skip=skip, limit=limit
        )

    def create_mention(
        self, db: Session, *, obj_in: CommentMentionCreate
    ) -> CommentMention:
        """Create a new mention."""
        return comment_mention_repository.create(db, obj_in=obj_in)

# Create service instance
comment_service = CommentService() 