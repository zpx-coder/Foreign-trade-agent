"""管理后台 API — Phase 7"""

import uuid as _uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth import get_current_admin, require_admin_roles
from app.models.platform_admin import PlatformAdmin
from app.models.tenant import Tenant
from app.models.user import User
from app.models.icp import Icp
from app.models.customer import Customer
from app.models.send_log import SendLog
from app.models.email_campaign import EmailCampaign
from app.models.contact import Contact
from app.schemas.admin import (
    AdminStatsResponse,
    TenantListItem,
    TenantListResponse,
    TenantDetailResponse,
    TenantUserInfo,
    TenantUpdateRequest,
    TenantStatsResponse,
    TenantIcpStats,
    TenantCustomerStats,
    TenantEmailStats,
    TopTenantInfo,
)

router = APIRouter()


def _parse_uuid(val: str, label: str = "ID") -> _uuid.UUID:
    try:
        return _uuid.UUID(val)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"{label}格式无效")


# ── 平台统计 ──

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    current_admin: PlatformAdmin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """平台运营统计（跨全部租户聚合）"""
    # ── 基础 ──
    total_tenants = (await db.execute(
        select(func.count(Tenant.id))
    )).scalar() or 0

    active_tenants = (await db.execute(
        select(func.count(Tenant.id)).where(Tenant.status == "active")
    )).scalar() or 0

    total_users = (await db.execute(
        select(func.count(User.id))
    )).scalar() or 0

    # ── ICP 统计 ──
    total_icps = (await db.execute(
        select(func.count(Icp.id))
    )).scalar() or 0
    completed_icps = (await db.execute(
        select(func.count(Icp.id)).where(Icp.status == "completed")
    )).scalar() or 0
    generating_icps = (await db.execute(
        select(func.count(Icp.id)).where(Icp.status == "generating")
    )).scalar() or 0
    draft_icps = (await db.execute(
        select(func.count(Icp.id)).where(Icp.status == "draft")
    )).scalar() or 0
    failed_icps = (await db.execute(
        select(func.count(Icp.id)).where(Icp.status == "failed")
    )).scalar() or 0

    # ── 客户统计 ──
    total_customers = (await db.execute(
        select(func.count(Customer.id))
    )).scalar() or 0

    customers_reached_by_status = (await db.execute(
        select(func.count(Customer.id)).where(Customer.status != "new")
    )).scalar() or 0

    customers_reached_by_email = (await db.execute(
        select(func.count(func.distinct(Contact.customer_id)))
        .select_from(SendLog)
        .join(Contact, SendLog.contact_id == Contact.id)
        .where(SendLog.status.in_(["sent", "delivered", "replied"]))
    )).scalar() or 0

    customers_reached = max(customers_reached_by_status, customers_reached_by_email)
    reach_rate = round(customers_reached / total_customers, 4) if total_customers > 0 else 0.0

    # ── 邮件统计 ──
    total_emails_sent = (await db.execute(
        select(func.count(SendLog.id)).where(
            SendLog.status.in_(["sent", "delivered", "replied"])
        )
    )).scalar() or 0

    total_emails_opened = (await db.execute(
        select(func.count(SendLog.id)).where(
            SendLog.opened_at.isnot(None)
        )
    )).scalar() or 0

    total_emails_replied = (await db.execute(
        select(func.count(SendLog.id)).where(SendLog.status == "replied")
    )).scalar() or 0

    open_rate = round(total_emails_opened / total_emails_sent, 4) if total_emails_sent > 0 else 0.0
    reply_rate = round(total_emails_replied / total_emails_sent, 4) if total_emails_sent > 0 else 0.0

    # ── 租户分布 ──
    plan_rows = (await db.execute(
        select(Tenant.plan_type, func.count(Tenant.id)).group_by(Tenant.plan_type)
    )).all()
    tenants_by_plan: dict = {row[0]: row[1] for row in plan_rows}

    status_rows = (await db.execute(
        select(Tenant.status, func.count(Tenant.id)).group_by(Tenant.status)
    )).all()
    tenants_by_status: dict = {row[0]: row[1] for row in status_rows}

    # ── Top 榜单 ──
    top_cust_rows = (await db.execute(
        select(Tenant.name, func.count(Customer.id).label("cnt"))
        .join(Customer, Customer.tenant_id == Tenant.id)
        .group_by(Tenant.id, Tenant.name)
        .order_by(func.count(Customer.id).desc())
        .limit(5)
    )).all()
    top_tenants_by_customers = [
        TopTenantInfo(name=row[0], value=row[1]) for row in top_cust_rows
    ]

    top_email_rows = (await db.execute(
        select(Tenant.name, func.count(SendLog.id).label("cnt"))
        .select_from(SendLog)
        .join(EmailCampaign, SendLog.campaign_id == EmailCampaign.id)
        .join(Tenant, EmailCampaign.tenant_id == Tenant.id)
        .where(SendLog.status.in_(["sent", "delivered", "replied"]))
        .group_by(Tenant.id, Tenant.name)
        .order_by(func.count(SendLog.id).desc())
        .limit(5)
    )).all()
    top_tenants_by_emails = [
        TopTenantInfo(name=row[0], value=row[1]) for row in top_email_rows
    ]

    return AdminStatsResponse(
        total_tenants=total_tenants,
        active_tenants=active_tenants,
        total_users=total_users,
        total_icps=total_icps,
        completed_icps=completed_icps,
        generating_icps=generating_icps,
        draft_icps=draft_icps,
        failed_icps=failed_icps,
        total_customers=total_customers,
        customers_reached=customers_reached,
        reach_rate=reach_rate,
        total_emails_sent=total_emails_sent,
        total_emails_opened=total_emails_opened,
        total_emails_replied=total_emails_replied,
        open_rate=open_rate,
        reply_rate=reply_rate,
        tenants_by_plan=tenants_by_plan,
        tenants_by_status=tenants_by_status,
        top_tenants_by_customers=top_tenants_by_customers,
        top_tenants_by_emails=top_tenants_by_emails,
    )


# ── 租户列表 ──

@router.get("/tenants", response_model=TenantListResponse)
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    plan_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_admin: PlatformAdmin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """租户列表（分页+筛选）"""
    conditions = []
    if search:
        conditions.append(Tenant.name.ilike("%" + search + "%"))
    if plan_type:
        conditions.append(Tenant.plan_type == plan_type)
    if status_filter:
        conditions.append(Tenant.status == status_filter)

    base_q = select(Tenant)
    if conditions:
        base_q = base_q.where(conditions[0])
        for c in conditions[1:]:
            base_q = base_q.where(c)

    count_q = select(func.count()).select_from(base_q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    rows = (await db.execute(
        base_q.order_by(Tenant.created_at.desc()).offset(offset).limit(page_size)
    )).scalars().all()

    # 批量获取各租户的业务统计（避免 N+1）
    tenant_ids = [t.id for t in rows]

    # ICP 数量
    icp_counts: dict = {}
    if tenant_ids:
        icp_rows = (await db.execute(
            select(Icp.tenant_id, func.count(Icp.id))
            .where(Icp.tenant_id.in_(tenant_ids))
            .group_by(Icp.tenant_id)
        )).all()
        icp_counts = {row[0]: row[1] for row in icp_rows}

    # 客户数量
    customer_counts: dict = {}
    if tenant_ids:
        cust_rows = (await db.execute(
            select(Customer.tenant_id, func.count(Customer.id))
            .where(Customer.tenant_id.in_(tenant_ids))
            .group_by(Customer.tenant_id)
        )).all()
        customer_counts = {row[0]: row[1] for row in cust_rows}

    # 已发邮件数量（sent + delivered + replied）
    email_counts: dict = {}
    if tenant_ids:
        email_rows = (await db.execute(
            select(EmailCampaign.tenant_id, func.count(SendLog.id))
            .select_from(SendLog)
            .join(EmailCampaign, SendLog.campaign_id == EmailCampaign.id)
            .where(
                EmailCampaign.tenant_id.in_(tenant_ids),
                SendLog.status.in_(["sent", "delivered", "replied"]),
            )
            .group_by(EmailCampaign.tenant_id)
        )).all()
        email_counts = {row[0]: row[1] for row in email_rows}

    items = []
    for t in rows:
        user_count = (await db.execute(
            select(func.count(User.id)).where(User.tenant_id == t.id)
        )).scalar() or 0
        items.append(TenantListItem(
            id=t.id,
            name=t.name,
            plan_type=t.plan_type,
            status=t.status,
            user_count=user_count,
            icp_count=icp_counts.get(t.id, 0),
            customer_count=customer_counts.get(t.id, 0),
            email_sent_count=email_counts.get(t.id, 0),
            created_at=t.created_at,
        ))

    return TenantListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


# ── 租户详情 ──

@router.get("/tenants/{tenant_id}", response_model=TenantDetailResponse)
async def get_tenant_detail(
    tenant_id: str,
    current_admin: PlatformAdmin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """租户详情（含用户列表）"""
    uid = _parse_uuid(tenant_id, "租户ID")

    result = await db.execute(
        select(Tenant).where(Tenant.id == uid)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    users_result = await db.execute(
        select(User).where(User.tenant_id == uid).order_by(User.created_at.desc())
    )
    users = users_result.scalars().all()

    return TenantDetailResponse(
        id=tenant.id,
        name=tenant.name,
        plan_type=tenant.plan_type,
        status=tenant.status,
        settings=tenant.settings,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        users=[TenantUserInfo.model_validate(u) for u in users],
    )


# ── 租户业务数据统计 ──

@router.get("/tenants/{tenant_id}/stats", response_model=TenantStatsResponse)
async def get_tenant_stats(
    tenant_id: str,
    current_admin: PlatformAdmin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取指定租户的业务数据统计（ICP/客户/邮件）"""
    tid = _parse_uuid(tenant_id, "租户ID")

    # 验证租户存在
    tenant_exists = (await db.execute(
        select(func.count(Tenant.id)).where(Tenant.id == tid)
    )).scalar() or 0
    if not tenant_exists:
        raise HTTPException(status_code=404, detail="租户不存在")

    # ── 客户画像统计 ──
    icp_base = select(func.count(Icp.id)).where(Icp.tenant_id == tid)
    total_icps = (await db.execute(icp_base)).scalar() or 0
    completed_icps = (await db.execute(
        icp_base.where(Icp.status == "completed")
    )).scalar() or 0
    generating_icps = (await db.execute(
        icp_base.where(Icp.status == "generating")
    )).scalar() or 0
    draft_icps = (await db.execute(
        icp_base.where(Icp.status == "draft")
    )).scalar() or 0
    failed_icps = (await db.execute(
        icp_base.where(Icp.status == "failed")
    )).scalar() or 0

    # ── 客户统计 ──
    customer_base = select(func.count(Customer.id)).where(
        Customer.tenant_id == tid
    )
    total_customers = (await db.execute(customer_base)).scalar() or 0

    customers_reached_by_status = (await db.execute(
        select(func.count(Customer.id)).where(
            Customer.tenant_id == tid,
            Customer.status != "new",
        )
    )).scalar() or 0

    customers_reached_by_email = (await db.execute(
        select(func.count(func.distinct(Contact.customer_id)))
        .select_from(SendLog)
        .join(Contact, SendLog.contact_id == Contact.id)
        .join(EmailCampaign, SendLog.campaign_id == EmailCampaign.id)
        .where(
            EmailCampaign.tenant_id == tid,
            SendLog.status.in_(["sent", "delivered", "replied"]),
        )
    )).scalar() or 0

    customers_reached = max(customers_reached_by_status, customers_reached_by_email)
    reach_rate = round(customers_reached / total_customers, 4) if total_customers > 0 else 0.0

    # 客户状态分布
    status_rows = (await db.execute(
        select(Customer.status, func.count(Customer.id))
        .where(Customer.tenant_id == tid)
        .group_by(Customer.status)
    )).all()
    status_counts: dict = {row[0]: row[1] for row in status_rows}

    # ── 邮件统计 ──
    email_join = select(SendLog).join(
        EmailCampaign, SendLog.campaign_id == EmailCampaign.id
    ).where(EmailCampaign.tenant_id == tid)

    total_emails_sent = (await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == tid,
            SendLog.status.in_(["sent", "delivered", "replied"]),
        )
    )).scalar() or 0

    total_emails_opened = (await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == tid,
            SendLog.opened_at.isnot(None),
        )
    )).scalar() or 0

    total_emails_replied = (await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == tid,
            SendLog.status == "replied",
        )
    )).scalar() or 0

    open_rate = round(total_emails_opened / total_emails_sent, 4) if total_emails_sent > 0 else 0.0
    reply_rate = round(total_emails_replied / total_emails_sent, 4) if total_emails_sent > 0 else 0.0

    return TenantStatsResponse(
        icp=TenantIcpStats(
            total=total_icps,
            completed=completed_icps,
            generating=generating_icps,
            draft=draft_icps,
            failed=failed_icps,
        ),
        customer=TenantCustomerStats(
            total=total_customers,
            reached=customers_reached,
            reach_rate=reach_rate,
            status_counts=status_counts,
        ),
        email=TenantEmailStats(
            total_sent=total_emails_sent,
            total_opened=total_emails_opened,
            open_rate=open_rate,
            total_replied=total_emails_replied,
            reply_rate=reply_rate,
        ),
    )


# ── 更新租户（套餐/状态） ──

@router.put("/tenants/{tenant_id}", response_model=TenantDetailResponse)
async def update_tenant(
    tenant_id: str,
    data: TenantUpdateRequest,
    current_admin: PlatformAdmin = Depends(require_admin_roles("super_admin")),
    db: AsyncSession = Depends(get_db),
):
    """修改租户套餐或状态（仅超级管理员）"""
    uid = _parse_uuid(tenant_id, "租户ID")

    result = await db.execute(select(Tenant).where(Tenant.id == uid))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    await db.commit()
    await db.refresh(tenant)

    users_result = await db.execute(
        select(User).where(User.tenant_id == uid).order_by(User.created_at.desc())
    )
    users = users_result.scalars().all()

    return TenantDetailResponse(
        id=tenant.id,
        name=tenant.name,
        plan_type=tenant.plan_type,
        status=tenant.status,
        settings=tenant.settings,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        users=[TenantUserInfo.model_validate(u) for u in users],
    )
