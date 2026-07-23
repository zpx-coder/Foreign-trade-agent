"""联系人爬虫 — 多页面抓取 + 正则提取邮箱/电话 + LLM 结构化"""

import logging
import re
import asyncio
import json as _json
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.services.ai_service import AIServiceError, get_ai_service

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# 要抓取的页面路径（按优先级）
_CONTACT_PATHS = [
    "",                # 首页
    "contact",         # /contact
    "contact-us",      # /contact-us
    "about",           # /about
    "about-us",        # /about-us
    "team",            # /team
    "our-team",        # /our-team
    "people",          # /people
    "management",      # /management
    "leadership",      # /leadership
    "company",         # /company
    "imprint",         # /imprint (德国公司常有)
    "impressum",       # /impressum
]

_PAGE_TIMEOUT = 12.0
_MAX_PAGES = 8  # 最多抓取 8 个页面
_MAX_CONTENT_LENGTH = 8000

# 邮箱正则（常见 B2B 模式）
_EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE,
)

# 电话正则（国际格式）
_PHONE_RE = re.compile(
    r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{3,6}',
)

# 联系人提取 System Prompt（轻量，聚焦于找人）
EXTRACT_CONTACTS_PROMPT = """你是一位商业数据提取专家。从网页内容中提取联系人信息。

## 规则
1. 仅提取网页中明确出现的人员信息，不要编造
2. 只提取看起来像真实员工的信息（有姓名+职位/邮箱/电话）
3. 如果没有有效的联系人信息，返回空数组 []
4. 邮箱地址格式必须合法

## 输出格式（仅 JSON 数组）
[
  {
    "name": "姓名",
    "title": "职位",
    "email": "邮箱",
    "phone": "电话",
    "linkedin_url": null
  }
]
"""


class ContactScraper:
    """多页面联系人抓取器"""

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    async def scrape(self, website: str) -> List[Dict[str, Any]]:
        """从公司网站抓取联系人信息

        Args:
            website: 公司网站 URL（如 https://example.com 或 example.com）

        Returns:
            联系人列表 [{"name": ..., "title": ..., "email": ..., "phone": ...}, ...]
        """
        if not website:
            return []

        base_url = website if "://" in website else f"https://{website}"
        parsed = urlparse(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"

        all_emails: set = set()
        all_phones: set = set()
        all_text = ""

        async with httpx.AsyncClient(
            timeout=_PAGE_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as client:
            pages_fetched = 0

            for path in _CONTACT_PATHS:
                if pages_fetched >= _MAX_PAGES:
                    break

                page_url = urljoin(origin, path) if path else base_url

                try:
                    resp = await client.get(page_url)
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "lxml")

                    # 提取邮箱（从页面文本）
                    text = resp.text
                    emails = set(_EMAIL_RE.findall(text))
                    # 过滤掉图片/资源路径中的假邮箱
                    valid_emails = {
                        e for e in emails
                        if not e.endswith((".png", ".jpg", ".gif", ".svg", ".css", ".js"))
                        and len(e.split("@")[0]) >= 2
                    }
                    all_emails.update(valid_emails)

                    # 新增：提取 mailto: 链接中的邮箱（更可靠）
                    for mailto_link in soup.select("a[href^='mailto:']"):
                        href = mailto_link.get("href", "")
                        if href:
                            mailto_email = href.replace("mailto:", "").split("?")[0].strip()
                            if "@" in mailto_email and len(mailto_email.split("@")[0]) >= 2:
                                all_emails.add(mailto_email.lower())

                    # 新增：提取 Schema.org Person JSON-LD 结构化数据
                    for script_tag in soup.select('script[type="application/ld+json"]'):
                        try:
                            ld_data = _json.loads(script_tag.string or "{}")
                            if isinstance(ld_data, dict):
                                ld_data = [ld_data]
                            if isinstance(ld_data, list):
                                for item in ld_data:
                                    if item.get("@type") == "Person":
                                        person_email = item.get("email")
                                        if person_email and "@" in str(person_email):
                                            all_emails.add(str(person_email).lower())
                                        person_name = item.get("name")
                                        person_title = item.get("jobTitle")
                                        if person_name:
                                            all_text += f"\n--- Schema.org Person ---\n{person_name}"
                                            if person_title:
                                                all_text += f" — {person_title}"
                                    elif item.get("@type") == "Organization":
                                        org_emails = item.get("email")
                                        contact_point = item.get("contactPoint", {})
                                        if isinstance(contact_point, dict):
                                            cp_email = contact_point.get("email")
                                            if cp_email:
                                                all_emails.add(str(cp_email).lower())
                                            cp_name = contact_point.get("name")
                                            if cp_name:
                                                all_text += f"\n--- Schema.org ContactPoint ---\n{cp_name}"
                        except (_json.JSONDecodeError, TypeError, AttributeError):
                            pass

                    # 新增：提取 <meta> 标签中的邮箱和联系人信息
                    for meta in soup.select('meta[name="author"], meta[name="email"], meta[property="og:email"], meta[name="contact"]'):
                        content = meta.get("content", "")
                        if "@" in content:
                            meta_emails = _EMAIL_RE.findall(content)
                            all_emails.update(
                                e.lower() for e in meta_emails
                                if len(e.split("@")[0]) >= 2
                            )

                    # 提取电话
                    phones = set(_PHONE_RE.findall(text))
                    all_phones.update(phones)

                    # 提取文本内容
                    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                        tag.decompose()
                    page_text = soup.get_text(separator="\n", strip=True)
                    all_text += f"\n--- {page_url} ---\n{page_text[:_MAX_CONTENT_LENGTH]}"

                    pages_fetched += 1
                    logger.debug(f"Scraped {page_url}: {len(valid_emails)} emails, {len(phones)} phones")

                except httpx.HTTPError as e:
                    logger.debug(f"Failed to fetch {page_url}: {e}")
                except Exception as e:
                    logger.warning(f"Error scraping {page_url}: {e}")

        if not all_emails and not all_phones:
            logger.info(f"No emails/phones found on {website}")
            return []

        # 用 LLM 将邮箱/电话与人名/职位关联
        contacts = await self._extract_contacts(all_text, list(all_emails), list(all_phones))

        return contacts

    async def _extract_contacts(
        self,
        page_text: str,
        emails: List[str],
        phones: List[str],
    ) -> List[Dict[str, Any]]:
        """使用 LLM 从页面文本中提取结构化联系人"""
        if not page_text.strip():
            return self._fallback_contacts(emails, phones)

        # 截断文本
        truncated = page_text[:_MAX_CONTENT_LENGTH * 2] if len(page_text) > _MAX_CONTENT_LENGTH * 2 else page_text

        email_list = ", ".join(emails[:10])
        phone_list = ", ".join(phones[:10])

        user_prompt = f"""## 网页文本内容
{truncated}

## 发现的邮箱地址
{email_list or "无"}

## 发现的电话
{phone_list or "无"}

请从上述信息中提取联系人与邮箱/电话的对应关系。将邮箱/电话关联到正确的人名和职位。"""

        messages = [
            {"role": "system", "content": EXTRACT_CONTACTS_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        try:
            ai_service = get_ai_service()
            response = await ai_service.chat_completion(
                messages=messages,
                temperature=0.2,
                max_tokens=2048,
                timeout=30.0,
            )
            content = response.choices[0].message.content
            contacts = self._parse_response(content)

            if contacts:
                logger.info(f"LLM extracted {len(contacts)} contacts")
                return contacts
        except AIServiceError as e:
            logger.warning(f"AI contact extraction failed: {e}")
        except Exception as e:
            logger.warning(f"Contact extraction error: {e}")

        # LLM 失败时，用纯正则结果兜底
        return self._fallback_contacts(emails, phones)

    def _fallback_contacts(self, emails: List[str], phones: List[str]) -> List[Dict[str, Any]]:
        """LLM 提取失败时的兜底：返回无姓名的邮箱/电话"""
        contacts = []
        for email in emails[:5]:
            # 用邮箱前缀推测姓名
            name_part = email.split("@")[0]
            # 尝试将 "john.smith" 转为 "John Smith"
            name = name_part.replace(".", " ").replace("_", " ").replace("-", " ").title()
            if len(name) < 2:
                name = name_part
            contacts.append({
                "name": name,
                "title": None,
                "email": email,
                "phone": None,
                "linkedin_url": None,
            })
        # 纯电话号码无法关联人名
        for phone in phones[:3]:
            if not contacts:
                contacts.append({
                    "name": None,
                    "title": None,
                    "email": None,
                    "phone": phone,
                    "linkedin_url": None,
                })
        return contacts

    def _parse_response(self, content: str) -> List[Dict[str, Any]]:
        """解析 LLM 返回的 JSON"""
        import json
        if not content:
            return []
        content = content.strip()
        # 策略 1: ```json ... ```
        if "```json" in content:
            block = content.split("```json")[1].split("```")[0].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                pass
        elif "```" in content:
            block = content.split("```")[1].split("```")[0].strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                pass
        # 策略 2: 直接 JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        # 策略 3: [...] 提取
        try:
            start = content.index("[")
            end = content.rindex("]") + 1
            return json.loads(content[start:end])
        except (ValueError, json.JSONDecodeError):
            pass
        return []
