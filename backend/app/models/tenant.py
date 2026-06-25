"""租户模型"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenant"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_type: Mapped[str] = mapped_column(
        Enum("free", "pro", "enterprise", name="plan_type", create_type=False),
        default="free",
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "suspended", "cancelled", name="tenant_status", create_type=False),
        default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关联
    users = relationship("User", back_populates="tenant", lazy="dynamic")
