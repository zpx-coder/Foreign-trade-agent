"""成员管理 API — Phase 7"""

import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth import get_current_user, require_roles
from app.core.security import hash_password
from app.models.user import User
from app.schemas.members import (
    MemberResponse,
    MemberListResponse,
    InviteMemberRequest,
    UpdateMemberRequest,
)

router = APIRouter()


def _parse_uuid(val: str, label: str = "ID") -> _uuid.UUID:
    try:
        return _uuid.UUID(val)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"{label}格式无效")


# ── 成员列表 ──

@router.get("", response_model=MemberListResponse)
async def list_members(
    current_user: User = Depends(require_roles("super_admin", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """获取当前租户成员列表"""
    result = await db.execute(
        select(User)
        .where(User.tenant_id == current_user.tenant_id)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return MemberListResponse(
        items=[MemberResponse.model_validate(u) for u in users],
        total=len(users),
    )


# ── 邀请成员 ──

@router.post("/invite", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    data: InviteMemberRequest,
    current_user: User = Depends(require_roles("super_admin", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """邀请新成员加入当前租户"""
    # 检查邮箱是否已注册
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="该邮箱已注册")

    # 只能创建 sales 或 readonly 角色
    if data.role not in ("sales", "readonly"):
        raise HTTPException(status_code=400, detail="只能邀请销售或只读角色")

    user = User(
        tenant_id=current_user.tenant_id,
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ── 更新成员 ──

@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: str,
    data: UpdateMemberRequest,
    current_user: User = Depends(require_roles("super_admin", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """修改成员角色或状态"""
    uid = _parse_uuid(member_id, "成员ID")

    result = await db.execute(
        select(User).where(
            User.id == uid,
            User.tenant_id == current_user.tenant_id,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="成员不存在")

    # 不能操作自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色或状态")

    # 只有 super_admin 可以提升为 admin
    if data.role == "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可设置管理员角色")

    # 不能将别人提升为 super_admin（租户内唯一）
    if data.role == "super_admin":
        raise HTTPException(status_code=400, detail="不能通过此接口设置超级管理员")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


# ── 移除成员（软删除） ──

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: str,
    current_user: User = Depends(require_roles("super_admin", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """禁用成员（软删除）"""
    uid = _parse_uuid(member_id, "成员ID")

    result = await db.execute(
        select(User).where(
            User.id == uid,
            User.tenant_id == current_user.tenant_id,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="成员不存在")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    if user.role == "super_admin":
        raise HTTPException(status_code=400, detail="不能禁用超级管理员")

    user.is_active = False
    await db.commit()
