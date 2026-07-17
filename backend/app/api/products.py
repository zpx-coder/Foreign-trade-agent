"""产品管理 CRUD API"""

import os
import uuid as _uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.config import settings
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
)

UPLOAD_DIR = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="搜索产品名称"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """产品列表（分页 + 筛选 + 搜索）"""
    conditions = [Product.tenant_id == current_user.tenant_id]

    if category:
        conditions.append(Product.category == category)
    if is_active is not None:
        conditions.append(Product.is_active == is_active)
    if search:
        conditions.append(Product.name.ilike(f"%{search}%"))

    where_clause = and_(*conditions)

    # 总数
    count_q = select(func.count(Product.id)).where(where_clause)
    total = (await db.execute(count_q)).scalar() or 0

    # 分页
    offset = (page - 1) * page_size
    q = (
        select(Product)
        .where(where_clause)
        .order_by(Product.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    products = (await db.execute(q)).scalars().all()

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建产品"""
    product = Product(tenant_id=current_user.tenant_id, **data.model_dump(exclude_unset=True))
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """产品详情"""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == current_user.tenant_id,
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新产品"""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == current_user.tenant_id,
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除产品"""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == current_user.tenant_id,
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    await db.delete(product)
    await db.commit()
    return None


@router.post("/{product_id}/images")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传产品图片（v1.2 — 支持多图）"""
    # 校验产品归属
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == current_user.tenant_id,
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

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

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "png"
    filename = f"{_uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    image_url = f"/uploads/{filename}"

    # 追加到 images 数组
    current_images = product.images or []
    current_images.append(image_url)
    product.images = current_images
    flag_modified(product, "images")
    await db.commit()

    return {"url": image_url, "filename": filename, "images": current_images}
