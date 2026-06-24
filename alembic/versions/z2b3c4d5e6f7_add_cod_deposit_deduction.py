"""add_cod_deposit_deduction

Revision ID: z2b3c4d5e6f7
Revises: z1a2b3c4d5e6
Create Date: 2026-06-25

Thêm dữ liệu audit cho luồng COD:
- orders.cod_deposit_amount
- orders.cod_deposit_deducted
- orders.cod_deposit_deducted_at
- deposit_transactions.order_id
"""
from alembic import op
import sqlalchemy as sa


revision = "z2b3c4d5e6f7"
down_revision = "z1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("cod_deposit_amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "orders",
        sa.Column("cod_deposit_deducted", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "orders",
        sa.Column("cod_deposit_deducted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_orders_cod_deposit_deducted",
        "orders",
        ["cod_deposit_deducted"],
    )

    op.add_column(
        "deposit_transactions",
        sa.Column("order_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_deposit_transactions_order_id",
        "deposit_transactions",
        ["order_id"],
    )
    op.create_foreign_key(
        "fk_deposit_transactions_order_id",
        "deposit_transactions",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_deposit_transactions_order_id", "deposit_transactions", type_="foreignkey")
    op.drop_index("ix_deposit_transactions_order_id", table_name="deposit_transactions")
    op.drop_column("deposit_transactions", "order_id")

    op.drop_index("ix_orders_cod_deposit_deducted", table_name="orders")
    op.drop_column("orders", "cod_deposit_deducted_at")
    op.drop_column("orders", "cod_deposit_deducted")
    op.drop_column("orders", "cod_deposit_amount")
