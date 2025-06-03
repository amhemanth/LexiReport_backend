from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from .base import BaseSchema, TimestampSchema
from app.core.validators import (
    validate_password_strength,
    validate_email_format,
    validate_full_name,
    validate_pagination_params
)
from app.models.user import UserRole
import uuid

class PasswordUpdate(BaseModel):
    """Schema for password update."""
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

class PermissionUpdate(BaseModel):
    """Schema for permission update."""
    permissions: List[str]

class RoleUpdate(BaseModel):
    """Schema for role update."""
    role: UserRole

class UserBase(BaseSchema):
    """Base user schema with common attributes."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is not None:
            return validate_email_format(v)
        return v

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None:
            return validate_full_name(v)
        return v

class UserCreate(UserBase):
    """Schema for user creation."""
    email: EmailStr
    full_name: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

class UserInDB(UserBase):
    """Schema for user in database."""
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(UserBase):
    """Schema for user updates."""
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            return validate_password_strength(v)
        return v

class UserResponse(UserInDB):
    """Schema for user response."""
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserList(BaseSchema):
    """Schema for paginated user list."""
    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int

    @field_validator('page', 'size')
    @classmethod
    def validate_pagination(cls, v, info):
        if info.field_name == 'page':
            if v < 1:
                raise ValueError("Page number must be greater than 0")
        elif info.field_name == 'size':
            if v < 1:
                raise ValueError("Page size must be greater than 0")
            if v > 100:
                raise ValueError("Page size cannot be greater than 100")
        return v 