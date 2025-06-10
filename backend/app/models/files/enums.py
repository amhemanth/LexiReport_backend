from enum import Enum

class FileType(str, Enum):
    """File type enum"""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"

class FileStatus(str, Enum):
    """File status enum"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"

class StorageType(str, Enum):
    """Storage type enum"""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs" 