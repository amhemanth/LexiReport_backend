from enum import Enum

class EventType(str, Enum):
    """Event type enum"""
    LOGIN = "login"
    LOGOUT = "logout"
    REPORT_CREATE = "report_create"
    REPORT_UPDATE = "report_update"
    REPORT_DELETE = "report_delete"
    REPORT_SHARE = "report_share"
    REPORT_VIEW = "report_view"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    SYSTEM_ERROR = "system_error" 