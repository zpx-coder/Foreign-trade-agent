"""FastAPI 应用入口"""

import asyncio
import logging
import os
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings

logger = logging.getLogger(__name__)

# 后台 IMAP 轮询任务引用（用于优雅关闭）
_imap_poll_task: Optional[asyncio.Task] = None


async def _imap_poll_loop():
    """后台 IMAP 回复轮询循环"""
    interval = max(settings.IMAP_POLL_INTERVAL_MINUTES, 1) * 60
    logger.info(
        f"IMAP reply poll started (interval: {settings.IMAP_POLL_INTERVAL_MINUTES} min)"
    )
    # 首次启动后等待 30 秒再开始，确保服务完全就绪
    await asyncio.sleep(30)
    while True:
        try:
            from app.services.email.reply_tracker import check_replies_for_all_tenants
            await check_replies_for_all_tenants()
        except Exception:
            logger.exception("IMAP poll loop error")
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global _imap_poll_task

    # 启动时：启动 IMAP 回复轮询
    _imap_poll_task = asyncio.create_task(_imap_poll_loop())

    yield

    # 关闭时：取消后台任务
    if _imap_poll_task:
        _imap_poll_task.cancel()
        try:
            await _imap_poll_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="AI 外贸助手",
    description="企业级 AI Agent 产品，自动化外贸客户开发与营销",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 静态文件（Logo 上传） ──
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ── 健康检查 ──
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


# ── 路由注册 ──
from app.api import auth
from app.api import enterprise
from app.api import products
from app.api import icps
from app.api import customers
from app.api import dashboard
from app.api import email_templates
from app.api import email_campaigns
from app.api import email_tracking
from app.api import admin
from app.api import members
from app.api import settings as settings_api

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(enterprise.router, prefix="/api/v1/enterprise", tags=["企业资料"])
app.include_router(products.router, prefix="/api/v1/products", tags=["产品管理"])
app.include_router(icps.router, prefix="/api/v1/icps", tags=["客户画像"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["客户管理"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["工作台"])
app.include_router(email_templates.router, prefix="/api/v1/email-templates", tags=["邮件模板"])
app.include_router(email_campaigns.router, prefix="/api/v1/email-campaigns", tags=["发送任务"])
app.include_router(email_tracking.router, prefix="/api/v1", tags=["邮件追踪"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理后台"])
app.include_router(members.router, prefix="/api/v1/members", tags=["成员管理"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["系统设置"])
