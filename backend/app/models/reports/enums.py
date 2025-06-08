"""Report-related enums."""
from enum import Enum

class ReportType(str, Enum):
    """Report type enum"""
    STANDARD = "standard"
    TEMPLATE = "template"
    CUSTOM = "custom"
    DASHBOARD = "dashboard"
    ANALYTICAL = "analytical"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"

class ReportStatus(str, Enum):
    """Report status enum"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"

class ReportTypeCategory(str, Enum):
    """Report type category enum"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class AnalysisType(str, Enum):
    """Report analysis type enum"""
    TREND = "trend"
    COMPARISON = "comparison"
    FORECAST = "forecast"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    CUSTOM = "custom"

class MetadataType(str, Enum):
    """Report metadata type enum"""
    SOURCE = "source"
    AUTHOR = "author"
    DEPARTMENT = "department"
    TAGS = "tags"
    CUSTOM = "custom"

class SharePermission(str, Enum):
    """Permissions for shared reports."""
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin" 