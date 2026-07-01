"""fix missing promotions and orders columns causing 500 errors

Revision ID: s1t2u3v4w5x6
Revises: r3s4t5u6v7w8
Create Date: 2026-05-10

Fixes:
  - psycopg2.errors.UndefinedColumn: column promotions.applicable_to does not exist
  - psycopg2.errors.UndefinedColumn: column orders.currency does not exist
  - psycopg2.errors.UndefinedColumn: column orders.wallet_credited does not exist
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 's1t2u3v4w5x6'
down_revision = 'r3s4t5u6v7w8'
branch_labels = None
depends_on = None


def upgrade():
    # ── PROMOTIONS: thêm cột còn thiếu ──
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        # Dùng try/except-style qua server_default để an toàn
        batch_op.add_column(sa.Column('applicable_to', sa.String(50), server_default='ALL', nullable=True))
        batch_op.add_column(sa.Column('seller_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
        batch_op.add_column(sa.Column('applicable_product_ids', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('applicable_category_ids', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('user_conditions', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_public', sa.Boolean(), server_default=sa.text('true'), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
        batch_op.add_column(sa.Column('usage_limit_per_user', sa.Integer(), nullable=True))
        batch_op.create_index('ix_promotions_seller_id', ['seller_id'])

    # ── ORDERS: thêm cột còn thiếu ──
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currency', sa.String(3), server_default='VND', nullable=False))
        batch_op.add_column(sa.Column('wallet_credited', sa.Boolean(), server_default=sa.text('false'), nullable=False))
        batch_op.add_column(sa.Column('channel', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('coupon_code', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('tax_breakdown', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('fee_breakdown', sa.Text(), nullable=True))
        batch_op.create_index('ix_orders_wallet_credited', ['wallet_credited'])


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_index('ix_orders_wallet_credited')
        batch_op.drop_column('fee_breakdown')
        batch_op.drop_column('tax_breakdown')
        batch_op.drop_column('coupon_code')
        batch_op.drop_column('channel')
        batch_op.drop_column('wallet_credited')
        batch_op.drop_column('currency')

    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.drop_index('ix_promotions_seller_id')
        batch_op.drop_column('usage_limit_per_user')
        batch_op.drop_column('created_by')
        batch_op.drop_column('is_public')
        batch_op.drop_column('user_conditions')
        batch_op.drop_column('applicable_category_ids')
        batch_op.drop_column('applicable_product_ids')
        batch_op.drop_column('seller_id')
        batch_op.drop_column('applicable_to')
