"""initial_schema

Revision ID: 2e5947dbd20b
Revises: 
Create Date: 2026-06-25 15:14:14.584548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e5947dbd20b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建基础扩展与枚举类型"""
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # 枚举类型 — 按 Phase 逐步创建
    # Phase 1
    op.execute("DROP TYPE IF EXISTS plan_type CASCADE")
    op.execute("CREATE TYPE plan_type AS ENUM ('free', 'pro', 'enterprise')")
    op.execute("DROP TYPE IF EXISTS tenant_status CASCADE")
    op.execute("CREATE TYPE tenant_status AS ENUM ('active', 'suspended', 'cancelled')")

    # Phase 3
    op.execute("DROP TYPE IF EXISTS icp_status CASCADE")
    op.execute("CREATE TYPE icp_status AS ENUM ('draft', 'generated', 'archived')")

    # Phase 4
    op.execute("DROP TYPE IF EXISTS customer_status CASCADE")
    op.execute("CREATE TYPE customer_status AS ENUM ('new', 'interested', 'not_interested', 'marketing')")
    op.execute("DROP TYPE IF EXISTS email_validity CASCADE")
    op.execute("CREATE TYPE email_validity AS ENUM ('valid', 'invalid', 'risky', 'unknown')")
    op.execute("DROP TYPE IF EXISTS decision_level CASCADE")
    op.execute("CREATE TYPE decision_level AS ENUM ('c_level', 'vp', 'director', 'manager', 'staff')")

    # Phase 6
    op.execute("DROP TYPE IF EXISTS campaign_status CASCADE")
    op.execute("CREATE TYPE campaign_status AS ENUM ('draft', 'scheduled', 'sending', 'completed', 'paused', 'cancelled')")


def downgrade() -> None:
    """回退所有枚举类型"""
    op.execute("DROP TYPE IF EXISTS campaign_status CASCADE")
    op.execute("DROP TYPE IF EXISTS decision_level CASCADE")
    op.execute("DROP TYPE IF EXISTS email_validity CASCADE")
    op.execute("DROP TYPE IF EXISTS customer_status CASCADE")
    op.execute("DROP TYPE IF EXISTS icp_status CASCADE")
    op.execute("DROP TYPE IF EXISTS tenant_status CASCADE")
    op.execute("DROP TYPE IF EXISTS plan_type CASCADE")
