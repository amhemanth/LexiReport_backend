import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.permission import Permission
from app.models.user_permission import UserPermission
import uuid
from datetime import datetime, timezone

def test_get_user_me(client, test_user):
    """Test getting current user information"""
    # Login as test user
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert data["role"] == test_user.role
    assert "permissions" in data
    assert len(data["permissions"]) == 3  # api_access, read_users, write_users

def test_get_user_by_id(client, test_user, test_admin):
    """Test getting user by ID with different permission levels"""
    # Login as admin
    admin_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    admin_token = admin_login.json()["access_token"]
    
    # Admin can get any user
    response = client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    
    # Login as regular user
    user_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    user_token = user_login.json()["access_token"]
    
    # Regular user can get their own info
    response = client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    
    # Regular user cannot get other users' info
    response = client.get(
        f"/api/v1/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_update_user(client, test_user):
    """Test updating user information"""
    # Login as user
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Update user info
    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com"
    }
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

def test_update_user_permissions(client, test_user, test_admin):
    """Test updating user permissions"""
    # Login as admin
    admin_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    admin_token = admin_login.json()["access_token"]
    
    # Admin can update permissions
    new_permissions = ["api_access", "read_users", "write_users", "manage_users"]
    response = client.post(
        f"/api/v1/users/{test_user.id}/permissions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"permissions": new_permissions}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["permissions"]) == len(new_permissions)
    
    # Regular user cannot update permissions
    user_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    user_token = user_login.json()["access_token"]
    
    response = client.post(
        f"/api/v1/users/{test_user.id}/permissions",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"permissions": new_permissions}
    )
    assert response.status_code == 403

def test_update_user_role(client, test_user, test_admin):
    """Test updating user role"""
    # Login as admin
    admin_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    admin_token = admin_login.json()["access_token"]
    
    # Admin can update role
    response = client.put(
        f"/api/v1/users/{test_user.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    
    # Regular user cannot update role
    user_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    user_token = user_login.json()["access_token"]
    
    response = client.put(
        f"/api/v1/users/{test_user.id}/role",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"role": "admin"}
    )
    assert response.status_code == 403

def test_list_users(client, test_user, test_admin):
    """Test listing users with different permission levels"""
    # Login as admin
    admin_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    admin_token = admin_login.json()["access_token"]
    
    # Admin can list all users
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # At least admin and test user
    
    # Login as regular user
    user_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    user_token = user_login.json()["access_token"]
    
    # Regular user can only see themselves
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == test_user.email

def test_deactivate_user(client, test_user, test_admin):
    """Test deactivating a user"""
    # Login as admin
    admin_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    admin_token = admin_login.json()["access_token"]
    
    # Admin can deactivate user
    response = client.put(
        f"/api/v1/users/{test_user.id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False
    
    # Deactivated user cannot login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Inactive user"

def test_reactivate_user(client, test_user, test_admin):
    """Test reactivating a user"""
    # First deactivate the user
    admin_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_admin.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    admin_token = admin_login.json()["access_token"]
    
    client.put(
        f"/api/v1/users/{test_user.id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Admin can reactivate user
    response = client.put(
        f"/api/v1/users/{test_user.id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == True
    
    # Reactivated user can login
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_password_update(client, test_user):
    """Test updating user password"""
    # Login as user
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Update password
    new_password = "NewStrongP@ssw0rd123"
    response = client.put(
        f"/api/v1/users/{test_user.id}/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "StrongP@ssw0rd123",
            "new_password": new_password
        }
    )
    assert response.status_code == 200
    
    # Try login with new password
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": new_password
        }
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    
    # Try login with old password
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "StrongP@ssw0rd123"
        }
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid credentials" 