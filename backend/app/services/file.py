from sqlalchemy.orm import Session
from app.repositories.file import file_repository
from app.models.files.file_storage import FileStorage
from app.schemas.file import FileUpload
from typing import List
import uuid

class FileService:
    def get_files(self, db: Session, user_id: uuid.UUID) -> List[FileStorage]:
        return file_repository.get_by_user(db, user_id)

    def upload_file(self, db: Session, user_id: uuid.UUID, obj_in: FileUpload, file_path: str) -> FileStorage:
        return file_repository.create(db, user_id, obj_in, file_path)

file_service = FileService() 