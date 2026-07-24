"""客户管理 Pydantic Schema — Phase 4"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── 联系人 ──

class ContactCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=100)
    linkedin_url: Optional[str] = Field(default=None, max_length=512)
    is_primary: bool = False
    contact_type: Optional[str] = Field(default="scraped", max_length=20)
    confidence: Optional[str] = Field(default=None, max_length=10)
    notes: Optional[str] = Field(default=None, max_length=2000)


class ContactUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=100)
    linkedin_url: Optional[str] = Field(default=None, max_length=512)
    is_primary: Optional[bool] = None
    contact_type: Optional[str] = Field(default=None, max_length=20)
    confidence: Optional[str] = Field(default=None, max_length=10)
    notes: Optional[str] = Field(default=None, max_length=2000)


class ContactResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_primary: bool
    contact_type: Optional[str] = None
    confidence: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── 客户 ──

class CustomerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    company_size: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)
    source: str = Field(default="manual", max_length=50)
    source_url: Optional[str] = Field(default=None, max_length=512)
    icp_id: Optional[uuid.UUID] = None
    status: str = Field(default="new", max_length=20)
    notes: Optional[str] = Field(default=None, max_length=2000)
    contacts: Optional[List[ContactCreateRequest]] = None


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    company_size: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)
    source: Optional[str] = Field(default=None, max_length=50)
    source_url: Optional[str] = Field(default=None, max_length=512)
    icp_id: Optional[uuid.UUID] = None
    status: Optional[str] = Field(default=None, max_length=20)
    source_data: Optional[dict] = None
    ai_summary: Optional[str] = Field(default=None, max_length=5000)
    notes: Optional[str] = Field(default=None, max_length=2000)


class CustomerListItem(BaseModel):
    """列表项（不含大段 JSON）"""
    id: uuid.UUID
    name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    source: str
    status: str
    website: Optional[str] = None
    contacts_count: int = 0
    contacts_with_email_count: int = 0  # 有邮箱地址的联系人数（用于邮件发送筛选）
    icp_id: Optional[uuid.UUID] = None
    icp_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    icp_id: Optional[uuid.UUID] = None
    status: str
    source_data: Optional[dict] = None
    ai_summary: Optional[str] = None
    notes: Optional[str] = None
    contacts_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerDetailResponse(CustomerResponse):
    """详情（含联系人列表）"""
    contacts: List[ContactResponse] = []


class CustomerListResponse(BaseModel):
    items: List[CustomerListItem]
    total: int
    page: int
    page_size: int


# ── 搜索 ──

class CustomerSearchRequest(BaseModel):
    icp_id: uuid.UUID
    channels: List[str] = Field(default=["google"])
    region: Optional[str] = Field(default=None, max_length=100)


class BatchStatusRequest(BaseModel):
    ids: List[uuid.UUID]
    status: str = Field(min_length=1, max_length=20)


class CustomerImportRowError(BaseModel):
    """Excel 导入单行错误"""
    row: int
    message: str


class CustomerImportResponse(BaseModel):
    """Excel 导入结果"""
    created: int = 0
    skipped: int = 0
    total: int = 0
    errors: List[CustomerImportRowError] = []
