"""DuckDuckGo 搜索渠道 — 基于 HTML 版搜索（无 JS，爬虫友好）"""

import logging
from typing import List, Optional
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from app.services.search.base import (
    SearchChannel, SearchResult,
    is_non_company_url, looks_like_article_title,
)

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

# DDG HTML 版端点——无需 JS，返回简单 HTML，反爬力度低
_DDG_HTML_URL = "https://html.duckduckgo.com/html/"


class DuckDuckGoSearchChannel(SearchChannel):
    """DuckDuckGo HTML 搜索 — httpx + BeautifulSoup 解析搜索结果"""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
        site_filter: str = "",
    ) -> List[SearchResult]:
        """执行 DuckDuckGo 搜索

        Args:
            query: 搜索关键词
            region: 目标区域（附加到查询）
            max_results: 最大结果数
            site_filter: 可选的 site: 过滤，如 "linkedin.com/company"
        """
        search_terms = [query]
        if region:
            search_terms.append(region)
        if site_filter:
            search_terms.append(f"site:{site_filter}")
        search_query = " ".join(search_terms).strip()

        results: List[SearchResult] = []

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True,
            ) as client:
                resp = await client.post(
                    _DDG_HTML_URL,
                    data={"q": search_query, "b": ""},
                )
                resp.raise_for_status()

                soup = BeautifulSoup(resp.text, "lxml")

                # DDG HTML 版结果结构：div.result > a.result__a (标题+链接) + a.result__snippet
                for result_div in soup.select(".result"):
                    parsed = self._parse_result(result_div, "duckduckgo_search")
                    if parsed and parsed.company_name:
                        if is_non_company_url(parsed.website):
                            continue
                        if looks_like_article_title(parsed.company_name):
                            continue
                        results.append(parsed)

                logger.info(
                    f"DDG search '{search_query}': found {len(results)} results"
                )

        except httpx.HTTPError as e:
            logger.warning(f"DDG search HTTP error: {e}")
        except Exception as e:
            logger.error(f"DDG search unexpected error: {e}")

        return results[:max_results]

    def _parse_result(
        self, result_div, channel: str
    ) -> Optional[SearchResult]:
        """从单个 DDG 搜索结果 div 提取信息"""
        # 标题 + 链接
        link_el = result_div.select_one("a.result__a")
        if not link_el:
            return None

        company_name = link_el.get_text(strip=True)

        # DDG HTML 版的链接格式：//duckduckgo.com/l/?uddg=<encoded_url>
        website = None
        source_url = None
        href = link_el.get("href", "")
        if "uddg=" in href:
            from urllib.parse import unquote
            # 提取实际 URL
            uddg_part = href.split("uddg=")[1].split("&")[0]
            decoded = unquote(uddg_part)
            if decoded.startswith("http"):
                website = decoded
                source_url = decoded
        elif href.startswith("http"):
            website = href
            source_url = href

        # 摘要
        snippet_el = result_div.select_one("a.result__snippet")
        description = snippet_el.get_text(strip=True) if snippet_el else None

        # 尝试从摘要中提取国家/行业信息
        country = None
        industry = None

        return SearchResult(
            company_name=company_name,
            website=website,
            industry=industry,
            country=country,
            description=description,
            source_url=source_url,
            source_channel=channel,
        )

