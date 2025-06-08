"""
Tags models package initialization.
This module imports and exposes all tag-related models.
"""

from app.models.tags.tag import (
    Tag,
    EntityTag
)

__all__ = [
    "Tag",
    "EntityTag"
] 