"""邮件追踪与退订 API — Phase 6 Email Marketing"""

import hmac
import logging
import uuid as _uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.send_log import SendLog
from app.models.unsubscribe import Unsubscribe
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["邮件追踪"])

# 1x1 透明 PNG
_TRACKING_PIXEL = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

# 追踪像素处理标记缓存（防重复计数）
_TRACKING_SEEN: set = set()


@router.get("/tracking/{tracking_id}.png")
async def tracking_pixel(
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
):
    """邮件打开追踪像素 — 同一 tracking_id 只记录一次打开"""
    # 快速路径：已处理过的直接返回（防滥用）
    if tracking_id in _TRACKING_SEEN:
        return Response(content=_TRACKING_PIXEL, media_type="image/png")

    try:
        uid = _uuid.UUID(tracking_id)
    except (ValueError, AttributeError):
        return Response(content=_TRACKING_PIXEL, media_type="image/png")

    result = await db.execute(
        select(SendLog).where(SendLog.tracking_id == uid)
    )
    log = result.scalar_one_or_none()

    if log and log.status in ("sent", "delivered") and not log.opened_at:
        log.status = "delivered"
        log.opened_at = datetime.now(timezone.utc)
        # 更新对应 campaign 的计数
        from app.models.email_campaign import EmailCampaign
        camp_result = await db.execute(
            select(EmailCampaign).where(EmailCampaign.id == log.campaign_id)
        )
        campaign = camp_result.scalar_one_or_none()
        if campaign:
            campaign.opened_count = (campaign.opened_count or 0) + 1
        await db.commit()

    _TRACKING_SEEN.add(tracking_id)
    return Response(content=_TRACKING_PIXEL, media_type="image/png")


UNSUBSCRIBE_HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>退订确认</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 480px; margin: 80px auto; padding: 24px; text-align: center; }
  h2 { color: #1e293b; } p { color: #64748b; line-height: 1.6; }
  .btn { display: inline-block; margin-top: 16px; padding: 10px 24px;
         background: #ef4444; color: #fff; border: none; border-radius: 8px;
         font-size: 15px; cursor: pointer; text-decoration: none; }
  .btn:hover { background: #dc2626; }
  .success { color: #16a34a; }
</style>
</head>
<body>
{body}
</body>
</html>"""


def _parse_tenant_id_uuid(val: Optional[str]):
    """将 tenant_id 字符串转为 UUID，失败时返回 None"""
    if not val:
        return None
    try:
        return _uuid.UUID(val)
    except (ValueError, AttributeError):
        return None


@router.get("/unsubscribe")
async def unsubscribe_page(
    email: str = Query(...),
    token: str = Query(...),
    tenant_id: Optional[str] = Query(None),
):
    """退订确认页面（GET）"""
    tenant_param = "&tenant_id=" + tenant_id if tenant_id else ""
    return HTMLResponse(
        UNSUBSCRIBE_HTML.format(
            body=(
                "<h2>退订确认</h2>"
                "<p>邮箱：<strong>" + email + "</strong></p>"
                "<p>点击下方按钮确认退订，之后将不再收到来自我们的营销邮件。</p>"
                '<form method="post" action="/api/v1/email/unsubscribe?email='
                + email + "&token=" + token + tenant_param + '">'
                '<button type="submit" class="btn">确认退订</button>'
                "</form>"
            )
        )
    )


@router.post("/unsubscribe")
async def unsubscribe_confirm(
    email: str = Query(...),
    token: str = Query(...),
    tenant_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """退订确认（POST）— 按租户隔离，一个邮箱在一个租户内只退订一次"""
    tenant_uuid = _parse_tenant_id_uuid(tenant_id)

    # 验证 token（tenant-specific）
    payload = email + ":" + tenant_id if tenant_id else email
    expected_token = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        "sha256",
    ).hexdigest()
    if not hmac.compare_digest(token, expected_token):
        return HTMLResponse(
            UNSUBSCRIBE_HTML.format(
                body='<h2>退订失败</h2><p>无效的退订链接，请联系发件人。</p>'
            )
        )

    # 按租户+邮箱查找已有退订记录
    if tenant_uuid:
        result = await db.execute(
            select(Unsubscribe).where(
                Unsubscribe.email == email,
                Unsubscribe.tenant_id == tenant_uuid,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return HTMLResponse(
                UNSUBSCRIBE_HTML.format(
                    body='<h2 class="success">✓ 您已退订</h2>'
                         '<p>该邮箱在此租户下已在退订列表中，不会收到后续营销邮件。</p>'
                )
            )

        # 创建租户级退订记录
        unsub = Unsubscribe(email=email, tenant_id=tenant_uuid)
        db.add(unsub)
        await db.commit()
        return HTMLResponse(
            UNSUBSCRIBE_HTML.format(
                body='<h2 class="success">✓ 退订成功</h2>'
                     '<p>您已成功退订，之后将不再收到来自我们的营销邮件。</p>'
            )
        )

    # 无 tenant_id 的旧链接兼容：从发送记录推断租户
    log_result = await db.execute(
        select(SendLog).where(SendLog.recipient_email == email).limit(1)
    )
    send_log = log_result.scalar_one_or_none()

    if send_log:
        from app.models.email_campaign import EmailCampaign
        camp_result = await db.execute(
            select(EmailCampaign).where(EmailCampaign.id == send_log.campaign_id)
        )
        campaign = camp_result.scalar_one_or_none()
        if campaign:
            # 检查该租户下是否已有退订
            existing_check = await db.execute(
                select(Unsubscribe).where(
                    Unsubscribe.email == email,
                    Unsubscribe.tenant_id == campaign.tenant_id,
                )
            )
            if existing_check.scalar_one_or_none():
                return HTMLResponse(
                    UNSUBSCRIBE_HTML.format(
                        body='<h2 class="success">✓ 您已退订</h2>'
                             '<p>该邮箱在此租户下已在退订列表中。</p>'
                    )
                )
            unsub = Unsubscribe(email=email, tenant_id=campaign.tenant_id)
            db.add(unsub)
            await db.commit()
            return HTMLResponse(
                UNSUBSCRIBE_HTML.format(
                    body='<h2 class="success">✓ 退订成功</h2>'
                         '<p>您已成功退订，之后将不再收到来自我们的营销邮件。</p>'
                )
            )

    return HTMLResponse(
        UNSUBSCRIBE_HTML.format(
            body='<h2>退订失败</h2><p>未找到对应的发送记录，请联系发件人手动处理。</p>'
        )
    )


# ── IMAP 回复检查（手动触发） ──

@router.post("/check-replies")
async def manual_check_replies():
    """手动触发一次全租户 IMAP 回复检查"""
    try:
        from app.services.email.reply_tracker import check_replies_for_all_tenants
        results = await check_replies_for_all_tenants()
        return {
            "status": "ok",
            "tenants_checked": len(results),
            "new_replies": sum(results.values()),
            "details": results,
        }
    except Exception as e:
        logger.exception("Manual reply check failed")
        raise HTTPException(status_code=500, detail=str(e))
