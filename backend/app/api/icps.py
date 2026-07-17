"""ICP 客户画像 CRUD + AI 生成 API"""

import json
import time
import uuid as _uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, get_session
from app.core.auth import get_current_user
from app.models.user import User
from app.models.icp import Icp
from app.schemas.icp import (
    IcpCreateRequest,
    IcpUpdateRequest,
    IcpResponse,
    IcpListItem,
    IcpListResponse,
)
from app.services.ai_service import AIServiceError, get_ai_service
from app.services.ai.icp_generator import IcpGenerator

router = APIRouter()

# 清理超过此时间的 stuck generating 记录
_GENERATING_TIMEOUT_MINUTES = 15


def _parse_uuid(val: str, label: str = "ID") -> _uuid.UUID:
    """将路径参数解析为 UUID，无效时返回 400"""
    try:
        return _uuid.UUID(val)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"{label}格式无效")


async def _cleanup_stuck_generating(db: AsyncSession, tenant_id: _uuid.UUID) -> int:
    """将超时的 generating 记录标记为 failed"""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=_GENERATING_TIMEOUT_MINUTES)
    result = await db.execute(
        update(Icp)
        .where(
            Icp.tenant_id == tenant_id,
            Icp.status == "generating",
            Icp.updated_at < cutoff,
        )
        .values(status="failed", error_message="生成超时，请重试")
    )
    if result.rowcount:
        await db.commit()
    return result.rowcount


@router.get("", response_model=IcpListResponse)
async def list_icps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ICP 列表（分页 + 状态筛选）"""
    await _cleanup_stuck_generating(db, current_user.tenant_id)
    conditions = [Icp.tenant_id == current_user.tenant_id]
    if status:
        conditions.append(Icp.status == status)

    where_clause = conditions[0]
    for c in conditions[1:]:
        where_clause = where_clause & c

    count_q = select(func.count(Icp.id)).where(where_clause)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    q = (
        select(Icp)
        .where(where_clause)
        .order_by(Icp.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(q)).scalars().all()

    # v1.3: 从 input_data 提取列表显示字段
    items = []
    for icp in rows:
        input_data = icp.input_data or {}
        company_size = input_data.get("company_size")
        if isinstance(company_size, str):
            company_size = [company_size]
        # 构建预算显示文本
        budget_min = input_data.get("customer_budget_min")
        budget_max = input_data.get("customer_budget_max")
        if budget_min is not None and budget_max is not None:
            budget_display = f"${budget_min:,.0f} — ${budget_max:,.0f} USD"
        elif budget_min is not None:
            budget_display = f"≥ ${budget_min:,.0f} USD"
        elif budget_max is not None:
            budget_display = f"≤ ${budget_max:,.0f} USD"
        else:
            budget_display = input_data.get("customer_budget")  # 回退旧字段
        items.append(IcpListItem(
            id=icp.id,
            name=icp.name,
            status=icp.status,
            target_region=input_data.get("target_region"),
            target_industry=input_data.get("target_industry"),
            company_size=company_size,
            customer_budget=budget_display,
            created_at=icp.created_at,
            updated_at=icp.updated_at,
        ))

    return IcpListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=IcpResponse, status_code=status.HTTP_201_CREATED)
async def create_icp(
    data: IcpCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建 ICP（保存输入数据，状态为 draft）"""
    icp = Icp(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        name=data.name,
        status="draft",
        input_data=data.input_data.model_dump(exclude_unset=True),
    )
    db.add(icp)
    await db.commit()
    await db.refresh(icp)
    return icp


@router.get("/{icp_id}", response_model=IcpResponse)
async def get_icp(
    icp_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ICP 详情"""
    uid = _parse_uuid(icp_id, "画像ID")
    result = await db.execute(
        select(Icp).where(
            Icp.id == uid,
            Icp.tenant_id == current_user.tenant_id,
        )
    )
    icp = result.scalar_one_or_none()
    if not icp:
        raise HTTPException(status_code=404, detail="画像不存在")
    return icp


@router.put("/{icp_id}", response_model=IcpResponse)
async def update_icp(
    icp_id: str,
    data: IcpUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新 ICP 输入数据"""
    uid = _parse_uuid(icp_id, "画像ID")
    result = await db.execute(
        select(Icp).where(
            Icp.id == uid,
            Icp.tenant_id == current_user.tenant_id,
        )
    )
    icp = result.scalar_one_or_none()
    if not icp:
        raise HTTPException(status_code=404, detail="画像不存在")

    update_dict = data.model_dump(exclude_unset=True)
    if "input_data" in update_dict:
        update_dict["input_data"] = update_dict["input_data"].model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(icp, field, value)

    await db.commit()
    await db.refresh(icp)
    return icp


@router.delete("/{icp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_icp(
    icp_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除 ICP"""
    uid = _parse_uuid(icp_id, "画像ID")
    result = await db.execute(
        select(Icp).where(
            Icp.id == uid,
            Icp.tenant_id == current_user.tenant_id,
        )
    )
    icp = result.scalar_one_or_none()
    if not icp:
        raise HTTPException(status_code=404, detail="画像不存在")

    await db.delete(icp)
    await db.commit()
    return None


@router.post("/{icp_id}/generate")
async def generate_icp(
    icp_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SSE 端点：调用 AI 生成 ICP 画像"""
    uid = _parse_uuid(icp_id, "画像ID")

    # 验证 ICP 存在且属于当前租户
    result = await db.execute(
        select(Icp).where(
            Icp.id == uid,
            Icp.tenant_id == current_user.tenant_id,
        )
    )
    icp = result.scalar_one_or_none()
    if not icp:
        raise HTTPException(status_code=404, detail="画像不存在")

    # 标记为生成中
    icp.status = "generating"
    icp.error_message = None
    await db.commit()

    async def event_stream():
        start_time = time.monotonic()
        try:
            ai_service = get_ai_service()
            generator = IcpGenerator(ai_service)

            async for chunk in generator.generate(icp.input_data):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

            # 生成完成 — 用独立 session 写库（get_session 自动 commit）
            output = generator.get_output()
            elapsed_ms = int((time.monotonic() - start_time) * 1000)

            async for session in get_session():
                result = await session.execute(
                    select(Icp).where(Icp.id == uid)
                )
                row = result.scalar_one_or_none()
                if row:
                    row.status = "completed"
                    row.output_data = output
                    row.generation_time_ms = elapsed_ms

            yield f"data: {json.dumps({'type': 'complete', 'elapsed_ms': elapsed_ms}, ensure_ascii=False)}\n\n"

        except Exception as e:
            error_msg = str(e)
            try:
                async for session in get_session():
                    result = await session.execute(
                        select(Icp).where(Icp.id == uid)
                    )
                    row = result.scalar_one_or_none()
                    if row:
                        row.status = "failed"
                        row.error_message = error_msg
            except Exception:
                pass
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
