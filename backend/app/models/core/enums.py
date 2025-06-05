from enum import Enum

class UserRole(str, Enum):
    """User role enum"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class PermissionType(str, Enum):
    """Permission type enum"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin" 