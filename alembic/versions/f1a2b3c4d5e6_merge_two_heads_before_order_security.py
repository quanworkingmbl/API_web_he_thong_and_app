"""merge_two_heads_before_order_security

Revision ID: f1a2b3c4d5e6
Revises: b82aa2f98076, e2f3a4b5c6d7
Create Date: 2026-04-05 11:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = ('b82aa2f98076', 'e2f3a4b5c6d7')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
