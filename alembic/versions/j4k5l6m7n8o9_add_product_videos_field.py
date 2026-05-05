"""add_product_videos_field

Revision ID: j4k5l6m7n8o9
Revises: i3j4k5l6m7n8
Create Date: 2026-04-16 19:20:00.000000

Changes:
- products: add videos (Text, nullable) for product video URL(s)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "j4k5l6m7n8o9"
down_revision = "i3j4k5l6m7n8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from alembic import context
    if context.is_offline_mode():
        op.add_column("products", sa.Column("videos", sa.Text(), nullable=True))
        return

    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("products")}
    if "videos" not in columns:
        op.add_column("products", sa.Column("videos", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("products")}
    if "videos" in columns:
        op.drop_column("products", "videos")
