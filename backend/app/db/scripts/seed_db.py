"""Database seeding script for initial data."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config.settings import get_settings
from app.models.user import User, UserRole
from app.models.password import Password
from app.models.permission import Permission
from app.models.user_permission import UserPermission
import bcrypt

# Default permissions
PERMISSIONS = [
    ("api_access", "Access the API"),
    ("read_users", "Read user data"),
    ("write_users", "Modify user data"),
    ("manage_users", "Manage users and permissions"),
]

# Admin user defaults
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "Admin User"

def get_db_session():
    """Create and return a database session."""
    settings = get_settings()
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def seed_permissions(session) -> list:
    """Seed default permissions and return the permission objects."""
    permission_objs = []
    for name, desc in PERMISSIONS:
        perm = session.query(Permission).filter_by(name=name).first()
        if not perm:
            perm = Permission(id=uuid.uuid4(), name=name, description=desc)
            session.add(perm)
        permission_objs.append(perm)
    session.commit()
    return permission_objs

def seed_admin_user(session, permissions: list):
    """Create admin user with all permissions."""
    # Create or get admin user
    admin = session.query(User).filter_by(email=ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            id=uuid.uuid4(),
            email=ADMIN_EMAIL,
            full_name=ADMIN_FULL_NAME,
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
            hashed_password=hash_password(ADMIN_PASSWORD),
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
    """Main seeding function."""
    session = get_db_session()
    try:
        # Seed permissions
        permissions = seed_permissions(session)
        
        # Seed admin user with permissions
        seed_admin_user(session, permissions)
        
        print("Successfully seeded database with initial data.")
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed() 