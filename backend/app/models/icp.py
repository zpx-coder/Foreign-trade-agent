"""ICP 客户画像 ORM 模型"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Icp(Base):
    """理想客户画像 (Ideal Customer Profile)"""

    __tablename__ = "icps"

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

    # 用户命名的画像标题
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # 状态: draft | generating | completed | failed
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )

    # 用户填写的输入数据（三步表单的汇总）
    input_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # AI 生成的画像输出
    output_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # 生成耗时（秒）
    generation_time_ms: Mapped[Optional[int]] = mapped_column(nullable=True)

    # 错误信息（生成失败时）
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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

    # 关系
    tenant = relationship("Tenant", backref="icps")
    creator = relationship("User", backref="icps")

    __table_args__ = (
        Index("ix_icps_tenant_status", "tenant_id", "status"),
        Index("ix_icps_tenant_created", "tenant_id", "created_at"),
    )
