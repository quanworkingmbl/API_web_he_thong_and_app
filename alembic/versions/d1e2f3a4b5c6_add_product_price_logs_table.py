"""add_product_price_logs_table

Revision ID: d1e2f3a4b5c6
Revises: c9d8e7f6a5b4
Create Date: 2026-04-05 08:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = 'c9d8e7f6a5b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create product_price_logs table
    op.create_table(
        'product_price_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('old_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('new_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_product_price_logs_id', 'product_price_logs', ['id'])
    op.create_index('ix_product_price_logs_product_id', 'product_price_logs', ['product_id'])


def downgrade() -> None:
    op.drop_index('ix_product_price_logs_product_id', table_name='product_price_logs')
    op.drop_index('ix_product_price_logs_id', table_name='product_price_logs')
    op.drop_table('product_price_logs')
