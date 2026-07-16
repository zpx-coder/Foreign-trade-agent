"""企业资料 API"""

import os
import uuid as _uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.enterprise import EnterpriseProfile
from app.schemas.enterprise import EnterpriseUpdateRequest, EnterpriseResponse

router = APIRouter()

UPLOAD_DIR = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=EnterpriseResponse)
async def get_enterprise(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前租户的企业资料"""
    result = await db.execute(
        select(EnterpriseProfile).where(
            EnterpriseProfile.tenant_id == current_user.tenant_id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="企业资料未填写")
    return profile


@router.put("", response_model=EnterpriseResponse)
async def upsert_enterprise(
    data: EnterpriseUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建或更新企业资料"""
    result = await db.execute(
        select(EnterpriseProfile).where(
            EnterpriseProfile.tenant_id == current_user.tenant_id
        )
    )
    profile = result.scalar_one_or_none()

    if profile:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
    else:
        profile = EnterpriseProfile(
            tenant_id=current_user.tenant_id, **data.model_dump(exclude_unset=True)
        )
        db.add(profile)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传企业 Logo 并更新 enterprise_profile.logo_url"""
    # 校验文件类型
    allowed_types = {"image/png", "image/jpeg", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的图片格式: {file.content_type}，仅允许 PNG/JPEG/GIF/WebP",
        )

    # 校验文件大小
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    contents = await file.read()
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大 {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # 生成唯一文件名
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "png"
    filename = f"{_uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    logo_url = f"/uploads/{filename}"

    # 更新企业资料中的 logo_url
    result = await db.execute(
        select(EnterpriseProfile).where(
            EnterpriseProfile.tenant_id == current_user.tenant_id
        )
    )
    profile = result.scalar_one_or_none()

    if profile:
        profile.logo_url = logo_url
    else:
        profile = EnterpriseProfile(
            tenant_id=current_user.tenant_id,
            company_name="",
            logo_url=logo_url,
        )
        db.add(profile)

    await db.commit()
    await db.refresh(profile)

    return {"logo_url": logo_url, "filename": filename}
