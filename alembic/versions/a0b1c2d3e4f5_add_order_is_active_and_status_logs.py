"""add_order_is_active_and_status_logs

Revision ID: a0b1c2d3e4f5
Revises: f1a2b3c4d5e6
Create Date: 2026-04-05 11:06:00.000000

Thay đổi:
1. Thêm cột `is_active` (Boolean, default True) vào bảng `orders`
   - Dùng cho soft-delete: admin ẩn đơn thay vì xóa cứng
2. Tạo bảng `order_status_logs` để audit trail mọi thay đổi trạng thái đơn
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0b1c2d3e4f5'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Thêm cột is_active vào bảng orders (soft-delete)
    op.add_column(
        'orders',
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),  # PostgreSQL: mọi đơn hiện tại = active
        )
    )
    op.create_index('ix_orders_is_active', 'orders', ['is_active'], unique=False)

    # 2. Tạo bảng order_status_logs (audit trail)
    op.create_table(
        'order_status_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('old_status', sa.String(length=30), nullable=True),
        sa.Column('new_status', sa.String(length=30), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),          # NULL = system/webhook
        sa.Column('role', sa.String(length=30), nullable=True),      # consumer/seller/admin/system
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column(
            'timestamp',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_order_status_logs_id', 'order_status_logs', ['id'], unique=False)
    op.create_index('ix_order_status_logs_order_id', 'order_status_logs', ['order_id'], unique=False)


def downgrade() -> None:
    # 2. Xóa bảng order_status_logs
    op.drop_index('ix_order_status_logs_order_id', table_name='order_status_logs')
    op.drop_index('ix_order_status_logs_id', table_name='order_status_logs')
    op.drop_table('order_status_logs')

    # 1. Xóa cột is_active khỏi orders
    op.drop_index('ix_orders_is_active', table_name='orders')
    op.drop_column('orders', 'is_active')
