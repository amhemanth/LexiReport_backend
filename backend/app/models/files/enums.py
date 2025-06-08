from enum import Enum

class FileType(str, Enum):
    """Types of files."""
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    OTHER = "other"

class FileStatus(str, Enum):
    """Status of files."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING = "pending"
    PROCESSING = "processing"

class StorageType(str, Enum):
    """Types of storage."""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCP = "gcp"
    CUSTOM = "custom" 