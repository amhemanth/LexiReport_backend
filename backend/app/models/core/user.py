from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid

from sqlalchemy import String, Boolean, Enum as SQLEnum, Index, ForeignKey, Text, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base
from app.models.audit.audit_log import AuditLog
from app.models.comments.comment import Comment
from app.models.media.voice import VoiceProfile


class User(Base):
    """User model"""
    
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with cascade rules
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        foreign_keys="UserRole.user_id",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        viewonly=True,
        foreign_keys="[UserRole.user_id, UserRole.role_id]"
    )
    user_permissions: Mapped[List["UserPermission"]] = relationship(
        "UserPermission",
        back_populates="user",
        foreign_keys="UserPermission.user_id",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="user_permissions",
        back_populates="users",
        viewonly=True,
        foreign_keys="[UserPermission.user_id, UserPermission.permission_id]"
    )
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    password: Mapped[Optional["Password"]] = relationship(
        "Password",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    login_attempts: Mapped[List["LoginAttempt"]] = relationship(
        "LoginAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Voice command relationship
    voice_commands: Mapped[List["VoiceCommand"]] = relationship(
        "VoiceCommand",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Notification relationships
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    notification_preferences: Mapped[Optional["NotificationPreference"]] = relationship(
        "NotificationPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Report relationships
    created_reports: Mapped[List["Report"]] = relationship(
        "Report",
        foreign_keys="Report.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    updated_reports: Mapped[List["Report"]] = relationship(
        "Report",
        foreign_keys="Report.updated_by",
        back_populates="updater",
        passive_deletes=True
    )
    shared_reports: Mapped[List["ReportShare"]] = relationship(
        "ReportShare",
        foreign_keys="ReportShare.shared_by",
        back_populates="sharer",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    received_reports: Mapped[List["ReportShare"]] = relationship(
        "ReportShare",
        foreign_keys="ReportShare.shared_with",
        back_populates="sharee",
        passive_deletes=True
    )
    report_schedules: Mapped[List["ReportSchedule"]] = relationship(
        "ReportSchedule",
        foreign_keys="ReportSchedule.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    updated_schedules: Mapped[List["ReportSchedule"]] = relationship(
        "ReportSchedule",
        foreign_keys="ReportSchedule.updated_by",
        back_populates="updater",
        passive_deletes=True
    )
    created_exports: Mapped[List["ReportExport"]] = relationship(
        "ReportExport",
        foreign_keys="ReportExport.created_by",
        back_populates="creator",
        passive_deletes=True
    )
    report_insights: Mapped[List["ReportInsight"]] = relationship(
        "ReportInsight",
        foreign_keys="ReportInsight.user_id",
        back_populates="user",
        passive_deletes=True
    )
    report_queries: Mapped[List["ReportQuery"]] = relationship(
        "ReportQuery",
        foreign_keys="ReportQuery.user_id",
        back_populates="user",
        passive_deletes=True
    )
    bi_integrations: Mapped[List["BIIntegration"]] = relationship(
        "BIIntegration",
        foreign_keys="BIIntegration.created_by",
        back_populates="creator",
        passive_deletes=True
    )

    # File relationships
    files: Mapped[List["FileStorage"]] = relationship(
        "FileStorage",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Document relationships
    created_documents: Mapped[List["Document"]] = relationship(
        "Document",
        foreign_keys="Document.created_by",
        back_populates="creator",
        passive_deletes=True
    )
    updated_documents: Mapped[List["Document"]] = relationship(
        "Document",
        foreign_keys="Document.updated_by",
        back_populates="updater",
        passive_deletes=True
    )
    
    # Report content relationships
    created_report_contents: Mapped[List["ReportContent"]] = relationship(
        "ReportContent",
        foreign_keys="ReportContent.created_by",
        back_populates="creator",
        passive_deletes=True
    )
    
    # Report template relationships
    report_templates: Mapped[List["ReportTemplate"]] = relationship(
        "ReportTemplate",
        foreign_keys="ReportTemplate.created_by",
        back_populates="creator",
        passive_deletes=True
    )
    updated_templates: Mapped[List["ReportTemplate"]] = relationship(
        "ReportTemplate",
        foreign_keys="ReportTemplate.updated_by",
        back_populates="updater",
        passive_deletes=True
    )
    
    # User role relationships
    created_user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        foreign_keys="UserRole.created_by",
        back_populates="creator",
        passive_deletes=True
    )
    
    # User permission relationships
    created_user_permissions: Mapped[List["UserPermission"]] = relationship(
        "UserPermission",
        foreign_keys="UserPermission.created_by",
        back_populates="creator",
        passive_deletes=True
    )

    # Audit log relationships
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        foreign_keys="AuditLog.user_id",
        back_populates="user",
        passive_deletes=True
    )

    # Comment relationships
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        foreign_keys="Comment.user_id",
        back_populates="user",
        passive_deletes=True
    )
    mentioned_in_comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        secondary="comment_mentions",
        back_populates="mentions",
        passive_deletes=True
    )

    # Voice profile relationship
    voice_profile: Mapped[Optional["VoiceProfile"]] = relationship(
        "VoiceProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Tag relationships
    entity_tags: Mapped[List["EntityTag"]] = relationship(
        "EntityTag",
        foreign_keys="EntityTag.user_id",
        back_populates="user",
        passive_deletes=True
    )
    
    # Add composite index for common queries
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('username', name='uq_user_username'),
        Index('idx_user_email_username', 'email', 'username'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
        
    def get_permissions(self) -> List[str]:
        """Get list of permission names for the user."""
        return [p.name for p in self.permissions if p.is_active] 