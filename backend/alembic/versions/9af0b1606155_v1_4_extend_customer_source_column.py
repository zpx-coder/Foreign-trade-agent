"""v1_4_extend_customer_source_column

Revision ID: 9af0b1606155
Revises: 8a1c3d5e7f92
Create Date: 2026-07-23 09:16:58.453195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9af0b1606155'
down_revision: Union[str, None] = '8a1c3d5e7f92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("customers", "source",
                    existing_type=sa.String(50),
                    type_=sa.String(200),
                    existing_nullable=False,
                    existing_server_default=None)


def downgrade() -> None:
    op.alter_column("customers", "source",
                    existing_type=sa.String(200),
                    type_=sa.String(50),
                    existing_nullable=False,
                    existing_server_default=None)
