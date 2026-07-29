"""Dashboard 统计数据 API"""

from typing import Optional, List, Tuple
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


# v1.6: 企业档案字段分组及完整度计算
_ENT_FIELD_GROUPS = {
    "basic": ["company_name", "logo_url", "industry", "website", "country", "city", "address", "description"],
    "trade": ["year_established", "employee_count", "factory_area", "annual_export_volume",
              "main_markets", "certifications", "oem_odm", "company_advantages"],
    "contact": ["contact_email", "contact_phone", "contact_position"],
    "media": ["factory_photos", "certificate_photos"],
}


def _is_field_filled(val) -> bool:
    """判断字段是否有实际内容"""
    if val is None:
        return False
    if isinstance(val, str) and val.strip() == "":
        return False
    if isinstance(val, list) and len(val) == 0:
        return False
    if isinstance(val, dict) and len(val) == 0:
        return False
    return True


def _calc_enterprise_completion(ent) -> Tuple[float, dict]:
    """计算企业档案完整度，返回 (总体百分比, 各区块详情)。"""
    group_scores: dict = {}
    total_filled = 0
    total_fields = 0

    for group_name, fields in _ENT_FIELD_GROUPS.items():
        filled = sum(1 for f in fields if _is_field_filled(getattr(ent, f, None)))
        group_scores[group_name] = {
            "filled": filled,
            "total": len(fields),
            "rate": round(filled / len(fields), 4) if fields else 0.0,
        }
        total_filled += filled
        total_fields += len(fields)

    overall = round(total_filled / total_fields, 4) if total_fields > 0 else 0.0
    return overall, group_scores


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

    # v1.6: 计算企业档案完整度
    enterprise_completion = 0.0
    enterprise_completion_detail: dict = {}
    if has_enterprise > 0:
        ent_row = (
            await db.execute(
                select(EnterpriseProfile).where(
                    EnterpriseProfile.tenant_id == tenant_id
                )
            )
        ).scalar_one_or_none()
        if ent_row:
            enterprise_completion, enterprise_completion_detail = _calc_enterprise_completion(ent_row)

    # ── 客户统计（Phase 4） ──
    customer_base = select(func.count(Customer.id)).where(
        Customer.tenant_id == tenant_id
    )
    total_customers = (await db.execute(customer_base)).scalar() or 0
    # 触达 = 客户状态非 new（手动标记已联系/已筛选/洽谈中/已成交）或曾通过邮件成功发送
    customers_reached_by_status = (await db.execute(
        select(func.count(Customer.id)).where(
            Customer.tenant_id == tenant_id,
            Customer.status != "new",
        )
    )).scalar() or 0
    customers_reached_by_email = (await db.execute(
        select(func.count(func.distinct(Contact.customer_id)))
        .select_from(SendLog)
        .join(Contact, SendLog.contact_id == Contact.id)
        .join(EmailCampaign, SendLog.campaign_id == EmailCampaign.id)
        .where(
            EmailCampaign.tenant_id == tenant_id,
            SendLog.status.in_(["sent", "delivered", "replied"]),
        )
    )).scalar() or 0
    customers_reached = max(customers_reached_by_status, customers_reached_by_email)
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
            SendLog.status.in_(["sent", "delivered", "replied"]),
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
        "enterprise_completion": enterprise_completion,
        "enterprise_completion_detail": enterprise_completion_detail,
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
