"""Google 搜索渠道 — 通过 DuckDuckGo 后端实现（Google 直接抓取会触发 CAPTCHA）"""

import logging
from typing import List, Optional

from app.services.search.base import SearchChannel, SearchResult
from app.services.search.duckduckgo_channel import DuckDuckGoSearchChannel

logger = logging.getLogger(__name__)


class GoogleSearchChannel(SearchChannel):
    """Google 公开搜索 — 底层使用 DDG HTML 搜索，附加 site: 过滤模拟 Google 搜索结果"""

    def __init__(self, timeout: float = 15.0) -> None:
        self._ddg = DuckDuckGoSearchChannel(timeout=timeout)

    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
    ) -> List[SearchResult]:
        search_query = f"{query} {region} company".strip()
        results = await self._ddg.search(
            query=search_query,
            region="",
            max_results=max_results,
        )
        # 将渠道标记为 google_search
        for r in results:
            r.source_channel = "google_search"
        logger.info(f"Google (via DDG) search '{query}': found {len(results)} results")
        return results
