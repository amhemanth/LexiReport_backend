"""Validation utilities for auth and user data."""
import re
from typing import Any
from pydantic import validator

def validate_password_strength(password: str) -> str:
    """Validate password strength.
    
    Requirements:
    - At least 8 characters long
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password

def validate_email_format(email: str) -> str:
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()

def validate_full_name(name: str) -> str:
    """Validate full name format."""
    name = name.strip()
    if not name:
        raise ValueError("Full name cannot be empty")
    if len(name) < 2:
        raise ValueError("Full name must be at least 2 characters long")
    if len(name) > 100:
        raise ValueError("Full name must be less than 100 characters")
    if not re.match(r'^[a-zA-Z\s\-\.\']+$', name):
        raise ValueError("Full name can only contain letters, spaces, hyphens, periods, and apostrophes")
    return name

def validate_pagination_params(page: int, size: int) -> tuple[int, int]:
    """Validate pagination parameters."""
    if page < 1:
        raise ValueError("Page number must be greater than 0")
    if size < 1:
        raise ValueError("Page size must be greater than 0")
    if size > 100:
        raise ValueError("Page size cannot be greater than 100")
    return page, size 