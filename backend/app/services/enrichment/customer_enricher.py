"""客户信息补全服务 — Phase 5"""

import logging
from datetime import datetime, timezone
from typing import AsyncIterator, Dict, Any, Optional, List

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.contact import Contact
from app.services.ai_service import AIService, AIServiceError, get_ai_service
from app.services.ai.customer_extractor import CustomerExtractor

logger = logging.getLogger(__name__)

_PAGE_FETCH_TIMEOUT = 10.0
_MAX_CONTENT_LENGTH = 10000

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class CustomerEnricher:
    """客户信息补全编排器 — 从客户网站抓取并 LLM 提取联系人"""

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or get_ai_service()

    async def enrich(
        self,
        customer_id: str,
        tenant_id: str,
        db: AsyncSession,
    ) -> AsyncIterator[Dict[str, Any]]:
        """流式补全单个客户，yield SSE 事件"""

        # 1. 加载客户
        result = await db.execute(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.tenant_id == tenant_id,
            )
        )
        customer = result.scalar_one_or_none()
        if not customer:
            yield {"type": "error", "message": "客户不存在"}
            return

        website = customer.website
        if not website:
            yield {"type": "error", "message": "该客户没有网站 URL，无法补全"}
            return

        # 标记开始
        customer.enrichment_status = "in_progress"
        await db.commit()

        try:
            # 2. 抓取页面
            yield {"type": "progress", "message": f"正在抓取 {website}..."}

            page_content = ""
            url = website if "://" in website else f"https://{website}"

            try:
                async with httpx.AsyncClient(
                    timeout=_PAGE_FETCH_TIMEOUT,
                    headers={"User-Agent": USER_AGENT},
                    follow_redirects=True,
                ) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "lxml")
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()
                    page_content = soup.get_text(separator="\n", strip=True)[
                        :_MAX_CONTENT_LENGTH
                    ]
            except httpx.HTTPError as e:
                logger.warning(f"Page fetch failed for {website}: {e}")
                yield {"type": "progress", "message": f"网站抓取失败: {e}，使用已有信息尝试提取..."}
            except Exception as e:
                logger.error(f"Unexpected error fetching {website}: {e}")
                yield {"type": "progress", "message": f"网站处理异常: {e}"}

            # 3. LLM 提取
            yield {"type": "progress", "message": "AI 正在分析网页内容..."}

            extractor = CustomerExtractor(self.ai_service)
            async for event in extractor.extract(page_content, url):
                if event["type"] == "text":
                    yield event

            output = extractor.get_output()

            if not output or output.get("parse_error"):
                customer.enrichment_status = "failed"
                await db.commit()
                yield {"type": "error", "message": "AI 提取失败，请重试"}
                return

            # 4. 合并结果 — 仅填充空字段
            fill_map = {
                "industry": output.get("industry"),
                "country": output.get("country"),
                "city": output.get("city"),
                "company_size": output.get("company_size"),
                "description": output.get("description"),
            }
            filled_fields: List[str] = []
            for field, value in fill_map.items():
                if value and not getattr(customer, field, None):
                    setattr(customer, field, value)
                    filled_fields.append(field)

            if output.get("description") and not customer.ai_summary:
                customer.ai_summary = output["description"]

            # 5. 追加联系人（按 name 去重）
            existing_names = await self._existing_contact_names(db, customer.id)
            new_contacts = output.get("contacts") or []
            added_count = 0

            for c_data in new_contacts:
                c_name = c_data.get("name", "").strip()
                if not c_name or c_name.lower() in existing_names:
                    continue
                contact = Contact(
                    customer_id=customer.id,
                    tenant_id=tenant_id,
                    name=c_name,
                    title=c_data.get("title"),
                    email=c_data.get("email"),
                    phone=c_data.get("phone"),
                    linkedin_url=c_data.get("linkedin_url"),
                )
                db.add(contact)
                existing_names.add(c_name.lower())
                added_count += 1

            # 6. 更新补全状态
            customer.enrichment_status = "completed"
            customer.last_enriched_at = datetime.now(timezone.utc)
            customer.enrichment_count = (customer.enrichment_count or 0) + 1

            # 合并 source_data
            if customer.source_data:
                merged = dict(customer.source_data)
                merged["enrichment"] = output
                customer.source_data = merged
            else:
                customer.source_data = {"enrichment": output}

            await db.commit()

            yield {
                "type": "complete",
                "customer_id": str(customer.id),
                "filled_fields": filled_fields,
                "contacts_added": added_count,
            }

        except AIServiceError as e:
            logger.error(f"AI enrichment error: {e}")
            customer.enrichment_status = "failed"
            await db.commit()
            yield {"type": "error", "message": f"AI 服务异常: {e}"}
        except Exception as e:
            logger.error(f"Enrichment error: {e}")
            customer.enrichment_status = "failed"
            await db.commit()
            yield {"type": "error", "message": f"补全失败: {e}"}

    async def _existing_contact_names(
        self, db: AsyncSession, customer_id: str
    ) -> set:
        """获取已有联系人姓名（用于去重）"""
        result = await db.execute(
            select(Contact.name).where(Contact.customer_id == customer_id)
        )
        return {r[0].lower().strip() for r in result.all() if r[0]}
