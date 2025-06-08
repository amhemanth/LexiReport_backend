"""Database seeding script for initial data."""
import logging
import uuid
from datetime import datetime, timezone, timedelta, time
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from app.config.settings import get_settings
from app.db.base import *  # Import all models from base.py
from app.core.security import get_password_hash
from typing import Dict
from contextlib import contextmanager
from app.models.reports.enums import ReportType, ReportStatus, ReportTypeCategory
from app.models.notifications.enums import NotificationType, NotificationStatus
from app.models.files.enums import FileType, FileStatus
from app.models.processing.enums import ProcessingType, ProcessingStatus
from app.models.integration.enums import BIPlatformType, SyncStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_db_session():
    """Create and return a database session with proper transaction handling."""
    settings = get_settings()
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def get_or_create_permission(db, name, description):
    permission = db.query(Permission).filter_by(name=name).first()
    if not permission:
        now = datetime.now(timezone.utc)
        permission = Permission(
            name=name,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        db.add(permission)
        db.flush()
    return permission

def get_or_create_role(db, name, description):
    role = db.query(Role).filter_by(name=name).first()
    if not role:
        now = datetime.now(timezone.utc)
        role = Role(
            name=name,
            description=description,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        db.add(role)
        db.flush()
    return role

def get_or_create_role_permission(db, role_id, permission_id):
    rp = db.query(RolePermission).filter_by(role_id=role_id, permission_id=permission_id).first()
    if not rp:
        rp = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(rp)
        db.flush()
    return rp

def get_or_create_user(db, email, username, full_name, is_active, is_superuser, meta_data=None):
    user = db.query(User).filter_by(email=email).first()
    if not user:
        now = datetime.now(timezone.utc)
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
            meta_data=meta_data or {},
            created_at=now,
            updated_at=now
        )
        db.add(user)
        db.flush()
    return user

def get_or_create_user_role(db, user_id, role_id, is_primary=True):
    ur = db.query(UserRole).filter_by(user_id=user_id, role_id=role_id).first()
    if not ur:
        now = datetime.now(timezone.utc)
        ur = UserRole(
            user_id=user_id,
            role_id=role_id,
            is_primary=is_primary,
            created_by=user_id,
            created_at=now,
            updated_at=now
        )
        db.add(ur)
        db.flush()
    return ur

def get_or_create_user_preferences(db, user_id):
    pref = db.query(UserPreferences).filter_by(user_id=user_id).first()
    if not pref:
        pref = UserPreferences(
            user_id=user_id,
            theme="light",
            language="en",
            timezone="UTC",
            notification_settings={
                "email": True,
                "push": True,
                "in_app": True
            },
            display_settings={
                "font_size": "medium",
                "color_scheme": "default"
            },
            accessibility_settings={
                "high_contrast": False,
                "screen_reader": False
            },
            is_default=True,
            email_enabled=True,
            push_enabled=True,
            in_app_enabled=True,
            notification_frequency="immediate",
            quiet_hours_start=time(22, 0),  # 10:00 PM
            quiet_hours_end=time(7, 0)      # 7:00 AM
        )
        db.add(pref)
        db.flush()
    return pref

def get_or_create_password(db, user_id, password):
    pw = db.query(Password).filter_by(user_id=user_id).first()
    if not pw:
        now = datetime.now(timezone.utc)
        pw = Password(
            user_id=user_id,
            hashed_password=get_password_hash(password),
            is_current=True,
            password_updated_at=now,
            created_at=now
        )
        db.add(pw)
        db.flush()
    return pw

def get_or_create_notification(db, user_id, title, message, type, status, is_important=False):
    notification = db.query(Notification).filter_by(
        user_id=user_id,
        title=title,
        type=type
    ).first()
    
    if not notification:
        now = datetime.now(timezone.utc)
        notification = Notification(
            user_id=user_id,
            template_id=None,  # No template for system notifications
            title=title,
            message=message,
            type=type,
            status=status,
            data={},  # Empty data for system notifications
            is_important=is_important,
            read_at=None,
            expires_at=now + timedelta(days=30),  # Expire after 30 days
            entity_type=None,
            entity_id=None,
            created_at=now,
            updated_at=now
        )
        db.add(notification)
        db.flush()
    return notification

def get_or_create_tag(db, name, description=None, color=None, is_system=False):
    tag = db.query(Tag).filter_by(name=name).first()
    if not tag:
        now = datetime.now(timezone.utc)
        tag = Tag(
            name=name,
            description=description,
            color=color,
            is_system=is_system,
            created_at=now,
            updated_at=now
        )
        db.add(tag)
        db.flush()
    return tag

def get_or_create_report(db, title, description, type, category, created_by, is_public=False):
    report = db.query(Report).filter_by(title=title).first()
    if not report:
        now = datetime.now(timezone.utc)
        report = Report(
            title=title,
            description=description,
            type=type,
            category=category,
            is_public=is_public,
            created_by=created_by,
            created_at=now,
            updated_at=now
        )
        db.add(report)
        db.flush()
    return report

def get_or_create_report_content(db, report_id, content_type, content_data):
    content = db.query(ReportContent).filter_by(
        report_id=report_id,
        content_type=content_type
    ).first()
    
    if not content:
        now = datetime.now(timezone.utc)
        content = ReportContent(
            report_id=report_id,
            content_type=content_type,
            content_data=content_data,
            version=1,
            created_at=now,
            updated_at=now
        )
        db.add(content)
        db.flush()
    return content

def get_or_create_report_schedule(db, report_id, name, schedule, recipients, format, created_by):
    schedule_obj = db.query(ReportSchedule).filter_by(
        report_id=report_id,
        name=name
    ).first()
    
    if not schedule_obj:
        now = datetime.now(timezone.utc)
        schedule_obj = ReportSchedule(
            report_id=report_id,
            name=name,
            description=f"Schedule for {name}",
            schedule=schedule,
            recipients=recipients,
            format=format,
            is_active=True,
            last_run=None,
            next_run=now + timedelta(days=30),  # Set next run to 30 days from now
            created_by=created_by,
            updated_by=created_by,
            created_at=now,
            updated_at=now
        )
        db.add(schedule_obj)
        db.flush()
    return schedule_obj

def get_or_create_bi_connection(db, name, platform_type, connection_details):
    connection = db.query(BIConnection).filter_by(name=name).first()
    if not connection:
        now = datetime.now(timezone.utc)
        connection = BIConnection(
            name=name,
            platform_type=platform_type,
            connection_details=connection_details,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        db.add(connection)
        db.flush()
    return connection

def create_sample_data(db: Session, admin: User) -> None:
    """Create sample data for testing."""
    try:
        logger.info("Starting to create sample data...")
        
        # Create sample report
        report = get_or_create_report(
            db=db,
            title="Monthly Sales Report",
            description="Monthly sales analysis report",
            type=ReportType.STANDARD,
            category=ReportTypeCategory.ANALYTICAL,
            created_by=admin.id,
            is_public=True
        )
        
        # Create report content
        report_content = get_or_create_report_content(
            db=db,
            report_id=report.id,
            content_type="analytics",
            content_data={
                "charts": [
                    {
                        "type": "bar",
                        "title": "Monthly Sales",
                        "data": {
                            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                            "datasets": [
                                {
                                    "label": "Sales",
                                    "data": [1000, 1200, 900, 1500, 1800, 2000]
                                }
                            ]
                        }
                    }
                ]
            }
        )
        
        # Create report schedule
        report_schedule = get_or_create_report_schedule(
            db=db,
            report_id=report.id,
            name="Monthly Schedule",
            schedule={"cron": "0 0 1 * *"},  # Run at midnight on the 1st of each month
            recipients=["admin@example.com"],
            format="PDF",
            created_by=admin.id
        )
        
        # Create sample tags
        tags = [
            get_or_create_tag(db, "Important", "High priority items", "#FF0000", True),
            get_or_create_tag(db, "Review", "Needs review", "#FFA500"),
            get_or_create_tag(db, "Completed", "Completed items", "#00FF00")
        ]
        
        # Create sample BI connection
        bi_connection = get_or_create_bi_connection(
            db=db,
            name="Production BI",
            platform_type=BIPlatformType.POWER_BI,
            connection_details={
                "workspace_id": "sample-workspace",
                "dataset_id": "sample-dataset"
            }
        )
        
        # Create sample notifications
        notifications = [
            get_or_create_notification(
                db=db,
                user_id=admin.id,
                title="Welcome to the System",
                message="Welcome to the reporting system!",
                type=NotificationType.SYSTEM,
                status=NotificationStatus.UNREAD,
                is_important=True
            ),
            get_or_create_notification(
                db=db,
                user_id=admin.id,
                title="Report Generated",
                message="Your monthly report has been generated.",
                type=NotificationType.REPORT,
                status=NotificationStatus.UNREAD
            )
        ]
        
        logger.info("Sample data created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        raise

def seed_database(db: Session) -> None:
    """Seed the database with initial data."""
    try:
        logger.info("Starting database seeding...")
        
        # Create permissions
        permissions = {
            "admin": get_or_create_permission(db, "admin", "Administrator access"),
            "user": get_or_create_permission(db, "user", "Regular user access"),
            "report_create": get_or_create_permission(db, "report:create", "Create reports"),
            "report_read": get_or_create_permission(db, "report:read", "Read reports"),
            "report_update": get_or_create_permission(db, "report:update", "Update reports"),
            "report_delete": get_or_create_permission(db, "report:delete", "Delete reports")
        }
        
        # Create roles
        roles = {
            "admin": get_or_create_role(db, "admin", "Administrator role"),
            "user": get_or_create_role(db, "user", "Regular user role")
        }
        
        # Assign permissions to roles
        role_permissions = {
            "admin": [p.id for p in permissions.values()],
            "user": [permissions["report_read"].id]
        }
        
        for role_name, permission_ids in role_permissions.items():
            for permission_id in permission_ids:
                get_or_create_role_permission(db, roles[role_name].id, permission_id)
        
        # Create admin user
        admin = get_or_create_user(
            db=db,
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            is_active=True,
            is_superuser=True
        )
        
        # Set admin password
        get_or_create_password(db, admin.id, "admin123")
        
        # Assign admin role to admin user
        get_or_create_user_role(db, admin.id, roles["admin"].id)
        
        # Create user preferences for admin
        get_or_create_user_preferences(db, admin.id)
        
        # Create sample data
        create_sample_data(db, admin)
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        raise

def seed():
    """Main seeding function."""
    with get_db_session() as db:
        seed_database(db)

if __name__ == "__main__":
    seed() 