from enum import Enum
from app.models.common.enums import SyncStatus

class IntegrationType(str, Enum):
    """Type of integration."""
    BI = "bi"
    API = "api"
    DATABASE = "database"
    FILE = "file"
    CUSTOM = "custom"

class IntegrationStatus(str, Enum):
    """Status of BI integrations."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    CONFIGURING = "configuring"

class SyncFrequency(str, Enum):
    """Frequency of synchronization."""
    MANUAL = "manual"
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

# Re-export SyncStatus from common
__all__ = ['IntegrationType', 'IntegrationStatus', 'SyncFrequency', 'SyncStatus'] 