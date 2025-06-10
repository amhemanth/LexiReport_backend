"""Authentication tests."""
import pytest
from fastapi import status
from app.schemas.user import UserCreate
from app.core.exceptions import AuthenticationError, ValidationException
from app.schemas.auth import (
    RegisterRequest, LoginRequest, PasswordResetRequest,
    PasswordResetConfirm, TokenResponse
)

def test_register_user_success(test_client, db_session):
    """Test successful user registration."""
    user_data = RegisterRequest(
        email="newuser@example.com",
        password="StrongPass123!",
        full_name="New User",
        confirm_password="StrongPass123!"
    )
    response = test_client.post("/api/v1/auth/register", json=user_data.dict())
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user_id" in data
    assert "message" in data
    assert data["email"] == user_data.email

def test_register_duplicate_email(test_client, db_session, test_user):
    """Test registration with duplicate email."""
    user_data = RegisterRequest(
        email=test_user.email,
        password="StrongPass123!",
        full_name="Duplicate User",
        confirm_password="StrongPass123!"
    )
    response = test_client.post("/api/v1/auth/register", json=user_data.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()

def test_register_weak_password(test_client, db_session):
    """Test registration with weak password."""
    user_data = RegisterRequest(
        email="weakpass@example.com",
        password="weak",
        full_name="Weak Password User",
        confirm_password="weak"
    )
    response = test_client.post("/api/v1/auth/register", json=user_data.dict())
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "password" in response.json()["detail"][0]["loc"]

def test_register_password_mismatch(test_client, db_session):
    """Test registration with mismatched passwords."""
    user_data = RegisterRequest(
        email="mismatch@example.com",
        password="StrongPass123!",
        full_name="Mismatch User",
        confirm_password="DifferentPass123!"
    )
    response = test_client.post("/api/v1/auth/register", json=user_data.dict())
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "passwords do not match" in response.json()["detail"][0]["msg"].lower()

def test_login_success(test_client, db_session, test_user):
    """Test successful login."""
    login_data = LoginRequest(
        email=test_user.email,
        password="password"  # From test_user fixture
    )
    response = test_client.post("/api/v1/auth/login", json=login_data.dict())
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == test_user.email

def test_login_invalid_credentials(test_client, db_session):
    """Test login with invalid credentials."""
    login_data = LoginRequest(
        email="nonexistent@example.com",
        password="wrongpassword"
    )
    response = test_client.post("/api/v1/auth/login", json=login_data.dict())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid credentials" in response.json()["detail"].lower()

def test_login_inactive_user(test_client, db_session, test_user):
    """Test login with inactive user."""
    # Deactivate user
    test_user.is_active = False
    db_session.commit()

    login_data = LoginRequest(
        email=test_user.email,
        password="password"
    )
    response = test_client.post("/api/v1/auth/login", json=login_data.dict())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "inactive" in response.json()["detail"].lower()

def test_refresh_token_success(test_client, db_session, test_user):
    """Test successful token refresh."""
    # First login to get refresh token
    login_data = LoginRequest(
        email=test_user.email,
        password="password"
    )
    login_response = test_client.post("/api/v1/auth/login", json=login_data.dict())
    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token to get new access token
    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_invalid(test_client):
    """Test refresh token with invalid token."""
    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()

def test_password_reset_request_success(test_client, db_session, test_user):
    """Test successful password reset request."""
    reset_request = PasswordResetRequest(email=test_user.email)
    response = test_client.post(
        "/api/v1/auth/password-reset-request",
        json=reset_request.dict()
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
    assert "reset_token" in response.json()

def test_password_reset_confirm_success(test_client, db_session, test_user):
    """Test successful password reset confirmation."""
    # First request reset token
    reset_request = PasswordResetRequest(email=test_user.email)
    reset_response = test_client.post(
        "/api/v1/auth/password-reset-request",
        json=reset_request.dict()
    )
    reset_token = reset_response.json()["reset_token"]

    # Confirm password reset
    reset_confirm = PasswordResetConfirm(
        reset_token=reset_token,
        new_password="NewStrongPass123!",
        confirm_password="NewStrongPass123!"
    )
    response = test_client.post(
        "/api/v1/auth/password-reset-confirm",
        json=reset_confirm.dict()
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

def test_password_reset_confirm_invalid_token(test_client):
    """Test password reset confirmation with invalid token."""
    reset_confirm = PasswordResetConfirm(
        reset_token="invalid_token",
        new_password="NewStrongPass123!",
        confirm_password="NewStrongPass123!"
    )
    response = test_client.post(
        "/api/v1/auth/password-reset-confirm",
        json=reset_confirm.dict()
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid" in response.json()["detail"].lower()

def test_get_current_user_success(test_client, user_token_headers):
    """Test getting current user with valid token."""
    response = test_client.get(
        "/api/v1/users/me",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "id" in data

def test_get_current_user_invalid_token(test_client):
    """Test getting current user with invalid token."""
    response = test_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()

def test_get_current_user_no_token(test_client):
    """Test getting current user without token."""
    response = test_client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not authenticated" in response.json()["detail"].lower() 