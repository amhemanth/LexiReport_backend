from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.repositories.tag import tag_repository
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagList

logger = logging.getLogger(__name__)

class TagService:
    def get_tags(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> TagList:
        """Get all tags with optional search and pagination."""
        try:
            items = tag_repository.get_multi(
                db, skip=skip, limit=limit, search=search
            )
            total = tag_repository.get_total(db, search=search)
            return TagList(
                items=items,
                total=total,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error getting tags: {str(e)}")
            raise

    def create_tag(
        self,
        db: Session,
        *,
        obj_in: TagCreate,
        created_by: int
    ) -> TagResponse:
        """Create a new tag."""
        try:
            tag = tag_repository.create(
                db, obj_in=obj_in, created_by=created_by
            )
            return tag
        except Exception as e:
            logger.error(f"Error creating tag: {str(e)}")
            raise

    def get_tag(
        self,
        db: Session,
        *,
        id: int
    ) -> TagResponse:
        """Get a specific tag by ID."""
        try:
            tag = tag_repository.get(db, id=id)
            if not tag:
                raise ValueError(f"Tag with id {id} not found")
            return tag
        except Exception as e:
            logger.error(f"Error getting tag: {str(e)}")
            raise

    def update_tag(
        self,
        db: Session,
        *,
        id: int,
        obj_in: TagUpdate
    ) -> TagResponse:
        """Update an existing tag."""
        try:
            tag = tag_repository.get(db, id=id)
            if not tag:
                raise ValueError(f"Tag with id {id} not found")
            tag = tag_repository.update(
                db, db_obj=tag, obj_in=obj_in
            )
            return tag
        except Exception as e:
            logger.error(f"Error updating tag: {str(e)}")
            raise

    def delete_tag(
        self,
        db: Session,
        *,
        id: int
    ) -> Dict[str, str]:
        """Delete a tag."""
        try:
            tag = tag_repository.delete(db, id=id)
            return {"message": "Tag deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting tag: {str(e)}")
            raise

# Create service instance
tag_service = TagService() 