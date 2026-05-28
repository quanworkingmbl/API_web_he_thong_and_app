"""add product_change_logs table

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2026-05-28

Thêm bảng product_change_logs để ghi lịch sử mọi thay đổi của sản phẩm.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'product_change_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=False, server_default='UPDATE'),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_product_change_logs_id', 'product_change_logs', ['id'], unique=False)
    op.create_index('ix_product_change_logs_product_id', 'product_change_logs', ['product_id'], unique=False)
    op.create_index('ix_product_change_logs_changed_by', 'product_change_logs', ['changed_by'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_product_change_logs_changed_by', table_name='product_change_logs')
    op.drop_index('ix_product_change_logs_product_id', table_name='product_change_logs')
    op.drop_index('ix_product_change_logs_id', table_name='product_change_logs')
    op.drop_table('product_change_logs')
