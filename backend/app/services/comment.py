from sqlalchemy.orm import Session
from app.repositories.comment import comment_repository, tag_repository
from app.models.comments.comment import Comment
from app.models.tags.tag import Tag
from app.schemas.comment import CommentCreate, TagCreate
from typing import List
import uuid

class CommentService:
    def get_comments(self, db: Session, report_id: uuid.UUID) -> List[Comment]:
        return comment_repository.get_by_report(db, report_id)

    def create_comment(self, db: Session, user_id: uuid.UUID, obj_in: CommentCreate) -> Comment:
        return comment_repository.create(db, user_id, obj_in)

    def get_tags(self, db: Session) -> List[Tag]:
        return tag_repository.get_all(db)

    def create_tag(self, db: Session, obj_in: TagCreate) -> Tag:
        return tag_repository.create(db, obj_in)

comment_service = CommentService() 