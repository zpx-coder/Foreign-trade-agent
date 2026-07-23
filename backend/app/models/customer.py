"""客户模型 — Phase 4 Customer Acquisition"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.contact import Contact


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── 基本信息 ──
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── 来源信息 ──
    source: Mapped[str] = mapped_column(
        String(200), nullable=False, default="manual", index=True,
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    icp_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("icps.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── 状态 ──
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="new", index=True,
    )

    # ── 结构化数据 ──
    source_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── 信息补全（Phase 5） ──
    enrichment_status: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, index=True,
    )
    last_enriched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    enrichment_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── 关系 ──
    tenant = relationship("Tenant", backref="customers")
    creator = relationship("User", backref="customers")
    icp = relationship("Icp", backref="customers")
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact", back_populates="customer", cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_customers_tenant_status", "tenant_id", "status"),
        Index("ix_customers_tenant_source", "tenant_id", "source"),
        Index("ix_customers_tenant_created", "tenant_id", "created_at"),
    )
