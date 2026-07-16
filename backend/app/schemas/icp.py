"""ICP 客户画像 Pydantic Schema"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── 输入数据（三步表单）──

class IcpInputData(BaseModel):
    """用户填写的 ICP 输入"""
    # Step 1: 目标市场
    target_industry: Optional[str] = Field(default=None, description="目标行业")
    target_region: Optional[str] = Field(default=None, description="目标地区")
    company_size: Optional[str] = Field(default=None, description="公司规模")
    # Step 2: 产品/服务
    product_category: Optional[str] = Field(default=None, description="产品品类")
    product_price_range: Optional[str] = Field(default=None, description="价格区间")
    product_features: Optional[str] = Field(default=None, description="产品特点/优势")
    # Step 3: 理想客户特征
    customer_budget: Optional[str] = Field(default=None, description="客户预算")
    pain_points: Optional[str] = Field(default=None, description="客户痛点")
    decision_makers: Optional[str] = Field(default=None, description="决策者角色")
    additional_notes: Optional[str] = Field(default=None, description="补充说明")


# ── 请求 / 响应 ──

class IcpCreateRequest(BaseModel):
    """创建 ICP（输入数据 + 可选名称）"""
    name: str = Field(min_length=1, max_length=255, description="画像名称")
    input_data: IcpInputData = Field(default_factory=IcpInputData)


class IcpUpdateRequest(BaseModel):
    """更新 ICP 输入数据"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    input_data: Optional[IcpInputData] = None


class IcpResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    status: str
    input_data: dict
    output_data: Optional[dict] = None
    generation_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IcpListItem(BaseModel):
    """列表项（不含大段 JSON）"""
    id: uuid.UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IcpListResponse(BaseModel):
    items: List[IcpListItem]
    total: int
    page: int
    page_size: int
