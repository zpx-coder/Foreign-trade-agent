"""认证 API — 用户端 + 管理后台"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.platform_admin import PlatformAdmin
from app.core.security import hash_password, verify_password
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_current_admin,
)
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserLoginResponse,
    UserMeResponse,
    UserInfo,
    TenantInfo,
    TokenResponse,
    RefreshRequest,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminInfo,
)

router = APIRouter()

# ────────────────────────── 用户端 API ──────────────────────────


@router.post("/register", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册 — 同时创建租户 + 用户（注册者为超管）"""
    # 检查邮箱是否已注册
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="该邮箱已注册"
        )

    # 创建租户
    tenant = Tenant(name=data.company_name)
    db.add(tenant)
    await db.flush()

    # 创建用户（超管角色）
    user = User(
        tenant_id=tenant.id,
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        role="super_admin",
    )
    db.add(user)
    await db.flush()

    # 生成 Token
    access_token = create_access_token(
        str(user.id),
        extra_claims={"tenant_id": str(tenant.id), "role": user.role},
    )
    refresh_token = create_refresh_token(str(user.id))

    await db.commit()

    return UserLoginResponse(
        user=UserInfo.model_validate(user),
        tenant=TenantInfo.model_validate(tenant),
        token=TokenResponse(access_token=access_token, refresh_token=refresh_token),
    )


@router.post("/login", response_model=UserLoginResponse)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

    # 获取租户
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = tenant_result.scalar_one()

    if tenant.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="企业账户已被停用")

    # 生成 Token
    access_token = create_access_token(
        str(user.id),
        extra_claims={"tenant_id": str(tenant.id), "role": user.role},
    )
    refresh_token = create_refresh_token(str(user.id))

    # 更新最后登录时间
    from datetime import datetime, timezone
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return UserLoginResponse(
        user=UserInfo.model_validate(user),
        tenant=TenantInfo.model_validate(tenant),
        token=TokenResponse(access_token=access_token, refresh_token=refresh_token),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest):
    """刷新 Access Token（Refresh Token 轮换）"""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="请使用 Refresh Token"
        )

    user_id = payload.get("sub")
    # 生成新的 Token 对（Refresh Token 轮换）
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取当前登录用户信息"""
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = tenant_result.scalar_one()

    # 角色 → 权限列表
    permission_map = {
        "super_admin": ["manage_members", "manage_templates", "view_all_data", "manage_billing"],
        "admin": ["manage_templates", "view_all_data"],
        "sales": ["view_own_data"],
        "readonly": ["view_own_data"],
    }

    return UserMeResponse(
        user=UserInfo.model_validate(current_user),
        tenant=TenantInfo.model_validate(tenant),
        permissions=permission_map.get(current_user.role, []),
    )


@router.post("/logout")
async def logout(_current_user: User = Depends(get_current_user)):
    """登出（客户端删除 Token，服务端可在此追加 Token 黑名单逻辑）"""
    return {"success": True}


# ────────────────────────── 管理后台 API ──────────────────────────


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(data: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """平台管理员登录"""
    result = await db.execute(
        select(PlatformAdmin).where(PlatformAdmin.email == data.email)
    )
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误"
        )
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

    access_token = create_access_token(
        str(admin.id), extra_claims={"admin_role": admin.role}
    )
    refresh_token = create_refresh_token(str(admin.id))

    from datetime import datetime, timezone
    admin.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return AdminLoginResponse(
        admin=AdminInfo.model_validate(admin),
        token=TokenResponse(access_token=access_token, refresh_token=refresh_token),
    )
