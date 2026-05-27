"""Merge multiple alembic heads before notification table

Revision ID: n2o3p4q5r6s7
Revises: h2i3j4k5l6m7, m1n2o3p4q5r6
Create Date: 2026-04-20
"""

from alembic import op
import sqlalchemy as sa

revision = 'n2o3p4q5r6s7'
down_revision = ('h2i3j4k5l6m7', 'l6m7n8o9p0q1')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
