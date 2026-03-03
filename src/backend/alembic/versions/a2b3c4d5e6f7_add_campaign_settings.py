"""add campaign settings columns

Revision ID: a2b3c4d5e6f7
Revises: 41f5195956f4
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = '41f5195956f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('campaigns', sa.Column('match_types', sa.JSON(), nullable=True))
    op.add_column('campaigns', sa.Column('negative_keywords', sa.JSON(), nullable=True))
    op.add_column('campaigns', sa.Column('bid_value', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('campaigns', sa.Column('location_targeting', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('campaigns', 'location_targeting')
    op.drop_column('campaigns', 'bid_value')
    op.drop_column('campaigns', 'negative_keywords')
    op.drop_column('campaigns', 'match_types')
