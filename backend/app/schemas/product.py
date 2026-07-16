"""产品管理 Pydantic Schema"""

import uuid
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=100)
    hs_code: Optional[str] = Field(default=None, max_length=20)
    price_usd: Optional[Decimal] = Field(default=None, ge=0)
    moq: Optional[int] = Field(default=None, ge=1)
    image_url: Optional[str] = Field(default=None, max_length=512)


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=100)
    hs_code: Optional[str] = Field(default=None, max_length=20)
    price_usd: Optional[Decimal] = Field(default=None, ge=0)
    moq: Optional[int] = Field(default=None, ge=1)
    image_url: Optional[str] = Field(default=None, max_length=512)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    hs_code: Optional[str] = None
    price_usd: Optional[Decimal] = None
    moq: Optional[int] = None
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
