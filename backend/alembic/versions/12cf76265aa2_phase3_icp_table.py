"""phase3_icp_table

Revision ID: 12cf76265aa2
Revises: a86d65d55164
Create Date: 2026-06-26 15:50:08.210376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '12cf76265aa2'
down_revision: Union[str, None] = 'a86d65d55164'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('icps',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('generation_time_ms', sa.Integer(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_icps_status'), 'icps', ['status'], unique=False)
    op.create_index('ix_icps_tenant_created', 'icps', ['tenant_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_icps_tenant_id'), 'icps', ['tenant_id'], unique=False)
    op.create_index('ix_icps_tenant_status', 'icps', ['tenant_id', 'status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_icps_tenant_status', table_name='icps')
    op.drop_index(op.f('ix_icps_tenant_id'), table_name='icps')
    op.drop_index('ix_icps_tenant_created', table_name='icps')
    op.drop_index(op.f('ix_icps_status'), table_name='icps')
    op.drop_table('icps')
