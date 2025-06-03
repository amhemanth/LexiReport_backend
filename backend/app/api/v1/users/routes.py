from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.core.security import verify_password, get_password_hash
from app.core.permissions import Permission, require_permission, require_admin
from app.models.user import User, UserRole
from app.models.enums import UserRole
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.schemas.user import (
    UserResponse, UserUpdate, UserList, PasswordUpdate,
    PermissionUpdate, RoleUpdate
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel

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
@require_permission(Permission.API_ACCESS)
async def read_user_me(
    *,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's data."""
    user_dict = current_user.__dict__.copy()
    user_dict["permissions"] = current_user.get_permissions()
    return user_dict

@router.get("/{user_id}", response_model=UserResponse)
@require_permission(Permission.READ_USERS)
async def read_user(
    *,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID. Only allows users to access their own data or admins to access any data."""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_dict = user.__dict__.copy()
    user_dict["permissions"] = user.get_permissions()
    return user_dict

@router.put("/me", response_model=UserResponse)
@require_permission(Permission.API_ACCESS)
async def update_user_me(
    *,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(lambda: user_service)
):
    """Update current user's data."""
    user = user_service.update_user(db, db_obj=current_user, obj_in=user_in)
    return user

@router.put("/{user_id}", response_model=UserResponse)
@require_permission(Permission.WRITE_USERS)
async def update_user(
    *,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(lambda: user_service)
):
    """Update user. Only allows users to update their own data or admins to update any data."""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's data"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user = user_service.update_user(db, db_obj=user, obj_in=user_in)
    return user

@router.put("/me/password", response_model=UserResponse)
@require_permission(Permission.API_ACCESS)
async def update_password(
    *,
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's password."""
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    hashed_password = get_password_hash(password_update.new_password)
    user = user_repository.update(
        db,
        db_obj=current_user,
        obj_in=UserUpdate(),
        hashed_password=hashed_password,
        password_updated_at=datetime.now(timezone.utc)
    )
    return user

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
    
    user.role = role_update.role
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