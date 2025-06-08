"""Base class for database models."""
from app.db.base_class import Base
from app.models.core import (
    User, Password, Permission, Role, RolePermission,
    UserPermission, UserRole, UserPreferences, UserActivity, ActivityType
)
from app.models.reports import (
    Report, ReportShare, ReportContent, ReportInsight,
    ReportQuery, ReportVersion, ReportComment, ReportTemplate,
    ReportSchedule, ReportExport, ReportType, ReportStatus,
    ReportTypeCategory, AnalysisType, MetadataType
)
from app.models.analytics import SystemMetrics, ErrorLog, VoiceCommand
from app.models.notifications import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationStatus, NotificationPriority
)
from app.models.audit import AuditLog, AuditAction
from app.models.files import FileStorage, FileType, FileStatus, StorageType
from app.models.comments import Comment, CommentThread, CommentMention
from app.models.tags import Tag, EntityTag
from app.models.processing import (
    DocumentProcessing, DocumentProcessingQueue, DocumentProcessingResult,
    ProcessingType, OfflineContent, SyncQueue, ContentType,
    SyncAction, ProcessingStatus
)
from app.models.integration import BIIntegration, IntegrationType, IntegrationStatus
from app.models.media import VoiceProfile, AudioCache, MediaType, MediaStatus

# No need to define __all__ here since we're importing everything from models/__init__.py