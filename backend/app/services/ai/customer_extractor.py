"""客户信息提取器 — 从网页 HTML 中 LLM 提取结构化公司数据"""

import json
import re
from typing import AsyncIterator, Dict, Any, Optional

from app.services.ai_service import AIService


EXTRACTOR_SYSTEM_PROMPT = """你是一位专业的商业数据提取专家。你的任务是分析网页内容，判断该页面是否为潜在客户公司的官网/企业信息页/B2B平台公司页，如果是则提取结构化公司信息。

## 第一步：页面类型判断

首先判断页面内容是否属于以下类型之一（公司页面）：
- 公司官方网站的首页或关于我们页面
- B2B 平台上的公司主页（如 Alibaba、Made-in-China、Global Sources 等）
- LinkedIn 公司页面
- 行业协会会员列表中的公司详情页
- 企业黄页/工商信息页面

如果页面属于以下类型，则**不是**公司页面，不应提取：
- 行业资讯/新闻文章
- 博客文章/技术教程
- 论坛帖子/问答页面
- 产品列表聚合页（列出了多家公司的产品）
- 行业分析报告/市场研究报告
- 采购指南/选型指南类文章
- 知乎/百度知道等问答平台内容
- 维基百科词条
- 招聘信息页面

## 第二步：输出格式

如果页面是公司页面，请严格按照以下 JSON 结构输出，不要输出任何其他内容：

```json
{
  "is_company_page": true,
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

如果页面**不是**公司页面（文章、博客、新闻、论坛等），请输出：

```json
{
  "is_company_page": false,
  "company_name": null,
  "industry": null,
  "website": null,
  "country": null,
  "city": null,
  "company_size": null,
  "description": null,
  "contacts": []
}
```

注意事项：
- 仅提取网页中明确出现的信息，不要编造
- 如果某字段信息不存在，使用 null（不是空字符串）
- contacts 数组中只包含网页中确实出现的联系人
- 如果完全没有联系人信息，contacts 应为空数组 []
- 忽略广告、导航栏等无关内容
- **关键**：如果页面不是公司官网/企业信息页，必须返回 is_company_page: false，不要强行从文章内容中提取公司名
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
        """获取解析后的完整输出。

        如果 LLM 判断页面不是公司页面（is_company_page=False），返回 None，
        调用方应跳过该结果。
        """
        if self._output is None:
            return None
        # 门禁检查：非公司页面则返回 None
        if self._output.get("is_company_page") is False:
            return None
        # 兼容旧版 prompt（无 is_company_page 字段），按有效结果返回
        if "is_company_page" not in self._output:
            return self._output
        return self._output
