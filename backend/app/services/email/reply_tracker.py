"""IMAP 轮询回复追踪服务

通过 IMAP 连接收件箱，搜索对已发送邮件的回复（基于 Message-ID / In-Reply-To 匹配）。
使用 Python 标准库 imaplib + email，零外部依赖。
"""

import asyncio
import email
import imaplib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from app.core.security import decrypt_smtp_password
from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.send_log import SendLog
from app.models.email_campaign import EmailCampaign
from sqlalchemy import select, update

logger = logging.getLogger(__name__)

# 常见邮箱 SMTP → IMAP host 映射
_SMTP_TO_IMAP_MAP = {
    "smtp.gmail.com": ("imap.gmail.com", 993),
    "smtp.office365.com": ("outlook.office365.com", 993),
    "smtp-mail.outlook.com": ("imap-mail.outlook.com", 993),
    "smtp.qq.com": ("imap.qq.com", 993),
    "smtp.163.com": ("imap.163.com", 993),
    "smtp.126.com": ("imap.126.com", 993),
    "smtp.zoho.com": ("imap.zoho.com", 993),
    "smtp.yandex.com": ("imap.yandex.com", 993),
    "smtp.qiye.aliyun.com": ("imap.qiye.aliyun.com", 993),  # 阿里云企业邮箱
    "smtp.mxhichina.com": ("imap.mxhichina.com", 993),  # 阿里云企业邮箱（万网）
    "smtp.mailgun.org": (None, 0),  # Mailgun 不支持 IMAP
    "smtp.sendgrid.net": (None, 0),  # SendGrid 不支持 IMAP
}


def _get_imap_config(tenant: Tenant) -> Optional[dict]:
    """获取租户的 IMAP 配置。

    优先级：
    1. Tenant.settings["imap_config"] 显式配置
    2. 从 Tenant.settings["smtp_config"] 自动推导
    """
    settings = tenant.settings or {}

    # 显式配置的 IMAP
    imap_cfg = settings.get("imap_config")
    if imap_cfg and imap_cfg.get("host") and imap_cfg.get("password"):
        return imap_cfg

    # 尝试从 SMTP 推导
    smtp_cfg = settings.get("smtp_config") or {}
    smtp_host = smtp_cfg.get("host", "")
    if not smtp_host:
        return None

    derived = _SMTP_TO_IMAP_MAP.get(smtp_host)
    if not derived or not derived[0]:
        return None

    imap_host, imap_port = derived
    return {
        "host": imap_host,
        "port": imap_port,
        "username": smtp_cfg.get("username", ""),
        "password": smtp_cfg.get("password", ""),  # 已加密
    }


async def _get_recent_message_ids(
    tenant_id: str, since_days: int = 30
) -> Set[str]:
    """获取租户最近 N 天内发送的 Message-ID 集合"""
    from datetime import timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    ids: Set[str] = set()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SendLog.message_id).where(
                SendLog.message_id.isnot(None),
                SendLog.status.in_(["sent", "delivered"]),
                SendLog.created_at >= cutoff,
            )
        )
        for row in result.all():
            mid = row[0]
            if mid:
                # IMAP 搜索中的 Message-ID 通常不带 <>
                ids.add(mid.strip("<>"))
    return ids


async def _update_replied(
    send_log_id: str,
    campaign_id: Optional[str],
    replied_at: datetime,
) -> bool:
    """更新 SendLog 为已回复状态，并递增 campaign 的 replied_count"""
    async with AsyncSessionLocal() as session:
        log = await session.get(SendLog, send_log_id)
        if not log or log.status == "replied":
            return False

        log.status = "replied"
        log.replied_at = replied_at

        # 更新对应 campaign 的回复计数
        if campaign_id or log.campaign_id:
            cid = campaign_id or log.campaign_id
            camp = await session.get(EmailCampaign, cid)
            if camp:
                camp.replied_count = (camp.replied_count or 0) + 1

        await session.commit()
        logger.info(
            f"Reply detected: SendLog {send_log_id} "
            f"(recipient: {log.recipient_email})"
        )
        return True


async def check_replies_for_tenant(
    tenant_id: str, imap_config: dict
) -> int:
    """对单个租户执行 IMAP 回复检查。

    连接到收件箱，搜索对已发邮件（基于 Message-ID）的回复，
    匹配后更新 SendLog 状态。

    Returns:
        新检测到的回复数量
    """
    if not imap_config.get("host"):
        return 0

    host = imap_config["host"]
    port = imap_config.get("port", 993)
    username = imap_config.get("username", "")
    password_encrypted = imap_config.get("password", "")

    if not username or not password_encrypted:
        logger.debug(f"Tenant {tenant_id}: IMAP credentials incomplete, skip")
        return 0

    # 解密密码
    try:
        password = decrypt_smtp_password(password_encrypted)
    except Exception:
        logger.warning(
            f"Tenant {tenant_id}: failed to decrypt IMAP password"
        )
        return 0

    # 获取最近发送的 Message-ID 列表
    recent_ids = await _get_recent_message_ids(tenant_id)
    if not recent_ids:
        logger.debug(f"Tenant {tenant_id}: no recent message_ids, skip IMAP check")
        return 0

    # ── IMAP 连接与搜索 ──
    found_count = 0

    def _imap_worker() -> List[dict]:
        """在 executor 中运行的同步 IMAP 操作"""
        results = []
        conn = None
        try:
            conn = imaplib.IMAP4_SSL(host, port)
            # Python 3.8 不支持 timeout 参数；通过 socket 设置
            try:
                conn.socket().settimeout(30)
            except Exception:
                pass
            conn.login(username, password)
            conn.select("INBOX", readonly=True)

            # 搜索条件：UNSEEN 或最近 7 天的邮件
            # IMAP SEARCH 语法限制，先搜 UNSEEN，不够再扩大范围
            status, data = conn.search(None, "(UNSEEN)")
            if status != "OK":
                conn.logout()
                return results

            msg_ids = data[0].split() if data[0] else []
            if not msg_ids:
                conn.logout()
                return results

            # 取最近 200 封未读邮件（避免一次取太多）
            msg_ids = msg_ids[-200:]
            batch = b",".join(msg_ids)

            status, data = conn.fetch(
                batch, "(BODY.PEEK[HEADER.FIELDS (IN-REPLY-TO REFERENCES SUBJECT FROM DATE)])"
            )
            if status != "OK":
                conn.logout()
                return results

            # 解析邮件头
            current_item = None
            for item in data:
                if isinstance(item, tuple):
                    header_bytes = item[1]
                    if not header_bytes:
                        continue
                    try:
                        msg = email.message_from_bytes(
                            header_bytes,
                            _class=email.message.EmailMessage,
                        )
                    except Exception:
                        continue

                    in_reply_to = (
                        msg.get("In-Reply-To", "")
                        .strip()
                        .strip("<>")
                    )
                    references = (
                        msg.get("References", "")
                        .strip()
                        .strip("<>")
                    )
                    from_addr = msg.get("From", "")
                    date_str = msg.get("Date", "")

                    # 合并所有可匹配的 ID
                    candidate_ids: Set[str] = set()
                    if in_reply_to:
                        candidate_ids.add(in_reply_to)
                    # References 可能包含多个 Message-ID（空格分隔）
                    if references:
                        for ref in references.split():
                            ref_clean = ref.strip().strip("<>")
                            if ref_clean:
                                candidate_ids.add(ref_clean)

                    if candidate_ids:
                        results.append({
                            "candidate_ids": candidate_ids,
                            "from_addr": from_addr,
                            "date_str": date_str,
                        })

            conn.logout()
        except imaplib.IMAP4.error as e:
            logger.warning(
                f"IMAP error for tenant {tenant_id} ({host}): {e}"
            )
        except Exception as e:
            logger.error(
                f"IMAP unexpected error for tenant {tenant_id}: {e}"
            )
        finally:
            try:
                if conn:
                    conn.logout()
            except Exception:
                pass

        return results

    # 在线程池中运行同步 IMAP
    try:
        reply_candidates = await asyncio.get_event_loop().run_in_executor(
            None, _imap_worker
        )
    except Exception as e:
        logger.error(f"IMAP worker failed for tenant {tenant_id}: {e}")
        return 0

    if not reply_candidates:
        return 0

    # ── 匹配 Message-ID → 更新 SendLog ──
    # 查询所有候选 SendLog 的 message_id（去重后匹配）
    all_candidate_ids = set()
    for rc in reply_candidates:
        all_candidate_ids |= rc["candidate_ids"]

    # 找交集：候选 ID ∩ 已发 Message-ID
    matched_raw_ids = all_candidate_ids & recent_ids
    if not matched_raw_ids:
        return 0

    # 查询匹配的 SendLog
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SendLog).where(
                SendLog.message_id.isnot(None),
            )
        )
        send_logs = result.scalars().all()

        # 构建 message_id → SendLog 映射
        log_by_msg_id: Dict[str, SendLog] = {}
        for sl in send_logs:
            if sl.message_id:
                mid_clean = sl.message_id.strip("<>")
                log_by_msg_id[mid_clean] = sl

    # 逐条更新
    for rc in reply_candidates:
        matched = rc["candidate_ids"] & matched_raw_ids
        if not matched:
            continue

        # 解析回复时间
        replied_at = datetime.now(timezone.utc)
        if rc.get("date_str"):
            try:
                from email.utils import parsedate_to_datetime
                replied_at = parsedate_to_datetime(rc["date_str"])
            except Exception:
                pass

        for mid in matched:
            sl = log_by_msg_id.get(mid)
            if sl and sl.status != "replied":
                updated = await _update_replied(
                    str(sl.id), str(sl.campaign_id), replied_at
                )
                if updated:
                    found_count += 1

    if found_count > 0:
        logger.info(
            f"Tenant {tenant_id}: detected {found_count} new replies "
            f"from {len(reply_candidates)} IMAP candidates"
        )

    return found_count


async def check_replies_for_all_tenants() -> Dict[str, int]:
    """遍历所有租户，检查回复。

    Returns:
        {tenant_id: new_reply_count}
    """
    results: Dict[str, int] = {}

    async with AsyncSessionLocal() as session:
        tenant_result = await session.execute(
            select(Tenant).where(Tenant.status == "active")
        )
        tenants = tenant_result.scalars().all()

    for tenant in tenants:
        try:
            imap_config = _get_imap_config(tenant)
            if not imap_config:
                continue

            count = await check_replies_for_tenant(
                str(tenant.id), imap_config
            )
            if count > 0:
                results[str(tenant.id)] = count
        except Exception as e:
            logger.error(
                f"check_replies failed for tenant {tenant.id}: {e}"
            )

    total = sum(results.values())
    if total > 0:
        logger.info(
            f"IMAP poll complete: {total} new replies "
            f"across {len(results)} tenants"
        )

    return results
