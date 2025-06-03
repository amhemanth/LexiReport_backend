import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db

# Get test settings
settings = get_settings()

# Create test database URL
TEST_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/test_{settings.POSTGRES_DB}"

# Create test engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    # Create test database
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    from app.models.user import User
    from app.models.permission import Permission
    from app.models.user_permission import UserPermission
    from app.core.security import get_password_hash
    import uuid
    from datetime import datetime, timezone

    # Create test user
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        role="user",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.flush()

    # Add permissions
    permissions = ["api_access", "read_users", "write_users"]
    for perm_name in permissions:
        permission = Permission(name=perm_name)
        db_session.add(permission)
        db_session.flush()
        
        user_permission = UserPermission(
            id=uuid.uuid4(),
            user_id=user.id,
            permission_id=permission.id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(user_permission)

    db_session.commit()
    return user

@pytest.fixture(scope="function")
def test_admin(db_session):
    """Create a test admin user."""
    from app.models.user import User
    from app.models.permission import Permission
    from app.models.user_permission import UserPermission
    from app.core.security import get_password_hash
    import uuid
    from datetime import datetime, timezone

    # Create admin user
    admin = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        full_name="Admin User",
        is_active=True,
        role="admin",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(admin)
    db_session.flush()

    # Add all permissions
    permissions = ["api_access", "read_users", "write_users", "manage_users"]
    for perm_name in permissions:
        permission = Permission(name=perm_name)
        db_session.add(permission)
        db_session.flush()
        
        user_permission = UserPermission(
            id=uuid.uuid4(),
            user_id=admin.id,
            permission_id=permission.id,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(user_permission)

    db_session.commit()
    return admin 