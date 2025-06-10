"""Report-related enums."""
from enum import Enum

class ReportType(str, Enum):
    """Report type enum"""
    STANDARD = "standard"
    CUSTOM = "custom"
    DASHBOARD = "dashboard"
    ANALYTICAL = "analytical"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    COMPARATIVE = "comparative"
    TREND = "trend"
    FORECAST = "forecast"

class ReportStatus(str, Enum):
    """Report status enum"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ReportExportStatus(str, Enum):
    """Report export status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CommentStatus(str, Enum):
    """Comment status enum"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"
    HIDDEN = "hidden"
    DELETED = "deleted"
    PENDING = "pending"
    FLAGGED = "flagged"
    LOCKED = "locked"

class ReportTypeCategory(str, Enum):
    """Report type category enum"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"
    STRATEGIC = "strategic"

class AnalysisType(str, Enum):
    """Report analysis type enum"""
    TREND = "trend"
    COMPARATIVE = "comparative"
    PREDICTIVE = "predictive"
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PRESCRIPTIVE = "prescriptive"
    CUSTOM = "custom"

class MetadataType(str, Enum):
    """Report metadata type enum"""
    SOURCE = "source"
    AUTHOR = "author"
    DEPARTMENT = "department"
    TAGS = "tags"
    CUSTOM = "custom"
    BASIC = "basic"
    EXTENDED = "extended"
    NONE = "none"

class SharePermission(str, Enum):
    """Permissions for shared reports."""
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin" 