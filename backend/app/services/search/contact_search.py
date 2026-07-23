"""AI 驱动的定向联系人搜索 — 对每个公司生成精确搜索查询"""

import logging
import re
from typing import List, Dict, Any, Optional

from app.services.search.base import SearchChannel, SearchResult
from app.services.search.duckduckgo_channel import DuckDuckGoSearchChannel

logger = logging.getLogger(__name__)

# 从搜索结果提取邮箱的正则
_EMAIL_IN_TEXT_RE = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE,
)

# 从搜索结果提取 "Name, Title" 模式
_NAME_PLUS_TITLE_RE = re.compile(
    r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\s*[,—–-]\s*(?:'
    r'procurement|purchasing|sourcing|buyer|manager|director|VP|head|chief'
    r')',
    re.IGNORECASE,
)


class ContactSearchService:
    """AI 驱动的定向联系人搜索器

    对已知公司生成精确搜索查询，从搜索结果中提取联系人信息。
    不依赖外部 AI，纯搜索 + 正则提取。
    """

    def __init__(self, timeout: float = 15.0) -> None:
        self._ddg = DuckDuckGoSearchChannel(timeout=timeout)

    async def search_company_contacts(
        self,
        company_name: str,
        domain: Optional[str] = None,
        region: str = "",
    ) -> List[Dict[str, Any]]:
        """针对单个公司搜索联系人

        Args:
            company_name: 公司名称
            domain: 公司域名（用于邮箱搜索）
            region: 目标区域

        Returns:
            联系人列表
        """
        all_contacts: List[Dict[str, Any]] = []

        # 生成多个搜索查询
        queries = self._build_search_queries(company_name, domain, region)

        for query_info in queries:
            try:
                results = await self._ddg.search(
                    query=query_info["query"],
                    region=region,
                    max_results=10,
                )
                for r in results:
                    contacts = self._extract_contacts_from_result(r, company_name, domain)
                    for c in contacts:
                        # 避免重复
                        c_name = c.get("name", "").lower()
                        if c_name and not any(
                            existing.get("name", "").lower() == c_name
                            for existing in all_contacts
                        ):
                            all_contacts.append(c)

            except Exception as e:
                logger.warning(
                    f"Contact search failed for '{company_name}' "
                    f"query '{query_info['query']}': {e}"
                )

        logger.info(
            f"Contact search for '{company_name}': "
            f"found {len(all_contacts)} contacts across {len(queries)} queries"
        )
        return all_contacts

    def _build_search_queries(
        self, company_name: str, domain: Optional[str], region: str
    ) -> List[Dict[str, str]]:
        """构建针对性的搜索查询"""
        queries = []

        # Query 1: 公司名 + 联系人邮箱
        if domain:
            domain_clean = domain.replace("https://", "").replace("http://", "").rstrip("/")
            queries.append({
                "query": f'"{company_name}" email @{domain_clean} contact',
                "type": "email",
            })
            # Query 2: 公司名 + 邮箱域名（可能出现在第三方目录中）
            queries.append({
                "query": f'"{company_name}" "@{domain_clean.split(".")[0]}" contact email',
                "type": "email",
            })

        # Query 3: 公司名 + 采购/管理关键词
        queries.append({
            "query": f'"{company_name}" procurement OR purchasing OR sourcing manager',
            "type": "people",
        })

        # Query 4: 公司名 + LinkedIn
        queries.append({
            "query": f'"{company_name}" linkedin.com/in procurement OR purchasing',
            "type": "linkedin",
        })

        # Query 5: 公司名 + 联系方式页面
        queries.append({
            "query": f'"{company_name}" "contact us" OR "our team" email phone',
            "type": "contact_page",
        })

        return queries

    def _extract_contacts_from_result(
        self,
        result: SearchResult,
        company_name: str,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """从单个搜索结果中提取联系人信息"""
        contacts = []

        text_to_search = f"{result.company_name} {result.description or ''}"

        # 提取邮箱
        emails = _EMAIL_IN_TEXT_RE.findall(text_to_search)
        valid_emails = [
            e for e in emails
            if not e.endswith((".png", ".jpg", ".gif", ".svg", ".css", ".js", ".ico"))
            and len(e.split("@")[0]) >= 2
        ]

        # 提取人名+职位
        name_title_matches = _NAME_PLUS_TITLE_RE.findall(text_to_search)

        # 如果有邮箱信息，创建联系人
        for email in valid_emails[:3]:
            # 尝试从邮箱前缀推断名字
            name_part = email.split("@")[0]
            inferred_name = name_part.replace(".", " ").replace("_", " ").replace("-", " ").title()
            contacts.append({
                "name": inferred_name if len(inferred_name) > 2 else None,
                "title": None,
                "email": email,
                "phone": None,
                "linkedin_url": None,
            })

        # 如果有 name+title 匹配
        for name in name_title_matches:
            contacts.append({
                "name": name.strip(),
                "title": None,
                "email": None,
                "phone": None,
                "linkedin_url": result.source_url if "linkedin.com/in" in (result.source_url or "") else None,
            })

        return contacts
