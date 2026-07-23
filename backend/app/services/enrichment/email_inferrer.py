"""邮箱模式推断服务 — 从人名+域名推断企业邮箱地址"""

import logging
import re
from typing import List, Dict, Any, Optional, Set

logger = logging.getLogger(__name__)

# 常见企业邮箱命名模式
_EMAIL_PATTERNS = [
    # (pattern_fn, description)
    ("first_dot_last", lambda f, l, d: f"{f}.{l}@{d}"),
    ("first_last", lambda f, l, d: f"{f}{l}@{d}"),
    ("first_last_no_dot", lambda f, l, d: f"{f}_{l}@{d}"),
    ("first_initial_last", lambda f, l, d: f"{f[0]}{l}@{d}"),
    ("first", lambda f, l, d: f"{f}@{d}"),
    ("last", lambda f, l, d: f"{l}@{d}"),
    ("first_dot_last_initial", lambda f, l, d: f"{f}.{l[0]}@{d}"),
    ("first_initial_dot_last", lambda f, l, d: f"{f[0]}.{l}@{d}"),
]

# 用于从页面邮箱反推模式
_EMAIL_DOMAIN_RE = re.compile(r'[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')


class EmailInferrer:
    """从已知人名和域名推断最可能的邮箱地址"""

    def __init__(self):
        self._known_emails: Set[str] = set()

    def infer_emails(
        self,
        names: List[str],
        domain: str,
        known_emails_from_page: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """从人名列表和域名推断邮箱地址

        Args:
            names: 人名列表（如 ["John Smith", "Jane Doe"]）
            domain: 公司域名（如 "example.com"）
            known_emails_from_page: 页面中已知的邮箱（用于推断命名模式）

        Returns:
            推断的邮箱列表，每个包含 email, pattern, confidence
        """
        if not names or not domain:
            return []

        domain = domain.lower().strip()
        # 提取纯域名
        if "@" in domain:
            domain = domain.split("@")[1]
        if "://" in domain:
            from urllib.parse import urlparse
            parsed = urlparse(domain)
            domain = parsed.netloc or domain

        # 去掉 www. 前缀
        if domain.startswith("www."):
            domain = domain[4:]

        results = []

        # 确定该公司的邮箱命名模式
        preferred_pattern = self._detect_company_pattern(
            names, domain, known_emails_from_page or []
        )

        for full_name in names:
            full_name = full_name.strip()
            if not full_name or " " not in full_name:
                continue

            parts = full_name.split()
            first = parts[0].lower().replace("'", "").replace("-", "")
            last = parts[-1].lower().replace("'", "").replace("-", "")

            if len(first) < 2 or len(last) < 2:
                continue

            # 如果已推断出该公司模式，优先使用
            if preferred_pattern:
                fn = dict(_EMAIL_PATTERNS).get(preferred_pattern)
                if fn:
                    email = fn(first, last, domain)
                    if email not in self._known_emails:
                        results.append({
                            "email": email,
                            "pattern": preferred_pattern,
                            "confidence": "medium",
                        })
                        self._known_emails.add(email)
                        continue

            # 否则生成所有可能的邮箱
            for pattern_name, fn in _EMAIL_PATTERNS:
                email = fn(first, last, domain)
                if email not in self._known_emails:
                    results.append({
                        "email": email,
                        "pattern": pattern_name,
                        "confidence": "low",
                    })

        logger.info(
            f"Inferred {len(results)} emails for {len(names)} names "
            f"at {domain} (preferred pattern: {preferred_pattern or 'unknown'})"
        )

        return results

    def _detect_company_pattern(
        self,
        names: List[str],
        domain: str,
        known_emails: List[str],
    ) -> Optional[str]:
        """从已知邮箱推断该公司的命名规则"""
        if not known_emails:
            return None

        # 过滤出属于该域名的邮箱
        domain_emails = [
            e.lower() for e in known_emails
            if domain in e.lower() and "@" in e
        ]
        if not domain_emails:
            return None

        # 对每个人名测试每种模式，找出匹配的模式
        pattern_votes: Dict[str, int] = {}
        for full_name in names:
            parts = full_name.strip().split()
            if len(parts) < 2:
                continue
            first = parts[0].lower().replace("'", "").replace("-", "")
            last = parts[-1].lower().replace("'", "").replace("-", "")
            if len(first) < 2 or len(last) < 2:
                continue

            for pattern_name, fn in _EMAIL_PATTERNS:
                expected = fn(first, last, domain).lower()
                if expected in domain_emails:
                    pattern_votes[pattern_name] = pattern_votes.get(pattern_name, 0) + 1

        if pattern_votes:
            best = max(pattern_votes, key=pattern_votes.get)
            logger.debug(f"Detected email pattern for {domain}: {best} ({pattern_votes[best]} votes)")
            return best

        return None
