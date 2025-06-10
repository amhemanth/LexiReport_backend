"""Security utilities for the application."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, Tuple
from jose import jwt
from passlib.context import CryptContext
from app.config.settings import settings
import re
from app.core.exceptions import SecurityException, AuthenticationException
import uuid
from app.core.redis import get_redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis_client = get_redis_client()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    # Check for common passwords
    common_passwords = ["password123", "admin123", "qwerty123"]
    if password.lower() in common_passwords:
        return False, "Password is too common"
    
    return True, ""

def check_password_history(user_id: str, new_password: str, db) -> bool:
    """Check if password was used before."""
    # Get last 5 passwords from history
    password_history = redis_client.lrange(f"password_history:{user_id}", 0, 4)
    
    for old_hash in password_history:
        if verify_password(new_password, old_hash.decode()):
            return False
    return True

def add_to_password_history(user_id: str, password_hash: str):
    """Add password hash to history."""
    redis_client.lpush(f"password_history:{user_id}", password_hash)
    redis_client.ltrim(f"password_history:{user_id}", 0, 4)  # Keep only last 5

def check_login_attempts(user_id: str) -> bool:
    """Check if user is locked out due to too many failed attempts."""
    attempts = redis_client.get(f"login_attempts:{user_id}")
    if attempts and int(attempts) >= settings.MAX_LOGIN_ATTEMPTS:
        return False
    return True

def increment_login_attempts(user_id: str):
    """Increment failed login attempts."""
    key = f"login_attempts:{user_id}"
    redis_client.incr(key)
    redis_client.expire(key, settings.LOGIN_ATTEMPT_WINDOW)

def reset_login_attempts(user_id: str):
    """Reset failed login attempts."""
    redis_client.delete(f"login_attempts:{user_id}")

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    session_id: Optional[str] = None,
) -> str:
    """Create a new JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    session_id = session_id or str(uuid.uuid4())
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "session_id": session_id,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # Store session info
    redis_client.setex(
        f"session:{session_id}",
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        str(subject)
    )
    
    return token

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    session_id: Optional[str] = None,
) -> str:
    """Create a new JWT refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    session_id = session_id or str(uuid.uuid4())
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "session_id": session_id,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # Store refresh token info
    redis_client.setex(
        f"refresh_token:{session_id}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Convert days to seconds
        str(subject)
    )
    
    return token

def revoke_token(session_id: str):
    """Revoke a token by its session ID."""
    redis_client.delete(f"session:{session_id}")
    redis_client.delete(f"refresh_token:{session_id}")

def revoke_all_user_tokens(user_id: str):
    """Revoke all tokens for a user."""
    # Get all sessions for user
    sessions = redis_client.keys(f"session:*")
    for session in sessions:
        if redis_client.get(session).decode() == str(user_id):
            session_id = session.split(":")[1]
            revoke_token(session_id)

def verify_token(token: str) -> Dict[str, Any]:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check if token is revoked
        session_id = payload.get("session_id")
        if not session_id:
            raise SecurityException("Invalid token format")
            
        token_type = payload.get("type")
        if token_type == "access":
            if not redis_client.exists(f"session:{session_id}"):
                raise SecurityException("Token has been revoked")
        elif token_type == "refresh":
            if not redis_client.exists(f"refresh_token:{session_id}"):
                raise SecurityException("Token has been revoked")
                
        return payload
    except jwt.JWTError:
        raise AuthenticationException("Invalid token")

def generate_email_verification_token(email: str) -> str:
    """Generate a token for email verification."""
    expire = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification",
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def generate_password_reset_token(email: str) -> str:
    """Generate password reset token."""
    delta = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    
    to_encode = {
        "exp": exp,
        "nbf": now,
        "sub": email,
        "type": "password_reset",
        "iat": now
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token."""
    try:
        decoded_token = verify_token(token)
        if decoded_token["type"] != "password_reset":
            raise SecurityException("Invalid token type")
        return decoded_token["sub"]
    except SecurityException:
        return None 