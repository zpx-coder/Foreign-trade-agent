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
from app.models.send_log import SendLog
from app.schemas.admin import (
    AdminStatsResponse,
    TenantListItem,
    TenantListResponse,
    TenantDetailResponse,
    TenantUserInfo,
    TenantUpdateRequest,
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
    """平台运营统计"""
    total_tenants = (await db.execute(
        select(func.count(Tenant.id))
    )).scalar() or 0

    active_tenants = (await db.execute(
        select(func.count(Tenant.id)).where(Tenant.status == "active")
    )).scalar() or 0

    total_users = (await db.execute(
        select(func.count(User.id))
    )).scalar() or 0

    total_emails_sent = (await db.execute(
        select(func.count(SendLog.id)).where(
            SendLog.status.in_(["sent", "delivered"])
        )
    )).scalar() or 0

    return AdminStatsResponse(
        total_tenants=total_tenants,
        active_tenants=active_tenants,
        total_users=total_users,
        total_emails_sent=total_emails_sent,
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
