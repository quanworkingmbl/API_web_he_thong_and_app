"""Add PLATFORM_CREDITS to paymentmethod enum

Revision ID: r3s4t5u6v7w8
Revises: q2r3s4t5u6v7
Create Date: 2026-04-20
"""

from alembic import op
import sqlalchemy as sa

revision = 'r3s4t5u6v7w8'
down_revision = 'q2r3s4t5u6v7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL: thêm giá trị mới vào ENUM type đã tồn tại
    # Cú pháp: ALTER TYPE <type_name> ADD VALUE IF NOT EXISTS '<value>';
    op.execute("ALTER TYPE paymentmethod ADD VALUE IF NOT EXISTS 'PLATFORM_CREDITS'")


def downgrade() -> None:
    # PostgreSQL không hỗ trợ xóa giá trị khỏi ENUM
    # Muốn downgrade thực sự cần recreate enum — skip ở đây
    pass
