"""add promotion approval and flash sale fields

Revision ID: t1u2v3w4x5y6
Revises: s1t2u3v4w5x6
Create Date: 2026-05-26

Thêm:
  - promotionstatus ENUM: giá trị PENDING
  - promotions.is_flash_sale  (Boolean)
  - promotions.approved_by    (Integer FK → users.id)
  - promotions.approved_at    (DateTime)
  - promotions.rejection_reason (Text)

Lưu ý PostgreSQL:
  ALTER TYPE ... ADD VALUE không thể chạy trong transaction.
  → Dùng autocommit_block() cho phần ENUM, batch_alter cho phần cột.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 't1u2v3w4x5y6'
down_revision = 's1t2u3v4w5x6'
branch_labels = None
depends_on = None


def upgrade():
    # ── 1. Thêm giá trị PENDING vào Enum promotionstatus ─────────────────────
    # PHẢI chạy ngoài transaction (PostgreSQL constraint)
    # autocommit_block() commit transaction hiện tại, chạy ALTER TYPE, rồi bắt transaction mới.
    from alembic import context
    if not context.is_offline_mode():
        try:
            with op.get_context().autocommit_block():
                op.execute(
                    "ALTER TYPE promotionstatus ADD VALUE IF NOT EXISTS 'PENDING'"
                )
        except Exception as e:
            # Bỏ qua nếu value đã tồn tại (PostgreSQL < 9.6 không có IF NOT EXISTS)
            print(f"[migration] Skipped ENUM alter (likely already exists): {e}")

    # ── 2. Thêm các cột mới vào bảng promotions ──────────────────────────────
    # batch_alter_table an toàn khi chạy trên DB đang có data
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        # Flash Sale flag
        batch_op.add_column(
            sa.Column('is_flash_sale', sa.Boolean(), server_default=sa.text('false'), nullable=False)
        )
        # Admin approval
        batch_op.add_column(
            sa.Column('approved_by', sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column('rejection_reason', sa.Text(), nullable=True)
        )
        # FK: approved_by → users.id
        batch_op.create_foreign_key(
            'fk_promotions_approved_by',
            'users',
            ['approved_by'], ['id'],
            ondelete='SET NULL'
        )
        # Index để query flash sales nhanh
        batch_op.create_index('ix_promotions_is_flash_sale', ['is_flash_sale'])


def downgrade():
    with op.batch_alter_table('promotions', schema=None) as batch_op:
        batch_op.drop_index('ix_promotions_is_flash_sale')
        batch_op.drop_constraint('fk_promotions_approved_by', type_='foreignkey')
        batch_op.drop_column('rejection_reason')
        batch_op.drop_column('approved_at')
        batch_op.drop_column('approved_by')
        batch_op.drop_column('is_flash_sale')

    # Lưu ý: PostgreSQL KHÔNG hỗ trợ xóa ENUM value đã add.
    # Nếu cần rollback hoàn toàn, phải DROP và RECREATE type (nguy hiểm với data).
    # → Bỏ qua downgrade cho ENUM PENDING.
