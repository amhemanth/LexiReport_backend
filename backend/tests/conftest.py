"""Test configuration and fixtures."""
import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import get_db
from app.core.security import create_access_token
from app.models.core.user import User, UserRole
from app.models.core.permission import Permission
from app.models.core.user_permission import UserPermission
import uuid

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_client() -> Generator:
    """Create a test client."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Create a test database session."""
    from app.db.session import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Test User",
        is_active=True,
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db_session: Session) -> User:
    """Create a test admin user."""
    admin = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Admin User",
        is_active=True,
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_permission(db_session: Session) -> Permission:
    """Create a test permission."""
    permission = Permission(
        id=uuid.uuid4(),
        name="test_permission",
        description="Test permission",
        module="test",
        action="test",
        is_active=True
    )
    db_session.add(permission)
    db_session.commit()
    db_session.refresh(permission)
    return permission

@pytest.fixture(scope="function")
def test_user_permission(db_session: Session, test_user: User, test_permission: Permission) -> UserPermission:
    """Create a test user permission."""
    user_permission = UserPermission(
        id=uuid.uuid4(),
        user_id=test_user.id,
        permission_id=test_permission.id,
        is_active=True
    )
    db_session.add(user_permission)
    db_session.commit()
    db_session.refresh(user_permission)
    return user_permission

@pytest.fixture(scope="function")
def user_token_headers(test_user: User) -> Dict[str, str]:
    """Create token headers for test user."""
    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def admin_token_headers(test_admin: User) -> Dict[str, str]:
    """Create token headers for test admin."""
    access_token = create_access_token(
        data={"sub": str(test_admin.id), "email": test_admin.email}
    )
    return {"Authorization": f"Bearer {access_token}"} 