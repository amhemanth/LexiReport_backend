from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from .base import BaseSchema
from app.core.validators import (
    validate_password_strength,
    validate_email_format,
    validate_full_name
)
from app.models.user import UserRole

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
    role: UserRole
    permissions: List[str]

class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None
    role: Optional[UserRole] = None
    permissions: Optional[List[str]] = None

class RegistrationResponse(BaseModel):
    """Registration response schema."""
    message: str
    email: str
    role: UserRole
    permissions: List[str]

class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: constr(min_length=8, max_length=100)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_format(v)

class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_format(v)

class PasswordReset(BaseModel):
    """Schema for password reset."""
    token: str
    new_password: constr(min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v) 