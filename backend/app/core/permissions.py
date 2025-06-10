from enum import Enum
from typing import Optional, Callable, List, Dict
from fastapi import HTTPException, status, Depends
from functools import wraps
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import json

from app.models.core.user import User
from app.models.core.enums import UserRole
from app.db.session import get_db
from app.core.deps import get_current_user, get_current_active_user
from app.core.exceptions import PermissionException
from app.core.redis import get_redis_client

redis_client = get_redis_client()

class Permission(str, Enum):
    """Available permissions in the system."""
    # User management
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    MANAGE_USERS = "manage_users"
    API_ACCESS = "api_access"

    # Comments
    READ_COMMENTS = "read_comments"
    WRITE_COMMENTS = "write_comments"
    MANAGE_COMMENTS = "manage_comments"
    MENTION_USERS = "mention_users"

    # Voice
    READ_VOICE = "read_voice"
    WRITE_VOICE = "write_voice"
    MANAGE_VOICE = "manage_voice"
    TEXT_TO_SPEECH = "text_to_speech"

    # Audit
    READ_AUDIT = "read_audit"
    WRITE_AUDIT = "write_audit"
    MANAGE_AUDIT = "manage_audit"
    VIEW_METRICS = "view_metrics"
    VIEW_ERRORS = "view_errors"

    @classmethod
    def validate_permission(cls, permission_name: str) -> bool:
        """Validate if a permission name is valid."""
        return permission_name in [p.value for p in cls]

def log_permission_change(
    actor_id: UUID,
    target_id: UUID,
    action: str,
    permission: str,
    reason: Optional[str] = None
):
    """Log permission changes for audit purposes."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "actor_id": str(actor_id),
        "target_id": str(target_id),
        "action": action,
        "permission": permission,
        "reason": reason
    }
    
    # Store in Redis for quick access
    redis_client.lpush(
        "permission_audit_log",
        json.dumps(log_entry)
    )
    redis_client.ltrim("permission_audit_log", 0, 999)  # Keep last 1000 entries

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
            
            # Check if permission is temporarily revoked
            if redis_client.exists(f"revoked_permission:{current_user.id}:{permission}"):
                raise PermissionException(f"Permission {permission} is temporarily revoked")
            
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
            
            # Check if any permission is temporarily revoked
            for permission in required_permissions:
                if redis_client.exists(f"revoked_permission:{current_user.id}:{permission}"):
                    raise PermissionException(f"Permission {permission} is temporarily revoked")
            
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
    
    # Get base permissions
    permissions = user.get_permissions()
    
    # Check for temporarily revoked permissions
    revoked_permissions = redis_client.keys(f"revoked_permission:{user_id}:*")
    for revoked in revoked_permissions:
        permission = revoked.split(":")[-1]
        if permission in permissions:
            permissions.remove(permission)
    
    return permissions

def assign_permission(
    user_id: UUID,
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reason: Optional[str] = None
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
    
    # Log the permission change
    log_permission_change(
        actor_id=current_user.id,
        target_id=user_id,
        action="assign",
        permission=permission_name,
        reason=reason
    )
    
    return user.add_permission(db, permission_name)

def remove_permission(
    user_id: UUID,
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reason: Optional[str] = None
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
    
    # Log the permission change
    log_permission_change(
        actor_id=current_user.id,
        target_id=user_id,
        action="remove",
        permission=permission_name,
        reason=reason
    )
    
    return user.remove_permission(db, permission_name)

def temporarily_revoke_permission(
    user_id: UUID,
    permission_name: str,
    duration_minutes: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reason: Optional[str] = None
) -> bool:
    """Temporarily revoke a permission from a user."""
    if not current_user:
        raise PermissionException("Authentication required")
    
    # Check if current user has permission to manage users
    if not current_user.has_permission(Permission.MANAGE_USERS):
        raise PermissionException("Not authorized to manage user permissions")
    
    # Validate permission name
    if not Permission.validate_permission(permission_name):
        raise PermissionException(f"Invalid permission: {permission_name}")
    
    # Prevent revoking critical permissions
    if permission_name == Permission.API_ACCESS.value:
        raise PermissionException("Cannot revoke api_access permission")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise PermissionException("User not found")
    
    # Set temporary revocation
    redis_client.setex(
        f"revoked_permission:{user_id}:{permission_name}",
        duration_minutes * 60,
        "1"
    )
    
    # Log the permission change
    log_permission_change(
        actor_id=current_user.id,
        target_id=user_id,
        action="temporary_revoke",
        permission=permission_name,
        reason=reason
    )
    
    return True

def get_permission_audit_log(
    user_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """Get permission audit log entries."""
    if not current_user:
        raise PermissionException("Authentication required")
    
    # Check if user has permission to view audit logs
    if not current_user.has_permission(Permission.READ_AUDIT):
        raise PermissionException("Not authorized to view audit logs")
    
    # Get all log entries
    log_entries = redis_client.lrange("permission_audit_log", 0, -1)
    entries = []
    
    for entry in log_entries:
        entry_data = json.loads(entry)
        
        # Apply filters
        if user_id and entry_data["target_id"] != str(user_id):
            continue
            
        entry_date = datetime.fromisoformat(entry_data["timestamp"])
        if start_date and entry_date < start_date:
            continue
        if end_date and entry_date > end_date:
            continue
            
        entries.append(entry_data)
    
    return entries 