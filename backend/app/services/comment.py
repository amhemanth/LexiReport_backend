from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
from fastapi import HTTPException, status
from app.repositories.comment import (
    comment_repository,
    comment_thread_repository,
    comment_mention_repository
)
from app.models.comments import Comment, CommentThread, CommentMention
from app.schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse,
    CommentThreadCreate, CommentThreadUpdate, CommentThreadResponse,
    CommentMentionCreate, CommentMentionResponse,
    CommentList, CommentThreadList
)

class CommentService:
    """Service for managing comments and related operations."""

    async def get_comments_by_thread(
        self, db: Session, *, thread_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> CommentList:
        """Get comments in a thread."""
        try:
            comments = comment_repository.get_by_thread(
                db, thread_id=thread_id, skip=skip, limit=limit
            )
            total = len(comments)  # TODO: Implement proper count
            return CommentList(
                items=comments,
                total=total,
                page=skip // limit + 1,
                size=limit,
                pages=(total + limit - 1) // limit
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_comments_by_entity(
        self, db: Session, *, entity_type: str, entity_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> CommentList:
        """Get comments for an entity."""
        try:
            comments = comment_repository.get_by_entity(
                db, entity_type=entity_type, entity_id=entity_id,
                skip=skip, limit=limit
            )
            total = len(comments)  # TODO: Implement proper count
            return CommentList(
                items=comments,
                total=total,
                page=skip // limit + 1,
                size=limit,
                pages=(total + limit - 1) // limit
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_replies(
        self, db: Session, *, comment_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> CommentList:
        """Get replies to a comment."""
        try:
            replies = comment_repository.get_replies(
                db, comment_id=comment_id, skip=skip, limit=limit
            )
            total = len(replies)  # TODO: Implement proper count
            return CommentList(
                items=replies,
                total=total,
                page=skip // limit + 1,
                size=limit,
                pages=(total + limit - 1) // limit
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def create_comment(
        self, db: Session, *, user_id: uuid.UUID, obj_in: CommentCreate
    ) -> CommentResponse:
        """Create a new comment."""
        try:
            comment = comment_repository.create(db, obj_in=obj_in)
            return CommentResponse.from_orm(comment)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def update_comment(
        self, db: Session, *, comment_id: uuid.UUID, obj_in: CommentUpdate
    ) -> CommentResponse:
        """Update a comment."""
        try:
            comment = comment_repository.get(db, id=comment_id)
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            updated_comment = comment_repository.update(db, db_obj=comment, obj_in=obj_in)
            return CommentResponse.from_orm(updated_comment)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def delete_comment(self, db: Session, *, comment_id: uuid.UUID) -> None:
        """Delete a comment."""
        try:
            comment = comment_repository.get(db, id=comment_id)
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            comment_repository.remove(db, id=comment_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_threads_by_entity(
        self, db: Session, *, entity_type: str, entity_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> CommentThreadList:
        """Get threads for an entity."""
        try:
            threads = comment_thread_repository.get_by_entity(
                db, entity_type=entity_type, entity_id=entity_id,
                skip=skip, limit=limit
            )
            total = len(threads)  # TODO: Implement proper count
            return CommentThreadList(
                items=threads,
                total=total,
                page=skip // limit + 1,
                size=limit,
                pages=(total + limit - 1) // limit
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def create_thread(
        self, db: Session, *, obj_in: CommentThreadCreate
    ) -> CommentThreadResponse:
        """Create a new thread."""
        try:
            thread = comment_thread_repository.create(db, obj_in=obj_in)
            return CommentThreadResponse.from_orm(thread)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def update_thread(
        self, db: Session, *, thread_id: uuid.UUID, obj_in: CommentThreadUpdate
    ) -> CommentThreadResponse:
        """Update a thread."""
        try:
            thread = comment_thread_repository.get(db, id=thread_id)
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
            updated_thread = comment_thread_repository.update(db, db_obj=thread, obj_in=obj_in)
            return CommentThreadResponse.from_orm(updated_thread)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_mentions_by_comment(
        self, db: Session, *, comment_id: uuid.UUID,
        skip: int = 0, limit: int = 100
    ) -> List[CommentMentionResponse]:
        """Get mentions in a comment."""
        try:
            mentions = comment_mention_repository.get_by_comment(
                db, comment_id=comment_id, skip=skip, limit=limit
            )
            return [CommentMentionResponse.from_orm(m) for m in mentions]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def create_mention(
        self, db: Session, *, obj_in: CommentMentionCreate
    ) -> CommentMentionResponse:
        """Create a new mention."""
        try:
            mention = comment_mention_repository.create(db, obj_in=obj_in)
            return CommentMentionResponse.from_orm(mention)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create service instance
comment_service = CommentService() 