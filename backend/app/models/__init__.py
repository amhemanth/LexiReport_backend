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
    Password,
    LoginAttempt
)

# Report models
from app.models.reports import (
    Report,
    ReportShare,
    ReportContent,
    ReportInsight,
    ReportQuery,
    ReportTemplate,
    ReportSchedule,
    ReportExport,
    ReportType,
    ReportStatus,
    ReportTypeCategory,
    AnalysisType,
    MetadataType,
    ReportExportStatus
)

# Analytics models
from app.models.analytics import (
    SystemMetrics,
    ErrorLog,
    VoiceCommand,
    VoiceCommandStatus,
    VoiceCommandType
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
    AuditAction,
    ChangeHistory,
    UserActivity
)

# File models
from app.models.files import (
    FileStorage,
    FileVersion,
    FileAccessLog,
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
    Document,
    DocumentProcessing,
    DocumentProcessingQueue,
    DocumentProcessingResult,
    ProcessingType,
    OfflineContent,
    SyncQueue,
    ContentType,
    SyncAction,
    ProcessingStatus,
    ProcessingPriority,
    SyncStatus
)

# Integration models
from app.models.integration import (
    BIConnection,
    BIDashboard,
    BIIntegration,
    BISyncJob,
    IntegrationType,
    IntegrationStatus,
    SyncFrequency,
    SyncStatus
)

# Media models
from app.models.media import (
    VoiceProfile,
    AudioCache,
    MediaType,
    MediaStatus
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
    "Password",
    "LoginAttempt",
    
    # Report models
    "Report",
    "ReportShare",
    "ReportContent",
    "ReportInsight",
    "ReportQuery",
    "ReportTemplate",
    "ReportSchedule",
    "ReportExport",
    "ReportType",
    "ReportStatus",
    "ReportTypeCategory",
    "AnalysisType",
    "MetadataType",
    "ReportExportStatus",
    
    # Analytics models
    "SystemMetrics",
    "ErrorLog",
    "VoiceCommand",
    "VoiceCommandStatus",
    "VoiceCommandType",
    
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
    "ChangeHistory",
    "UserActivity", 
    
    # File models
    "FileStorage",
    "FileVersion",
    "FileAccessLog",
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
    "Document",
    "DocumentProcessing",
    "DocumentProcessingQueue",
    "DocumentProcessingResult",
    "ProcessingType",
    "OfflineContent",
    "SyncQueue",
    "ContentType",
    "SyncAction",
    "ProcessingStatus",
    "ProcessingPriority",
    "SyncStatus",
    
    # Integration models
    "BIConnection",
    "BIDashboard",
    "BIIntegration",
    "BISyncJob",
    "IntegrationType",
    "IntegrationStatus",
    "SyncFrequency",
    "SyncStatus",
    
    # Media models
    "VoiceProfile",
    "AudioCache",
    "MediaType",
    "MediaStatus"
] 