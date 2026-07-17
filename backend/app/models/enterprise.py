"""企业资料模型 — 每租户一条记录"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EnterpriseProfile(Base):
    __tablename__ = "enterprise_profile"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True,
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="中国")
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # v1.2 外贸扩展字段
    year_established: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    employee_count: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    factory_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    annual_export_volume: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    main_markets: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    certifications: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    oem_odm: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_advantages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    factory_photos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    certificate_photos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
