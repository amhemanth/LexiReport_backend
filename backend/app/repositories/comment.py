from sqlalchemy.orm import Session
from app.models.comments.comment import Comment
from app.models.tags.tag import Tag
from app.schemas.comment import CommentCreate, TagCreate
from typing import Optional, List
import uuid

class CommentRepository:
    def get_by_report(self, db: Session, report_id: uuid.UUID) -> List[Comment]:
        return db.query(Comment).filter(Comment.report_id == report_id).all()

    def create(self, db: Session, user_id: uuid.UUID, obj_in: CommentCreate) -> Comment:
        db_obj = Comment(user_id=user_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

comment_repository = CommentRepository()

class TagRepository:
    def get_all(self, db: Session) -> List[Tag]:
        return db.query(Tag).all()

    def create(self, db: Session, obj_in: TagCreate) -> Tag:
        db_obj = Tag(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

tag_repository = TagRepository() 