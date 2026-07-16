"""邮件模板 API — Phase 6 Email Marketing"""

import json
import logging
import uuid as _uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, get_session
from app.core.auth import get_current_user
from app.models.user import User
from app.models.icp import Icp
from app.models.product import Product
from app.models.enterprise import EnterpriseProfile
from app.models.email_template import EmailTemplate
from app.schemas.email_template import (
    EmailTemplateCreateRequest,
    EmailTemplateUpdateRequest,
    EmailTemplateResponse,
    EmailTemplateListItem,
    EmailTemplateListResponse,
    TestSendRequest,
)
from app.services.ai_service import AIServiceError, get_ai_service
from app.services.ai.email_generator import EmailGenerator
from app.services.email_sender import send_email

logger = logging.getLogger(__name__)

router = APIRouter()


def _parse_uuid(val: str, label: str = "ID") -> _uuid.UUID:
    try:
        return _uuid.UUID(val)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"{label}格式无效")


# ── CRUD ──

@router.get("", response_model=EmailTemplateListResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """邮件模板列表"""
    conditions = [EmailTemplate.tenant_id == current_user.tenant_id]
    if status:
        conditions.append(EmailTemplate.status == status)
    where = conditions[0]
    for c in conditions[1:]:
        where = where & c

    count_q = select(func.count(EmailTemplate.id)).where(where)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    q = (
        select(EmailTemplate)
        .where(where)
        .order_by(EmailTemplate.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(q)).scalars().all()

    return EmailTemplateListResponse(
        items=[EmailTemplateListItem.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: EmailTemplateCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建模板草稿"""
    payload = data.model_dump(exclude={"reference_email"})
    # JSONB 不能存储 UUID 对象，需要转为字符串
    input_data_safe = {}
    for k, v in payload.items():
        if isinstance(v, _uuid.UUID):
            input_data_safe[k] = str(v)
        else:
            input_data_safe[k] = v
    template = EmailTemplate(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        status="draft",
        input_data=input_data_safe,
        **{k: v for k, v in payload.items() if k not in ("input_data",)},
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """模板详情"""
    uid = _parse_uuid(template_id, "模板ID")
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == uid,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.put("/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: str,
    data: EmailTemplateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新模板"""
    uid = _parse_uuid(template_id, "模板ID")
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == uid,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除模板"""
    uid = _parse_uuid(template_id, "模板ID")
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == uid,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    await db.delete(template)
    await db.commit()


# ── AI 生成 (SSE) ──

@router.post("/{template_id}/generate")
async def generate_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SSE 端点：AI 生成邮件模板"""
    uid = _parse_uuid(template_id, "模板ID")
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == uid,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    async def event_stream():
        ai_service = get_ai_service()
        generator = EmailGenerator(ai_service)

        # 构建生成输入
        input_data = template.input_data or {}

        # 获取 ICP 摘要
        if template.icp_id:
            icp_result = await db.execute(select(Icp).where(Icp.id == template.icp_id))
            icp = icp_result.scalar_one_or_none()
            if icp and icp.output_data:
                input_data["icp_summary"] = json.dumps(icp.output_data, ensure_ascii=False)
            elif icp:
                input_data["icp_summary"] = icp.name

        # 获取产品信息
        if template.product_id:
            prod_result = await db.execute(select(Product).where(Product.id == template.product_id))
            product = prod_result.scalar_one_or_none()
            if product:
                parts = [f"产品名称：{product.name}"]
                if product.description:
                    parts.append(f"产品描述：{product.description}")
                if product.category:
                    parts.append(f"产品品类：{product.category}")
                if product.moq:
                    parts.append(f"最小起订量：{product.moq}")
                if product.price_usd:
                    parts.append(f"参考价格：USD {product.price_usd}")
                input_data["product_info"] = "\n".join(parts)

        # 获取企业信息
        ent_result = await db.execute(
            select(EnterpriseProfile).where(
                EnterpriseProfile.tenant_id == current_user.tenant_id
            )
        )
        enterprise = ent_result.scalar_one_or_none()
        if enterprise:
            input_data.setdefault("company_name", enterprise.company_name)

        yield f"data: {json.dumps({'type': 'progress', 'message': 'AI 正在生成邮件模板...'}, ensure_ascii=False)}\n\n"

        try:
            async for chunk in generator.generate(input_data):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except AIServiceError as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'AI 服务异常: {e}'}, ensure_ascii=False)}\n\n"
            return

        output = generator.get_output()
        if output and not output.get("parse_error"):
            # 保存生成结果
            async for sess in get_session():
                tpl = await sess.get(EmailTemplate, uid)
                if tpl:
                    tpl.subject = output.get("subjects", [""])[0] if output.get("subjects") else ""
                    tpl.body_html = output.get("body_html")
                    tpl.body_text = output.get("body_text")
                    tpl.spam_score = output.get("spam_score")
                    tpl.read_time_seconds = output.get("read_time_seconds")
                    tpl.output_data = output
                    tpl.status = "ready"
                    await sess.commit()
                    yield f"data: {json.dumps({'type': 'complete', 'template_id': str(uid), 'subjects': output.get('subjects', []), 'body_html': output.get('body_html', ''), 'body_text': output.get('body_text', ''), 'spam_score': output.get('spam_score'), 'read_time_seconds': output.get('read_time_seconds')}, ensure_ascii=False)}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': 'AI 生成失败，请重试'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── 测试发送 ──

@router.post("/{template_id}/test-send")
async def test_send(
    template_id: str,
    data: TestSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送测试邮件到指定邮箱"""
    uid = _parse_uuid(template_id, "模板ID")
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == uid,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    if not template.body_html:
        raise HTTPException(status_code=400, detail="模板尚未生成邮件内容")

    # 获取企业信息用于签名
    ent_result = await db.execute(
        select(EnterpriseProfile).where(
            EnterpriseProfile.tenant_id == current_user.tenant_id
        )
    )
    enterprise = ent_result.scalar_one_or_none()

    # 测试变量
    variables = {
        "客户联系人": "Test Contact",
        "客户公司": "Test Company",
        "客户行业": "Manufacturing",
        "我方企业": enterprise.company_name if enterprise else "Your Company",
        "我方联系人": current_user.name or "Test Sender",
        "产品名称": "Test Product",
    }

    from app.services.email_sender import render_template
    html_body = render_template(template.body_html, variables)
    subject = render_template(template.subject or "Test", variables)

    return {
        "subject": subject,
        "body_html": html_body,
        "message": "测试邮件预览已生成（实际发送需要配置 SMTP）",
    }
