from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.files import FileStorage, FileType, FileStatus, StorageType
from app.schemas.file import FileCreate, FileUpdate
from .base import BaseRepository

class FileRepository(BaseRepository[FileStorage, FileCreate, FileUpdate]):
    """Repository for FileStorage model."""

    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[FileStorage]:
        """Get files uploaded by user."""
        return self.get_multi_by_field(
            db, field="user_id", value=user_id, skip=skip, limit=limit
        )

    def get_by_type(
        self, db: Session, *, file_type: FileType,
        skip: int = 0, limit: int = 100
    ) -> List[FileStorage]:
        """Get files by type."""
        return self.get_multi_by_field(
            db, field="file_type", value=file_type, skip=skip, limit=limit
        )

    def get_by_status(
        self, db: Session, *, status: FileStatus,
        skip: int = 0, limit: int = 100
    ) -> List[FileStorage]:
        """Get files by status."""
        return self.get_multi_by_field(
            db, field="status", value=status, skip=skip, limit=limit
        )

    def get_by_storage_type(
        self, db: Session, *, storage_type: StorageType,
        skip: int = 0, limit: int = 100
    ) -> List[FileStorage]:
        """Get files by storage type."""
        return self.get_multi_by_field(
            db, field="storage_type", value=storage_type, skip=skip, limit=limit
        )

    def get_public_files(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[FileStorage]:
        """Get public files."""
        return self.get_multi_by_field(
            db, field="is_public", value=True, skip=skip, limit=limit
        )

    def get_by_checksum(
        self, db: Session, *, checksum: str
    ) -> Optional[FileStorage]:
        """Get file by checksum."""
        return self.get_by_field(db, field="checksum", value=checksum)

    def get_by_path(
        self, db: Session, *, file_path: str
    ) -> Optional[FileStorage]:
        """Get file by path."""
        return self.get_by_field(db, field="file_path", value=file_path)

    def get_by_storage_path(
        self, db: Session, *, storage_path: str
    ) -> Optional[FileStorage]:
        """Get file by storage path."""
        return self.get_by_field(db, field="storage_path", value=storage_path)

# Create repository instance
file_repository = FileRepository(FileStorage) 