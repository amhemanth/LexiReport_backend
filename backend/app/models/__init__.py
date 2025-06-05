from app.db.base_class import Base

# Core models
from app.models.core import (
    User, UserRole, Permission, UserPermission, Password, PermissionType
)

# Report models
from app.models.reports import (
    Report, ReportStatus, ReportType, ReportTypeCategory,
    ReportMetadata, ReportContent, ReportAnalysis,
    ReportShare, SharePermission
)

# Analytics models
from app.models.analytics import (
    UserActivity, EventType, SystemMetrics, ErrorLog
)

# Integration models
from app.models.integration import (
    BIConnection, BIDashboard, BIPlatformType, SyncStatus
)

# Processing models
from app.models.processing import (
    DocumentProcessingQueue, DocumentProcessingResult,
    ProcessingStatus, ProcessingType,
    OfflineContent, SyncQueue, ContentType, SyncAction
)

# Media models
from app.models.media import (
    VoiceProfile, AudioCache
)

# Notification models
from app.models.notifications import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationStatus
)

# Audit models
from app.models.audit import (
    AuditLog, ChangeHistory, AuditAction
)

# File management models
from app.models.files import (
    FileStorage, FileVersion, FileAccessLog,
    FileType, FileStatus
)

# Comment models
from app.models.comments import (
    Comment, CommentThread, CommentMention
)

# Tag models
from app.models.tags import (
    Tag, EntityTag
)

# Export all models
__all__ = [
    # Base
    "Base",
    
    # Core models
    "User", "UserRole", "Permission", "UserPermission", "Password", "PermissionType",
    
    # Report models
    "Report", "ReportStatus", "ReportType", "ReportTypeCategory",
    "ReportMetadata", "ReportContent", "ReportAnalysis",
    "ReportShare", "SharePermission",
    
    # Analytics models
    "UserActivity", "EventType", "SystemMetrics", "ErrorLog",
    
    # Integration models
    "BIConnection", "BIDashboard", "BIPlatformType", "SyncStatus",
    
    # Processing models
    "DocumentProcessingQueue", "DocumentProcessingResult",
    "ProcessingStatus", "ProcessingType", "ContentType", "SyncAction",
    "OfflineContent", "SyncQueue",
    
    # Media models
    "VoiceProfile", "AudioCache",
    
    # Notification models
    "Notification", "NotificationTemplate", "NotificationPreference",
    "NotificationType", "NotificationStatus",
    
    # Audit models
    "AuditLog", "ChangeHistory", "AuditAction",
    
    # File management models
    "FileStorage", "FileVersion", "FileAccessLog",
    "FileType", "FileStatus",
    
    # Comment models
    "Comment", "CommentThread", "CommentMention",
    
    # Tag models
    "Tag", "EntityTag"
] 