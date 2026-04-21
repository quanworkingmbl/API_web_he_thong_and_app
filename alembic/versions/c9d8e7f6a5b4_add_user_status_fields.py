"""add_user_status_fields

Revision ID: c9d8e7f6a5b4
Revises: 944b201b5ae7
Create Date: 2026-04-05 08:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9d8e7f6a5b4'
down_revision = '944b201b5ae7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add status enum column (default: ACTIVE)
    op.add_column('users', sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'BANNED', name='userstatus'), nullable=False, server_default='ACTIVE'))
    
    # Add status_reason column (nullable)
    op.add_column('users', sa.Column('status_reason', sa.Text(), nullable=True))
    
    # Add status_expire_at column (nullable)
    op.add_column('users', sa.Column('status_expire_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Drop columns
    op.drop_column('users', 'status_expire_at')
    op.drop_column('users', 'status_reason')
    op.drop_column('users', 'status')
    
    # Drop enum type (PostgreSQL specific)
    op.execute('DROP TYPE IF EXISTS userstatus')
