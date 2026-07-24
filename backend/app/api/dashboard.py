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
from app.models.contact import Contact
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
    # 触达 = 至少有一个联系人成功发送过邮件（非 pending/failed）
    customers_reached = (await db.execute(
        select(func.count(func.distinct(Contact.customer_id)))
        .select_from(SendLog)
        .join(Contact, SendLog.contact_id == Contact.id)
        .join(EmailCampaign, SendLog.campaign_id == EmailCampaign.id)
        .where(
            EmailCampaign.tenant_id == tenant_id,
            SendLog.status.in_(["sent", "delivered", "opened", "replied"]),
        )
    )).scalar() or 0
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

    # ── 客户画像维度统计（按 ICP 分组 + 状态分布） ──
    # 按 (icp_id, status) 分组计数
    icp_status_rows = (
        await db.execute(
            select(
                Customer.icp_id,
                Customer.status,
                func.count(Customer.id),
            )
            .where(Customer.tenant_id == tenant_id)
            .group_by(Customer.icp_id, Customer.status)
        )
    ).all()

    # 构建 ICP ID → {status: count} 映射
    icp_status_map: dict = {}
    for icp_id, status, cnt in icp_status_rows:
        key = str(icp_id) if icp_id else "__unassigned__"
        if key not in icp_status_map:
            icp_status_map[key] = {"total": 0, "statuses": {}}
        icp_status_map[key]["statuses"][status] = cnt
        icp_status_map[key]["total"] += cnt

    # 获取 ICP 名称映射
    icp_ids = [
        row[0] for row in icp_status_rows if row[0] is not None
    ]
    icp_name_map: dict = {}
    if icp_ids:
        icp_rows = (
            await db.execute(
                select(Icp.id, Icp.name).where(
                    Icp.id.in_(list(set(icp_ids))),
                    Icp.tenant_id == tenant_id,
                )
            )
        ).all()
        icp_name_map = {str(row[0]): row[1] for row in icp_rows}

    # 组装响应
    customer_icp_stats: List[dict] = []
    for key, data in icp_status_map.items():
        if key == "__unassigned__":
            customer_icp_stats.append({
                "icp_id": None,
                "icp_name": "未关联画像",
                "total": data["total"],
                "statuses": data["statuses"],
            })
        else:
            customer_icp_stats.append({
                "icp_id": key,
                "icp_name": icp_name_map.get(key, "未知画像"),
                "total": data["total"],
                "statuses": data["statuses"],
            })

    # 按客户总数降序排列
    customer_icp_stats.sort(key=lambda x: x["total"], reverse=True)

    # ── 邮件统计（Phase 6） ──
    sendlog_base = select(SendLog).join(
        EmailCampaign, SendLog.campaign_id == EmailCampaign.id
    ).where(EmailCampaign.tenant_id == tenant_id)

    total_emails_sent = (await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == tenant_id,
            SendLog.status.in_(["sent", "delivered", "opened", "replied"]),
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

    # 近 30 天按日统计
    daily_email_stats: List[dict] = []
    try:
        from sqlalchemy import case, text
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        daily_q = (
            select(
                func.date_trunc("day", SendLog.created_at).label("day"),
                func.count(SendLog.id).label("sent"),
                func.count(func.nullif(SendLog.opened_at, None)).label("opened"),
                func.sum(
                    case((SendLog.status == "replied", 1), else_=0)
                ).label("replied"),
            )
            .select_from(SendLog)
            .join(EmailCampaign, SendLog.campaign_id == EmailCampaign.id)
            .where(
                EmailCampaign.tenant_id == tenant_id,
                SendLog.created_at >= func.now() - text("interval '30 days'"),
            )
            .group_by(text("1"))
            .order_by(text("1 ASC"))
        )
        daily_rows = (await db.execute(daily_q)).all()
        daily_email_stats = [
            {"day": str(r[0])[:10], "sent": r[1], "opened": r[2], "replied": r[3] or 0}
            for r in daily_rows
        ]
    except Exception:
        daily_email_stats = []

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
        "customer_icp_stats": customer_icp_stats,
        # 邮件 (Phase 6)
        "total_emails_sent": total_emails_sent,
        "total_emails_opened": total_emails_opened,
        "total_emails_replied": total_emails_replied,
        "open_rate": open_rate,
        "reply_rate": total_emails_replied / total_emails_sent if total_emails_sent > 0 else 0.0,
        "daily_email_stats": daily_email_stats,
    }
