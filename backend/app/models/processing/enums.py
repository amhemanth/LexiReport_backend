from enum import Enum

class ProcessingStatus(str, Enum):
    """Status of document processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingPriority(str, Enum):
    """Priority levels for processing."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class SyncStatus(str, Enum):
    """Status of sync operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class ProcessingType(str, Enum):
    """Processing type enum"""
    TEXT_EXTRACTION = "text_extraction"
    SUMMARIZATION = "summarization"
    INSIGHT_GENERATION = "insight_generation"
    VOICE_OVER = "voice_over"

class ContentType(str, Enum):
    """Content type enum"""
    REPORT = "report"
    DASHBOARD = "dashboard"
    DOCUMENT = "document"
    MEDIA = "media"

class SyncAction(str, Enum):
    """Sync action enum"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete" 