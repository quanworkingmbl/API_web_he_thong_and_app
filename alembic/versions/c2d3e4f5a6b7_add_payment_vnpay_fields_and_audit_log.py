"""add_payment_vnpay_fields_and_audit_log

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-04-05 11:41:00.000000

Thay đổi:
1. Thêm cột vào bảng `payments`:
   - vnpay_transaction_no, vnpay_response_code, vnpay_bank_code
   - amount_from_gateway, amount_mismatch
   - refunded_amount, refund_note, refunded_at
   - Thêm enum value PARTIAL_REFUNDED vào paymentstatus

2. Thêm cột vào bảng `payment_transactions`:
   - gateway_ref

3. Tạo bảng `payment_audit_logs`
"""
from alembic import op
import sqlalchemy as sa


revision = 'c2d3e4f5a6b7'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Thêm PARTIAL_REFUNDED vào enum paymentstatus (PostgreSQL)
    op.execute("""
        DO $$ BEGIN
            ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'PARTIAL_REFUNDED';
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # 1. Thêm cột vào payments
    op.add_column('payments', sa.Column('vnpay_transaction_no', sa.String(100), nullable=True))
    op.add_column('payments', sa.Column('vnpay_response_code',  sa.String(10),  nullable=True))
    op.add_column('payments', sa.Column('vnpay_bank_code',      sa.String(20),  nullable=True))
    op.add_column('payments', sa.Column('amount_from_gateway',  sa.Numeric(15, 2), nullable=True))
    op.add_column('payments', sa.Column('amount_mismatch',      sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('payments', sa.Column('refunded_amount',      sa.Numeric(15, 2), nullable=True))
    op.add_column('payments', sa.Column('refund_note',          sa.Text(), nullable=True))
    op.add_column('payments', sa.Column('refunded_at',          sa.DateTime(timezone=True), nullable=True))

    op.create_index('ix_payments_vnpay_transaction_no', 'payments', ['vnpay_transaction_no'])

    # 2. Thêm cột vào payment_transactions
    op.add_column('payment_transactions', sa.Column('gateway_ref', sa.String(255), nullable=True))

    # 3. Tạo bảng payment_audit_logs
    op.create_table(
        'payment_audit_logs',
        sa.Column('id',         sa.Integer(),     nullable=False),
        sa.Column('payment_id', sa.Integer(),     nullable=True),
        sa.Column('action',     sa.String(50),    nullable=False),
        sa.Column('actor_id',   sa.Integer(),     nullable=True),
        sa.Column('amount',     sa.Numeric(15, 2), nullable=True),
        sa.Column('note',       sa.Text(),        nullable=True),
        sa.Column('ip_address', sa.String(50),    nullable=True),
        sa.Column('user_agent', sa.String(500),   nullable=True),
        sa.Column('timestamp',  sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['actor_id'],   ['users.id'],   ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_payment_audit_logs_id',         'payment_audit_logs', ['id'])
    op.create_index('ix_payment_audit_logs_payment_id', 'payment_audit_logs', ['payment_id'])


def downgrade() -> None:
    # 3. Drop payment_audit_logs
    op.drop_index('ix_payment_audit_logs_payment_id', table_name='payment_audit_logs')
    op.drop_index('ix_payment_audit_logs_id',         table_name='payment_audit_logs')
    op.drop_table('payment_audit_logs')

    # 2. Drop cột payment_transactions
    op.drop_column('payment_transactions', 'gateway_ref')

    # 1. Drop cột payments
    op.drop_index('ix_payments_vnpay_transaction_no', table_name='payments')
    for col in ['refunded_at', 'refund_note', 'refunded_amount',
                'amount_mismatch', 'amount_from_gateway',
                'vnpay_bank_code', 'vnpay_response_code', 'vnpay_transaction_no']:
        op.drop_column('payments', col)
