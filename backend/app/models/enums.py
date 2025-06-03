import enum

class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    USER = "user" 