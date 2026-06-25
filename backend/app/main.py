"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    yield
    # 关闭时 — 清理资源（后续添加 Redis / ES 连接关闭）


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


# ── 健康检查 ──
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


# ── 路由注册（后续 Phase 逐步挂载） ──
# from app.api import auth, enterprise, products, icps, customers, email_templates, email_campaigns, email_auth
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
