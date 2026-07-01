"""add deposit wallet tables

Revision ID: v1w2x3y4z5a6
Revises: t1u2v3w4x5y6
Create Date: 2026-06-01

Tạo 2 bảng mới cho tính năng Ví Sàn (Platform Deposit Wallet):
  - seller_deposit_wallets : số dư ký quỹ của từng seller
  - deposit_transactions   : lịch sử mỗi lần nạp / khấu trừ / hoàn tiền
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "v1w2x3y4z5a6"
down_revision = "t1u2v3w4x5y6"
branch_labels = None
depends_on = None


def upgrade():
    # ── seller_deposit_wallets ────────────────────────────────────────────────
    op.create_table(
        "seller_deposit_wallets",
        sa.Column("id",              sa.Integer(),      primary_key=True, index=True),
        sa.Column("seller_id",       sa.Integer(),      sa.ForeignKey("users.id"), unique=True, nullable=False, index=True),
        sa.Column("deposit_balance", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("total_deposited", sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("total_deducted",  sa.Numeric(15, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at",      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",      sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # ── deposit_transactions ──────────────────────────────────────────────────
    op.create_table(
        "deposit_transactions",
        sa.Column("id",             sa.Integer(), primary_key=True, index=True),
        sa.Column("seller_id",      sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("amount",         sa.Numeric(15, 2), nullable=False),
        sa.Column("tx_type",        sa.Enum("TOP_UP", "DEDUCT", "REFUND", name="deposittransactiontype"),
                  nullable=False, server_default="TOP_UP"),
        sa.Column("status",         sa.Enum("PENDING", "CONFIRMED", "REJECTED", name="depositstatus"),
                  nullable=False, server_default="PENDING", index=True),
        sa.Column("payment_method", sa.String(50),  nullable=True),
        sa.Column("bank_ref",       sa.String(255), nullable=True),
        sa.Column("receipt_url",    sa.Text(),      nullable=True),
        sa.Column("vnpay_txn_ref",  sa.String(255), nullable=True, index=True),
        sa.Column("vnpay_response", sa.Text(),      nullable=True),
        sa.Column("note",           sa.Text(),      nullable=True),
        sa.Column("reviewed_by",    sa.Integer(),   sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at",    sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at",     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",     sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table("deposit_transactions")
    op.drop_table("seller_deposit_wallets")
    op.execute("DROP TYPE IF EXISTS deposittransactiontype")
    op.execute("DROP TYPE IF EXISTS depositstatus")
