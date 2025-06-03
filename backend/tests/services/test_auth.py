import pytest
from unittest.mock import MagicMock, patch
from app.services.auth import AuthService
from app.schemas.auth import UserCreate, UserLogin, Token
from app.models.user import User, UserRole
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError, InactiveUserError, DatabaseError
import uuid

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_user_repository():
    repo = MagicMock()
    repo.get_by_email.return_value = None
    repo.create.return_value = MagicMock(id=uuid.uuid4(), email='test@example.com', role=UserRole.USER, is_active=True, get_permissions=lambda: ['api_access', 'read_users', 'write_users'])
    repo.get_current_password.return_value = MagicMock(hashed_password='hashed')
    return repo

@pytest.fixture
def auth_service(mock_user_repository):
    return AuthService(mock_user_repository)

@patch('app.services.auth.get_password_hash', return_value='hashed')
def test_register_success(mock_hash, auth_service, mock_db, mock_user_repository):
    user_in = UserCreate(email='test@example.com', full_name='Test User', password='Password1!')
    result = auth_service.register(mock_db, user_in)
    assert result['message'] == 'Registration successful'
    assert result['email'] == 'test@example.com'

@patch('app.services.auth.get_password_hash', return_value='hashed')
def test_register_user_already_exists(mock_hash, auth_service, mock_db, mock_user_repository):
    mock_user_repository.get_by_email.return_value = True
    user_in = UserCreate(email='test@example.com', full_name='Test User', password='Password1!')
    with pytest.raises(UserAlreadyExistsError):
        auth_service.register(mock_db, user_in)

@patch('app.services.auth.verify_password', return_value=True)
@patch('app.services.auth.create_access_token', return_value='token')
def test_login_success(mock_token, mock_verify, auth_service, mock_db, mock_user_repository):
    mock_user_repository.get_by_email.return_value = MagicMock(id=uuid.uuid4(), email='test@example.com', role=UserRole.USER, is_active=True, get_permissions=lambda: ['api_access'])
    mock_user_repository.get_current_password.return_value = MagicMock(hashed_password='hashed')
    user_in = UserLogin(email='test@example.com', password='password')
    token = auth_service.login(mock_db, user_in)
    assert isinstance(token, Token)
    assert token.access_token == 'token'
    assert token.token_type == 'bearer'

@patch('app.services.auth.verify_password', return_value=False)
def test_login_invalid_password(mock_verify, auth_service, mock_db, mock_user_repository):
    mock_user_repository.get_by_email.return_value = MagicMock(id=uuid.uuid4(), email='test@example.com', role=UserRole.USER, is_active=True, get_permissions=lambda: ['api_access'])
    mock_user_repository.get_current_password.return_value = MagicMock(hashed_password='hashed')
    user_in = UserLogin(email='test@example.com', password='wrong')
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(mock_db, user_in)

@patch('app.services.auth.verify_password', return_value=True)
def test_login_inactive_user(mock_verify, auth_service, mock_db, mock_user_repository):
    mock_user_repository.get_by_email.return_value = MagicMock(id=uuid.uuid4(), email='test@example.com', role=UserRole.USER, is_active=False, get_permissions=lambda: ['api_access'])
    mock_user_repository.get_current_password.return_value = MagicMock(hashed_password='hashed')
    user_in = UserLogin(email='test@example.com', password='password')
    with pytest.raises(InactiveUserError):
        auth_service.login(mock_db, user_in) 