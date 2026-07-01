"""add return_policy columns to products

Revision ID: rp_001
Revises: 
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa

revision = 'rp_001'
down_revision = None   # ← đặt revision cha nếu có
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('return_days', sa.Integer(), nullable=True, comment='Số ngày được đổi trả (NULL/0 = không hỗ trợ)')
    )
    op.add_column(
        'products',
        sa.Column('return_fee_paid', sa.Boolean(), nullable=False, server_default=sa.false(),
                  comment='True = có phí đổi trả, False = miễn phí')
    )


def downgrade() -> None:
    op.drop_column('products', 'return_fee_paid')
    op.drop_column('products', 'return_days')
