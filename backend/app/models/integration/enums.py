from enum import Enum

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