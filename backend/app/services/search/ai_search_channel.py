"""AI 搜索渠道 — 基于 LLM 知识生成潜在客户列表（无需外部搜索 API）"""

import json
import logging
from typing import List, Optional

from app.services.search.base import SearchChannel, SearchResult
from app.services.ai_service import AIServiceError, get_ai_service

logger = logging.getLogger(__name__)

AI_SEARCH_SYSTEM_PROMPT = """你是一个 B2B 外贸客户开发专家。根据用户提供的客户画像条件，列出真实存在的潜在客户公司及其关键联系人。

要求：
1. 返回真实存在的公司（基于你的训练数据）
2. 公司名称必须是正式注册名称
3. 网站域名尽可能准确
4. 每条记录包含：company_name（必填）、website、industry、country、city、company_size、description
5. 尽可能提供该公司的关键联系人（采购、销售或管理层），格式为 contacts 数组
6. 联系人信息按 confidence 区分：verified（网页确认过的）> inferred（根据命名规则推测的）> null（完全不确定则不填）
7. 邮箱地址在合理推测时可填写（如根据该公司命名规则推测 firstname.lastname@company.com），标记 confidence 为 "inferred"
8. 返回至少 10 条，最多 20 条结果
9. 仅返回 JSON 数组，不要包含任何其他文字

输出格式示例：
[
  {
    "company_name": "Siemens AG",
    "website": "https://www.siemens.com",
    "industry": "Industrial Automation",
    "country": "Germany",
    "city": "Munich",
    "company_size": "1000+",
    "description": "Global industrial manufacturing conglomerate",
    "contacts": [
      {
        "name": "Roland Busch",
        "title": "CEO",
        "email": "roland.busch@siemens.com",
        "phone": null,
        "linkedin_url": "https://www.linkedin.com/in/roland-busch",
        "confidence": "inferred"
      }
    ]
  }
]
"""


class AISearchChannel(SearchChannel):
    """AI 驱动搜索 — 使用 LLM 基于 ICP 画像生成潜在客户列表"""

    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
    ) -> List[SearchResult]:
        ai_service = get_ai_service()

        user_prompt = f"目标行业/产品：{query}"
        if region:
            user_prompt += f"\n目标区域：{region}"
        user_prompt += f"\n请列出 {max_results} 个潜在客户公司。"

        messages = [
            {"role": "system", "content": AI_SEARCH_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        results: List[SearchResult] = []

        try:
            response = await ai_service.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                timeout=self.timeout,
            )

            content = response.choices[0].message.content
            companies = self._parse_response(content)

            for c in companies:
                name = c.get("company_name", "").strip()
                if not name:
                    continue
                # 处理联系人，保留 confidence 字段
                raw_contacts = c.get("contacts") or []
                contacts = []
                for rc in raw_contacts:
                    contact = {
                        "name": rc.get("name"),
                        "title": rc.get("title"),
                        "email": rc.get("email"),
                        "phone": rc.get("phone"),
                        "linkedin_url": rc.get("linkedin_url"),
                        "confidence": rc.get("confidence", "inferred"),
                    }
                    if contact["name"]:
                        contacts.append(contact)
                results.append(
                    SearchResult(
                        company_name=name,
                        website=c.get("website"),
                        industry=c.get("industry"),
                        country=c.get("country"),
                        city=c.get("city"),
                        company_size=c.get("company_size"),
                        description=c.get("description"),
                        contacts=contacts,
                        source_url=c.get("website"),
                        source_channel="ai_search",
                        skip_extraction=True,
                    )
                )

            logger.info(f"AI search '{query}': found {len(results)} results")

        except AIServiceError as e:
            logger.error(f"AI search error: {e}")
        except Exception as e:
            logger.error(f"AI search unexpected error: {e}")

        return results[:max_results]

    def _parse_response(self, content: str) -> list:
        """解析 LLM 返回的 JSON，兼容多种格式"""
        if not content:
            return []

        content = content.strip()

        # 策略 1：直接 JSON 数组
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "companies" in data:
                return data["companies"]
        except json.JSONDecodeError:
            pass

        # 策略 2：提取 ```json ... ``` 代码块
        if "```json" in content:
            block = content.split("```json")[1].split("```")[0].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                pass
        elif "```" in content:
            block = content.split("```")[1].split("```")[0].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                pass

        # 策略 3：尝试从第一个 [ 到最后一个 ] 提取
        try:
            start = content.index("[")
            end = content.rindex("]") + 1
            return json.loads(content[start:end])
        except (ValueError, json.JSONDecodeError):
            pass

        logger.warning(f"Failed to parse AI search response: {content[:200]}")
        return []
