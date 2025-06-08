"""
Core models package initialization.
This module imports and exposes all core models from the application.
"""

from app.models.core.user import User
from app.models.core.password import Password
from app.models.core.permission import Permission, Role, RolePermission
from app.models.core.user_permission import UserPermission
from app.models.core.user_role import UserRole
from app.models.core.user_preferences import UserPreferences
from app.models.core.user_activity import UserActivity, ActivityType

__all__ = [
    # User related
    "User",
    "Password",
    "UserPreferences",
    "UserActivity",
    "ActivityType",
    "UserRole",
    
    # Permission related
    "Permission",
    "Role",
    "RolePermission",
    "UserPermission"
] 