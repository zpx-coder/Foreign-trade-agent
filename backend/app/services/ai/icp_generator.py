"""ICP 画像生成器 — Prompt 模板 + 流式输出解析"""

import json
import re
from typing import AsyncIterator, Dict, Any, Optional

from app.services.ai_service import AIService


ICP_SYSTEM_PROMPT = """你是一位资深的外贸 B2B 市场分析专家。你的任务是根据用户提供的信息，生成一份专业的理想客户画像（Ideal Customer Profile）。

## 输出格式要求

请严格按照以下 JSON 结构输出，不要输出任何其他内容。在 JSON 之前和之后都不要添加解释文字。

```json
{
  "summary": "一段 100-150 字的中文摘要，概括该画像的核心客户特征",
  "target_market": {
    "primary_industries": ["行业1", "行业2"],
    "primary_regions": ["地区1", "地区2"],
    "company_size_range": "描述目标公司规模"
  },
  "customer_persona": {
    "decision_makers": [
      {"role": "职位名称", "title": "典型头衔", "concerns": ["关注点1", "关注点2"]}
    ],
    "pain_points": ["痛点1", "痛点2", "痛点3"],
    "buying_motivations": ["采购动机1", "采购动机2"]
  },
  "competitive_advantages": ["我方优势1", "我方优势2", "我方优势3"],
  "recommended_approach": {
    "outreach_channels": ["渠道1", "渠道2"],
    "messaging_angles": ["切入点1", "切入点2"],
    "qualifying_questions": ["筛选问题1", "筛选问题2", "筛选问题3"]
  }
}
```

注意：
- 所有字段必须填写，不能为空数组或空字符串
- 使用中文输出
- 基于用户提供的数据进行分析，不要凭空编造不相关的内容
- 如果用户某些信息缺失，根据行业常识合理推断并标注为"推断"
"""

ICP_USER_PROMPT_TEMPLATE = """请根据以下信息生成理想客户画像：

## 目标市场
- 目标行业：{target_industry}
- 目标地区：{target_region}
- 公司规模：{company_size}

## 产品/服务信息
{products_section}

## 采购商核心特征
- 买家类型：{buyer_type}
- 单批次采购预算：{customer_budget}
- 采购频次：{procurement_frequency}
- 主要采购渠道：{sourcing_channels}
- 关键决策因素：{key_decision_factors}
- 决策者角色：{decision_makers}
- 客户痛点：{pain_points}

## 补充说明
{additional_notes}
"""


def _fmt_list_or_str(value) -> str:
    """格式化列表或字符串为 prompt 可读文本"""
    if isinstance(value, list):
        return "、".join(value) if value else "未指定"
    if isinstance(value, str) and value.strip():
        return value
    return "未指定"


class IcpGenerator:
    """ICP 画像流式生成器"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self._accumulated_text = ""
        self._output: Optional[Dict[str, Any]] = None

    def _build_user_prompt(self, input_data: dict) -> str:
        """根据输入数据构建 user prompt（v1.3 适配结构化字段）"""
        # ── 公司规模（v1.3：支持数组）──
        company_size = input_data.get("company_size")
        if isinstance(company_size, list):
            company_size = "、".join(company_size) if company_size else "未指定"
        elif isinstance(company_size, str) and company_size.strip():
            company_size = company_size
        else:
            company_size = "未指定"

        # ── 产品信息（v1.5：支持 manual_products 手动填写 + _products_inline 关联产品 + 旧字段回退）──
        product_source = input_data.get("product_source", "linked")
        products_inline = input_data.get("_products_inline")  # 前端快照传入
        manual_products = input_data.get("manual_products")  # v1.5 手动填写

        def _format_product(p: dict) -> str:
            """格式化单个产品为 prompt 文本"""
            name = p.get("name", "未命名")
            desc = p.get("description", "")
            price = p.get("price_usd")
            moq = p.get("moq")
            category = p.get("category", "")
            hs_code = p.get("hs_code", "")
            parts = [f"- 产品：{name}"]
            if category:
                parts.append(f"  品类：{category}")
            if desc:
                parts.append(f"  描述：{desc}")
            if price is not None:
                parts.append(f"  单价：${price} USD")
            if moq is not None:
                parts.append(f"  起订量：{moq}")
            if hs_code:
                parts.append(f"  HS编码：{hs_code}")
            return "\n".join(parts)

        if product_source == "manual" and manual_products and isinstance(manual_products, list):
            products_section = "\n\n".join(_format_product(p) for p in manual_products)
        elif products_inline and isinstance(products_inline, list):
            products_section = "\n\n".join(_format_product(p) for p in products_inline)
        else:
            # 结构化价格
            price_min = input_data.get("product_price_min")
            price_max = input_data.get("product_price_max")
            price_range = input_data.get("product_price_range", "未指定")
            if price_min is not None and price_max is not None:
                price_range = f"${price_min} — ${price_max} USD"
            elif price_min is not None:
                price_range = f"≥ ${price_min} USD"
            elif price_max is not None:
                price_range = f"≤ ${price_max} USD"

            old_category = input_data.get("product_category", "未指定") or "未指定"
            old_features = input_data.get("product_features", "未指定") or "未指定"
            products_section = (
                f"- 产品品类：{old_category}\n"
                f"- 价格区间：{price_range}\n"
                f"- 产品特点/优势：{old_features}"
            )

        # ── 客户预算（v1.3：结构化 min/max 优先）──
        budget_min = input_data.get("customer_budget_min")
        budget_max = input_data.get("customer_budget_max")
        if budget_min is not None and budget_max is not None:
            customer_budget = f"${budget_min:,.0f} — ${budget_max:,.0f} USD"
        elif budget_min is not None:
            customer_budget = f"≥ ${budget_min:,.0f} USD"
        elif budget_max is not None:
            customer_budget = f"≤ ${budget_max:,.0f} USD"
        else:
            customer_budget = input_data.get("customer_budget", "未指定") or "未指定"

        data = {
            "target_industry": input_data.get("target_industry") or "未指定",
            "target_region": input_data.get("target_region") or "未指定",
            "company_size": company_size,
            "products_section": products_section,
            "customer_budget": customer_budget,
            # v1.3 采购商核心特征
            "buyer_type": input_data.get("buyer_type") or "未指定",
            "procurement_frequency": input_data.get("procurement_frequency") or "未指定",
            "sourcing_channels": _fmt_list_or_str(input_data.get("sourcing_channels")),
            "key_decision_factors": _fmt_list_or_str(input_data.get("key_decision_factors")),
            "pain_points": input_data.get("pain_points") or "未指定",
            "decision_makers": input_data.get("decision_makers") or "未指定",
            "additional_notes": input_data.get("additional_notes") or "无",
        }
        # 转义花括号防止 str.format() 崩溃
        safe_data = {k: str(v).replace("{", "{{").replace("}", "}}") for k, v in data.items()}
        return ICP_USER_PROMPT_TEMPLATE.format(**safe_data)

    def _parse_output(self, text: str) -> Optional[Dict[str, Any]]:
        """从完整文本中提取 JSON"""
        # 尝试提取 ```json ... ``` 块
        match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 尝试直接解析整个文本
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # 尝试找到第一个 { 和最后一个 }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None

    def _detect_section(self, text: str) -> Optional[str]:
        """检测当前正在生成的章节"""
        sections = ["summary", "target_market", "customer_persona", "competitive_advantages", "recommended_approach"]
        for section in sections:
            if f'"{section}"' in text and not self._is_section_complete(text, section):
                return section
        return None

    def _is_section_complete(self, text: str, section: str) -> bool:
        """简单判断某个章节是否已完成（存在该 key 且有后续 key 或结尾）"""
        keys_in_order = ["summary", "target_market", "customer_persona", "competitive_advantages", "recommended_approach"]
        if section not in keys_in_order:
            return False
        idx = keys_in_order.index(section)
        if idx + 1 < len(keys_in_order):
            return keys_in_order[idx + 1] in text
        return "}" in text.split(f'"{section}"')[1] if f'"{section}"' in text else False

    async def generate(self, input_data: dict) -> AsyncIterator[Dict[str, Any]]:
        """流式生成 ICP 画像，逐 chunk yield 结构化事件"""
        user_prompt = self._build_user_prompt(input_data)
        messages = [
            {"role": "system", "content": ICP_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        current_section: Optional[str] = None
        self._accumulated_text = ""

        async for token in self.ai_service.chat_stream(messages, temperature=0.7, max_tokens=4096):
            self._accumulated_text += token

            # 检测当前段落
            section = self._detect_section(self._accumulated_text)
            if section and section != current_section:
                current_section = section
                yield {"type": "section", "section": section}

            yield {"type": "text", "content": token}

        # 解析最终输出
        self._output = self._parse_output(self._accumulated_text)

        if self._output is None:
            # 解析失败时提供原始文本
            self._output = {
                "raw_text": self._accumulated_text,
                "parse_error": True,
            }

        yield {"type": "done"}

    def get_output(self) -> Optional[Dict[str, Any]]:
        """获取解析后的完整输出"""
        return self._output
