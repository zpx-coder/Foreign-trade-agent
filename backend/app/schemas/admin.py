"""管理后台 Pydantic Schema — Phase 7"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


# ── 统计 ──

class TopTenantInfo(BaseModel):
    name: str
    value: int


class AdminStatsResponse(BaseModel):
    # 基础
    total_tenants: int = 0
    active_tenants: int = 0
    total_users: int = 0
    # ICP
    total_icps: int = 0
    completed_icps: int = 0
    generating_icps: int = 0
    draft_icps: int = 0
    failed_icps: int = 0
    # 客户
    total_customers: int = 0
    customers_reached: int = 0
    reach_rate: float = 0.0
    # 邮件
    total_emails_sent: int = 0
    total_emails_opened: int = 0
    total_emails_replied: int = 0
    open_rate: float = 0.0
    reply_rate: float = 0.0
    # 分布
    tenants_by_plan: Dict[str, int] = {}
    tenants_by_status: Dict[str, int] = {}
    # Top 榜单
    top_tenants_by_customers: List[TopTenantInfo] = []
    top_tenants_by_emails: List[TopTenantInfo] = []


# ── 租户列表 ──

class TenantListItem(BaseModel):
    id: uuid.UUID
    name: str
    plan_type: str
    status: str
    user_count: int
    icp_count: int = 0
    customer_count: int = 0
    email_sent_count: int = 0
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


# ── 租户业务数据统计（管理后台用） ──

class TenantIcpStats(BaseModel):
    total: int = 0
    completed: int = 0
    generating: int = 0
    draft: int = 0
    failed: int = 0


class TenantCustomerStats(BaseModel):
    total: int = 0
    reached: int = 0
    reach_rate: float = 0.0
    status_counts: Dict[str, int] = {}


class TenantEmailStats(BaseModel):
    total_sent: int = 0
    total_opened: int = 0
    open_rate: float = 0.0
    total_replied: int = 0
    reply_rate: float = 0.0


class TenantStatsResponse(BaseModel):
    icp: TenantIcpStats
    customer: TenantCustomerStats
    email: TenantEmailStats
