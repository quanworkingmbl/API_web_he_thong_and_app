"""Add notifications table

Revision ID: m1n2o3p4q5r6
Revises: l6m7n8o9p0q1
Create Date: 2026-04-20

Tạo bảng notifications để lưu thông báo cho tất cả người dùng:
- Buyer: đơn hàng, khuyến mãi
- Seller: đơn mới, duyệt sản phẩm/bài viết, KYC
- Admin: hồ sơ seller, chờ duyệt, khiếu nại
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'm1n2o3p4q5r6'
down_revision = 'n2o3p4q5r6s7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),

        # Người nhận
        sa.Column('user_id', sa.Integer(), nullable=False),

        # Phân loại: ORDER | SYSTEM | PROMOTION | PAYMENT
        sa.Column('category', sa.String(length=20), nullable=False, server_default='SYSTEM'),

        # Nội dung thông báo
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),

        # Deep link khi tap vào thông báo
        sa.Column('action_url', sa.String(length=500), nullable=True),

        # Object liên quan (polymorphic)
        # ref_type: order | product | complaint | return | content | seller_profile
        sa.Column('ref_type', sa.String(length=50), nullable=True),
        sa.Column('ref_id', sa.Integer(), nullable=True),

        # Trạng thái đọc
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('read_at', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Indexes để truy vấn nhanh
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'], unique=False)
    op.create_index('idx_notifications_user_unread', 'notifications', ['user_id', 'is_read'], unique=False)
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'], unique=False)
    op.create_index('idx_notifications_ref', 'notifications', ['ref_type', 'ref_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_notifications_ref', table_name='notifications')
    op.drop_index('idx_notifications_created_at', table_name='notifications')
    op.drop_index('idx_notifications_user_unread', table_name='notifications')
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
