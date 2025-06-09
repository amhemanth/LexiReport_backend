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
from app.models.core.user import UserRole
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

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str
    is_active: bool = True
    is_superuser: bool = False

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
    """User creation schema."""
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            return validate_password_strength(v)
        return v

class UserInDBBase(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserInDBBase):
    """User response schema."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class UserInDB(UserInDBBase):
    """User in database schema."""
    hashed_password: str

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