from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid

from sqlalchemy import String, ForeignKey, Enum as SQLEnum, JSON, Column, Integer, DateTime, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.models.core.user import User
from app.models.integration.enums import BIPlatformType, SyncStatus


class BIConnection(Base):
    __tablename__ = "bi_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    platform_type: Mapped[BIPlatformType] = mapped_column(SQLEnum(BIPlatformType), nullable=False)
    connection_details: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships with cascade rules
    dashboards: Mapped[List["BIDashboard"]] = relationship(
        "BIDashboard",
        back_populates="connection",
        cascade="all, delete-orphan"
    )

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_bi_connection_platform', 'platform_type', 'is_active'),
        Index('idx_bi_connection_created', 'created_at'),
        Index('idx_bi_connection_updated', 'updated_at'),
    )

    def __repr__(self):
        return f"<BIConnection {self.name}>"


class BIDashboard(Base):
    __tablename__ = "bi_dashboards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    dashboard_id: Mapped[str] = mapped_column(String, nullable=False)
    connection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bi_connections.id", ondelete="CASCADE"), nullable=False)
    sync_status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.PENDING)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connection: Mapped["BIConnection"] = relationship("BIConnection", back_populates="dashboards")

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_bi_dashboard_connection', 'connection_id', 'sync_status'),
    )

    def __repr__(self):
        return f"<BIDashboard {self.name}>"


class BIPlatformType(str, PyEnum):
    """BI platform type enum"""
    POWER_BI = "power_bi"
    TABLEAU = "tableau"
    QLIK = "qlik"
    LOOKER = "looker"
    OTHER = "other"


class SyncStatus(str, PyEnum):
    """Sync status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BIIntegration(Base):
    """BI integration model"""
    
    __tablename__ = "bi_integrations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform_type: Mapped[BIPlatformType] = mapped_column(SQLEnum(BIPlatformType), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    api_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(100))
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_bi_integration_type', 'platform_type'),
        Index('idx_bi_integration_active', 'is_active'),
        Index('idx_bi_integration_created', 'created_at'),
        Index('idx_bi_integration_creator', 'created_by'),
        Index('idx_bi_integration_entity', 'entity_type', 'entity_id'),
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    sync_jobs: Mapped[List["BISyncJob"]] = relationship(
        "BISyncJob",
        back_populates="integration",
        cascade="all, delete-orphan"
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        primaryjoin="and_(foreign(BIIntegration.entity_type) == 'report', foreign(BIIntegration.entity_id) == Report.id)",
        back_populates="bi_integrations",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<BIIntegration {self.name}>"


class BISyncJob(Base):
    """BI sync job model"""
    
    __tablename__ = "bi_sync_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bi_integrations.id", ondelete="CASCADE"), nullable=False)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    sync_status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(String)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_bi_sync_integration', 'integration_id'),
        Index('idx_bi_sync_report', 'report_id'),
        Index('idx_bi_sync_status', 'sync_status'),
        Index('idx_bi_sync_created', 'created_at'),
    )

    # Relationships
    integration: Mapped["BIIntegration"] = relationship("BIIntegration", back_populates="sync_jobs")
    report: Mapped["Report"] = relationship("Report")

    def __repr__(self) -> str:
        return f"<BISyncJob {self.integration_id}:{self.report_id}>" 