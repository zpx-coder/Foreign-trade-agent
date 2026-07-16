"""搜索渠道抽象接口 — Phase 4"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class SearchResult:
    """搜索结果 — 渠道无关的标准化结构"""
    company_name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    contacts: List[Dict[str, Any]] = field(default_factory=list)
    source_url: Optional[str] = None
    source_channel: str = ""
    # 如果为 True，跳过 LLM 提取步骤直接保存（AI 渠道已返回结构化数据）
    skip_extraction: bool = False

    @property
    def domain(self) -> str:
        """提取域名用于去重"""
        if not self.website:
            return self.company_name.lower().strip()
        from urllib.parse import urlparse
        parsed = urlparse(self.website if "://" in self.website else f"https://{self.website}")
        return parsed.netloc or self.website.lower().strip()


class SearchChannel(ABC):
    """搜索渠道抽象基类"""

    @abstractmethod
    async def search(
        self,
        query: str,
        region: str = "",
        max_results: int = 20,
    ) -> List[SearchResult]:
        """执行搜索，返回标准化结果列表"""
        ...
