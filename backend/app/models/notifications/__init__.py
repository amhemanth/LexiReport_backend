"""
Notifications models package initialization.
This module imports and exposes all notification-related models.
"""

from app.models.notifications.notification import (
    Notification,
    NotificationTemplate,
    NotificationPreference
)
from app.models.notifications.enums import NotificationType, NotificationPriority, NotificationStatus

# Export all models and enums
__all__ = [
    # Models
    "Notification",
    "NotificationTemplate",
    "NotificationPreference",
    
    # Enums
    "NotificationType",
    "NotificationPriority",
    "NotificationStatus"
] 