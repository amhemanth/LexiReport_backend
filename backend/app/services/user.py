"""User service."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.core.user import User
from app.models.core.user_permission import UserPermission
from app.models.audit.user_activity import UserActivity
from app.models.core.user_preferences import UserPreferences
from app.models.core.permission import Permission
from app.core.exceptions import (
    DatabaseError,
    NotFoundException,
    ValidationException,
    PermissionDeniedError
)
from app.core.logger import logger

class UserService:
    """Service for user operations."""

    def __init__(self, user_repository):
        """Initialize the user service with dependencies."""
        self.user_repository = user_repository

    def get_user(self, db: Session, user_id: uuid.UUID) -> User:
        """Get a user by ID."""
        try:
            user = self.user_repository.get(db, id=user_id)
            if not user:
                raise NotFoundException("User not found")
            return user
        except NotFoundException as e:
            logger.error(f"User not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise DatabaseError("Failed to get user")

    def get_user_by_email(self, db: Session, email: str) -> User:
        """Get a user by email."""
        try:
            user = self.user_repository.get_by_email(db, email=email)
            if not user:
                raise NotFoundException("User not found")
            return user
        except NotFoundException as e:
            logger.error(f"User not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise DatabaseError("Failed to get user")

    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get a list of users."""
        try:
            return self.user_repository.get_multi(db, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise DatabaseError("Failed to get users")

    def update_user(
        self,
        db: Session,
        user_id: uuid.UUID,
        obj_in: UserUpdate
    ) -> User:
        """Update a user."""
        try:
            user = self.get_user(db, user_id=user_id)
            if not user.is_active:
                raise PermissionDeniedError("Inactive user cannot update profile")
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(user, field, value)
            db.commit()
            db.refresh(user)
            return user
        except NotFoundException as e:
            logger.error(f"User not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise DatabaseError("Failed to update user")

    def get_user_permissions(
        self,
        db: Session,
        user_id: uuid.UUID
    ) -> List[str]:
        """Get user permissions."""
        try:
            user = self.get_user(db, user_id=user_id)
            return [p.name for p in user.permissions]
        except NotFoundException as e:
            logger.error(f"User not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            raise DatabaseError("Failed to get user permissions")

    def update_user_permissions(
        self,
        db: Session,
        user_id: uuid.UUID,
        permissions: List[str]
    ) -> List[str]:
        """Update user permissions."""
        try:
            user = self.get_user(db, user_id=user_id)
            
            # Remove existing permissions
            self.user_repository.remove_all_permissions(db, user_id=user_id)
            
            # Add new permissions
            for perm_name in permissions:
                permission = self.user_repository.get_permission_by_name(db, name=perm_name)
                if permission:
                    self.user_repository.add_permission(db, user_id=user_id, permission_id=permission.id)
            
            db.commit()
            db.refresh(user)
            return [p.name for p in user.permissions]
        except NotFoundException as e:
            logger.error(f"User not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating user permissions: {str(e)}")
            raise DatabaseError("Failed to update user permissions")

    def get_user_preferences(
        self,
        db: Session,
        user_id: uuid.UUID
    ) -> UserPreferences:
        """Get user preferences."""
        try:
            user = self.get_user(db, user_id=user_id)
            if not user.preferences:
                # Create default preferences if none exist
                preferences = UserPreferences(user_id=user_id)
                db.add(preferences)
                db.commit()
                db.refresh(preferences)
                return preferences
            return user.preferences
        except Exception as e:
            db.rollback()
            logger.error(f"Error getting user preferences: {str(e)}")
            raise DatabaseError("Failed to get user preferences")

    def update_user_preferences(
        self,
        db: Session,
        user_id: uuid.UUID,
        preferences: Dict[str, Any]
    ) -> UserPreferences:
        """Update user preferences."""
        try:
            user = self.get_user(db, user_id=user_id)
            if not user.is_active:
                raise PermissionDeniedError("Inactive user cannot update preferences")
            user_preferences = self.get_user_preferences(db, user_id=user_id)
            for field, value in preferences.items():
                if hasattr(user_preferences, field):
                    setattr(user_preferences, field, value)
            db.commit()
            db.refresh(user_preferences)
            return user_preferences
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user preferences: {str(e)}")
            raise DatabaseError("Failed to update user preferences")

    def get_user_activity(
        self,
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user activity."""
        try:
            activities = db.query(UserActivity).filter(
                UserActivity.user_id == user_id
            ).order_by(
                UserActivity.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            return [
                {
                    "id": str(activity.id),
                    "type": activity.type,
                    "description": activity.description,
                    "created_at": activity.created_at.isoformat(),
                    "metadata": activity.metadata
                }
                for activity in activities
            ]
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            raise DatabaseError("Failed to get user activity")

# Create service instance
user_service = UserService(user_repository) 