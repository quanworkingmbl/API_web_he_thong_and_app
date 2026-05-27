"""add_origin_verification_fields

Revision ID: e7f8a9b0c1d2
Revises: d3e4f5a6b7c8
Create Date: 2026-04-07 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7f8a9b0c1d2"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    origin_status = sa.Enum("PENDING", "VERIFIED", "REJECTED", name="originstatus")
    origin_status.create(bind, checkfirst=True)

    op.add_column(
        "product_origins",
        sa.Column("verification_status", origin_status, nullable=True, server_default="PENDING"),
    )
    op.add_column("product_origins", sa.Column("verified_by", sa.Integer(), nullable=True))
    op.add_column("product_origins", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("product_origins", sa.Column("rejection_reason", sa.Text(), nullable=True))

    op.create_foreign_key(
        "fk_product_origins_verified_by_users",
        "product_origins",
        "users",
        ["verified_by"],
        ["id"],
    )

    # Existing rows were previously visible without review, keep them visible after migration.
    op.execute("UPDATE product_origins SET verification_status = 'VERIFIED' WHERE verification_status IS NULL")


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_constraint("fk_product_origins_verified_by_users", "product_origins", type_="foreignkey")

    op.drop_column("product_origins", "rejection_reason")
    op.drop_column("product_origins", "verified_at")
    op.drop_column("product_origins", "verified_by")
    op.drop_column("product_origins", "verification_status")

    origin_status = sa.Enum("PENDING", "VERIFIED", "REJECTED", name="originstatus")
    origin_status.drop(bind, checkfirst=True)
