"""Database seeding script for initial data."""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from app.config.settings import get_settings
from app.db.base import *  # Import all models from base.py
from app.core.security import get_password_hash
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_session():
    """Create and return a database session."""
    try:
        settings = get_settings()
        logger.info(f"Creating database session with URI: {settings.SQLALCHEMY_DATABASE_URI}")
        
        engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Test the connection
        session.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        
        return session
    except Exception as e:
        logger.error(f"Error creating database session: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        raise

def create_default_permissions(db: Session) -> Dict[str, Permission]:
    """Create default permissions."""
    try:
        permissions = {
            "user:read": Permission(name="user:read", description="Read user information"),
            "user:write": Permission(name="user:write", description="Create and update users"),
            "user:delete": Permission(name="user:delete", description="Delete users"),
            "user:manage": Permission(name="user:manage", description="Manage users and permissions"),
            "report:read": Permission(name="report:read", description="Read reports"),
            "report:write": Permission(name="report:write", description="Create and update reports"),
            "report:delete": Permission(name="report:delete", description="Delete reports"),
            "report:share": Permission(name="report:share", description="Share reports with others"),
            "report:manage": Permission(name="report:manage", description="Manage all reports"),
            "comment:read": Permission(name="comment:read", description="Read comments"),
            "comment:write": Permission(name="comment:write", description="Create and update comments"),
            "comment:delete": Permission(name="comment:delete", description="Delete comments"),
            "tag:read": Permission(name="tag:read", description="Read tags"),
            "tag:write": Permission(name="tag:write", description="Create and update tags"),
            "tag:delete": Permission(name="tag:delete", description="Delete tags"),
            "system:access": Permission(name="system:access", description="Access the system"),
            "system:admin": Permission(name="system:admin", description="Administrative access")
        }
        
        for permission in permissions.values():
            db.add(permission)
        db.commit()
        logger.info(f"Successfully created {len(permissions)} permissions")
        return permissions
    except Exception as e:
        logger.error(f"Error creating permissions: {str(e)}")
        db.rollback()
        raise

def create_default_roles(db: Session, permissions: Dict[str, Permission]) -> Dict[str, Role]:
    """Create default roles with permissions."""
    try:
        roles = {
            "admin": Role(name="admin", description="Administrator with full access", is_system=True),
            "manager": Role(name="manager", description="Manager with elevated access", is_system=True),
            "user": Role(name="user", description="Regular user with basic access", is_system=True),
        }
        
        # Add roles to database
        for role in roles.values():
            db.add(role)
        db.commit()
        logger.info(f"Successfully created {len(roles)} roles")
        
        # Assign permissions to roles
        role_permissions = {
            "admin": ["system:access", "system:admin", "user:read", "user:write", "user:delete", "user:manage",
                     "report:read", "report:write", "report:delete", "report:share", "report:manage",
                     "comment:read", "comment:write", "comment:delete", "tag:read", "tag:write", "tag:delete"],
            "manager": ["system:access", "user:read", "report:read", "report:write", "report:share",
                       "comment:read", "comment:write", "tag:read", "tag:write"],
            "user": ["system:access", "report:read", "comment:read", "comment:write", "tag:read"]
        }
        
        # Create role-permission associations
        for role_name, permission_names in role_permissions.items():
            role = roles[role_name]
            for perm_name in permission_names:
                permission = permissions[perm_name]
                role_permission = RolePermission(role=role, permission=permission)
                db.add(role_permission)
        
        db.commit()
        logger.info("Successfully assigned permissions to roles")
        return roles
    except Exception as e:
        logger.error(f"Error creating roles: {str(e)}")
        db.rollback()
        raise

def create_admin_user(db: Session, roles: Dict[str, Role]) -> User:
    """Create admin user with all permissions."""
    try:
        admin = User(
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info(f"Created admin user with ID: {admin.id}")
        
        # Set admin password
        password = Password(
            user_id=admin.id,
            hashed_password=get_password_hash("admin123")
        )
        db.add(password)
        
        # Assign admin role
        user_role = UserRole(user_id=admin.id, role_id=roles["admin"].id)
        db.add(user_role)
        
        # Create user preferences
        preferences = UserPreferences(
            user_id=admin.id,
            theme="light",
            language="en",
            timezone="UTC",
            email_notifications=True,
            push_notifications=True
        )
        db.add(preferences)
        
        db.commit()
        logger.info("Successfully set up admin user with password and preferences")
        return admin
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        db.rollback()
        raise

def create_sample_data(db: Session, admin: User) -> None:
    """Create sample data for testing."""
    try:
        # Create sample report
        report = Report(
            title="Sample Report",
            description="A sample report for testing",
            status=ReportStatus.DRAFT,
            type=ReportType.ANALYSIS,
            category=ReportTypeCategory.GENERAL,
            created_by=admin.id,
            updated_by=admin.id
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        logger.info(f"Created sample report with ID: {report.id}")
        
        # Create report content
        content = ReportContent(
            report_id=report.id,
            content={"sections": [{"title": "Introduction", "content": "This is a sample report."}]},
            version=1,
            created_by=admin.id
        )
        db.add(content)
        
        # Create sample tag
        tag = Tag(
            name="sample",
            description="Sample tag",
            created_by=admin.id
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        logger.info(f"Created sample tag with ID: {tag.id}")
        
        # Tag the report
        entity_tag = EntityTag(
            entity_type="report",
            entity_id=report.id,
            tag_id=tag.id,
            user_id=admin.id
        )
        db.add(entity_tag)
        
        # Create sample comment
        comment = Comment(
            content="This is a sample comment",
            entity_type="report",
            entity_id=report.id,
            user_id=admin.id
        )
        db.add(comment)
        
        # Create sample user activity
        activity = UserActivity(
            user_id=admin.id,
            activity_type=ActivityType.CREATE,
            entity_type="report",
            entity_id=report.id,
            metadata={"action": "created_report"}
        )
        db.add(activity)
        
        # Create sample audit log
        audit_log = AuditLog(
            user_id=admin.id,
            action=AuditAction.CREATE,
            entity_type="report",
            entity_id=report.id,
            changes={"title": "Sample Report"}
        )
        db.add(audit_log)
        
        # Create change history
        change_history = ChangeHistory(
            audit_log_id=audit_log.id,
            field_name="title",
            old_value=None,
            new_value="Sample Report"
        )
        db.add(change_history)
        
        db.commit()
        logger.info("Successfully created all sample data")
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        db.rollback()
        raise

def seed_database(db: Session) -> None:
    """Seed the database with initial data."""
    try:
        # Create permissions
        logger.info("Creating default permissions...")
        permissions = create_default_permissions(db)
        
        # Create roles
        logger.info("Creating default roles...")
        roles = create_default_roles(db, permissions)
        
        # Create admin user
        logger.info("Creating admin user...")
        admin = create_admin_user(db, roles)
        
        # Create sample data
        logger.info("Creating sample data...")
        create_sample_data(db, admin)
        
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        db.rollback()
        raise

def seed():
    """Main seeding function."""
    logger.info("Starting database seeding process...")
    db = None
    try:
        db = get_db_session()
        seed_database(db)
    except Exception as e:
        logger.error(f"Error during database seeding: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        raise
    finally:
        if db is not None:
            db.close()
            logger.info("Database session closed")

if __name__ == "__main__":
    seed() 