"""Add avatar_url to users table

Revision ID: q2r3s4t5u6v7
Revises: p1q2r3s4t5u6
Create Date: 2026-04-20
"""

from alembic import op
import sqlalchemy as sa

revision = 'q2r3s4t5u6v7'
down_revision = 'p1q2r3s4t5u6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Thêm cột avatar_url vào bảng users để lưu URL ảnh đại diện
    op.add_column(
        'users',
        sa.Column(
            'avatar_url',
            sa.String(length=512),
            nullable=True,
            comment='URL ảnh đại diện user lưu trên Supabase Storage'
        )
    )


def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
