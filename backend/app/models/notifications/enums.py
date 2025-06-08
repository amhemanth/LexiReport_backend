from enum import Enum

class NotificationType(str, Enum):
    """Types of notifications."""
    SYSTEM = "system"
    REPORT = "report"
    COMMENT = "comment"
    SHARE = "share"
    ALERT = "alert"
    MENTION = "mention"

class NotificationStatus(str, Enum):
    """Status of notifications."""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"

class NotificationPriority(str, Enum):
    """Priority levels for notifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent" 