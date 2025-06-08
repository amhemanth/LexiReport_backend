"""
Media enums package.
This module defines enums used in media-related models.
"""

from enum import Enum

class MediaType(str, Enum):
    """Types of media."""
    AUDIO = "audio"
    VOICE = "voice"
    OTHER = "other"

class MediaStatus(str, Enum):
    """Status of media."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING = "pending"
    PROCESSING = "processing" 