"""ICP 客户画像 Pydantic Schema"""

import uuid
from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator


# ── 输入数据（三步表单）──

class IcpInputData(BaseModel):
    """用户填写的 ICP 输入"""
    # Step 1: 目标市场
    target_industry: Optional[str] = Field(default=None, description="目标行业")
    target_region: Optional[str] = Field(default=None, description="目标地区")
    company_size: Optional[Union[str, List[str]]] = Field(
        default=None, description="公司规模（v1.3：支持多选，旧数据兼容单字符串）"
    )
    # Step 2: 产品/服务（v1.3：新增 product_ids 关联产品列表，旧字段保留兼容）
    product_ids: Optional[List[str]] = Field(
        default=None, description="关联产品 UUID 列表（v1.3 新增）"
    )
    product_category: Optional[str] = Field(
        default=None, description="产品品类（v1.3 废弃，保留兼容）"
    )
    product_price_min: Optional[float] = Field(
        default=None, description="产品最低单价 USD（v1.3 新增）"
    )
    product_price_max: Optional[float] = Field(
        default=None, description="产品最高单价 USD（v1.3 新增）"
    )
    product_price_range: Optional[str] = Field(
        default=None, description="价格区间（v1.3 废弃，保留兼容）"
    )
    product_features: Optional[str] = Field(
        default=None, description="产品特点/优势（v1.3 废弃，保留兼容）"
    )
    # Step 3: 理想客户特征（v1.3 采购商核心特征）
    customer_budget_min: Optional[float] = Field(
        default=None, description="客户单批次采购预算最低 USD（v1.3 新增）"
    )
    customer_budget_max: Optional[float] = Field(
        default=None, description="客户单批次采购预算最高 USD（v1.3 新增）"
    )
    customer_budget: Optional[str] = Field(
        default=None, description="客户预算（v1.3 废弃，保留兼容）"
    )
    # v1.3 采购商核心特征
    buyer_type: Optional[str] = Field(
        default=None, description="买家类型：进口商/品牌商/批发商/经销商/零售商/电商卖家"
    )
    procurement_frequency: Optional[str] = Field(
        default=None, description="采购频次：高频(月)/中等(季)/低频(半年)/不稳定"
    )
    sourcing_channels: Optional[List[str]] = Field(
        default=None, description="主要采购渠道：B2B平台/行业展会/同行推荐/搜索引擎/社交媒体/其他"
    )
    key_decision_factors: Optional[List[str]] = Field(
        default=None, description="关键决策因素：价格/质量/交期/认证资质/售后服务/付款条件/设计能力"
    )
    pain_points: Optional[str] = Field(default=None, description="客户痛点")
    decision_makers: Optional[str] = Field(default=None, description="决策者角色")
    additional_notes: Optional[str] = Field(default=None, description="补充说明")

    @field_validator("company_size", mode="before")
    @classmethod
    def normalize_company_size(cls, v):
        """兼容旧数据：单字符串自动包装为列表"""
        if isinstance(v, str):
            return [v]
        return v


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
    """列表项（含 input_data 摘要字段，v1.3 新增）"""
    id: uuid.UUID
    name: str
    status: str
    target_region: Optional[str] = None
    target_industry: Optional[str] = None
    company_size: Optional[List[str]] = None
    customer_budget: Optional[str] = None
    buyer_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IcpListResponse(BaseModel):
    items: List[IcpListItem]
    total: int
    page: int
    page_size: int
