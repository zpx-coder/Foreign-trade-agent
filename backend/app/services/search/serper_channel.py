"""Serper.dev Google 搜索渠道 — 结构化 JSON 返回，无需解析 HTML

Serper.dev 免费额度：2500 次/月
API 文档：https://serper.dev/api-reference
"""

import logging
from typing import List, Optional
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.services.search.base import SearchChannel, SearchResult

logger = logging.getLogger(__name__)

_SERPER_BASE = "https://google.serper.dev"

# 非公司网站域名黑名单：命中任一关键词则丢弃该结果
_NON_COMPANY_DOMAIN_KEYWORDS = [
    "zhihu.com", "medium.com", "blog.", "blogs.",
    "wikipedia.org", "baike.baidu.com", "wiki.",
    "news.", "forbes.com", "36kr.com", "sohu.com",
    "ifeng.com", "163.com", "qq.com", "sina.com.cn",
    "bbc.com", "cnn.com", "reuters.com", "bloomberg.com",
    "finance.yahoo.com", "marketwatch.com",
    "quora.com", "reddit.com", "stackexchange.com",
    "stackoverflow.com", "zhidao.baidu.com",
    "youtube.com", "youtu.be", "bilibili.com",
    "facebook.com", "twitter.com", "instagram.com",
    "tiktok.com", "weibo.com",
    "linkedin.com/jobs", "indeed.com", "glassdoor.com",
    "zhaopin.com", "51job.com",
    "amazon.com", "ebay.com", "alibaba.com/products",
]


class SerperSearchChannel(SearchChannel):
    """Serper.dev Google 搜索 — httpx + JSON 解析"""

    def __init__(self, timeout: float = 15.0) -> None:
        self._api_key = settings.SERPER_API_KEY
        self.timeout = timeout

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
        site_filter: str = "",
    ) -> List[SearchResult]:
        """执行 Google 搜索（通过 Serper.dev）

        Args:
            query: 搜索关键词
            region: 目标区域（附加到查询中）
            max_results: 最大结果数
            site_filter: 可选的 site: 过滤
        """
        if not self._api_key:
            logger.warning("Serper API key not configured, skipping")
            return []

        # 构建搜索词
        search_terms = [query]
        if region:
            search_terms.append(region)
        search_terms.append("company")  # 偏向公司结果
        if site_filter:
            search_terms.append(f"site:{site_filter}")
        search_query = " ".join(search_terms).strip()

        results: List[SearchResult] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{_SERPER_BASE}/search",
                    json={
                        "q": search_query,
                        "num": min(max_results, 100),
                        "gl": self._region_to_gl(region) if region else "us",
                    },
                    headers={
                        "X-API-KEY": self._api_key,
                        "Content-Type": "application/json",
                    },
                )

                if resp.status_code == 200:
                    data = resp.json()
                    organic = data.get("organic", [])

                    for item in organic:
                        parsed = self._parse_result(item)
                        if parsed and parsed.company_name:
                            if self._is_non_company_url(parsed.website):
                                continue
                            results.append(parsed)

                    logger.info(
                        f"Serper search '{search_query}': "
                        f"{len(results)}/{len(organic)} results kept"
                    )

                elif resp.status_code == 429:
                    logger.warning("Serper API rate limit exceeded")
                elif resp.status_code == 403:
                    logger.error("Serper API key invalid or expired")
                else:
                    logger.warning(
                        f"Serper API error {resp.status_code}: "
                        f"{resp.text[:200]}"
                    )

        except httpx.HTTPError as e:
            logger.warning(f"Serper API request failed: {e}")
        except Exception as e:
            logger.error(f"Serper API unexpected error: {e}")

        return results[:max_results]

    def _parse_result(self, item: dict) -> Optional[SearchResult]:
        """从 Serper 单条搜索结果提取公司信息"""
        title = item.get("title", "").strip()
        link = item.get("link", "").strip()
        snippet = item.get("snippet", "").strip()

        if not link:
            return None

        # 提取域名
        domain = self._extract_domain(link)
        if not domain:
            return None

        # 公司名称优先从标题取（去掉常见的后缀）
        company_name = self._clean_company_name(title)

        return SearchResult(
            company_name=company_name,
            website=link,
            industry=None,
            country=None,
            city=None,
            description=snippet or None,
            source_url=link,
            source_channel="serper_search",
        )

    @staticmethod
    def _extract_domain(url_str: str) -> Optional[str]:
        """从 URL 提取域名"""
        try:
            parsed = urlparse(url_str if "://" in url_str else f"https://{url_str}")
            netloc = parsed.netloc
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return None

    @staticmethod
    def _clean_company_name(title: str) -> str:
        """清理搜索结果标题，提取公司名"""
        # 去掉常见分隔符后的内容
        for sep in [" | ", " - ", " – ", " :: ", " — "]:
            if sep in title:
                # 取第一个分隔符前的部分作为公司名
                parts = title.split(sep)
                # 但如果是 "Company - Description" 格式，取第一部分
                first = parts[0].strip()
                if len(first) >= 2:
                    return first
        return title.strip()

    @staticmethod
    def _region_to_gl(region: str) -> str:
        """将区域名映射为 Google 国家代码（gl 参数）"""
        region_lower = region.lower().strip()
        mapping = {
            "us": "us", "usa": "us", "united states": "us",
            "uk": "gb", "united kingdom": "gb", "england": "gb",
            "germany": "de", "deutschland": "de",
            "france": "fr",
            "japan": "jp",
            "korea": "kr", "south korea": "kr",
            "canada": "ca",
            "australia": "au",
            "brazil": "br",
            "india": "in",
            "italy": "it",
            "spain": "es",
            "netherlands": "nl",
            "mexico": "mx",
            "singapore": "sg",
        }
        return mapping.get(region_lower, region_lower[:2])

    @staticmethod
    def _is_non_company_url(url: Optional[str]) -> bool:
        """检查 URL 是否命中非公司网站黑名单"""
        if not url:
            return False
        url_lower = url.lower()
        for keyword in _NON_COMPANY_DOMAIN_KEYWORDS:
            if keyword in url_lower:
                return True
        return False
