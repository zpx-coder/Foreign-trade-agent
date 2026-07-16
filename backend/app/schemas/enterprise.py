"""企业资料 Pydantic Schema"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EnterpriseUpdateRequest(BaseModel):
    """企业资料更新请求 — 全部字段可选"""
    company_name: str = Field(min_length=1, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=512)
    industry: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    contact_position: Optional[str] = Field(default=None, max_length=100)


class EnterpriseResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    company_name: str
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_position: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
