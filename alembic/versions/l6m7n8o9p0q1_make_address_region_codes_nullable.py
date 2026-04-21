"""make_address_region_codes_nullable

Revision ID: l6m7n8o9p0q1
Revises: k5l6m7n8o9p0
Create Date: 2026-04-16 23:30:00.000000

Changes:
- addresses: allow null for province_code, district_code, ward_code
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "l6m7n8o9p0q1"
down_revision = "k5l6m7n8o9p0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "addresses",
        "province_code",
        existing_type=sa.String(length=20),
        nullable=True,
    )
    op.alter_column(
        "addresses",
        "district_code",
        existing_type=sa.String(length=20),
        nullable=True,
    )
    op.alter_column(
        "addresses",
        "ward_code",
        existing_type=sa.String(length=20),
        nullable=True,
    )


def downgrade() -> None:
    bind = op.get_bind()
    null_rows = bind.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM addresses
            WHERE province_code IS NULL
               OR district_code IS NULL
               OR ward_code IS NULL
            """
        )
    ).scalar_one()
    if null_rows > 0:
        raise RuntimeError(
            "Cannot downgrade: addresses has rows with NULL region codes."
        )

    op.alter_column(
        "addresses",
        "ward_code",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.alter_column(
        "addresses",
        "district_code",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.alter_column(
        "addresses",
        "province_code",
        existing_type=sa.String(length=20),
        nullable=False,
    )
