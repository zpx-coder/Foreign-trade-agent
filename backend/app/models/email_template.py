"""邮件模板模型 — Phase 6 Email Marketing"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmailTemplate(Base):
    __tablename__ = "email_templates"

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

    # ── 模板内容 ──
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── 生成参数 ──
    tone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cta_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    key_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── 关联 ──
    icp_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("icps.id", ondelete="SET NULL"),
        nullable=True,
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── AI 输出 ──
    spam_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    read_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    input_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # ── 状态 ──
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )

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
    tenant = relationship("Tenant", backref="email_templates")
    creator = relationship("User", backref="email_templates")
    icp = relationship("Icp", backref="email_templates")
    product = relationship("Product", backref="email_templates")
