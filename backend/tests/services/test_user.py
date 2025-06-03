import pytest
from unittest.mock import MagicMock
from app.services.user import UserService
from app.core.exceptions import UserNotFoundError, DatabaseError
import uuid

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_user_repository():
    repo = MagicMock()
    repo.get.return_value = MagicMock(id=uuid.uuid4(), email='test@example.com')
    repo.get_multi.return_value = [MagicMock(id=uuid.uuid4(), email='test1@example.com'), MagicMock(id=uuid.uuid4(), email='test2@example.com')]
    repo.update.return_value = MagicMock(id=uuid.uuid4(), email='updated@example.com')
    repo.remove.return_value = None
    return repo

@pytest.fixture
def user_service(mock_user_repository):
    return UserService(mock_user_repository)

def test_get_user_success(user_service, mock_db, mock_user_repository):
    user_id = uuid.uuid4()
    mock_user_repository.get.return_value = MagicMock(id=user_id, email='test@example.com')
    user = user_service.get_user(mock_db, user_id)
    assert user.id == user_id
    assert user.email == 'test@example.com'

def test_get_user_not_found(user_service, mock_db, mock_user_repository):
    mock_user_repository.get.return_value = None
    with pytest.raises(UserNotFoundError):
        user_service.get_user(mock_db, uuid.uuid4())

def test_get_users_success(user_service, mock_db, mock_user_repository):
    users = user_service.get_users(mock_db)
    assert len(users) == 2

def test_update_user_success(user_service, mock_db, mock_user_repository):
    db_obj = MagicMock(id=uuid.uuid4(), email='old@example.com')
    obj_in = MagicMock()
    mock_user_repository.update.return_value = MagicMock(id=db_obj.id, email='updated@example.com')
    user = user_service.update_user(mock_db, db_obj=db_obj, obj_in=obj_in)
    assert user.email == 'updated@example.com'

def test_update_user_not_found(user_service, mock_db, mock_user_repository):
    db_obj = MagicMock(id=uuid.uuid4(), email='old@example.com')
    obj_in = MagicMock()
    mock_user_repository.update.return_value = None
    with pytest.raises(UserNotFoundError):
        user_service.update_user(mock_db, db_obj=db_obj, obj_in=obj_in)

def test_delete_user_success(user_service, mock_db, mock_user_repository):
    user_id = uuid.uuid4()
    mock_user_repository.get.return_value = MagicMock(id=user_id, email='test@example.com')
    user_service.delete_user(mock_db, user_id=user_id)
    mock_user_repository.remove.assert_called_once_with(mock_db, id=user_id)

def test_delete_user_not_found(user_service, mock_db, mock_user_repository):
    user_id = uuid.uuid4()
    mock_user_repository.get.return_value = None
    with pytest.raises(UserNotFoundError):
        user_service.delete_user(mock_db, user_id=user_id) 