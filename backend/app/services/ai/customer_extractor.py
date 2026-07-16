"""客户信息提取器 — 从网页 HTML 中 LLM 提取结构化公司数据"""

import json
import re
from typing import AsyncIterator, Dict, Any, Optional

from app.services.ai_service import AIService


EXTRACTOR_SYSTEM_PROMPT = """你是一位专业的商业数据提取专家。你的任务是分析网页内容，从中提取潜在客户公司的结构化信息。

## 输出格式要求

请严格按照以下 JSON 结构输出，不要输出任何其他内容。在 JSON 之前和之后都不要添加解释文字。

```json
{
  "company_name": "公司名称",
  "industry": "所属行业",
  "website": "公司官网 URL",
  "country": "国家",
  "city": "城市",
  "company_size": "公司规模（如 1-50, 50-200, 200+）",
  "description": "一段 50-100 字的公司业务描述",
  "contacts": [
    {
      "name": "联系人姓名",
      "title": "职位",
      "email": "邮箱地址",
      "phone": "电话（如有）",
      "linkedin_url": "LinkedIn URL（如有）"
    }
  ]
}
```

注意事项：
- 仅提取网页中明确出现的信息，不要编造
- 如果某字段信息不存在，使用 null（不是空字符串）
- contacts 数组中只包含网页中确实出现的联系人
- 如果完全没有联系人信息，contacts 应为空数组 []
- 忽略广告、导航栏等无关内容
"""

EXTRACTOR_USER_PROMPT_TEMPLATE = """请从以下网页内容中提取公司信息。

## 网页 URL
{url}

## 网页内容（截取前 10000 字符）
```
{content}
```
"""


class CustomerExtractor:
    """客户信息流式提取器 — 复用 IcpGenerator 模式"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self._accumulated_text = ""
        self._output: Optional[Dict[str, Any]] = None

    def _build_user_prompt(self, content: str, url: str) -> str:
        """构建提取 user prompt"""
        # 截断过长内容以避免超出 token 限制
        truncated = content[:10000] if len(content) > 10000 else content
        return EXTRACTOR_USER_PROMPT_TEMPLATE.format(url=url, content=truncated)

    def _parse_output(self, text: str) -> Optional[Dict[str, Any]]:
        """从 LLM 响应中提取 JSON"""
        # 策略 1: ```json ... ``` 代码块
        match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 策略 2: 直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # 策略 3: 首尾花括号
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None

    async def extract(
        self, content: str, url: str = ""
    ) -> AsyncIterator[Dict[str, Any]]:
        """流式提取，逐 chunk yield 结构化事件"""
        user_prompt = self._build_user_prompt(content, url)
        messages = [
            {"role": "system", "content": EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        self._accumulated_text = ""

        async for token in self.ai_service.chat_stream(
            messages, temperature=0.3, max_tokens=2048
        ):
            self._accumulated_text += token
            yield {"type": "text", "content": token}

        # 解析最终输出
        self._output = self._parse_output(self._accumulated_text)

        if self._output is None:
            self._output = {
                "raw_text": self._accumulated_text,
                "parse_error": True,
            }

        yield {"type": "done"}

    def get_output(self) -> Optional[Dict[str, Any]]:
        """获取解析后的完整输出"""
        return self._output
