"""v1.4 add contact_type and confidence to contacts

Revision ID: 8a1c3d5e7f92
Revises: 779370b0cfe1
Create Date: 2026-07-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a1c3d5e7f92'
down_revision: Union[str, None] = '779370b0cfe1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('contacts', sa.Column('contact_type', sa.String(length=20), nullable=True, server_default='scraped'))
    op.add_column('contacts', sa.Column('confidence', sa.String(length=10), nullable=True))


def downgrade() -> None:
    op.drop_column('contacts', 'confidence')
    op.drop_column('contacts', 'contact_type')
