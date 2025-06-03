import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.repositories.user import user_repository
import uuid
from datetime import datetime, timezone

client = TestClient(app)

def test_register_user():
    """Test user registration with valid data"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "StrongP@ssw0rd123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Registration successful"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "api_access" in data["permissions"]
    assert "read_users" in data["permissions"]
    assert "write_users" in data["permissions"]

def test_register_user_invalid_password():
    """Test user registration with invalid password"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test2@example.com",
            "password": "weak",  # Too short
            "full_name": "Test User"
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_register_user_invalid_email():
    """Test user registration with invalid email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "StrongP@ssw0rd123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_register_duplicate_email():
    """Test user registration with duplicate email"""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "StrongP@ssw0rd123",
            "full_name": "Test User"
        }
    )
    
    # Second registration with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "StrongP@ssw0rd123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already registered"

def test_login_success():
    """Test successful login"""
    # First register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "StrongP@ssw0rd123",
            "full_name": "Login Test"
        }
    )
    
    # Then try to login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "StrongP@ssw0rd123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "user"
    assert "permissions" in data

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"

def test_get_current_user():
    """Test getting current user information"""
    # First register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "current@example.com",
            "password": "StrongP@ssw0rd123",
            "full_name": "Current User"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "current@example.com",
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
    assert data["email"] == "current@example.com"
    assert data["full_name"] == "Current User"
    assert "permissions" in data

def test_get_current_user_unauthorized():
    """Test getting current user without token"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"

def test_password_requirements():
    """Test password validation requirements"""
    test_cases = [
        {
            "password": "short",  # Too short
            "expected_status": 422
        },
        {
            "password": "no_uppercase123!",  # No uppercase
            "expected_status": 422
        },
        {
            "password": "NO_LOWERCASE123!",  # No lowercase
            "expected_status": 422
        },
        {
            "password": "NoSpecialChar123",  # No special char
            "expected_status": 422
        },
        {
            "password": "NoNumbers!",  # No numbers
            "expected_status": 422
        },
        {
            "password": "ValidP@ssw0rd123",  # Valid password
            "expected_status": 200
        }
    ]
    
    for test_case in test_cases:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"test_{uuid.uuid4()}@example.com",
                "password": test_case["password"],
                "full_name": "Test User"
            }
        )
        assert response.status_code == test_case["expected_status"]

def test_token_expiration():
    """Test token expiration"""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "expire@example.com",
            "password": "StrongP@ssw0rd123",
            "full_name": "Expire Test"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "expire@example.com",
            "password": "StrongP@ssw0rd123"
        }
    )
    token = login_response.json()["access_token"]
    
    # TODO: Add test for token expiration
    # This would require mocking the token expiration time
    # or waiting for the token to expire naturally 