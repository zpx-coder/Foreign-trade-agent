"""发送日志模型 — Phase 6 Email Marketing"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SendLog(Base):
    __tablename__ = "send_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── 发送信息 ──
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ── 状态 ──
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )

    # ── 追踪 ──
    tracking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid.uuid4
    )
    message_id: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # 发件时 Message-ID，用于 IMAP 回复匹配
    opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    replied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # IMAP 检测到回复的时间

    # ── 错误 ──
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── 关系 ──
    campaign = relationship("EmailCampaign", back_populates="send_logs")
    customer = relationship("Customer", backref="send_logs")
    contact = relationship("Contact", backref="send_logs")
