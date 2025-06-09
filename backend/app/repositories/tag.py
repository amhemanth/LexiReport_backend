from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime

from app.models.core.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate

class TagRepository:
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Tag]:
        """Get multiple tags with optional search and pagination."""
        try:
            query = db.query(Tag)
            if search:
                query = query.filter(Tag.name.ilike(f"%{search}%"))
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise e

    def get(self, db: Session, id: int) -> Optional[Tag]:
        """Get a tag by ID."""
        try:
            return db.query(Tag).filter(Tag.id == id).first()
        except Exception as e:
            raise e

    def create(self, db: Session, *, obj_in: TagCreate, created_by: int) -> Tag:
        """Create a new tag."""
        try:
            db_obj = Tag(
                name=obj_in.name,
                description=obj_in.description,
                color=obj_in.color,
                created_by=created_by
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e

    def update(
        self,
        db: Session,
        *,
        db_obj: Tag,
        obj_in: TagUpdate
    ) -> Tag:
        """Update a tag."""
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e

    def delete(self, db: Session, *, id: int) -> Tag:
        """Delete a tag."""
        try:
            obj = db.query(Tag).get(id)
            if not obj:
                raise ValueError(f"Tag with id {id} not found")
            db.delete(obj)
            db.commit()
            return obj
        except Exception as e:
            db.rollback()
            raise e

    def get_total(self, db: Session, search: Optional[str] = None) -> int:
        """Get total number of tags."""
        try:
            query = db.query(func.count(Tag.id))
            if search:
                query = query.filter(Tag.name.ilike(f"%{search}%"))
            return query.scalar()
        except Exception as e:
            raise e

# Create repository instance
tag_repository = TagRepository() 