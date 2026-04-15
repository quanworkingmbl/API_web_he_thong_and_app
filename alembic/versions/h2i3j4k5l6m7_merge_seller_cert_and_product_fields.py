"""Merge seller cert branch with product fields branch

Revision ID: h2i3j4k5l6m7
Revises: f5a6b7c8d9e0, g1h2i3j4k5l6
Create Date: 2026-04-16
"""
from alembic import op
import sqlalchemy as sa

revision = "h2i3j4k5l6m7"
down_revision = ("f5a6b7c8d9e0", "g1h2i3j4k5l6")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
