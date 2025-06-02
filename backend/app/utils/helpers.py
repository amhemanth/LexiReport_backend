from typing import Any, Dict
from datetime import datetime

def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO format string."""
    return dt.isoformat()

def clean_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in d.items() if v is not None}

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..." 