"""Dashboard 统计数据 API"""

from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.icp import Icp
from app.models.product import Product
from app.models.enterprise import EnterpriseProfile
from app.models.customer import Customer
from app.models.send_log import SendLog
from app.models.email_campaign import EmailCampaign

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取工作台统计数据"""
    tenant_id = current_user.tenant_id

    # ── 客户画像统计 ──
    icp_base = select(func.count(Icp.id)).where(Icp.tenant_id == tenant_id)
    total_icps = (await db.execute(icp_base)).scalar() or 0
    completed_icps = (
        await db.execute(icp_base.where(Icp.status == "completed"))
    ).scalar() or 0
    generating_icps = (
        await db.execute(icp_base.where(Icp.status == "generating"))
    ).scalar() or 0
    draft_icps = (
        await db.execute(icp_base.where(Icp.status == "draft"))
    ).scalar() or 0
    failed_icps = (
        await db.execute(icp_base.where(Icp.status == "failed"))
    ).scalar() or 0

    # ── 产品统计 ──
    total_products = (
        await db.execute(
            select(func.count(Product.id)).where(Product.tenant_id == tenant_id)
        )
    ).scalar() or 0

    # ── 企业资料 ──
    has_enterprise = (
        await db.execute(
            select(func.count(EnterpriseProfile.id)).where(
                EnterpriseProfile.tenant_id == tenant_id
            )
        )
    ).scalar() or 0

    # ── 客户统计（Phase 4） ──
    customer_base = select(func.count(Customer.id)).where(
        Customer.tenant_id == tenant_id
    )
    total_customers = (await db.execute(customer_base)).scalar() or 0
    customers_reached = (
        await db.execute(customer_base.where(Customer.status != "new"))
    ).scalar() or 0
    reach_rate = (customers_reached / total_customers) if total_customers > 0 else 0.0

    # 客户状态分布
    status_rows = (
        await db.execute(
            select(Customer.status, func.count(Customer.id))
            .where(Customer.tenant_id == tenant_id)
            .group_by(Customer.status)
        )
    ).all()
    customer_status_counts: dict = {row[0]: row[1] for row in status_rows}

    # 客户来源分布
    source_rows = (
        await db.execute(
            select(Customer.source, func.count(Customer.id))
            .where(Customer.tenant_id == tenant_id)
            .group_by(Customer.source)
        )
    ).all()
    customer_sources: List[dict] = [
        {"name": s, "value": c} for s, c in source_rows
    ]

    # ── 邮件统计（Phase 6） ──
    sendlog_base = select(SendLog).join(
        EmailCampaign, SendLog.campaign_id == EmailCampaign.id
    ).where(EmailCampaign.tenant_id == tenant_id)

    total_emails_sent = (await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == tenant_id,
            SendLog.status.in_(["sent", "delivered"]),
        )
    )).scalar() or 0

    total_emails_opened = (await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == tenant_id,
            SendLog.opened_at.isnot(None),
        )
    )).scalar() or 0

    open_rate = round(total_emails_opened / total_emails_sent, 4) if total_emails_sent > 0 else 0.0

    # 近 6 个月月度统计
    monthly_email_stats: List[dict] = []
    try:
        from sqlalchemy import extract, text
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        monthly_q = (
            select(
                func.date_trunc("month", SendLog.created_at).label("month"),
                func.count(SendLog.id).label("sent"),
                func.count(func.nullif(SendLog.opened_at, None)).label("opened"),
            )
            .select_from(SendLog)
            .join(EmailCampaign, SendLog.campaign_id == EmailCampaign.id)
            .where(
                EmailCampaign.tenant_id == tenant_id,
                SendLog.created_at >= func.now() - text("interval '6 months'"),
            )
            .group_by(text("1"))
            .order_by(text("1 DESC"))
        )
        monthly_rows = (await db.execute(monthly_q)).all()
        monthly_email_stats = [
            {"month": str(r[0])[:7], "sent": r[1], "opened": r[2]}
            for r in monthly_rows
        ]
    except Exception:
        monthly_email_stats = []

    # 已回复数
    total_emails_replied = (await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == tenant_id,
            SendLog.status == "replied",
        )
    )).scalar() or 0

    return {
        # ICP
        "total_icps": total_icps,
        "completed_icps": completed_icps,
        "generating_icps": generating_icps,
        "draft_icps": draft_icps,
        "failed_icps": failed_icps,
        # 产品
        "total_products": total_products,
        # 企业
        "has_enterprise_profile": has_enterprise > 0,
        # 客户 (Phase 4)
        "total_customers": total_customers,
        "customers_reached": customers_reached,
        "reach_rate": round(reach_rate, 4),
        "customer_sources": customer_sources,
        "customer_status_counts": customer_status_counts,
        # 邮件 (Phase 6)
        "total_emails_sent": total_emails_sent,
        "total_emails_opened": total_emails_opened,
        "total_emails_replied": total_emails_replied,
        "open_rate": open_rate,
        "reply_rate": total_emails_replied / total_emails_sent if total_emails_sent > 0 else 0.0,
        "monthly_email_stats": monthly_email_stats,
    }
