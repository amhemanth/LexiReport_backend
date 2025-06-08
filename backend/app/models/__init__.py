"""
Models package initialization.
This module imports and exposes all models from the application.
"""

# Core models
from app.models.core import (
    User,
    Role,
    Permission,
    UserRole,
    UserPermission,
    RolePermission,
    UserPreferences,
    UserActivity,
    ActivityType,
    Password
)

# Report models
from app.models.reports import (
    Report,
    ReportShare,
    ReportTemplate,
    ReportSchedule,
    ReportExport,
    ReportContent,
    ReportMetadata,
    ReportAnalysis,
    ReportType,
    ReportStatus,
    ReportTypeCategory
)

# Analytics models
from app.models.analytics import (
    SystemMetrics,
    ErrorLog,
    VoiceCommand
)

# Notification models
from app.models.notifications import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    NotificationType,
    NotificationStatus,
    NotificationPriority
)

# Audit models
from app.models.audit import (
    AuditLog,
    AuditAction
)

# File models
from app.models.files import (
    FileStorage,
    FileType,
    FileStatus,
    StorageType
)

# Comment models
from app.models.comments import (
    Comment,
    CommentThread,
    CommentMention
)

# Tag models
from app.models.tags import (
    Tag,
    EntityTag
)

# Processing models
from app.models.processing import (
    DocumentProcessing,
    DocumentProcessingQueue,
    DocumentProcessingResult,
    ProcessingType,
    OfflineContent,
    SyncQueue,
    ContentType,
    SyncAction,
    ProcessingStatus
)

# Integration models
from app.models.integration import (
    BIIntegration,
    IntegrationType,
    IntegrationStatus
)

# Media models
from app.models.media import (
    VoiceProfile,
    AudioCache
)

__all__ = [
    # Core models
    "User",
    "Role",
    "Permission",
    "UserRole",
    "UserPermission",
    "RolePermission",
    "UserPreferences",
    "UserActivity",
    "ActivityType",
    "Password",
    
    # Report models
    "Report",
    "ReportShare",
    "ReportTemplate",
    "ReportSchedule",
    "ReportExport",
    "ReportContent",
    "ReportMetadata",
    "ReportAnalysis",
    "ReportType",
    "ReportStatus",
    "ReportTypeCategory",
    
    # Analytics models
    "SystemMetrics",
    "ErrorLog",
    "VoiceCommand",
    
    # Notification models
    "Notification",
    "NotificationTemplate",
    "NotificationPreference",
    "NotificationType",
    "NotificationStatus",
    "NotificationPriority",
    
    # Audit models
    "AuditLog",
    "AuditAction",
    
    # File models
    "FileStorage",
    "FileType",
    "FileStatus",
    "StorageType",
    
    # Comment models
    "Comment",
    "CommentThread",
    "CommentMention",
    
    # Tag models
    "Tag",
    "EntityTag",
    
    # Processing models
    "DocumentProcessing",
    "DocumentProcessingQueue",
    "DocumentProcessingResult",
    "ProcessingType",
    "OfflineContent",
    "SyncQueue",
    "ContentType",
    "SyncAction",
    "ProcessingStatus",
    
    # Integration models
    "BIIntegration",
    "IntegrationType",
    "IntegrationStatus",
    
    # Media models
    "VoiceProfile",
    "AudioCache"
] 