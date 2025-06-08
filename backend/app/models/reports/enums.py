"""Report-related enums."""
from enum import Enum

class ReportType(str, Enum):
    """Report type enum."""
    STANDARD = "standard"
    ANALYTICAL = "analytical"
    DASHBOARD = "dashboard"
    CUSTOM = "custom"

class ReportStatus(str, Enum):
    """Status of a report."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ReportTypeCategory(str, Enum):
    """Categories of report types."""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class SharePermission(str, Enum):
    """Permissions for shared reports."""
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin" 