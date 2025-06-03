import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, backend_dir)

"""Database seeding script for test data."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config.settings import get_settings
from app.models.user import User, UserRole
from app.models.password import Password
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.core.security import get_password_hash

# Default permissions for test environment
PERMISSIONS = [
    ("api_access", "Access the API"),
    ("read_users", "Read user data"),
    ("write_users", "Modify user data"),
    ("manage_users", "Manage users and permissions"),
]

# Test user defaults
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "StrongP@ssw0rd123!"
TEST_USER_FULL_NAME = "Test User"

def get_test_db_session():
    """Create and return a test database session."""
    settings = get_settings()
    # Override database name for test
    settings.POSTGRES_DB = "test_lexireport"
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def seed_test_permissions(session) -> list:
    """Seed test permissions and return the permission objects."""
    permission_objs = []
    for name, desc in PERMISSIONS:
        perm = session.query(Permission).filter_by(name=name).first()
        if not perm:
            perm = Permission(id=uuid.uuid4(), name=name, description=desc)
            session.add(perm)
        permission_objs.append(perm)
    session.commit()
    return permission_objs

def seed_test_user(session, permissions: list):
    """Create test user with basic permissions."""
    # Create or get test user
    user = session.query(User).filter_by(email=TEST_USER_EMAIL).first()
    if not user:
        user = User(
            id=uuid.uuid4(),
            email=TEST_USER_EMAIL,
            full_name=TEST_USER_FULL_NAME,
            is_active=True,
            role=UserRole.USER,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(user)
        session.commit()

    # Create user password
    user_password = session.query(Password).filter_by(user_id=user.id, is_current=True).first()
    if not user_password:
        user_password = Password(
            id=uuid.uuid4(),
            user_id=user.id,
            hashed_password=get_password_hash(TEST_USER_PASSWORD),
            password_updated_at=datetime.now(timezone.utc),
            is_current=True,
            created_at=datetime.now(timezone.utc),
        )
        session.add(user_password)
        session.commit()

    # Assign basic permissions to user
    basic_permissions = ["api_access", "read_users", "write_users"]
    for perm in permissions:
        if perm.name in basic_permissions:
            up = session.query(UserPermission).filter_by(user_id=user.id, permission_id=perm.id).first()
            if not up:
                up = UserPermission(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    permission_id=perm.id,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(up)
    session.commit()

def seed_test_admin(session, permissions: list):
    """Create test admin user with all permissions."""
    # Create or get admin user
    admin = session.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        admin = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            full_name="Admin User",
            is_active=True,
            role=UserRole.ADMIN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(admin)
        session.commit()

    # Create admin password
    admin_password = session.query(Password).filter_by(user_id=admin.id, is_current=True).first()
    if not admin_password:
        admin_password = Password(
            id=uuid.uuid4(),
            user_id=admin.id,
            hashed_password=get_password_hash(TEST_USER_PASSWORD),
            password_updated_at=datetime.now(timezone.utc),
            is_current=True,
            created_at=datetime.now(timezone.utc),
        )
        session.add(admin_password)
        session.commit()

    # Assign all permissions to admin
    for perm in permissions:
        up = session.query(UserPermission).filter_by(user_id=admin.id, permission_id=perm.id).first()
        if not up:
            up = UserPermission(
                id=uuid.uuid4(),
                user_id=admin.id,
                permission_id=perm.id,
                created_at=datetime.now(timezone.utc),
            )
            session.add(up)
    session.commit()

def seed():
    """Seed the test database with initial data."""
    session = get_test_db_session()
    try:
        # Seed permissions
        permissions = seed_test_permissions(session)
        
        # Seed test user
        seed_test_user(session, permissions)
        
        # Seed test admin
        seed_test_admin(session, permissions)
        
        print("Test database seeded successfully")
    except Exception as e:
        print(f"Error seeding test database: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed() 