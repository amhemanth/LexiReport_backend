"""Authentication routes."""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.schemas.auth import (
    TokenResponse, RegisterRequest, RegisterResponse,
    EmailVerificationRequest, EmailVerificationResponse,
    LoginResponse
)
from app.schemas.user import UserCreate, UserResponse, UserInDB
from app.services.auth import auth_service, AuthService
from app.core.deps import get_db, get_current_active_superuser
from app.core.exceptions import (
    AuthenticationError,
    ValidationException,
    DatabaseError
)
from app.core.logger import logger
from app.models.core.enums import UserRole

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserResponse:
    """Get current user from token."""
    try:
        user = auth_service.get_current_user(db, token)
        return UserResponse.from_orm(user)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def get_auth_service() -> AuthService:
    """Get AuthService instance."""
    return AuthService()

@router.post("/register", response_model=RegisterResponse)
async def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    Register a new regular user.
    """
    try:
        # Convert RegisterRequest to UserCreate with default values
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            username=user_data.username,
            is_superuser=False,
            role=UserRole.USER,
            is_active=True
        )
        
        # Register user
        result = await auth_service.register(db, user_data)
        return RegisterResponse(
            message="User registered successfully. Please check your email for verification.",
            user_id=str(result.id),
            email=result.email,
            username=result.username,
            verification_required=True
        )
    except ValidationException as e:
        logger.warning(f"Validation error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": str(e),
                "type": "validation_error",
                "field": "email" if "email" in str(e).lower() else None
            }
        )
    except DatabaseError as e:
        logger.error(f"Database error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Database error occurred", "type": "database_error"}
        )
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "An unexpected error occurred", "type": "server_error"}
        )

@router.post("/register/admin", response_model=RegisterResponse)
async def register_admin(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
    current_superuser: UserInDB = Depends(get_current_active_superuser),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    Register a new admin user. Only accessible by superusers.
    """
    try:
        # Convert RegisterRequest to UserCreate with admin privileges
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            username=user_data.username,
            is_superuser=True,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        # Register admin user
        result = await auth_service.register(db, user_data)
        return RegisterResponse(
            message="Admin user registered successfully.",
            user_id=str(result.id),
            email=result.email,
            username=result.username,
            verification_required=False  # Admin users don't need email verification
        )
    except ValidationException as e:
        logger.warning(f"Validation error during admin registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "type": "validation_error"}
        )
    except DatabaseError as e:
        logger.error(f"Database error during admin registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Database error occurred", "type": "database_error"}
        )
    except Exception as e:
        logger.error(f"Unexpected error during admin registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "An unexpected error occurred", "type": "server_error"}
        )

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Verify user email."""
    try:
        result = await auth_service.verify_email(db, verification_data.token)
        return result
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
) -> LoginResponse:
    """Login user and return tokens."""
    try:
        return await auth_service.login(db, form_data.username, form_data.password, request)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """Logout user and invalidate session."""
    try:
        # Extract session ID from token
        payload = auth_service.verify_token(token)
        session_id = payload.get("session_id")
        
        if not session_id:
            raise AuthenticationError("Invalid session")
        
        return await auth_service.logout(db, str(current_user.id), session_id)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Refresh access token."""
    try:
        return await auth_service.refresh_token(db, refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Get current user profile."""
    return current_user 