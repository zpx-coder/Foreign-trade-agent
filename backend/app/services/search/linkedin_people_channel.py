"""LinkedIn 人物搜索渠道 — 搜索 site:linkedin.com/in 找真实人名+职位"""

import logging
import re
from typing import List, Optional, Dict, Any

from app.services.search.base import SearchChannel, SearchResult
from app.services.search.duckduckgo_channel import DuckDuckGoSearchChannel

logger = logging.getLogger(__name__)

# 从 LinkedIn 摘要中提取 "Name — Title at Company" 模式
_NAME_TITLE_RE = re.compile(
    r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+?)\s*[—–-]\s*(.+?)(?:\s+at\s+(.+?))?(?:\s*[-—–]\s*|\s*$)',
    re.IGNORECASE,
)

# 单独的 "Name | Title" 或 "Name, Title" 模式
_NAME_TITLE_ALT_RE = re.compile(
    r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+?)\s*[|,]\s*(.+?)(?:\s*$)',
    re.IGNORECASE,
)


class LinkedInPeopleSearchChannel(SearchChannel):
    """LinkedIn 人物搜索 — 使用 DDG site:linkedin.com/in 查找真实个人资料"""

    def __init__(self, timeout: float = 15.0) -> None:
        self._ddg = DuckDuckGoSearchChannel(timeout=timeout)

    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
    ) -> List[SearchResult]:
        """执行 LinkedIn 人物搜索

        Args:
            query: 搜索关键词（行业/产品/地区）
            region: 目标区域（附加到查询）
            max_results: 最大结果数
        """
        # 构建针对人物的搜索查询
        search_terms = [query]
        if region:
            search_terms.append(region)
        # 添加职位相关关键词以提高命中率
        search_terms.append("(procurement OR purchasing OR sourcing OR buyer OR manager OR director)")
        search_query = " ".join(search_terms).strip()

        results: List[SearchResult] = []

        try:
            raw_results = await self._ddg.search(
                query=search_query,
                region="",
                max_results=max_results,
                site_filter="linkedin.com/in",
            )

            for r in raw_results:
                # 从搜索结果摘要中提取人名和职位
                contacts = self._extract_contacts_from_snippet(
                    r.company_name,  # 这是搜索结果的标题（通常是人名）
                    r.description,   # 搜索结果的摘要
                )

                result = SearchResult(
                    company_name="Unknown",  # 公司名通常不在个人资料摘要中
                    website=None,
                    industry=None,
                    country=None,
                    city=None,
                    company_size=None,
                    description=r.description,
                    contacts=contacts,
                    source_url=r.source_url,  # LinkedIn URL
                    source_channel="linkedin_people_search",
                    skip_extraction=False,
                )
                results.append(result)

            logger.info(
                f"LinkedIn People search '{query}': found {len(results)} profiles, "
                f"{sum(len(r.contacts) for r in results)} contacts extracted"
            )

        except Exception as e:
            logger.error(f"LinkedIn People search unexpected error: {e}")

        return results[:max_results]

    def _extract_contacts_from_snippet(
        self, title: str, snippet: Optional[str]
    ) -> List[Dict[str, Any]]:
        """从 LinkedIn 搜索结果摘要中提取联系人信息

        LinkedIn 在 DDG HTML 搜索结果中通常显示格式：
        - 标题: "John Smith - Procurement Manager at ABC Corp - LinkedIn"
        - 摘要: "Location: New York, NY · 500+ connections · ..."
        """
        contacts = []
        if not title:
            return contacts

        # 清理标题：去掉 " - LinkedIn" 和多余信息
        clean_title = re.sub(r'\s*[-—–]\s*LinkedIn\s*$', '', title, flags=re.IGNORECASE)

        # 模式 1: "Name — Title at Company"
        match = _NAME_TITLE_RE.match(clean_title)
        if not match:
            # 模式 2: "Name | Title"
            match = _NAME_TITLE_ALT_RE.match(clean_title)

        if match:
            name = match.group(1).strip()
            title_part = match.group(2).strip()
            company = match.group(3).strip() if match.lastindex and match.lastindex >= 3 else None

            # 过滤假人名（太短或包含非姓名关键词）
            name_parts = name.split()
            if len(name_parts) >= 2 and len(name) > 3 and not any(
                kw in name.lower() for kw in ("search", "find", "hire", "linkedin")
            ):
                linkedin_url = None
                # 尝试从摘要中提取 LinkedIn URL
                if snippet:
                    url_match = re.search(
                        r'(https?://[^\s]*linkedin\.com/in/[^\s)"]+)',
                        snippet,
                    )
                    if url_match:
                        linkedin_url = url_match.group(1)

                contacts.append({
                    "name": name,
                    "title": title_part if title_part else None,
                    "email": None,
                    "phone": None,
                    "linkedin_url": linkedin_url,
                })

                # 如果有公司名，尝试存储为联系人备注
                if company and not title_part.lower().startswith(company.lower()):
                    pass  # company name extracted from title

        elif len(clean_title.strip()) > 3 and " " in clean_title.strip():
            # 没有明确职位格式，但有可能是人名
            name_parts = clean_title.strip().split()
            if len(name_parts) >= 2:
                contacts.append({
                    "name": clean_title.strip(),
                    "title": None,
                    "email": None,
                    "phone": None,
                    "linkedin_url": None,
                })

        return contacts
