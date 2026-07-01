"""return_seller_flow – thêm trạng thái SELLER_APPROVED/REJECTED và cột seller_note/handled

Revision ID: z1a2b3c4d5e6
Revises: rp_001_add_return_policy_to_products
Create Date: 2026-06-24 19:00:00

Thay đổi:
- Thêm 2 giá trị enum mới vào returnstatus: SELLER_APPROVED, SELLER_REJECTED
- Thêm 3 cột vào bảng return_requests:
    seller_note           TEXT         nullable – ghi chú của seller khi xử lý
    seller_handled_by     INTEGER FK   nullable – seller đã xử lý
    seller_handled_at     TIMESTAMPTZ  nullable – thời điểm seller xử lý
"""
from alembic import op
import sqlalchemy as sa

revision = 'z1a2b3c4d5e6'
down_revision = ('x1y2z3a4b5c6', 'rp_001')  # merge cả 2 head hiện tại
branch_labels = None
depends_on = None


def upgrade() -> None:
    from alembic import context

    # ── Thêm 2 giá trị enum mới vào returnstatus ─────────────────────────────
    if not context.is_offline_mode():
        for value in ('SELLER_APPROVED', 'SELLER_REJECTED'):
            try:
                with op.get_context().autocommit_block():
                    op.execute(f"ALTER TYPE returnstatus ADD VALUE IF NOT EXISTS '{value}'")
            except Exception:
                pass  # Đã tồn tại → bỏ qua

    # ── Thêm cột seller_note ──────────────────────────────────────────────────
    op.add_column(
        'return_requests',
        sa.Column('seller_note', sa.Text(), nullable=True)
    )

    # ── Thêm cột seller_handled_by ────────────────────────────────────────────
    op.add_column(
        'return_requests',
        sa.Column('seller_handled_by', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_return_requests_seller_handled_by',
        'return_requests', 'users',
        ['seller_handled_by'], ['id'],
        ondelete='SET NULL'
    )

    # ── Thêm cột seller_handled_at ────────────────────────────────────────────
    op.add_column(
        'return_requests',
        sa.Column('seller_handled_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_constraint('fk_return_requests_seller_handled_by', 'return_requests', type_='foreignkey')
    op.drop_column('return_requests', 'seller_handled_at')
    op.drop_column('return_requests', 'seller_handled_by')
    op.drop_column('return_requests', 'seller_note')
    # Không thể xóa giá trị enum trong PostgreSQL (ALTER TYPE ... DROP VALUE không hỗ trợ)
