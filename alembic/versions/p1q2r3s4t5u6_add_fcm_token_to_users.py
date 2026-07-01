"""Add fcm_token to users table

Revision ID: p1q2r3s4t5u6
Revises: m1n2o3p4q5r6
Create Date: 2026-04-20
"""

from alembic import op
import sqlalchemy as sa

revision = 'p1q2r3s4t5u6'
down_revision = 'm1n2o3p4q5r6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Thêm cột fcm_token vào bảng users để lưu Firebase Cloud Messaging token
    op.add_column(
        'users',
        sa.Column('fcm_token', sa.String(length=512), nullable=True, comment='Firebase Cloud Messaging device token')
    )


def downgrade() -> None:
    op.drop_column('users', 'fcm_token')
