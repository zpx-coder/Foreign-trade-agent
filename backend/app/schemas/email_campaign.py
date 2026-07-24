"""邮件发送任务 Pydantic Schema — Phase 6"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── SMTP 配置 ──

class SmtpConfig(BaseModel):
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535, default=465)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(default="", max_length=255)
    from_name: str = Field(default="", max_length=255)
    from_email: str = Field(default="", max_length=255)


# ── 发送任务 ──

class CampaignCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    template_id: uuid.UUID
    customer_ids: List[uuid.UUID] = Field(min_length=1, max_length=500)
    smtp_config: SmtpConfig
    schedule_at: Optional[datetime] = None


class CampaignUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    smtp_config: Optional[SmtpConfig] = None


class CampaignResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    template_id: Optional[uuid.UUID] = None
    status: str
    total_recipients: int
    sent_count: int
    delivered_count: int
    opened_count: int
    bounced_count: int
    schedule_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignListItem(BaseModel):
    id: uuid.UUID
    name: str
    template_id: Optional[uuid.UUID] = None
    status: str
    total_recipients: int
    sent_count: int
    opened_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    items: List[CampaignListItem]
    total: int
    page: int
    page_size: int


class CampaignDetailResponse(CampaignResponse):
    smtp_config: Optional[dict] = None
    customer_ids: Optional[list] = None
    send_logs: list = []


# ── 预览 ──

class PreviewRequest(BaseModel):
    customer_id: uuid.UUID
    contact_id: Optional[uuid.UUID] = None


class PreviewResponse(BaseModel):
    subject: str
    body_html: str
    body_text: str


# ── 发送日志 ──

class SendLogResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    contact_id: Optional[uuid.UUID] = None
    recipient_email: str
    subject: Optional[str] = None
    status: str
    tracking_id: uuid.UUID
    message_id: Optional[str] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    # 关联信息
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    customer_name: Optional[str] = None
    customer_country: Optional[str] = None
    customer_industry: Optional[str] = None

    model_config = {"from_attributes": True}
