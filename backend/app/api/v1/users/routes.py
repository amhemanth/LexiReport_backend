from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.deps import get_db, get_current_active_user, get_current_user
from app.core.security import verify_password, get_password_hash
from app.core.permissions import Permission, require_permission, require_admin
from app.models.core.user import User
from app.models.core.enums import UserRole
from app.repositories.user import UserRepository
from app.services.user import UserService, user_service
from app.schemas.user import (
    UserResponse, UserUpdate, UserList, PasswordUpdate,
    PermissionUpdate, RoleUpdate
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import uuid
from app.core.exceptions import PermissionDeniedError

class PermissionUpdate(BaseModel):
    """Schema for permission update."""
    permissions: List[str]

    def validate_permissions(self):
        """Validate that all permissions are valid."""
        valid_permissions = [p.value for p in Permission]
        invalid_permissions = [p for p in self.permissions if p not in valid_permissions]
        if invalid_permissions:
            raise ValueError(f"Invalid permissions: {', '.join(invalid_permissions)}")

class RoleUpdate(BaseModel):
    """Schema for role update."""
    role: UserRole

router = APIRouter()

user_repository = UserRepository(User)
user_service = UserService(user_repository)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Get current user profile."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Update current user profile."""
    return user_service.update_user(db, current_user.id, user_update)

@router.get("/me/permissions", response_model=List[str])
def get_current_user_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[str]:
    """Get current user permissions."""
    return user_service.get_user_permissions(db, current_user.id)

@router.get("/me/preferences")
def get_current_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current user preferences."""
    preferences = user_service.get_user_preferences(db, current_user.id)
    return {
        "theme": preferences.theme,
        "language": preferences.language,
        "timezone": preferences.timezone,
        "notification_settings": preferences.notification_settings,
        "display_settings": preferences.display_settings,
        "accessibility_settings": preferences.accessibility_settings,
        "email_enabled": preferences.email_enabled,
        "push_enabled": preferences.push_enabled,
        "in_app_enabled": preferences.in_app_enabled,
        "notification_frequency": preferences.notification_frequency,
        "quiet_hours_start": preferences.quiet_hours_start,
        "quiet_hours_end": preferences.quiet_hours_end
    }

@router.put("/me/preferences")
def update_current_user_preferences(
    preferences_update: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update current user preferences."""
    preferences = user_service.update_user_preferences(db, current_user.id, preferences_update)
    return {
        "theme": preferences.theme,
        "language": preferences.language,
        "timezone": preferences.timezone,
        "notification_settings": preferences.notification_settings,
        "display_settings": preferences.display_settings,
        "accessibility_settings": preferences.accessibility_settings,
        "email_enabled": preferences.email_enabled,
        "push_enabled": preferences.push_enabled,
        "in_app_enabled": preferences.in_app_enabled,
        "notification_frequency": preferences.notification_frequency,
        "quiet_hours_start": preferences.quiet_hours_start,
        "quiet_hours_end": preferences.quiet_hours_end
    }

@router.get("/me/activity")
def get_current_user_activity(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get current user activity."""
    return user_service.get_user_activity(db, current_user.id, skip, limit)

# Admin only routes
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Get user by ID (admin only)."""
    if not current_user.is_superuser:
        raise PermissionDeniedError()
    return user_service.get_user(db, user_id)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Update user (admin only)."""
    if not current_user.is_superuser:
        raise PermissionDeniedError()
    return user_service.update_user(db, user_id, user_update)

@router.get("/{user_id}/permissions", response_model=List[str])
def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[str]:
    """Get user permissions (admin only)."""
    if not current_user.is_superuser:
        raise PermissionDeniedError()
    return user_service.get_user_permissions(db, user_id)

@router.put("/{user_id}/permissions", response_model=List[str])
def update_user_permissions(
    user_id: str,
    permissions: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[str]:
    """Update user permissions (admin only)."""
    if not current_user.is_superuser:
        raise PermissionDeniedError()
    return user_service.update_user_permissions(db, user_id, permissions)

@router.get("/", response_model=UserList)
@require_permission(Permission.READ_USERS)
async def read_users(
    *,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of users. Only admins can see all users."""
    try:
        if current_user.role != UserRole.ADMIN:
            # Regular users can only see their own data
            users = [current_user]
            total = 1
        else:
            skip = (page - 1) * size
            users = db.query(User).offset(skip).limit(size).all()
            total = db.query(User).count()
        
        pages = (total + size - 1) // size
        
        return UserList(
            items=users,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Admin-only routes
@router.post("/{user_id}/permissions", response_model=UserResponse)
@require_admin
async def update_user_permissions(
    *,
    user_id: uuid.UUID,
    permission_update: PermissionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user permissions. Only admins can update permissions."""
    try:
        # Validate permissions
        permission_update.validate_permissions()
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update permissions
        current_permissions = set(user.get_permissions())
        new_permissions = set(permission_update.permissions)
        
        # Add new permissions
        for permission in new_permissions - current_permissions:
            try:
                user.add_permission(db, permission)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        # Remove old permissions
        for permission in current_permissions - new_permissions:
            try:
                user.remove_permission(db, permission)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{user_id}/role", response_model=UserResponse)
@require_admin
async def update_user_role(
    *,
    user_id: uuid.UUID,
    role_update: RoleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user role. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Remove existing primary user role(s)
    for user_role in user.user_roles:
        if user_role.is_primary:
            db.delete(user_role)
    db.flush()

    # Get the new role object
    new_role = db.query(Role).filter(Role.name == role_update.role.value).first()
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_update.role.value}' not found"
        )

    # Add new primary user role
    from app.models.core.user_role import UserRole
    import uuid as uuidlib
    from datetime import datetime, timezone
    new_user_role = UserRole(
        id=uuidlib.uuid4(),
        user_id=user.id,
        role_id=new_role.id,
        is_primary=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(new_user_role)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/activate", response_model=UserResponse)
@require_admin
async def activate_user(
    *,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate a user. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/deactivate", response_model=UserResponse)
@require_admin
async def deactivate_user(
    *,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user 