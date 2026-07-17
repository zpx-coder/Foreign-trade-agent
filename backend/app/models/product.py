"""产品模型 — 租户内产品目录"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Text, Numeric, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hs_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    price_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True,
    )
    moq: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)  # 保留兼容旧数据
    images: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # v1.2 多图 URL 数组
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
