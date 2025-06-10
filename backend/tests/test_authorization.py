"""Authorization tests."""
import pytest
from fastapi import status
from app.core.exceptions import PermissionDeniedError
from app.schemas.auth import TokenResponse

def test_admin_access_success(test_client, admin_token_headers):
    """Test successful admin access."""
    response = test_client.get(
        "/api/v1/admin/users",
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "email" in data[0]
    assert "full_name" in data[0]

def test_admin_access_denied(test_client, user_token_headers):
    """Test admin access denied for regular user."""
    response = test_client.get(
        "/api/v1/admin/users",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "permission denied" in response.json()["detail"].lower()

def test_admin_create_user_success(test_client, admin_token_headers):
    """Test successful user creation by admin."""
    new_user = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "full_name": "New User",
        "role": "user"
    }
    response = test_client.post(
        "/api/v1/admin/users",
        headers=admin_token_headers,
        json=new_user
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == new_user["email"]
    assert data["full_name"] == new_user["full_name"]
    assert "id" in data

def test_admin_create_user_invalid_data(test_client, admin_token_headers):
    """Test user creation with invalid data."""
    invalid_user = {
        "email": "invalid-email",
        "password": "weak",
        "full_name": "Invalid User"
    }
    response = test_client.post(
        "/api/v1/admin/users",
        headers=admin_token_headers,
        json=invalid_user
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "email" in response.json()["detail"][0]["loc"]

def test_admin_update_user_success(test_client, admin_token_headers, test_user):
    """Test successful user update by admin."""
    update_data = {
        "full_name": "Updated Name",
        "is_active": True
    }
    response = test_client.patch(
        f"/api/v1/admin/users/{test_user.id}",
        headers=admin_token_headers,
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["is_active"] == update_data["is_active"]

def test_admin_update_user_not_found(test_client, admin_token_headers):
    """Test user update with non-existent user."""
    update_data = {
        "full_name": "Updated Name"
    }
    response = test_client.patch(
        "/api/v1/admin/users/99999",
        headers=admin_token_headers,
        json=update_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

def test_admin_delete_user_success(test_client, admin_token_headers, test_user):
    """Test successful user deletion by admin."""
    response = test_client.delete(
        f"/api/v1/admin/users/{test_user.id}",
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_admin_delete_user_not_found(test_client, admin_token_headers):
    """Test user deletion with non-existent user."""
    response = test_client.delete(
        "/api/v1/admin/users/99999",
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

def test_user_update_own_profile_success(test_client, user_token_headers, test_user):
    """Test successful profile update by user."""
    update_data = {
        "full_name": "Updated Name",
        "current_password": "password"  # From test_user fixture
    }
    response = test_client.patch(
        "/api/v1/users/me",
        headers=user_token_headers,
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]

def test_user_update_own_profile_invalid_password(test_client, user_token_headers):
    """Test profile update with invalid current password."""
    update_data = {
        "full_name": "Updated Name",
        "current_password": "wrongpassword"
    }
    response = test_client.patch(
        "/api/v1/users/me",
        headers=user_token_headers,
        json=update_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid password" in response.json()["detail"].lower()

def test_user_update_other_profile_denied(test_client, user_token_headers, test_user):
    """Test update of other user's profile denied."""
    update_data = {
        "full_name": "Updated Name"
    }
    response = test_client.patch(
        f"/api/v1/users/{test_user.id + 1}",  # Different user ID
        headers=user_token_headers,
        json=update_data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "permission denied" in response.json()["detail"].lower()

def test_user_delete_own_account_success(test_client, user_token_headers):
    """Test successful account deletion by user."""
    response = test_client.delete(
        "/api/v1/users/me",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_user_delete_other_account_denied(test_client, user_token_headers, test_user):
    """Test deletion of other user's account denied."""
    response = test_client.delete(
        f"/api/v1/users/{test_user.id + 1}",  # Different user ID
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "permission denied" in response.json()["detail"].lower()

def test_role_based_access_control(test_client, user_token_headers, admin_token_headers):
    """Test role-based access control for different endpoints."""
    # Test user endpoints
    user_response = test_client.get(
        "/api/v1/users/me",
        headers=user_token_headers
    )
    assert user_response.status_code == status.HTTP_200_OK

    # Test admin endpoints
    admin_response = test_client.get(
        "/api/v1/admin/users",
        headers=admin_token_headers
    )
    assert admin_response.status_code == status.HTTP_200_OK

    # Test user trying to access admin endpoint
    forbidden_response = test_client.get(
        "/api/v1/admin/users",
        headers=user_token_headers
    )
    assert forbidden_response.status_code == status.HTTP_403_FORBIDDEN

def test_user_access_admin_endpoint(test_client, user_token_headers):
    """Test regular user access to admin endpoint."""
    response = test_client.get(
        "/api/v1/admin/users",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_user_with_permission(test_client, db_session, test_user, test_permission, user_token_headers):
    """Test user access with specific permission."""
    # Add permission to user
    from app.models.core.user_permission import UserPermission
    user_permission = UserPermission(
        user_id=test_user.id,
        permission_id=test_permission.id,
        is_active=True
    )
    db_session.add(user_permission)
    db_session.commit()

    # Test access to endpoint requiring the permission
    response = test_client.get(
        f"/api/v1/test/{test_permission.name}",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK

def test_user_without_permission(test_client, user_token_headers):
    """Test user access without required permission."""
    response = test_client.get(
        "/api/v1/test/restricted",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_inactive_permission(test_client, db_session, test_user, test_permission, user_token_headers):
    """Test access with inactive permission."""
    # Deactivate permission
    test_permission.is_active = False
    db_session.commit()

    response = test_client.get(
        f"/api/v1/test/{test_permission.name}",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_role_based_access(test_client, admin_token_headers, user_token_headers):
    """Test role-based access control."""
    # Admin access
    admin_response = test_client.get(
        "/api/v1/admin/dashboard",
        headers=admin_token_headers
    )
    assert admin_response.status_code == status.HTTP_200_OK

    # User access
    user_response = test_client.get(
        "/api/v1/admin/dashboard",
        headers=user_token_headers
    )
    assert user_response.status_code == status.HTTP_403_FORBIDDEN

def test_multiple_permissions(test_client, db_session, test_user, test_permission, user_token_headers):
    """Test access requiring multiple permissions."""
    # Add another permission
    from app.models.core.permission import Permission
    second_permission = Permission(
        name="second_permission",
        description="Second test permission",
        module="test",
        action="test",
        is_active=True
    )
    db_session.add(second_permission)
    db_session.commit()

    # Add both permissions to user
    from app.models.core.user_permission import UserPermission
    permissions = [
        UserPermission(user_id=test_user.id, permission_id=test_permission.id, is_active=True),
        UserPermission(user_id=test_user.id, permission_id=second_permission.id, is_active=True)
    ]
    db_session.add_all(permissions)
    db_session.commit()

    # Test access to endpoint requiring both permissions
    response = test_client.get(
        "/api/v1/test/multi-permission",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK

def test_permission_inheritance(test_client, db_session, test_user, test_permission, user_token_headers):
    """Test permission inheritance."""
    # Add parent permission
    from app.models.core.permission import Permission
    parent_permission = Permission(
        name="parent_permission",
        description="Parent permission",
        module="test",
        action="test",
        is_active=True
    )
    db_session.add(parent_permission)
    db_session.commit()

    # Add child permission
    child_permission = Permission(
        name="child_permission",
        description="Child permission",
        module="test",
        action="test",
        is_active=True,
        parent_id=parent_permission.id
    )
    db_session.add(child_permission)
    db_session.commit()

    # Add parent permission to user
    from app.models.core.user_permission import UserPermission
    user_permission = UserPermission(
        user_id=test_user.id,
        permission_id=parent_permission.id,
        is_active=True
    )
    db_session.add(user_permission)
    db_session.commit()

    # Test access to endpoint requiring child permission
    response = test_client.get(
        f"/api/v1/test/{child_permission.name}",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK 