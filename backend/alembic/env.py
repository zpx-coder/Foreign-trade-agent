"""Alembic 环境配置 — 异步 PostgreSQL 迁移"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.database import Base

# 导入全部模型，确保 Base.metadata 包含所有表
# Phase 1 开始逐步取消注释：
# from app.models.tenant import Tenant           # Phase 1
# from app.models.user import User               # Phase 1
# from app.models.enterprise import EnterpriseProfile  # Phase 2
# from app.models.product import Product         # Phase 2
# from app.models.icp import Icp                 # Phase 3
# from app.models.customer import Customer       # Phase 4
# from app.models.contact import Contact         # Phase 4
# from app.models.email_template import EmailTemplate     # Phase 6
# from app.models.email_campaign import EmailCampaign     # Phase 6
# from app.models.send_log import SendLog                 # Phase 6
# from app.models.unsubscribe import Unsubscribe          # Phase 6

# Alembic Config 对象
config = context.config

# 日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线迁移：生成 SQL 脚本而非直接执行"""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """在给定的数据库连接上执行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在线迁移：连接数据库并执行"""
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
