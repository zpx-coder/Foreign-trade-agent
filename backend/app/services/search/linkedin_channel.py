"""LinkedIn 搜索渠道 — 通过 DuckDuckGo + site:linkedin.com/company 实现"""

import logging
from typing import List, Optional

from app.services.search.base import SearchChannel, SearchResult
from app.services.search.duckduckgo_channel import DuckDuckGoSearchChannel

logger = logging.getLogger(__name__)


class LinkedInSearchChannel(SearchChannel):
    """LinkedIn 公开搜索 — 底层使用 DDG HTML 搜索 + site:linkedin.com/company 过滤"""

    def __init__(self, timeout: float = 15.0) -> None:
        self._ddg = DuckDuckGoSearchChannel(timeout=timeout)

    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
    ) -> List[SearchResult]:
        search_query = f"{query} {region}".strip()
        results = await self._ddg.search(
            query=search_query,
            region="",
            max_results=max_results,
            site_filter="linkedin.com/company",
        )
        # 将渠道标记为 linkedin_search
        for r in results:
            r.source_channel = "linkedin_search"
        logger.info(
            f"LinkedIn (via DDG site:linkedin.com/company) search "
            f"'{query}': found {len(results)} results"
        )
        return results
