"""Database seeding script."""
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.models.core import (
    User, Role, Permission, UserRole, RolePermission,
    UserPreferences, Password, LoginAttempt
)
from app.models.audit import (
    UserActivity, AuditLog, ChangeHistory
)
from app.models.files import (
    FileStorage, FileVersion, FileAccessLog,
    FileType, FileStatus, StorageType
)
from app.models.comments import (
    Comment, CommentThread, CommentMention
)
from app.models.tags import (
    Tag, EntityTag
)
from app.models.processing import (
    Document, DocumentProcessing, DocumentProcessingResult,
    ProcessingType, ProcessingStatus
)
from app.models.integration import (
    BIConnection, BIDashboard, BIIntegration,
    IntegrationType, IntegrationStatus
)
from app.core.security import get_password_hash
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SeedingError(Exception):
    """Custom exception for seeding errors."""
    pass

def validate_data(data: Dict) -> bool:
    """Validate data before insertion.
    
    Args:
        data: Dictionary containing data to validate
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    required_fields = {
        'roles': ['name', 'description'],
        'permissions': ['name', 'description'],
        'users': ['email', 'username', 'password'],
    }
    
    for entity_type, fields in required_fields.items():
        if entity_type in data:
            for item in data[entity_type]:
                if not all(field in item for field in fields):
                    logger.error(f"Missing required fields in {entity_type}: {fields}")
                    return False
    return True

def cleanup_existing_data(db: Session, force: bool = False):
    """Clean up existing data before seeding.
    
    Args:
        db: Database session
        force: If True, will delete all data
    """
    if not force:
        return
        
    try:
        # Delete in reverse order of dependencies
        db.query(CommentMention).delete()
        db.query(Comment).delete()
        db.query(CommentThread).delete()
        db.query(EntityTag).delete()
        db.query(Tag).delete()
        db.query(FileAccessLog).delete()
        db.query(FileVersion).delete()
        db.query(FileStorage).delete()
        db.query(UserActivity).delete()
        db.query(AuditLog).delete()
        db.query(ChangeHistory).delete()
        db.query(UserPreferences).delete()
        db.query(Password).delete()
        db.query(LoginAttempt).delete()
        db.query(UserRole).delete()
        db.query(RolePermission).delete()
        db.query(Permission).delete()
        db.query(Role).delete()
        db.query(User).delete()
        
        db.commit()
        logger.info("Successfully cleaned up existing data")
    except Exception as e:
        db.rollback()
        raise SeedingError(f"Error cleaning up existing data: {str(e)}")

def seed_database(db: Session, force: bool = False):
    """Seed the database with initial data.
    
    Args:
        db: Database session
        force: Whether to force seeding even if data exists
    """
    try:
        logger.info(f"Starting database seeding with force={force}")
        
        # Clean up existing data if force is True
        if force:
            logger.info("Cleaning up existing data...")
            cleanup_existing_data(db, force)
            logger.info("Cleanup completed")
        
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        logger.info(f"Found {existing_roles} existing roles")
        
        if existing_roles > 0 and not force:
            logger.info("Roles already exist in the database. Skipping role creation.")
            roles = {role.name: role for role in db.query(Role).all()}
        else:
            # Create roles
            logger.info("Creating roles...")
            roles = create_roles(db)
            logger.info(f"Created {len(roles)} roles")
            db.flush()
        
        # Check if permissions already exist
        existing_permissions = db.query(Permission).count()
        logger.info(f"Found {existing_permissions} existing permissions")
        
        if existing_permissions > 0 and not force:
            logger.info("Permissions already exist in the database. Skipping permission creation.")
            permissions = {perm.name: perm for perm in db.query(Permission).all()}
        else:
            # Create permissions
            logger.info("Creating permissions...")
            permissions = create_permissions(db)
            logger.info(f"Created {len(permissions)} permissions")
            db.flush()
        
        # Only assign permissions if we're not using existing roles and permissions
        if not (existing_roles > 0 and existing_permissions > 0 and not force):
            logger.info("Assigning permissions to roles...")
            assign_permissions_to_roles(db, roles, permissions)
            logger.info("Assigned permissions to roles")
            db.flush()
        
        # Check if users already exist
        existing_users = db.query(User).count()
        logger.info(f"Found {existing_users} existing users")
        
        if existing_users > 0 and not force:
            logger.info("Users already exist in the database. Skipping user creation.")
            users = {user.email: user for user in db.query(User).all()}
        else:
            # Create users
            logger.info("Creating users...")
            users = create_users(db, roles)
            logger.info(f"Created {len(users)} users")
            db.flush()
        
        # Create tags
        logger.info("Creating tags...")
        tags = create_tags(db)
        logger.info(f"Created {len(tags)} tags")
        db.flush()
        
        # Create user activities
        logger.info("Creating user activities...")
        create_user_activities(db, users)
        logger.info("Created user activities")
        db.flush()
        
        # Commit all changes
        logger.info("Committing all changes...")
        db.commit()
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise SeedingError(f"Failed to seed database: {str(e)}")
    finally:
        # Ensure session is closed
        db.close()

def create_roles(db: Session) -> Dict[str, Role]:
    """Create initial roles.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary of role name to Role object
    """
    roles = {}
    
    # Create admin role
    admin_role = Role(
        name="admin",
        description="System administrator with full access",
        is_active=True
    )
    db.add(admin_role)
    roles["admin"] = admin_role
    
    # Create manager role
    manager_role = Role(
        name="manager",
        description="Manager with elevated access",
        is_active=True
    )
    db.add(manager_role)
    roles["manager"] = manager_role
    
    # Create analyst role
    analyst_role = Role(
        name="analyst",
        description="Data analyst with report management access",
        is_active=True
    )
    db.add(analyst_role)
    roles["analyst"] = analyst_role
    
    # Create viewer role
    viewer_role = Role(
        name="viewer",
        description="Report viewer with read-only access",
        is_active=True
    )
    db.add(viewer_role)
    roles["viewer"] = viewer_role
    
    # Create normal user role
    user_role = Role(
        name="user",
        description="Normal user with basic access to reports and own data",
        is_active=True
    )
    db.add(user_role)
    roles["user"] = user_role
    
    # Flush to ensure all roles are created
    db.flush()
    
    return roles

def create_permissions(db: Session) -> Dict[str, Permission]:
    """Create initial permissions.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary of permission name to Permission object
    """
    permissions = {}
    
    # User management permissions
    user_permissions = [
        ("user:create", "Create new users"),
        ("user:read", "View user information"),
        ("user:update", "Update user information"),
        ("user:delete", "Delete users")
    ]
    
    # Role management permissions
    role_permissions = [
        ("role:create", "Create new roles"),
        ("role:read", "View role information"),
        ("role:update", "Update role information"),
        ("role:delete", "Delete roles")
    ]
    
    # Permission management permissions
    permission_permissions = [
        ("permission:create", "Create new permissions"),
        ("permission:read", "View permission information"),
        ("permission:update", "Update permission information"),
        ("permission:delete", "Delete permissions")
    ]
    
    # System management permissions
    system_permissions = [
        ("system:settings:read", "View system settings"),
        ("system:settings:update", "Update system settings")
    ]
    
    # Audit management permissions
    audit_permissions = [
        ("audit:logs:read", "View audit logs"),
        ("audit:logs:export", "Export audit logs")
    ]
    
    # Report management permissions
    report_permissions = [
        ("report:create", "Create reports"),
        ("report:read", "View reports"),
        ("report:update", "Update reports"),
        ("report:delete", "Delete reports")
    ]
    
    # Create all permissions
    all_permissions = (
        user_permissions +
        role_permissions +
        permission_permissions +
        system_permissions +
        audit_permissions +
        report_permissions
    )
    
    for name, description in all_permissions:
        permission = Permission(
            name=name,
            description=description,
            is_active=True
        )
        db.add(permission)
        permissions[name] = permission
    
    # Flush to ensure all permissions are created
    db.flush()
    
    return permissions

def assign_permissions_to_roles(db: Session, roles: Dict[str, Role], permissions: Dict[str, Permission]) -> None:
    """Assign permissions to roles.
    
    Args:
        db: Database session
        roles: Dictionary of role name to Role object
        permissions: Dictionary of permission name to Permission object
    """
    # Admin role gets all permissions
    for permission in permissions.values():
        role_permission = RolePermission(
            role_id=roles["admin"].id,
            permission_id=permission.id
        )
        db.add(role_permission)
    
    # Manager role permissions
    manager_permissions = [
        "user:read",
        "role:read",
        "permission:read",
        "system:settings:read",
        "audit:logs:read",
        "report:create",
        "report:read",
        "report:update",
        "report:delete"
    ]
    for perm_name in manager_permissions:
        role_permission = RolePermission(
            role_id=roles["manager"].id,
            permission_id=permissions[perm_name].id
        )
        db.add(role_permission)
    
    # Analyst role permissions
    analyst_permissions = [
        "report:create",
        "report:read",
        "report:update"
    ]
    for perm_name in analyst_permissions:
        role_permission = RolePermission(
            role_id=roles["analyst"].id,
            permission_id=permissions[perm_name].id
        )
        db.add(role_permission)
    
    # Viewer role permissions
    viewer_permissions = [
        "report:read"
    ]
    for perm_name in viewer_permissions:
        role_permission = RolePermission(
            role_id=roles["viewer"].id,
            permission_id=permissions[perm_name].id
        )
        db.add(role_permission)
    
    # Normal user role permissions
    user_permissions = [
        "user:read",  # Can read own user data
        "user:update",  # Can update own user data
        "report:read",  # Can view reports
        "report:update"  # Can update reports
    ]
    for perm_name in user_permissions:
        role_permission = RolePermission(
            role_id=roles["user"].id,
            permission_id=permissions[perm_name].id
        )
        db.add(role_permission)
    
    # Flush to ensure all role permissions are created
    db.flush()

def create_users(db: Session, roles: Dict[str, Role]) -> Dict[str, User]:
    """Create initial users with roles.
    
    Args:
        db: Database session
        roles: Dictionary of role name to Role object
        
    Returns:
        Dictionary of email to User object
    """
    users = {}
    
    # Create admin user
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
            meta_data={"is_seed": True},
            last_login=datetime.utcnow()
        )
        db.add(admin_user)
        db.flush()  # Flush to get the ID
        
        # Create user role association
        user_role = UserRole(
            user_id=admin_user.id,
            role_id=roles["admin"].id
        )
        db.add(user_role)
        users["admin@example.com"] = admin_user
    
    # Create manager user
    manager_user = db.query(User).filter(User.email == "manager@example.com").first()
    if not manager_user:
        manager_user = User(
            email="manager@example.com",
            username="manager",
            full_name="Project Manager",
            is_active=True,
            is_superuser=False,
            meta_data={"is_seed": True},
            last_login=datetime.utcnow()
        )
        db.add(manager_user)
        db.flush()  # Flush to get the ID
        
        # Create user role association
        user_role = UserRole(
            user_id=manager_user.id,
            role_id=roles["manager"].id
        )
        db.add(user_role)
        users["manager@example.com"] = manager_user
    
    # Create analyst user
    analyst_user = db.query(User).filter(User.email == "analyst@example.com").first()
    if not analyst_user:
        analyst_user = User(
            email="analyst@example.com",
            username="analyst",
            full_name="Data Analyst",
            is_active=True,
            is_superuser=False,
            meta_data={"is_seed": True},
            last_login=datetime.utcnow()
        )
        db.add(analyst_user)
        db.flush()  # Flush to get the ID
        
        # Create user role association
        user_role = UserRole(
            user_id=analyst_user.id,
            role_id=roles["analyst"].id
        )
        db.add(user_role)
        users["analyst@example.com"] = analyst_user
    
    # Create viewer user
    viewer_user = db.query(User).filter(User.email == "viewer@example.com").first()
    if not viewer_user:
        viewer_user = User(
            email="viewer@example.com",
            username="viewer",
            full_name="Report Viewer",
            is_active=True,
            is_superuser=False,
            meta_data={"is_seed": True},
            last_login=datetime.utcnow()
        )
        db.add(viewer_user)
        db.flush()  # Flush to get the ID
        
        # Create user role association
        user_role = UserRole(
            user_id=viewer_user.id,
            role_id=roles["viewer"].id
        )
        db.add(user_role)
        users["viewer@example.com"] = viewer_user
    
    # Add any existing users to the dictionary
    existing_users = db.query(User).filter(
        User.email.in_(["admin@example.com", "manager@example.com", "analyst@example.com", "viewer@example.com"])
    ).all()
    for user in existing_users:
        users[user.email] = user
    
    return users

def create_user_activities(db: Session, users: dict):
    """Create initial user activities."""
    now = datetime.utcnow()
    
    # Create activities for each user
    for user_type, user in users.items():
        # Account creation activity
        creation_activity = UserActivity(
            id=uuid.uuid4(),
            user_id=user.id,
            activity_type="account_creation",
            description=f"Initial {user_type} account creation",
            entity_type="user",
            entity_id=user.id,
            created_at=now
        )
        db.add(creation_activity)
        
        # Login activity
        login_activity = UserActivity(
            id=uuid.uuid4(),
            user_id=user.id,
            activity_type="login",
            description=f"{user_type} user logged in",
            entity_type="user",
            entity_id=user.id,
            created_at=now
        )
        db.add(login_activity)
        
        # Profile update activity
        profile_activity = UserActivity(
            id=uuid.uuid4(),
            user_id=user.id,
            activity_type="profile_update",
            description=f"{user_type} user updated profile",
            entity_type="user",
            entity_id=user.id,
            created_at=now
        )
        db.add(profile_activity)
    
    db.flush()

def create_tags(db: Session) -> dict:
    """Create system tags."""
    now = datetime.utcnow()
    tags = {
        "important": Tag(
            id=uuid.uuid4(),
            name="important",
            description="Important items",
            is_system=True,
            created_at=now,
            updated_at=now
        ),
        "review": Tag(
            id=uuid.uuid4(),
            name="review",
            description="Items needing review",
            is_system=True,
            created_at=now,
            updated_at=now
        ),
        "archived": Tag(
            id=uuid.uuid4(),
            name="archived",
            description="Archived items",
            is_system=True,
            created_at=now,
            updated_at=now
        )
    }
    
    for tag in tags.values():
        db.add(tag)
    db.flush()
    return tags

if __name__ == "__main__":
    try:
        db = SessionLocal()
        seed_database(db, force=True)
    except Exception as e:
        logger.error(f"Error in seed_database: {str(e)}")
        sys.exit(1) 