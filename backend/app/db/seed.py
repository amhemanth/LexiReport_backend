"""
Database seeding module.
This module provides functions to seed the database with initial data.
"""

from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.core.user import User, UserRole
from app.models.core.permission import Permission
from app.models.core.user_permission import UserPermission
from app.models.core.user_preferences import UserPreferences
from app.models.core.user_activity import UserActivity

def seed_database(db: Session) -> None:
    """Seed the database with initial data."""
    # Create permissions
    permissions = create_permissions(db)
    
    # Create admin user
    admin_user = create_admin_user(db, permissions)
    
    # Create user preferences
    create_user_preferences(db, admin_user.id)
    
    # Create initial user activity
    create_initial_user_activity(db, admin_user.id)

def create_permissions(db: Session) -> dict:
    """Create initial permissions."""
    permissions = {
        # User management
        "users:create": Permission(
            id=uuid4(),
            name="users:create",
            description="Can create new users",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "users:read": Permission(
            id=uuid4(),
            name="users:read",
            description="Can view user details",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "users:update": Permission(
            id=uuid4(),
            name="users:update",
            description="Can update user details",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "users:delete": Permission(
            id=uuid4(),
            name="users:delete",
            description="Can delete users",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    }
    
    for permission in permissions.values():
        db.add(permission)
    db.commit()
    
    return permissions

def create_admin_user(db: Session, permissions: dict) -> User:
    """Create admin user with all permissions."""
    admin_user = User(
        id=uuid4(),
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="System Administrator",
        is_active=True,
        is_superuser=True,
        meta_data={"is_initial_admin": True},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # Assign all permissions to admin
    for permission in permissions.values():
        user_permission = UserPermission(
            id=uuid4(),
            user_id=admin_user.id,
            permission_id=permission.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user_permission)
    
    db.commit()
    return admin_user

def create_user_preferences(db: Session, user_id: UUID) -> None:
    """Create user preferences for the admin user."""
    preferences = UserPreferences(
        id=uuid4(),
        user_id=user_id,
        theme="light",
        language="en",
        timezone="UTC",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(preferences)
    db.commit()

def create_initial_user_activity(db: Session, user_id: UUID) -> None:
    """Create initial user activity for the admin user."""
    activity = UserActivity(
        id=uuid4(),
        user_id=user_id,
        activity_type="login",
        description="Initial login",
        ip_address="127.0.0.1",
        user_agent="System",
        created_at=datetime.utcnow()
    )
    
    db.add(activity)
    db.commit() 