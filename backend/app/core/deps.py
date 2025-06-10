"""Dependencies for FastAPI endpoints."""
from typing import Generator, Optional, Tuple, List, Dict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.db.session import get_db
from app.models.core.user import User
from app.repositories.user import user_repository
from app.schemas.auth import TokenData
from app.core.exceptions import (
    AuthenticationException,
    InvalidTokenError,
    TokenRevokedError,
    InactiveUserError
)
from app.core.redis import get_redis_client
from app.core.security import verify_token
from datetime import datetime

settings = get_settings()
redis_client = get_redis_client()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token."""
    try:
        # Verify token and get payload
        payload = verify_token(token)
        if not payload:
            raise InvalidTokenError()
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError()
            
        # Check if token is revoked
        session_id = payload.get("session_id")
        if not session_id:
            raise InvalidTokenError()
            
        if not redis_client.exists(f"session:{session_id}"):
            raise TokenRevokedError()
            
        # Get user from database
        user = user_repository.get(db, id=user_id)
        if user is None:
            raise InvalidTokenError()
            
        # Update last activity
        redis_client.setex(
            f"user_activity:{user_id}",
            settings.SESSION_EXPIRE_MINUTES * 60,
            request.client.host
        )
        
        return user
        
    except JWTError:
        raise InvalidTokenError()

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise InactiveUserError()
    return current_user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "The user doesn't have enough privileges",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    return current_user

async def get_current_user_with_session(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Tuple[User, str]:
    """Get current user and session ID from token."""
    try:
        # Verify token and get payload
        payload = verify_token(token)
        if not payload:
            raise InvalidTokenError()
            
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session_id")
        
        if user_id is None or session_id is None:
            raise InvalidTokenError()
            
        # Check if session exists
        if not redis_client.exists(f"session:{session_id}"):
            raise TokenRevokedError()
            
        # Get user from database
        user = user_repository.get(db, id=user_id)
        if user is None:
            raise InvalidTokenError()
            
        # Update last activity
        redis_client.setex(
            f"user_activity:{user_id}",
            settings.SESSION_EXPIRE_MINUTES * 60,
            request.client.host
        )
        
        return user, session_id
        
    except JWTError:
        raise InvalidTokenError()

async def get_user_sessions(
    current_user: User = Depends(get_current_active_user)
) -> List[Dict]:
    """Get all active sessions for current user."""
    sessions = []
    
    # Get all session keys for user
    session_keys = redis_client.keys(f"session:*")
    for key in session_keys:
        user_id = redis_client.get(key).decode()
        if user_id == str(current_user.id):
            session_id = key.split(":")[1]
            
            # Get session info
            activity = redis_client.get(f"user_activity:{user_id}")
            if activity:
                sessions.append({
                    "session_id": session_id,
                    "last_activity": activity.decode(),
                    "created_at": redis_client.ttl(key)
                })
    
    return sessions

async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
) -> bool:
    """Revoke a specific session."""
    # Check if session belongs to user
    user_id = redis_client.get(f"session:{session_id}")
    if not user_id or user_id.decode() != str(current_user.id):
        raise InvalidTokenError()
        
    # Revoke session
    redis_client.delete(f"session:{session_id}")
    redis_client.delete(f"refresh_token:{session_id}")
    
    return True

async def revoke_all_sessions(
    current_user: User = Depends(get_current_active_user)
) -> bool:
    """Revoke all sessions for current user."""
    # Get all session keys for user
    session_keys = redis_client.keys(f"session:*")
    for key in session_keys:
        user_id = redis_client.get(key).decode()
        if user_id == str(current_user.id):
            session_id = key.split(":")[1]
            
            # Revoke session
            redis_client.delete(f"session:{session_id}")
            redis_client.delete(f"refresh_token:{session_id}")
    
    return True 