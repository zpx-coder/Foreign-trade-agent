"""邮件模板 Pydantic Schema — Phase 6"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── 模板 ──

class EmailTemplateCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    subject: Optional[str] = Field(default=None, max_length=500)
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    tone: Optional[str] = Field(default=None, max_length=50)
    cta_type: Optional[str] = Field(default=None, max_length=50)
    key_points: Optional[str] = None
    icp_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    reference_email: Optional[str] = None  # 参考邮件样例（仅用于生成，不存储）
    input_data: Optional[dict] = None


class EmailTemplateUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    subject: Optional[str] = Field(default=None, max_length=500)
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    tone: Optional[str] = Field(default=None, max_length=50)
    cta_type: Optional[str] = Field(default=None, max_length=50)
    key_points: Optional[str] = None
    icp_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    status: Optional[str] = Field(default=None, max_length=20)


class EmailTemplateResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    tone: Optional[str] = None
    cta_type: Optional[str] = None
    key_points: Optional[str] = None
    icp_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    spam_score: Optional[int] = None
    read_time_seconds: Optional[int] = None
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailTemplateListItem(BaseModel):
    id: uuid.UUID
    name: str
    subject: Optional[str] = None
    tone: Optional[str] = None
    cta_type: Optional[str] = None
    status: str
    spam_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailTemplateListResponse(BaseModel):
    items: List[EmailTemplateListItem]
    total: int
    page: int
    page_size: int


class TestSendRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
