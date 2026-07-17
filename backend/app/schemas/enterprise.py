"""企业资料 Pydantic Schema"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EnterpriseUpdateRequest(BaseModel):
    """企业资料更新请求 — 全部字段可选"""
    company_name: str = Field(min_length=1, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=512)
    industry: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default="中国", max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    contact_position: Optional[str] = Field(default=None, max_length=100)
    # v1.2 外贸扩展字段
    year_established: Optional[int] = Field(default=None, ge=1900, le=2100)
    employee_count: Optional[str] = Field(default=None, max_length=50)
    factory_area: Optional[str] = Field(default=None, max_length=100)
    annual_export_volume: Optional[str] = Field(default=None, max_length=100)
    main_markets: Optional[List[str]] = Field(default=None)
    certifications: Optional[List[str]] = Field(default=None)
    oem_odm: Optional[str] = Field(default=None, max_length=255)
    company_advantages: Optional[str] = Field(default=None, max_length=2000)
    factory_photos: Optional[List[str]] = Field(default=None)
    certificate_photos: Optional[List[str]] = Field(default=None)


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
    # v1.2 外贸扩展字段
    year_established: Optional[int] = None
    employee_count: Optional[str] = None
    factory_area: Optional[str] = None
    annual_export_volume: Optional[str] = None
    main_markets: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    oem_odm: Optional[str] = None
    company_advantages: Optional[str] = None
    factory_photos: Optional[List[str]] = None
    certificate_photos: Optional[List[str]] = None
    # 时间戳
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
