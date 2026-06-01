"""merge deposit wallet and product_change_logs heads

Revision ID: w2x3y4z5a6b7
Revises: u1v2w3x4y5z6, v1w2x3y4z5a6
Create Date: 2026-06-01

Hai nhánh tách từ t1u2v3w4x5y6 khiến `alembic upgrade head` fail trên Cloud Build,
nên migration deposit_transactions không được áp dụng lên production.
"""

from alembic import op

revision = "w2x3y4z5a6b7"
down_revision = ("u1v2w3x4y5z6", "v1w2x3y4z5a6")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
