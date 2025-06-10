from datetime import datetime
from typing import Optional, List, ForwardRef
from pydantic import BaseModel, EmailStr, Field, field_validator, constr, validator, ConfigDict
from .base import BaseSchema
from app.core.validators import (
    validate_password_strength,
    validate_email_format,
    validate_full_name
)
from app.models.core.enums import UserRole
from uuid import UUID
import re

# Create a forward reference for UserResponse
UserResponse = ForwardRef('UserResponse')

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_format(v)

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        return validate_full_name(v)

class UserCreate(UserBase):
    """User creation schema."""
    password: constr(min_length=8, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_format(v)

class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data schema."""
    sub: Optional[str] = None

class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str

class RegistrationResponse(BaseModel):
    """Registration response schema."""
    message: str
    email: str
    role: UserRole
    permissions: List[str]

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class LoginAttempt(BaseModel):
    """Login attempt schema."""
    user_id: UUID = Field(..., description="User ID")
    ip_address: str = Field(..., description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    success: bool = Field(..., description="Whether login was successful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Attempt timestamp")

class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse
    session_id: str

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, **data):
        super().__init__(**data)
        # Convert user to dict if it's a UserResponse object
        if hasattr(self, 'user') and isinstance(self.user, UserResponse):
            self.user = self.user.model_dump()

class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="User's full name")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="User's username. If not provided, will be generated from email")
    confirm_password: str = Field(..., description="Password confirmation")

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate that passwords match."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('username')
    def validate_username(cls, v):
        """Validate username format if provided."""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9._-]+$', v):
                raise ValueError('Username can only contain letters, numbers, dots, underscores, and hyphens')
        return v

class RegisterResponse(BaseModel):
    """Registration response schema."""
    message: str = Field(..., description="Success message")
    user_id: str = Field(..., description="Created user ID")
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., description="User's username")
    verification_required: bool = Field(True, description="Whether email verification is required")

class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""
    token: str = Field(..., description="Email verification token")

class EmailVerificationResponse(BaseModel):
    """Email verification response schema."""
    message: str = Field(..., description="Success message")
    verified: bool = Field(..., description="Whether email was verified")

class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr = Field(..., description="User email")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    reset_token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str
    new_password: constr(min_length=8)

class UserPermissionsResponse(BaseModel):
    """User permissions response schema."""
    user_id: UUID
    permissions: List[str]

class PermissionAssignmentRequest(BaseModel):
    """Permission assignment request schema."""
    permission_name: str
    is_active: bool = True

class PermissionAssignmentResponse(BaseModel):
    """Permission assignment response schema."""
    success: bool
    message: str

# Import UserResponse here to avoid circular imports
from app.schemas.user import UserResponse

# Update forward references
LoginResponse.update_forward_refs()

class RateLimitResponse(BaseModel):
    """Rate limit response schema."""
    limit: int = Field(..., description="Rate limit")
    remaining: int = Field(..., description="Remaining requests")
    reset: int = Field(..., description="Reset timestamp") 