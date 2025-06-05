from enum import Enum as PyEnum

class ReportStatus(str, PyEnum):
    """Report status enum"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ReportType(str, PyEnum):
    """Report type enum"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class ReportTypeCategory(str, PyEnum):
    """Report category enum"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    AD_HOC = "ad_hoc"
    REGULAR = "regular"

class SharePermission(str, PyEnum):
    """Share permission enum"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin" 