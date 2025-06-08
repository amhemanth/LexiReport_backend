from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_current_user, get_db
from app.models.core.user import User
from app.schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse,
    CommentThreadCreate, CommentThreadUpdate, CommentThreadResponse,
    CommentMentionCreate, CommentMentionResponse
)
from app.services.comment import comment_service

router = APIRouter()

@router.get("/threads/{entity_type}/{entity_id}", response_model=List[CommentThreadResponse])
async def get_threads(
    entity_type: str,
    entity_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comment threads for an entity."""
    return comment_service.get_threads_by_entity(
        db, entity_type=entity_type, entity_id=entity_id,
        skip=skip, limit=limit
    )

@router.post("/threads", response_model=CommentThreadResponse)
async def create_thread(
    thread_in: CommentThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment thread."""
    return comment_service.create_thread(db, obj_in=thread_in)

@router.put("/threads/{thread_id}", response_model=CommentThreadResponse)
async def update_thread(
    thread_id: str,
    thread_in: CommentThreadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a comment thread."""
    return comment_service.update_thread(
        db, thread_id=thread_id, obj_in=thread_in
    )

@router.get("/threads/{thread_id}/comments", response_model=List[CommentResponse])
async def get_thread_comments(
    thread_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments in a thread."""
    return comment_service.get_comments_by_thread(
        db, thread_id=thread_id, skip=skip, limit=limit
    )

@router.post("/threads/{thread_id}/comments", response_model=CommentResponse)
async def create_comment(
    thread_id: str,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment in a thread."""
    comment_in.thread_id = thread_id
    return comment_service.create_comment(db, user_id=current_user.id, obj_in=comment_in)

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_in: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a comment."""
    return comment_service.update_comment(
        db, comment_id=comment_id, obj_in=comment_in
    )

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment."""
    comment_service.delete_comment(db, comment_id=comment_id)

@router.get("/comments/{comment_id}/replies", response_model=List[CommentResponse])
async def get_comment_replies(
    comment_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get replies to a comment."""
    return comment_service.get_replies(
        db, comment_id=comment_id, skip=skip, limit=limit
    )

@router.get("/comments/{comment_id}/mentions", response_model=List[CommentMentionResponse])
async def get_comment_mentions(
    comment_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mentions in a comment."""
    return comment_service.get_mentions_by_comment(
        db, comment_id=comment_id, skip=skip, limit=limit
    )

@router.post("/comments/{comment_id}/mentions", response_model=CommentMentionResponse)
async def create_mention(
    comment_id: str,
    mention_in: CommentMentionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a mention in a comment."""
    mention_in.comment_id = comment_id
    return comment_service.create_mention(db, obj_in=mention_in) 