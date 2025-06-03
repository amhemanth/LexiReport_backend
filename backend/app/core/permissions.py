from enum import Enum
from typing import Optional, Callable, List
from fastapi import HTTPException, status, Depends
from functools import wraps
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.enums import UserRole
from app.db.session import get_db
from app.core.deps import get_current_user, get_current_active_user

class Permission(str, Enum):
    """Available permissions in the system."""
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    MANAGE_USERS = "manage_users"
    API_ACCESS = "api_access"

def require_permission(permission: Permission):
    """Decorator to require a specific permission."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_active_user),
            **kwargs
        ):
            # Check if user has the required permission
            if not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission} required"
                )
            
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
        # The current_user is now injected via Depends, no need to get from kwargs
        if not current_user:
             # This case should ideally not happen with Depends(get_current_active_user)
             # but keeping a check for robustness.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return await func(*args, **kwargs)
    return wrapper

def require_permissions(required_permissions: List[str]):
    """
    Decorator to require specific permissions for an endpoint.
    Usage:
        @router.get("/users")
        @require_permissions(["read_users"])
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
            # Check if user has all required permissions
            for permission in required_permissions:
                if not current_user.has_permission(permission):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Missing required permission: {permission}"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role: str):
    """
    Decorator to require a specific role for an endpoint.
    Usage:
        @router.get("/admin")
        @require_role("admin")
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
            if current_user.role.value != required_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"Required role: {required_role}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Get all permissions for a user."""
    # Check if current user has permission to view other users' permissions
    if current_user.id != user_id and not current_user.has_permission("read_users"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view user permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.get_permissions()

def assign_permission(
    user_id: str,
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> bool:
    """Assign a permission to a user."""
    # Check if current user has permission to manage users
    if not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to manage user permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.add_permission(db, permission_name)

def remove_permission(
    user_id: str,
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> bool:
    """Remove a permission from a user."""
    # Check if current user has permission to manage users
    if not current_user.has_permission("manage_users"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to manage user permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.remove_permission(db, permission_name) 