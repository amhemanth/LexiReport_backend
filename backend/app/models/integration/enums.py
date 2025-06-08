from enum import Enum

class IntegrationType(str, Enum):
    """Types of BI integrations."""
    POWER_BI = "power_bi"
    TABLEAU = "tableau"
    QLIK = "qlik"
    LOOKER = "looker"
    CUSTOM = "custom"

class IntegrationStatus(str, Enum):
    """Status of BI integrations."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    CONFIGURING = "configuring"

class SyncFrequency(str, Enum):
    """Frequency of data sync."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class BIPlatformType(str, Enum):
    """BI platform type enum"""
    POWER_BI = "power_bi"
    TABLEAU = "tableau"
    LOOKER = "looker"
    METABASE = "metabase"
    CUSTOM = "custom"

class SyncStatus(str, Enum):
    """Sync status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed" 