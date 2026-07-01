"""add product_change_logs table

Revision ID: u1v2w3x4y5z6
Revises: t1u2v3w4x5y6
Create Date: 2026-05-28

Thêm bảng product_change_logs để ghi lịch sử mọi thay đổi của sản phẩm.
Mỗi lần cập nhật sản phẩm sẽ tạo N bản ghi – một bản ghi cho mỗi field
thay đổi, giúp audit đầy đủ cho cả Seller và Admin.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'u1v2w3x4y5z6'
down_revision = 't1u2v3w4x5y6'
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
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
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
