from enum import Enum
from app.models.common.enums import SyncStatus

class ProcessingStatus(str, Enum):
    """Status of a processing task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingPriority(str, Enum):
    """Priority level for processing tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Re-export SyncStatus from common
__all__ = ['ProcessingStatus', 'ProcessingPriority', 'SyncStatus']

class ProcessingType(str, Enum):
    """Type of processing to be performed."""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DATA = "data"
    OTHER = "other"

class ContentType(str, Enum):
    """Type of content being processed."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    OTHER = "other"

class SyncAction(str, Enum):
    """Type of synchronization action."""
    PUSH = "push"
    PULL = "pull"
    BIDIRECTIONAL = "bidirectional"
    MERGE = "merge"
    OVERWRITE = "overwrite" 