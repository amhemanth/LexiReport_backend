from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.deps import get_current_user, get_db
from app.core.permissions import Permission, require_permissions
from app.models.core.user import User
from app.schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse, CommentList,
    CommentThreadCreate, CommentThreadUpdate, CommentThreadResponse, CommentThreadList,
    CommentMentionCreate, CommentMentionResponse
)
from app.services.comment import comment_service

router = APIRouter()

@router.get("/threads/{entity_type}/{entity_id}", response_model=CommentThreadList)
@require_permissions([Permission.READ_COMMENTS])
async def get_threads(
    entity_type: str,
    entity_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comment threads for an entity."""
    return await comment_service.get_threads_by_entity(
        db, entity_type=entity_type, entity_id=entity_id,
        skip=skip, limit=limit
    )

@router.post("/threads", response_model=CommentThreadResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_COMMENTS])
async def create_thread(
    thread: CommentThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment thread."""
    return await comment_service.create_thread(db, obj_in=thread)

@router.put("/threads/{thread_id}", response_model=CommentThreadResponse)
@require_permissions([Permission.WRITE_COMMENTS])
async def update_thread(
    thread_id: uuid.UUID,
    thread: CommentThreadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a comment thread."""
    return await comment_service.update_thread(
        db, thread_id=thread_id, obj_in=thread
    )

@router.get("/threads/{thread_id}/comments", response_model=CommentList)
@require_permissions([Permission.READ_COMMENTS])
async def get_thread_comments(
    thread_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments in a thread."""
    return await comment_service.get_comments_by_thread(
        db, thread_id=thread_id, skip=skip, limit=limit
    )

@router.post("/threads/{thread_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_COMMENTS])
async def create_comment(
    thread_id: uuid.UUID,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment in a thread."""
    comment.thread_id = thread_id
    return await comment_service.create_comment(db, user_id=current_user.id, obj_in=comment)

@router.put("/comments/{comment_id}", response_model=CommentResponse)
@require_permissions([Permission.WRITE_COMMENTS])
async def update_comment(
    comment_id: uuid.UUID,
    comment: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a comment."""
    return await comment_service.update_comment(
        db, comment_id=comment_id, obj_in=comment
    )

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permissions([Permission.WRITE_COMMENTS])
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment."""
    await comment_service.delete_comment(db, comment_id=comment_id)

@router.get("/comments/{comment_id}/replies", response_model=CommentList)
@require_permissions([Permission.READ_COMMENTS])
async def get_comment_replies(
    comment_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get replies to a comment."""
    return await comment_service.get_replies(
        db, comment_id=comment_id, skip=skip, limit=limit
    )

@router.get("/comments/{comment_id}/mentions", response_model=List[CommentMentionResponse])
@require_permissions([Permission.READ_COMMENTS])
async def get_comment_mentions(
    comment_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mentions in a comment."""
    return await comment_service.get_mentions_by_comment(
        db, comment_id=comment_id, skip=skip, limit=limit
    )

@router.post("/comments/{comment_id}/mentions", response_model=CommentMentionResponse, status_code=status.HTTP_201_CREATED)
@require_permissions([Permission.WRITE_COMMENTS])
async def create_mention(
    comment_id: uuid.UUID,
    mention: CommentMentionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a mention in a comment."""
    mention.comment_id = comment_id
    return await comment_service.create_mention(db, obj_in=mention) 