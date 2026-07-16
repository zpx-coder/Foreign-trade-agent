"""系统设置 API — Phase 7"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.database import get_db
from app.core.auth import get_current_user
from app.core.security import encrypt_smtp_password, decrypt_smtp_password
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.members import SmtpConfigRequest, SmtpConfigResponse

router = APIRouter()


@router.get("/smtp", response_model=SmtpConfigResponse)
async def get_smtp_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取租户默认 SMTP 配置"""
    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    smtp = (tenant.settings or {}).get("smtp_config") or {}
    # 密码不返回（安全性），前端通过 host/username 是否为空判断是否已配置
    return SmtpConfigResponse(
        host=smtp.get("host", "smtp.gmail.com"),
        port=smtp.get("port", 465),
        username=smtp.get("username", ""),
        password="" if smtp.get("password") else "",
        from_name=smtp.get("from_name", ""),
        from_email=smtp.get("from_email", ""),
    )


@router.put("/smtp", response_model=SmtpConfigResponse)
async def update_smtp_config(
    data: SmtpConfigRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """保存租户默认 SMTP 配置"""
    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    smtp_dict = data.model_dump()
    # 如果密码非空且不是脱敏值，则加密存储
    if smtp_dict.get("password") and smtp_dict["password"] != "********":
        smtp_dict["password"] = encrypt_smtp_password(smtp_dict["password"])
    else:
        # 保留旧密码
        old_smtp = (tenant.settings or {}).get("smtp_config") or {}
        if old_smtp.get("password"):
            smtp_dict["password"] = old_smtp["password"]
        else:
            smtp_dict["password"] = ""

    current_settings = tenant.settings or {}
    current_settings["smtp_config"] = smtp_dict
    tenant.settings = current_settings
    flag_modified(tenant, "settings")  # JSONB 列需显式标记变更
    await db.commit()

    return SmtpConfigResponse(
        host=smtp_dict["host"],
        port=smtp_dict["port"],
        username=smtp_dict["username"],
        password="" if smtp_dict.get("password") else "",
        from_name=smtp_dict["from_name"],
        from_email=smtp_dict["from_email"],
    )
