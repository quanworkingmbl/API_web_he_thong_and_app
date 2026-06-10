"""add_deposit_withdrawal_requests_table

Revision ID: x1y2z3a4b5c6
Revises: w2x3y4z5a6b7
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa

revision = 'x1y2z3a4b5c6'
down_revision = 'w2x3y4z5a6b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'deposit_withdrawal_requests',
        sa.Column('id',                  sa.Integer(),      nullable=False),
        sa.Column('seller_id',           sa.Integer(),      nullable=False),
        sa.Column('amount',              sa.Numeric(15, 2), nullable=False),
        sa.Column('balance_snapshot',    sa.Numeric(15, 2), nullable=True),
        sa.Column('bank_name',           sa.String(255),    nullable=True),
        sa.Column('bank_account_number', sa.String(50),     nullable=True),
        sa.Column('bank_account_name',   sa.String(255),    nullable=True),
        sa.Column('status',              sa.Enum('PENDING', 'APPROVED', 'REJECTED',
                                                 name='depositwithdrawalstatus'),
                  nullable=False, server_default='PENDING'),
        sa.Column('note',            sa.Text(),      nullable=True),
        sa.Column('admin_note',      sa.Text(),      nullable=True),
        sa.Column('transaction_ref', sa.String(255), nullable=True),
        sa.Column('reviewed_by',     sa.Integer(),   nullable=True),
        sa.Column('reviewed_at',     sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',      sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['seller_id'],   ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_deposit_withdrawal_requests_id',        'deposit_withdrawal_requests', ['id'],        unique=False)
    op.create_index('ix_deposit_withdrawal_requests_seller_id', 'deposit_withdrawal_requests', ['seller_id'], unique=False)
    op.create_index('ix_deposit_withdrawal_requests_status',    'deposit_withdrawal_requests', ['status'],    unique=False)


def downgrade() -> None:
    op.drop_index('ix_deposit_withdrawal_requests_status',    table_name='deposit_withdrawal_requests')
    op.drop_index('ix_deposit_withdrawal_requests_seller_id', table_name='deposit_withdrawal_requests')
    op.drop_index('ix_deposit_withdrawal_requests_id',        table_name='deposit_withdrawal_requests')
    op.drop_table('deposit_withdrawal_requests')
    op.execute("DROP TYPE IF EXISTS depositwithdrawalstatus")
