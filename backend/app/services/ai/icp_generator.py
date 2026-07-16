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
- 产品品类：{product_category}
- 价格区间：{product_price_range}
- 产品特点/优势：{product_features}

## 理想客户特征
- 客户预算：{customer_budget}
- 客户痛点：{pain_points}
- 决策者角色：{decision_makers}

## 补充说明
{additional_notes}
"""


class IcpGenerator:
    """ICP 画像流式生成器"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self._accumulated_text = ""
        self._output: Optional[Dict[str, Any]] = None

    def _build_user_prompt(self, input_data: dict) -> str:
        """根据输入数据构建 user prompt"""
        defaults = {
            "target_industry": "未指定",
            "target_region": "未指定",
            "company_size": "未指定",
            "product_category": "未指定",
            "product_price_range": "未指定",
            "product_features": "未指定",
            "customer_budget": "未指定",
            "pain_points": "未指定",
            "decision_makers": "未指定",
            "additional_notes": "无",
        }
        data = {**defaults, **{k: (v or "未指定") for k, v in input_data.items()}}
        # 转义花括号防止 str.format() 崩溃（用户输入可能含 { }）
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
