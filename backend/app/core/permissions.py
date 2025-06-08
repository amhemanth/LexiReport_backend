from enum import Enum
from typing import Optional, Callable, List
from fastapi import HTTPException, status, Depends
from functools import wraps
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.core.user import User
from app.models.core.enums import UserRole
from app.db.session import get_db
from app.core.deps import get_current_user, get_current_active_user
from app.core.exceptions import PermissionException

class Permission(str, Enum):
    """Available permissions in the system."""
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    MANAGE_USERS = "manage_users"
    API_ACCESS = "api_access"

    @classmethod
    def validate_permission(cls, permission_name: str) -> bool:
        """Validate if a permission name is valid."""
        return permission_name in [p.value for p in cls]

def require_permission(permission: Permission):
    """Decorator to require a specific permission."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_active_user),
            **kwargs
        ):
            if not current_user:
                raise PermissionException("Authentication required")
            
            if not current_user.has_permission(permission):
                raise PermissionException(f"Permission denied: {permission} required")
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_admin(func: Callable):
    """Decorator to require admin role."""
    @wraps(func)
    async def wrapper(
        *args,
        current_user: User = Depends(get_current_active_user),
        **kwargs
    ):
        if not current_user:
            raise PermissionException("Authentication required")
        
        if current_user.role != UserRole.ADMIN:
            raise PermissionException("Admin access required")
        
        return await func(*args, **kwargs)
    return wrapper

def require_permissions(required_permissions: List[Permission]):
    """
    Decorator to require specific permissions for an endpoint.
    Usage:
        @router.get("/users")
        @require_permissions([Permission.READ_USERS])
        def get_users():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db),
            **kwargs
        ):
            if not current_user:
                raise PermissionException("Authentication required")
            
            # Check if user has all required permissions
            for permission in required_permissions:
                if not current_user.has_permission(permission):
                    raise PermissionException(f"Missing required permission: {permission}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role: UserRole):
    """
    Decorator to require a specific role for an endpoint.
    Usage:
        @router.get("/admin")
        @require_role(UserRole.ADMIN)
        def admin_only():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db),
            **kwargs
        ):
            if not current_user:
                raise PermissionException("Authentication required")
            
            if current_user.role != required_role:
                raise PermissionException(f"Required role: {required_role}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Get all permissions for a user."""
    if not current_user:
        raise PermissionException("Authentication required")
    
    # Check if current user has permission to view other users' permissions
    if current_user.id != user_id and not current_user.has_permission(Permission.READ_USERS):
        raise PermissionException("Not authorized to view user permissions")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise PermissionException("User not found")
    
    return user.get_permissions()

def assign_permission(
    user_id: UUID,
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> bool:
    """Assign a permission to a user."""
    if not current_user:
        raise PermissionException("Authentication required")
    
    # Check if current user has permission to manage users
    if not current_user.has_permission(Permission.MANAGE_USERS):
        raise PermissionException("Not authorized to manage user permissions")
    
    # Validate permission name
    if not Permission.validate_permission(permission_name):
        raise PermissionException(f"Invalid permission: {permission_name}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise PermissionException("User not found")
    
    return user.add_permission(db, permission_name)

def remove_permission(
    user_id: UUID,
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> bool:
    """Remove a permission from a user."""
    if not current_user:
        raise PermissionException("Authentication required")
    
    # Check if current user has permission to manage users
    if not current_user.has_permission(Permission.MANAGE_USERS):
        raise PermissionException("Not authorized to manage user permissions")
    
    # Validate permission name
    if not Permission.validate_permission(permission_name):
        raise PermissionException(f"Invalid permission: {permission_name}")
    
    # Prevent removing critical permissions
    if permission_name == Permission.API_ACCESS.value:
        raise PermissionException("Cannot remove api_access permission")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise PermissionException("User not found")
    
    return user.remove_permission(db, permission_name) 