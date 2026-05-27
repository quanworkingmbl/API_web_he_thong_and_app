"""add_origin_images_field

Revision ID: i3j4k5l6m7n8
Revises: f5a6b7c8d9e0
Create Date: 2026-04-16 17:35:00.000000

Changes:
- product_origins: add images (Text, nullable) for traceability evidence images
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "i3j4k5l6m7n8"
down_revision = "f5a6b7c8d9e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product_origins", sa.Column("images", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("product_origins", "images")
