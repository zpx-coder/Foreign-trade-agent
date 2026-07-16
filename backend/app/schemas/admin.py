"""管理后台 Pydantic Schema — Phase 7"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── 统计 ──

class AdminStatsResponse(BaseModel):
    total_tenants: int
    active_tenants: int
    total_users: int
    total_emails_sent: int


# ── 租户列表 ──

class TenantListItem(BaseModel):
    id: uuid.UUID
    name: str
    plan_type: str
    status: str
    user_count: int
    created_at: datetime


class TenantListResponse(BaseModel):
    items: List[TenantListItem]
    total: int
    page: int
    page_size: int


# ── 租户详情 ──

class TenantUserInfo(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    plan_type: str
    status: str
    settings: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    users: List[TenantUserInfo] = []

    model_config = {"from_attributes": True}


# ── 更新租户 ──

class TenantUpdateRequest(BaseModel):
    plan_type: Optional[str] = Field(default=None, pattern="^(free|pro|enterprise)$")
    status: Optional[str] = Field(default=None, pattern="^(active|suspended|cancelled)$")
