"""Database seeding script."""
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    try:
        logger.info("Starting database seeding...")
        
        # Create roles
        roles = create_roles(db)
        logger.info(f"Created {len(roles)} roles")
        
        # Create permissions
        permissions = create_permissions(db)
        logger.info(f"Created {len(permissions)} permissions")
        
        # Assign permissions to roles
        assign_permissions_to_roles(db, roles, permissions)
        logger.info("Assigned permissions to roles")
        
        # Create users
        users = create_users(db, roles)
        logger.info("Created users")
        
        # Create user activities
        create_user_activities(db, users)
        logger.info("Created user activities")
        
        # Create tags
        tags = create_tags(db)
        logger.info("Created tags")
        
        # Create sample files
        files = create_sample_files(db, users)
        logger.info("Created sample files")
        
        # Create sample documents
        documents = create_sample_documents(db, users)
        logger.info("Created sample documents")
        
        # Create sample comments
        create_sample_comments(db, users, documents)
        logger.info("Created sample comments")
        
        # Create sample BI integrations
        create_sample_bi_integrations(db, users)
        logger.info("Created sample BI integrations")
        
        # Commit all changes
        db.commit()
        logger.info("Successfully committed all changes to database")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {str(e)}")
        raise
    finally:
        db.close()

def create_roles(db: Session) -> dict:
    """Create system roles."""
    roles = {
        "admin": Role(
            id=uuid.uuid4(),
            name="admin",
            description="System administrator with full access",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "user": Role(
            id=uuid.uuid4(),
            name="user",
            description="Regular user with standard access",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "manager": Role(
            id=uuid.uuid4(),
            name="manager",
            description="Manager with elevated access",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    }
    
    for role in roles.values():
        db.add(role)
    db.flush()
    return roles

def create_permissions(db: Session) -> dict:
    """Create system permissions."""
    permissions = {
        # User management permissions
        "user_create": Permission(
            id=uuid.uuid4(),
            name="user:create",
            description="Create new users",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "user_read": Permission(
            id=uuid.uuid4(),
            name="user:read",
            description="View user information",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "user_update": Permission(
            id=uuid.uuid4(),
            name="user:update",
            description="Update user information",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "user_delete": Permission(
            id=uuid.uuid4(),
            name="user:delete",
            description="Delete users",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        # Role management permissions
        "role_create": Permission(
            id=uuid.uuid4(),
            name="role:create",
            description="Create new roles",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "role_read": Permission(
            id=uuid.uuid4(),
            name="role:read",
            description="View role information",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "role_update": Permission(
            id=uuid.uuid4(),
            name="role:update",
            description="Update role information",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "role_delete": Permission(
            id=uuid.uuid4(),
            name="role:delete",
            description="Delete roles",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        # Permission management permissions
        "permission_create": Permission(
            id=uuid.uuid4(),
            name="permission:create",
            description="Create new permissions",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "permission_read": Permission(
            id=uuid.uuid4(),
            name="permission:read",
            description="View permission information",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "permission_update": Permission(
            id=uuid.uuid4(),
            name="permission:update",
            description="Update permission information",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "permission_delete": Permission(
            id=uuid.uuid4(),
            name="permission:delete",
            description="Delete permissions",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        # System management permissions
        "system_settings_read": Permission(
            id=uuid.uuid4(),
            name="system:settings:read",
            description="View system settings",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "system_settings_update": Permission(
            id=uuid.uuid4(),
            name="system:settings:update",
            description="Update system settings",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        # Audit and logging permissions
        "audit_logs_read": Permission(
            id=uuid.uuid4(),
            name="audit:logs:read",
            description="View audit logs",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "audit_logs_export": Permission(
            id=uuid.uuid4(),
            name="audit:logs:export",
            description="Export audit logs",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        # Report management permissions
        "report_create": Permission(
            id=uuid.uuid4(),
            name="report:create",
            description="Create reports",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "report_read": Permission(
            id=uuid.uuid4(),
            name="report:read",
            description="View reports",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "report_update": Permission(
            id=uuid.uuid4(),
            name="report:update",
            description="Update reports",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        "report_delete": Permission(
            id=uuid.uuid4(),
            name="report:delete",
            description="Delete reports",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    }
    
    for permission in permissions.values():
        db.add(permission)
    db.flush()
    return permissions

def assign_permissions_to_roles(db: Session, roles: dict, permissions: dict):
    """Assign permissions to roles."""
    now = datetime.utcnow()
    
    # Admin role gets all permissions
    for permission in permissions.values():
        role_permission = RolePermission(
            id=uuid.uuid4(),
            role_id=roles["admin"].id,
            permission_id=permission.id,
            created_at=now,
            updated_at=now
        )
        db.add(role_permission)
    
    # Manager role permissions
    manager_permissions = [
        "user_read",
        "user_create",
        "user_update",
        "role_read",
        "permission_read",
        "system_settings_read",
        "audit_logs_read",
        "report_create",
        "report_read",
        "report_update",
        "report_delete"
    ]
    
    for perm_name in manager_permissions:
        role_permission = RolePermission(
            id=uuid.uuid4(),
            role_id=roles["manager"].id,
            permission_id=permissions[perm_name].id,
            created_at=now,
            updated_at=now
        )
        db.add(role_permission)
    
    # User role permissions - more granular access
    user_permissions = [
        "user_read",
        "role_read",
        "permission_read",
        "system_settings_read",
        "audit_logs_read",
        "report_read"
    ]
    
    for perm_name in user_permissions:
        role_permission = RolePermission(
            id=uuid.uuid4(),
            role_id=roles["user"].id,
            permission_id=permissions[perm_name].id,
            created_at=now,
            updated_at=now
        )
        db.add(role_permission)
    db.flush()

def create_users(db: Session, roles: dict) -> dict:
    """Create initial users."""
    now = datetime.utcnow()
    users = {}
    
    # Create admin user
    admin = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        username="admin",
        full_name="System Administrator",
        is_active=True,
        is_superuser=True,
        meta_data={"is_seed": True},
        last_login=now,
        created_at=now,
        updated_at=now
    )
    db.add(admin)
    db.flush()
    users["admin"] = admin
    
    # Add admin role
    admin_role = UserRole(
        id=uuid.uuid4(),
        user_id=admin.id,
        role_id=roles["admin"].id,
        created_at=now,
        updated_at=now
    )
    db.add(admin_role)
    
    # Create admin preferences
    admin_preferences = UserPreferences(
        id=uuid.uuid4(),
        user_id=admin.id,
        theme="dark",
        language="en",
        notifications_enabled=True,
        created_at=now,
        updated_at=now
    )
    db.add(admin_preferences)
    
    # Create manager user
    manager = User(
        id=uuid.uuid4(),
        email="manager@example.com",
        username="manager",
        full_name="System Manager",
        is_active=True,
        is_superuser=False,
        meta_data={"is_seed": True},
        last_login=now,
        created_at=now,
        updated_at=now
    )
    db.add(manager)
    db.flush()
    users["manager"] = manager
    
    # Add manager role
    manager_role = UserRole(
        id=uuid.uuid4(),
        user_id=manager.id,
        role_id=roles["manager"].id,
        created_at=now,
        updated_at=now
    )
    db.add(manager_role)
    
    # Create manager preferences
    manager_preferences = UserPreferences(
        id=uuid.uuid4(),
        user_id=manager.id,
        theme="light",
        language="en",
        notifications_enabled=True,
        created_at=now,
        updated_at=now
    )
    db.add(manager_preferences)
    
    # Create regular user
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        username="user",
        full_name="Regular User",
        is_active=True,
        is_superuser=False,
        meta_data={"is_seed": True},
        last_login=now,
        created_at=now,
        updated_at=now
    )
    db.add(user)
    db.flush()
    users["user"] = user
    
    # Add user role
    user_role = UserRole(
        id=uuid.uuid4(),
        user_id=user.id,
        role_id=roles["user"].id,
        created_at=now,
        updated_at=now
    )
    db.add(user_role)
    
    # Create user preferences
    user_preferences = UserPreferences(
        id=uuid.uuid4(),
        user_id=user.id,
        theme="light",
        language="en",
        notifications_enabled=True,
        created_at=now,
        updated_at=now
    )
    db.add(user_preferences)
    
    # Create passwords
    admin_password = Password(
        id=uuid.uuid4(),
        user_id=admin.id,
        hashed_password=get_password_hash("admin123"),
        created_at=now,
        updated_at=now
    )
    db.add(admin_password)
    
    manager_password = Password(
        id=uuid.uuid4(),
        user_id=manager.id,
        hashed_password=get_password_hash("manager123"),
        created_at=now,
        updated_at=now
    )
    db.add(manager_password)
    
    user_password = Password(
        id=uuid.uuid4(),
        user_id=user.id,
        hashed_password=get_password_hash("user123"),
        created_at=now,
        updated_at=now
    )
    db.add(user_password)
    db.flush()
    
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

def create_sample_files(db: Session, users: dict) -> dict:
    """Create sample files."""
    now = datetime.utcnow()
    files = {}
    
    # Create a sample file for each user
    for user_type, user in users.items():
        file = FileStorage(
            id=uuid.uuid4(),
            user_id=user.id,
            file_name=f"{user_type}_sample.pdf",
            file_type=FileType.PDF,
            file_size=1024 * 1024,  # 1MB
            storage_type=StorageType.LOCAL,
            status=FileStatus.COMPLETED,
            meta_data={"is_seed": True},
            created_at=now,
            updated_at=now
        )
        db.add(file)
        db.flush()
        files[user_type] = file
        
        # Create a file version
        version = FileVersion(
            id=uuid.uuid4(),
            file_id=file.id,
            version_number=1,
            file_path=f"/uploads/{file.id}/v1.pdf",
            file_size=file.file_size,
            created_at=now,
            updated_at=now
        )
        db.add(version)
        
        # Create an access log
        access_log = FileAccessLog(
            id=uuid.uuid4(),
            file_id=file.id,
            user_id=user.id,
            action="create",
            created_at=now
        )
        db.add(access_log)
    
    db.flush()
    return files

def create_sample_documents(db: Session, users: dict) -> dict:
    """Create sample documents."""
    now = datetime.utcnow()
    documents = {}
    
    # Create a sample document for each user
    for user_type, user in users.items():
        document = Document(
            id=uuid.uuid4(),
            user_id=user.id,
            title=f"{user_type}'s Document",
            content_type="text/plain",
            content="This is a sample document content.",
            status="active",
            meta_data={"is_seed": True},
            created_at=now,
            updated_at=now
        )
        db.add(document)
        db.flush()
        documents[user_type] = document
        
        # Create document processing record
        processing = DocumentProcessing(
            id=uuid.uuid4(),
            document_id=document.id,
            processing_type=ProcessingType.TEXT_EXTRACTION,
            status=ProcessingStatus.COMPLETED,
            result_data={"extracted_text": "Sample extracted text"},
            created_at=now,
            updated_at=now
        )
        db.add(processing)
    
    db.flush()
    return documents

def create_sample_comments(db: Session, users: dict, documents: dict):
    """Create sample comments."""
    now = datetime.utcnow()
    
    # Create a comment thread for each document
    for user_type, document in documents.items():
        thread = CommentThread(
            id=uuid.uuid4(),
            entity_type="document",
            entity_id=document.id,
            created_at=now,
            updated_at=now
        )
        db.add(thread)
        db.flush()
        
        # Add a comment from each user
        for commenter_type, commenter in users.items():
            comment = Comment(
                id=uuid.uuid4(),
                thread_id=thread.id,
                user_id=commenter.id,
                content=f"Comment from {commenter_type} on {user_type}'s document",
                created_at=now,
                updated_at=now
            )
            db.add(comment)
            
            # Add a mention if it's not the document owner
            if commenter_type != user_type:
                mention = CommentMention(
                    id=uuid.uuid4(),
                    comment_id=comment.id,
                    user_id=users[user_type].id,
                    created_at=now
                )
                db.add(mention)
    
    db.flush()

def create_sample_bi_integrations(db: Session, users: dict):
    """Create sample BI integrations."""
    now = datetime.utcnow()
    
    # Create a BI integration for the admin user
    admin = users["admin"]
    integration = BIIntegration(
        id=uuid.uuid4(),
        user_id=admin.id,
        name="Sample BI Integration",
        integration_type=IntegrationType.POWER_BI,
        status=IntegrationStatus.ACTIVE,
        config={"api_key": "sample_key"},
        created_at=now,
        updated_at=now
    )
    db.add(integration)
    db.flush()
    
    # Create a connection
    connection = BIConnection(
        id=uuid.uuid4(),
        integration_id=integration.id,
        name="Sample Connection",
        connection_string="sample_connection_string",
        is_active=True,
        created_at=now,
        updated_at=now
    )
    db.add(connection)
    
    # Create a dashboard
    dashboard = BIDashboard(
        id=uuid.uuid4(),
        connection_id=connection.id,
        name="Sample Dashboard",
        dashboard_id="sample_dashboard_id",
        is_active=True,
        created_at=now,
        updated_at=now
    )
    db.add(dashboard)
    
    db.flush()

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        logger.error(f"Error in seed_database: {str(e)}")
        sys.exit(1) 