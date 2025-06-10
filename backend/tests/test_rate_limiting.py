"""Rate limiting tests."""
import pytest
import time
from fastapi import status
from app.core.exceptions import RateLimitExceededError
from app.schemas.auth import LoginRequest, RegisterRequest
from app.core.redis import redis_manager

def test_login_rate_limit_success(test_client, db_session, test_user):
    """Test successful login within rate limit."""
    login_data = LoginRequest(
        email=test_user.email,
        password="password"  # From test_user fixture
    )
    
    # Make requests within rate limit
    for _ in range(5):  # Assuming rate limit is higher than 5
        response = test_client.post("/api/v1/auth/login", json=login_data.dict())
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

def test_login_rate_limit_exceeded(test_client, db_session, test_user):
    """Test login rate limit exceeded."""
    login_data = LoginRequest(
        email=test_user.email,
        password="wrongpassword"  # Intentionally wrong password
    )
    
    # Make requests until rate limit is exceeded
    for _ in range(10):  # Assuming rate limit is 5
        response = test_client.post("/api/v1/auth/login", json=login_data.dict())
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            break
    
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "rate limit exceeded" in response.json()["detail"].lower()
    assert "retry_after" in response.json()

def test_login_rate_limit_reset(test_client, db_session, test_user):
    """Test login rate limit reset after window."""
    login_data = LoginRequest(
        email=test_user.email,
        password="wrongpassword"
    )
    
    # Make requests until rate limit is exceeded
    for _ in range(10):
        response = test_client.post("/api/v1/auth/login", json=login_data.dict())
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            break
    
    # Wait for rate limit window to reset
    time.sleep(2)  # Assuming rate limit window is 1 second
    
    # Try again after window reset
    response = test_client.post("/api/v1/auth/login", json=login_data.dict())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Should fail due to wrong password, not rate limit

def test_register_rate_limit_success(test_client, db_session):
    """Test successful registration within rate limit."""
    for i in range(3):  # Assuming rate limit is higher than 3
        user_data = RegisterRequest(
            email=f"user{i}@example.com",
            password="StrongPass123!",
            full_name=f"User {i}",
            confirm_password="StrongPass123!"
        )
        response = test_client.post("/api/v1/auth/register", json=user_data.dict())
        assert response.status_code == status.HTTP_200_OK
        assert "user_id" in response.json()

def test_register_rate_limit_exceeded(test_client, db_session):
    """Test registration rate limit exceeded."""
    # Make requests until rate limit is exceeded
    for i in range(10):  # Assuming rate limit is 5
        user_data = RegisterRequest(
            email=f"user{i}@example.com",
            password="StrongPass123!",
            full_name=f"User {i}",
            confirm_password="StrongPass123!"
        )
        response = test_client.post("/api/v1/auth/register", json=user_data.dict())
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            break
    
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "rate limit exceeded" in response.json()["detail"].lower()
    assert "retry_after" in response.json()

def test_password_reset_rate_limit_success(test_client, db_session, test_user):
    """Test successful password reset request within rate limit."""
    for _ in range(3):  # Assuming rate limit is higher than 3
        response = test_client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": test_user.email}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

def test_password_reset_rate_limit_exceeded(test_client, db_session, test_user):
    """Test password reset request rate limit exceeded."""
    # Make requests until rate limit is exceeded
    for _ in range(10):  # Assuming rate limit is 5
        response = test_client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": test_user.email}
        )
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            break
    
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "rate limit exceeded" in response.json()["detail"].lower()
    assert "retry_after" in response.json()

def test_different_endpoints_rate_limits(test_client, db_session, test_user):
    """Test rate limits for different endpoints are independent."""
    # Exceed rate limit for login
    login_data = LoginRequest(
        email=test_user.email,
        password="wrongpassword"
    )
    for _ in range(10):
        response = test_client.post("/api/v1/auth/login", json=login_data.dict())
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            break
    
    # Should still be able to use password reset
    reset_response = test_client.post(
        "/api/v1/auth/password-reset-request",
        json={"email": test_user.email}
    )
    assert reset_response.status_code == status.HTTP_200_OK

def test_rate_limit_headers(test_client, db_session, test_user):
    """Test rate limit headers in response."""
    login_data = LoginRequest(
        email=test_user.email,
        password="password"
    )
    response = test_client.post("/api/v1/auth/login", json=login_data.dict())
    
    # Check for rate limit headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    
    # Verify header values
    assert int(response.headers["X-RateLimit-Limit"]) > 0
    assert int(response.headers["X-RateLimit-Remaining"]) > 0
    assert int(response.headers["X-RateLimit-Reset"]) > 0

def test_concurrent_rate_limiting(test_client, db_session, test_user):
    """Test rate limiting under concurrent requests."""
    import asyncio
    import aiohttp
    
    async def make_login_request():
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/v1/auth/login",
                data={
                    "username": test_user.email,
                    "password": "wrongpassword"
                }
            ) as response:
                return response.status
    
    # Make concurrent requests
    loop = asyncio.get_event_loop()
    tasks = [make_login_request() for _ in range(10)]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    
    # Check that some requests were rate limited
    assert status.HTTP_429_TOO_MANY_REQUESTS in results 