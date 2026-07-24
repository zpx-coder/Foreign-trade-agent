"""搜索结果聚合器 — 去重 + 合并 + LLM 结构化清洗"""

import logging
from typing import List
from urllib.parse import urlparse

from app.services.search.base import SearchResult

logger = logging.getLogger(__name__)


class SearchAggregator:
    """搜索结果聚合：按域名去重，保留信息最完整的条目"""

    def aggregate(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重 + 合并多渠道结果"""
        if not results:
            return []

        grouped: dict[str, SearchResult] = {}

        for r in results:
            key = self._normalize_key(r)
            if key in grouped:
                grouped[key] = self._merge(grouped[key], r)
            else:
                grouped[key] = r

        aggregated = list(grouped.values())
        # 按信息来源完整度排序：有网站 > 有描述 > 仅名称
        aggregated.sort(key=self._completeness_score, reverse=True)

        logger.info(
            f"Aggregated {len(results)} results → {len(aggregated)} unique"
        )
        return aggregated

    def _normalize_key(self, result: SearchResult) -> str:
        """去重键：域名的规范形式"""
        domain = result.domain
        # 去掉 www 前缀
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower().strip().rstrip("/")

    def _merge(self, a: SearchResult, b: SearchResult) -> SearchResult:
        """合并两个同域名的结果，保留非空字段"""
        # 合并 source_channel，按 ", " 拆分后去重再合并
        raw_sources = []
        for src in (a.source_channel, b.source_channel):
            if src:
                raw_sources.extend(s.strip() for s in src.split(", ") if s.strip())
        merged_source = ", ".join(dict.fromkeys(raw_sources))

        merged = SearchResult(
            company_name=a.company_name or b.company_name,
            website=a.website or b.website,
            industry=a.industry or b.industry,
            country=a.country or b.country,
            city=a.city or b.city,
            description=a.description or b.description,
            contacts=a.contacts if a.contacts else b.contacts,
            source_url=a.source_url or b.source_url,
            source_channel=merged_source,
        )
        return merged

    def _completeness_score(self, r: SearchResult) -> int:
        """信息完整度评分"""
        score = 0
        if r.website:
            score += 3
        if r.industry:
            score += 2
        if r.country:
            score += 1
        if r.description:
            score += 1
        if r.contacts:
            score += 2
        return score
