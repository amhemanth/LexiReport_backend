from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
from fastapi import HTTPException, status
from app.repositories.report_comment import report_comment_repository
from app.models.reports import ReportComment
from app.schemas.report_comment import (
    ReportCommentCreate, ReportCommentUpdate, ReportCommentResponse,
    ReportCommentList
)

class ReportCommentService:
    """Service for managing report comments."""

    async def get_comments_by_report(
        self, db: Session, *, report_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> ReportCommentList:
        """Get comments for a report."""
        try:
            comments = report_comment_repository.get_by_report(
                db, report_id=report_id, skip=skip, limit=limit
            )
            total = len(comments)  # TODO: Implement proper count
            return ReportCommentList(
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
    ) -> ReportCommentList:
        """Get replies to a report comment."""
        try:
            replies = report_comment_repository.get_replies(
                db, comment_id=comment_id, skip=skip, limit=limit
            )
            total = len(replies)  # TODO: Implement proper count
            return ReportCommentList(
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
        self, db: Session, *, user_id: uuid.UUID, obj_in: ReportCommentCreate
    ) -> ReportCommentResponse:
        """Create a new report comment."""
        try:
            comment = report_comment_repository.create(db, obj_in=obj_in)
            return ReportCommentResponse.from_orm(comment)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def update_comment(
        self, db: Session, *, comment_id: uuid.UUID, obj_in: ReportCommentUpdate
    ) -> ReportCommentResponse:
        """Update a report comment."""
        try:
            comment = report_comment_repository.get(db, id=comment_id)
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            updated_comment = report_comment_repository.update(db, db_obj=comment, obj_in=obj_in)
            return ReportCommentResponse.from_orm(updated_comment)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def delete_comment(self, db: Session, *, comment_id: uuid.UUID) -> None:
        """Delete a report comment."""
        try:
            comment = report_comment_repository.get(db, id=comment_id)
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            report_comment_repository.remove(db, id=comment_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create service instance
report_comment_service = ReportCommentService() 