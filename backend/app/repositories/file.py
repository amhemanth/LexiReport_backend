from sqlalchemy.orm import Session
from app.models.files.file import File, FileMetadata, FileVersion
from app.schemas.file import FileUpload
from typing import Optional, List
import uuid

class FileRepository:
    def get_by_user(self, db: Session, user_id: uuid.UUID) -> List[File]:
        return db.query(File).filter(File.user_id == user_id).all()

    def create(self, db: Session, user_id: uuid.UUID, obj_in: FileUpload, file_path: str) -> File:
        db_obj = File(user_id=user_id, file_name=obj_in.file_name, file_type=obj_in.file_type, file_path=file_path, description=obj_in.description, metadata=obj_in.metadata)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

file_repository = FileRepository() 