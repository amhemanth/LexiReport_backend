from enum import Enum

class AuditAction(str, Enum):
    """Types of audit actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    SHARE = "share"
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    ROLE_CHANGE = "role_change"
    PERMISSION_CHANGE = "permission_change" 