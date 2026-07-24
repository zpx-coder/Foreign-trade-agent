"""Hunter.io API 集成 — 域名邮箱发现与验证

Hunter.io 免费额度：25 次域名搜索 + 50 次邮箱验证 / 月
API 文档：https://hunter.io/api-documentation/v2
"""

import logging
from typing import List, Dict, Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_HUNTER_BASE = "https://api.hunter.io/v2"


class HunterService:
    """Hunter.io 邮箱发现服务"""

    def __init__(self) -> None:
        self._api_key = settings.HUNTER_API_KEY

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    async def domain_search(
        self, domain: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """搜索某个域名的所有公开邮箱地址。

        Args:
            domain: 公司域名（如 example.com）
            limit: 最多返回数量

        Returns:
            联系人列表 [{"name": ..., "title": ..., "email": ..., "phone": ..., "linkedin_url": ..., "confidence": ...}, ...]
        """
        if not self._api_key:
            return []

        domain_clean = domain.replace("https://", "").replace("http://", "").rstrip("/").split("/")[0]

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{_HUNTER_BASE}/domain-search",
                    params={
                        "domain": domain_clean,
                        "api_key": self._api_key,
                        "limit": min(limit, 50),
                    },
                )
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    emails = data.get("emails", [])

                    contacts = []
                    for entry in emails:
                        # 过滤掉 role/verification 中明确无效的
                        verification = entry.get("verification", {})
                        if verification.get("status") in ("invalid", "disabled"):
                            continue

                        name_parts = [
                            entry.get("first_name"),
                            entry.get("last_name"),
                        ]
                        name = " ".join(p for p in name_parts if p) or None

                        contacts.append({
                            "name": name,
                            "title": entry.get("position"),
                            "email": entry.get("value"),
                            "phone": entry.get("phone_number"),
                            "linkedin_url": entry.get("linkedin_url"),
                            "confidence": (
                                "high" if entry.get("confidence", 0) >= 80
                                else "medium" if entry.get("confidence", 0) >= 50
                                else "low"
                            ),
                            "source": "hunter_domain_search",
                            "email_type": entry.get("type"),  # personal / generic
                        })

                    # 按置信度排序
                    contacts.sort(
                        key=lambda c: (
                            0 if c["confidence"] == "high"
                            else 1 if c["confidence"] == "medium"
                            else 2
                        )
                    )

                    logger.info(
                        f"Hunter domain search for '{domain_clean}': "
                        f"{len(contacts)} contacts found "
                        f"(total: {data.get('results', 0)}, "
                        f"pattern: {data.get('pattern')})"
                    )
                    return contacts

                elif resp.status_code == 429:
                    logger.warning("Hunter API rate limit exceeded")
                elif resp.status_code == 401:
                    logger.error("Hunter API key invalid")
                else:
                    logger.warning(
                        f"Hunter API error {resp.status_code}: "
                        f"{resp.text[:200]}"
                    )

        except httpx.HTTPError as e:
            logger.warning(f"Hunter API request failed: {e}")
        except Exception as e:
            logger.error(f"Hunter API unexpected error: {e}")

        return []

    async def email_finder(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> Optional[Dict[str, Any]]:
        """根据姓名和域名查找具体邮箱地址（消耗 API 配额较多，谨慎使用）。

        Args:
            domain: 公司域名
            first_name: 名
            last_name: 姓

        Returns:
            单个联系人信息，或 None
        """
        if not self._api_key:
            return None

        domain_clean = domain.replace("https://", "").replace("http://", "").rstrip("/").split("/")[0]

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{_HUNTER_BASE}/email-finder",
                    params={
                        "domain": domain_clean,
                        "first_name": first_name,
                        "last_name": last_name,
                        "api_key": self._api_key,
                    },
                )
                if resp.status_code == 200:
                    entry = resp.json().get("data", {})
                    if entry.get("email"):
                        return {
                            "name": f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip(),
                            "title": entry.get("position"),
                            "email": entry.get("email"),
                            "phone": entry.get("phone_number"),
                            "linkedin_url": entry.get("linkedin_url"),
                            "confidence": "high" if entry.get("score", 0) >= 80 else "medium",
                            "source": "hunter_email_finder",
                        }
                elif resp.status_code == 429:
                    logger.warning("Hunter Finder API rate limit exceeded")

        except httpx.HTTPError as e:
            logger.warning(f"Hunter email finder failed: {e}")

        return None
