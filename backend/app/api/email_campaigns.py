"""邮件发送任务 API — Phase 6 Email Marketing"""

import asyncio
import logging
import uuid as _uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db, get_session
from app.core.auth import get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.models.customer import Customer
from app.models.contact import Contact
from app.models.enterprise import EnterpriseProfile
from app.models.product import Product
from app.models.email_template import EmailTemplate
from app.models.email_campaign import EmailCampaign
from app.models.send_log import SendLog
from app.models.unsubscribe import Unsubscribe
from app.schemas.email_campaign import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    CampaignResponse,
    CampaignListItem,
    CampaignListResponse,
    CampaignDetailResponse,
    PreviewRequest,
    PreviewResponse,
    SendLogResponse,
)
from app.services.email_sender import send_email, render_template
from app.core.security import encrypt_smtp_password, decrypt_smtp_password
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def _parse_uuid(val: str, label: str = "ID") -> _uuid.UUID:
    try:
        return _uuid.UUID(val)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"{label}格式无效")


# ── CRUD ──

@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送任务列表"""
    # 自动修复僵尸任务：已发完但状态卡在 sending
    stuck_fix_result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.tenant_id == current_user.tenant_id,
            EmailCampaign.status == "sending",
            EmailCampaign.sent_count >= EmailCampaign.total_recipients,
            EmailCampaign.total_recipients > 0,
        )
    )
    for stuck in stuck_fix_result.scalars().all():
        stuck.status = "completed"
        stuck.completed_at = datetime.now(timezone.utc)
        logger.warning(f"Auto-fixed stuck campaign {stuck.id}: {stuck.name}")
    if stuck_fix_result.scalars().all():
        await db.commit()

    conditions = [EmailCampaign.tenant_id == current_user.tenant_id]
    if status:
        conditions.append(EmailCampaign.status == status)
    where = conditions[0]
    for c in conditions[1:]:
        where = where & c

    count_q = select(func.count(EmailCampaign.id)).where(where)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    q = (
        select(EmailCampaign)
        .where(where)
        .order_by(EmailCampaign.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(q)).scalars().all()

    return CampaignListResponse(
        items=[CampaignListItem.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建发送任务"""
    # 验证模板归属
    tpl_result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == data.template_id,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = tpl_result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 验证客户归属 + 统计有邮箱的联系人数
    total_recipients = 0
    for cid in data.customer_ids:
        cust_result = await db.execute(
            select(Customer).where(
                Customer.id == cid,
                Customer.tenant_id == current_user.tenant_id,
            )
        )
        if not cust_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"客户不存在: {cid}")

        # 统计该客户有多少联系人有邮箱
        contact_count = await db.execute(
            select(func.count(Contact.id)).where(
                Contact.customer_id == cid,
                Contact.email.isnot(None),
                Contact.email != "",
            )
        )
        total_recipients += contact_count.scalar() or 0

    if total_recipients == 0:
        raise HTTPException(status_code=400, detail="所选客户没有可用的联系人邮箱")

    # 加密 SMTP 密码；空密码或脱敏占位符则从租户默认配置获取
    smtp_config_dict = data.smtp_config.model_dump()
    if smtp_config_dict.get("password") and smtp_config_dict["password"] != "********":
        smtp_config_dict["password"] = encrypt_smtp_password(smtp_config_dict["password"])
    else:
        # 从租户默认 SMTP 配置获取已加密的密码
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.id == current_user.tenant_id)
        )
        tenant_row = tenant_result.scalar_one_or_none()
        tenant_smtp = (tenant_row.settings or {}).get("smtp_config") or {} if tenant_row else {}
        if tenant_smtp.get("password"):
            smtp_config_dict["password"] = tenant_smtp["password"]  # 已加密
            # 如果用户未填 host/username，也一并从租户配置预填
            if not smtp_config_dict.get("host"):
                smtp_config_dict["host"] = tenant_smtp.get("host", "")
            if not smtp_config_dict.get("username"):
                smtp_config_dict["username"] = tenant_smtp.get("username", "")
            if not smtp_config_dict.get("port") or smtp_config_dict["port"] == 465:
                smtp_config_dict["port"] = tenant_smtp.get("port", 465)
        else:
            raise HTTPException(
                status_code=400,
                detail="请填写邮箱授权码，或先在系统设置中配置默认 SMTP",
            )

    campaign = EmailCampaign(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        name=data.name,
        template_id=data.template_id,
        total_recipients=total_recipients,
        smtp_config=smtp_config_dict,
        customer_ids=[str(cid) for cid in data.customer_ids],
        schedule_at=data.schedule_at,
        status="draft",
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """任务详情（含发送日志）"""
    uid = _parse_uuid(campaign_id, "任务ID")
    result = await db.execute(
        select(EmailCampaign)
        .options(
            selectinload(EmailCampaign.send_logs)
            .selectinload(SendLog.contact),
            selectinload(EmailCampaign.send_logs)
            .selectinload(SendLog.customer),
        )
        .where(
            EmailCampaign.id == uid,
            EmailCampaign.tenant_id == current_user.tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 构建含关联信息的发送日志
    logs_with_info = []
    for log in (campaign.send_logs or []):
        log_data = SendLogResponse.model_validate(log).model_dump()
        if log.contact:
            log_data["contact_name"] = log.contact.name
            log_data["contact_title"] = log.contact.title
        if log.customer:
            log_data["customer_name"] = log.customer.name
            log_data["customer_country"] = log.customer.country
            log_data["customer_industry"] = log.customer.industry
        logs_with_info.append(log_data)

    return CampaignDetailResponse(
        **CampaignResponse.model_validate(campaign).model_dump(),
        smtp_config=campaign.smtp_config,
        customer_ids=campaign.customer_ids,
        send_logs=logs_with_info,
    )


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    data: CampaignUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新任务（仅 draft 状态）"""
    uid = _parse_uuid(campaign_id, "任务ID")
    result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.id == uid,
            EmailCampaign.tenant_id == current_user.tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="任务不存在")
    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="仅草稿状态可编辑")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "smtp_config" and value:
            smtp_dict = value.model_dump()
            if smtp_dict.get("password"):
                smtp_dict["password"] = encrypt_smtp_password(smtp_dict["password"])
            setattr(campaign, field, smtp_dict)
        else:
            setattr(campaign, field, value)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除任务"""
    uid = _parse_uuid(campaign_id, "任务ID")
    result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.id == uid,
            EmailCampaign.tenant_id == current_user.tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="任务不存在")
    if campaign.status == "sending":
        raise HTTPException(status_code=400, detail="发送中的任务不可删除")
    await db.delete(campaign)
    await db.commit()


# ── 预览 ──

@router.post("/{campaign_id}/preview", response_model=PreviewResponse)
async def preview_campaign(
    campaign_id: str,
    data: PreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """预览对指定客户的邮件效果（变量替换后）"""
    uid = _parse_uuid(campaign_id, "任务ID")
    result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.id == uid,
            EmailCampaign.tenant_id == current_user.tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 获取模板
    if not campaign.template_id:
        raise HTTPException(status_code=400, detail="任务未关联模板")
    tpl_result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == campaign.template_id,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = tpl_result.scalar_one_or_none()
    if not template or not template.body_html:
        raise HTTPException(status_code=400, detail="模板不可用")

    # 获取客户和联系人
    customer = (await db.execute(
        select(Customer).where(Customer.id == data.customer_id, Customer.tenant_id == current_user.tenant_id)
    )).scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    contact = None
    if data.contact_id:
        contact = (await db.execute(
            select(Contact).where(Contact.id == data.contact_id, Contact.customer_id == data.customer_id)
        )).scalar_one_or_none()
    else:
        # 取第一个有邮箱的联系人
        contact = (await db.execute(
            select(Contact).where(
                Contact.customer_id == data.customer_id,
                Contact.email.isnot(None),
                Contact.email != "",
            ).limit(1)
        )).scalar_one_or_none()

    # 获取企业信息
    enterprise = (await db.execute(
        select(EnterpriseProfile).where(EnterpriseProfile.tenant_id == current_user.tenant_id)
    )).scalar_one_or_none()

    # 获取产品图片（防御性租户校验）
    product = None
    if template.product_id:
        product = (await db.execute(
            select(Product).where(
                Product.id == template.product_id,
                Product.tenant_id == current_user.tenant_id,
            )
        )).scalar_one_or_none()

    # 构建图片 URL
    base_url = settings.APP_BASE_URL.rstrip("/")
    logo_url = ""
    if enterprise and enterprise.logo_url:
        logo_path = enterprise.logo_url
        logo_url = logo_path if logo_path.startswith("http") else f"{base_url}/{logo_path.lstrip('/')}"
    product_image_url = ""
    if product and product.image_url:
        img_path = product.image_url
        product_image_url = img_path if img_path.startswith("http") else f"{base_url}/{img_path.lstrip('/')}"

    # 构建变量
    variables = {
        "客户联系人": contact.name if contact else "Sir/Madam",
        "客户公司": customer.name,
        "客户行业": customer.industry or "your industry",
        "我方企业": enterprise.company_name if enterprise else "Our Company",
        "我方联系人": current_user.name or "",
        "我方职位": (enterprise.contact_position or "") if enterprise else "",
        "我方邮箱": (enterprise.contact_email or "") if enterprise else "",
        "我方电话": (enterprise.contact_phone or "") if enterprise else "",
        "我方网站": (enterprise.website or "") if enterprise else "",
        "产品名称": (template.input_data or {}).get("product_name", "our products"),
        "产品描述": product.description if product else "",
        "企业Logo": logo_url,
        "产品图片": product_image_url,
    }

    # 优先使用外语版本（如果模板设置了语言且有外语内容）
    use_html = (template.body_html_foreign if template.language and template.body_html_foreign else template.body_html) or ""
    use_text = (template.body_text_foreign if template.language and template.body_text_foreign else template.body_text) or ""

    subject = render_template(template.subject or "Business Inquiry", variables)
    body_html = render_template(use_html, variables)
    body_text = render_template(use_text, variables)

    return PreviewResponse(subject=subject, body_html=body_html, body_text=body_text)


# ── 发送 ──

@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """启动发送（后台异步任务）"""
    uid = _parse_uuid(campaign_id, "任务ID")
    result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.id == uid,
            EmailCampaign.tenant_id == current_user.tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="任务不存在")
    if campaign.status == "sending":
        raise HTTPException(status_code=400, detail="任务正在发送中")
    if not campaign.smtp_config:
        raise HTTPException(status_code=400, detail="请先配置 SMTP")

    # 获取模板
    tpl_result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.id == campaign.template_id)
    )
    template = tpl_result.scalar_one_or_none()
    if not template or not template.body_html:
        raise HTTPException(status_code=400, detail="模板不可用")

    # 获取企业信息
    ent_result = await db.execute(
        select(EnterpriseProfile).where(EnterpriseProfile.tenant_id == current_user.tenant_id)
    )
    enterprise = ent_result.scalar_one_or_none()

    # 获取所有联系人
    customer_ids_for_query = []
    for cid_str in (campaign.customer_ids or []):
        try:
            customer_ids_for_query.append(_uuid.UUID(cid_str))
        except (ValueError, AttributeError):
            pass

    contacts_result = await db.execute(
        select(Contact, Customer).join(Customer, Contact.customer_id == Customer.id).where(
            Contact.customer_id.in_(customer_ids_for_query),
            Contact.email.isnot(None),
            Contact.email != "",
            Customer.tenant_id == current_user.tenant_id,
        )
    )
    contact_rows = contacts_result.all()

    if not contact_rows:
        raise HTTPException(status_code=400, detail="没有可用的联系人邮箱")

    # 获取退订列表
    unsub_result = await db.execute(
        select(Unsubscribe.email).where(Unsubscribe.tenant_id == current_user.tenant_id)
    )
    unsub_emails = {r[0].lower() for r in unsub_result.all()}

    # 过滤退订 + 生成发送日志
    send_logs_data = []
    for contact, customer in contact_rows:
        if contact.email.lower() in unsub_emails:
            continue
        send_logs_data.append((contact, customer))

    total = len(send_logs_data)
    if total == 0:
        raise HTTPException(status_code=400, detail="所有联系人均已退订")

    # 检查日发送配额
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    quota_result = await db.execute(
        select(func.count(SendLog.id)).select_from(SendLog).join(
            EmailCampaign, SendLog.campaign_id == EmailCampaign.id
        ).where(
            EmailCampaign.tenant_id == current_user.tenant_id,
            SendLog.created_at >= today_start,
            SendLog.status.in_(["sent", "delivered"]),
        )
    )
    sent_today = quota_result.scalar() or 0
    remaining = settings.EMAIL_DAILY_QUOTA - sent_today
    if remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail=f"今日发送配额({settings.EMAIL_DAILY_QUOTA}封)已用完，请明日再试",
        )
    if total > remaining:
        send_logs_data = send_logs_data[:remaining]
        total = len(send_logs_data)

    # 更新任务状态
    campaign.status = "sending"
    campaign.total_recipients = total
    campaign.sent_count = 0
    campaign.started_at = datetime.now(timezone.utc)
    await db.commit()

    # 获取产品图片（防御性租户校验）
    product = None
    if template.product_id:
        product = (await db.execute(
            select(Product).where(
                Product.id == template.product_id,
                Product.tenant_id == current_user.tenant_id,
            )
        )).scalar_one_or_none()

    # 构建图片 URL
    base_url = settings.APP_BASE_URL.rstrip("/")
    logo_url = ""
    if enterprise and enterprise.logo_url:
        logo_path = enterprise.logo_url
        logo_url = logo_path if logo_path.startswith("http") else f"{base_url}/{logo_path.lstrip('/')}"
    product_image_url = ""
    if product and product.image_url:
        img_path = product.image_url
        product_image_url = img_path if img_path.startswith("http") else f"{base_url}/{img_path.lstrip('/')}"

    # 后台发送
    smtp_config = campaign.smtp_config
    template_subject = template.subject or ""
    # 优先使用外语版本（如果模板设置了语言且有外语内容）
    template_html = (template.body_html_foreign if template.language and template.body_html_foreign else template.body_html) or ""
    template_text = (template.body_text_foreign if template.language and template.body_text_foreign else template.body_text) or ""

    async def background_send():
        try:
            sent = 0
            for contact, customer in send_logs_data:
                # 检查是否暂停
                async for sess in get_session():
                    camp = await sess.get(EmailCampaign, uid)
                    if camp and camp.status == "paused":
                        return

                # 变量替换（含图片）
                variables = {
                    "客户联系人": contact.name or "Sir/Madam",
                    "客户公司": customer.name,
                    "客户行业": customer.industry or "your industry",
                    "我方企业": enterprise.company_name if enterprise else "Our Company",
                    "我方联系人": current_user.name or "",
                    "我方职位": (enterprise.contact_position or "") if enterprise else "",
                    "我方邮箱": (enterprise.contact_email or "") if enterprise else "",
                    "我方电话": (enterprise.contact_phone or "") if enterprise else "",
                    "我方网站": (enterprise.website or "") if enterprise else "",
                    "产品名称": (template.input_data or {}).get("product_name", "our products"),
                    "产品描述": product.description if product else "",
                    "企业Logo": logo_url,
                    "产品图片": product_image_url,
                }
                subject = render_template(template_subject, variables)
                body_html = render_template(template_html, variables)
                body_text = render_template(template_text, variables)

                # 创建 SendLog
                log = SendLog(
                    campaign_id=uid,
                    customer_id=customer.id,
                    contact_id=contact.id,
                    recipient_email=contact.email,
                    subject=subject,
                    status="pending",
                )
                async for sess in get_session():
                    sess.add(log)
                    await sess.commit()
                    tracking_id = str(log.tracking_id)

                # 发送（传入 tenant_id 用于退订链接）
                result = await send_email(
                    smtp_config=smtp_config,
                    to_email=contact.email,
                    subject=subject,
                    html_body=body_html,
                    text_body=body_text,
                    tracking_id=tracking_id,
                    tenant_id=str(current_user.tenant_id),
                )

                # 更新日志
                async for sess in get_session():
                    log_entry = await sess.get(SendLog, log.id)
                    if log_entry:
                        # 存 Message-ID 供 IMAP 回复匹配
                        log_entry.message_id = result.get("message_id")
                        if result["success"]:
                            log_entry.status = "sent"
                        else:
                            log_entry.status = "failed"
                            log_entry.error_message = result.get("error", "未知错误")
                        await sess.commit()

                sent += 1

                # 更新任务计数
                async for sess in get_session():
                    camp = await sess.get(EmailCampaign, uid)
                    if camp:
                        camp.sent_count = sent
                        await sess.commit()

                # 速率控制
                await asyncio.sleep(settings.EMAIL_SEND_INTERVAL_SECONDS)

            # 发送完成
            async for sess in get_session():
                camp = await sess.get(EmailCampaign, uid)
                if camp:
                    camp.status = "completed"
                    camp.completed_at = datetime.now(timezone.utc)
                    await sess.commit()

            logger.info(f"Campaign {campaign_id} completed: {sent}/{total} sent")

        except Exception as e:
            logger.exception(f"Campaign {campaign_id} background send crashed: {e}")
            async for sess in get_session():
                camp = await sess.get(EmailCampaign, uid)
                if camp:
                    camp.status = "failed"
                    camp.completed_at = datetime.now(timezone.utc)
                    await sess.commit()

    asyncio.create_task(background_send())

    return {
        "message": f"发送任务已启动，共 {total} 封邮件",
        "total_recipients": total,
    }


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """暂停发送"""
    uid = _parse_uuid(campaign_id, "任务ID")
    result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.id == uid,
            EmailCampaign.tenant_id == current_user.tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="任务不存在")
    if campaign.status != "sending":
        raise HTTPException(status_code=400, detail="仅发送中的任务可暂停")

    campaign.status = "paused"
    await db.commit()
    return {"message": "发送已暂停"}


@router.post("/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """恢复发送（仅 paused 状态可恢复，重新启动后台任务）"""
    uid = _parse_uuid(campaign_id, "任务ID")
    result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.id == uid,
            EmailCampaign.tenant_id == current_user.tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="任务不存在")
    if campaign.status != "paused":
        raise HTTPException(status_code=400, detail="仅已暂停的任务可恢复")

    # 恢复逻辑复用 send 的主体，但需要重新获取未发送的联系人
    tpl_result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == campaign.template_id,
            EmailTemplate.tenant_id == current_user.tenant_id,
        )
    )
    template = tpl_result.scalar_one_or_none()
    if not template or not template.body_html:
        raise HTTPException(status_code=400, detail="模板不可用")

    ent_result = await db.execute(
        select(EnterpriseProfile).where(EnterpriseProfile.tenant_id == current_user.tenant_id)
    )
    enterprise = ent_result.scalar_one_or_none()

    # 获取未发送的联系人（排除已有 send_log 的）
    from sqlalchemy import and_
    customer_ids_for_query = []
    for cid_str in (campaign.customer_ids or []):
        try:
            customer_ids_for_query.append(_uuid.UUID(cid_str))
        except (ValueError, AttributeError):
            pass

    sent_contact_ids_result = await db.execute(
        select(SendLog.contact_id).where(SendLog.campaign_id == uid)
    )
    sent_contact_ids = {r[0] for r in sent_contact_ids_result.all() if r[0]}

    contacts_result = await db.execute(
        select(Contact, Customer).join(Customer, Contact.customer_id == Customer.id).where(
            and_(
                Contact.customer_id.in_(customer_ids_for_query),
                Contact.email.isnot(None),
                Contact.email != "",
                Customer.tenant_id == current_user.tenant_id,
                ~Contact.id.in_(sent_contact_ids) if sent_contact_ids else True,
            )
        )
    )
    contact_rows = contacts_result.all()

    if not contact_rows:
        campaign.status = "completed"
        campaign.completed_at = datetime.now(timezone.utc)
        await db.commit()
        return {"message": "所有联系人已发送完毕，任务标记为完成"}

    # 过滤退订
    unsub_result = await db.execute(
        select(Unsubscribe.email).where(Unsubscribe.tenant_id == current_user.tenant_id)
    )
    unsub_emails = {r[0].lower() for r in unsub_result.all()}

    remaining = []
    for contact, customer in contact_rows:
        if contact.email.lower() not in unsub_emails:
            remaining.append((contact, customer))

    if not remaining:
        campaign.status = "completed"
        campaign.completed_at = datetime.now(timezone.utc)
        await db.commit()
        return {"message": "剩余联系人均已退订，任务标记为完成"}

    total = len(remaining)
    campaign.status = "sending"
    await db.commit()

    # 构建图片 URL
    product = None
    if template.product_id:
        product = (await db.execute(
            select(Product).where(
                Product.id == template.product_id,
                Product.tenant_id == current_user.tenant_id,
            )
        )).scalar_one_or_none()

    base_url = settings.APP_BASE_URL.rstrip("/")
    logo_url = ""
    if enterprise and enterprise.logo_url:
        logo_path = enterprise.logo_url
        logo_url = logo_path if logo_path.startswith("http") else f"{base_url}/{logo_path.lstrip('/')}"
    product_image_url = ""
    if product and product.image_url:
        img_path = product.image_url
        product_image_url = img_path if img_path.startswith("http") else f"{base_url}/{img_path.lstrip('/')}"

    smtp_config = campaign.smtp_config
    template_subject = template.subject or ""
    # 优先使用外语版本（如果模板设置了语言且有外语内容）
    template_html = (template.body_html_foreign if template.language and template.body_html_foreign else template.body_html) or ""
    template_text = (template.body_text_foreign if template.language and template.body_text_foreign else template.body_text) or ""

    async def background_resume():
        try:
            sent = 0
            for contact, customer in remaining:
                async for sess in get_session():
                    camp = await sess.get(EmailCampaign, uid)
                    if camp and camp.status == "paused":
                        return

                variables = {
                    "客户联系人": contact.name or "Sir/Madam",
                    "客户公司": customer.name,
                    "客户行业": customer.industry or "your industry",
                    "我方企业": enterprise.company_name if enterprise else "Our Company",
                    "我方联系人": current_user.name or "",
                    "我方职位": (enterprise.contact_position or "") if enterprise else "",
                    "我方邮箱": (enterprise.contact_email or "") if enterprise else "",
                    "我方电话": (enterprise.contact_phone or "") if enterprise else "",
                    "我方网站": (enterprise.website or "") if enterprise else "",
                    "产品名称": (template.input_data or {}).get("product_name", "our products"),
                    "产品描述": product.description if product else "",
                    "企业Logo": logo_url,
                    "产品图片": product_image_url,
                }
                subject = render_template(template_subject, variables)
                body_html = render_template(template_html, variables)
                body_text = render_template(template_text, variables)

                log = SendLog(
                    campaign_id=uid,
                    customer_id=customer.id,
                    contact_id=contact.id,
                    recipient_email=contact.email,
                    subject=subject,
                    status="pending",
                )
                async for sess in get_session():
                    sess.add(log)
                    await sess.commit()
                    tracking_id = str(log.tracking_id)

                result = await send_email(
                    smtp_config=smtp_config,
                    to_email=contact.email,
                    subject=subject,
                    html_body=body_html,
                    text_body=body_text,
                    tracking_id=tracking_id,
                    tenant_id=str(current_user.tenant_id),
                )

                async for sess in get_session():
                    log_entry = await sess.get(SendLog, log.id)
                    if log_entry:
                        log_entry.message_id = result.get("message_id")
                        if result["success"]:
                            log_entry.status = "sent"
                        else:
                            log_entry.status = "failed"
                            log_entry.error_message = result.get("error", "未知错误")
                        await sess.commit()

                sent += 1
                async for sess in get_session():
                    camp = await sess.get(EmailCampaign, uid)
                    if camp:
                        camp.sent_count = (camp.sent_count or 0) + 1
                        await sess.commit()

                await asyncio.sleep(settings.EMAIL_SEND_INTERVAL_SECONDS)

            async for sess in get_session():
                camp = await sess.get(EmailCampaign, uid)
                if camp:
                    camp.status = "completed"
                    camp.completed_at = datetime.now(timezone.utc)
                    await sess.commit()

            logger.info(f"Campaign {campaign_id} resume completed: {sent} additional sent")

        except Exception as e:
            logger.exception(f"Campaign {campaign_id} resume crashed: {e}")
            async for sess in get_session():
                camp = await sess.get(EmailCampaign, uid)
                if camp:
                    camp.status = "failed"
                    camp.completed_at = datetime.now(timezone.utc)
                    await sess.commit()

    asyncio.create_task(background_resume())

    return {"message": f"发送已恢复，剩余 {total} 封邮件"}
