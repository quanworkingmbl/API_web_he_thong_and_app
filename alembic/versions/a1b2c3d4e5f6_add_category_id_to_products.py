"""Add category_id to products

Revision ID: a1b2c3d4e5f6
Revises: d709296f8c5c
Create Date: 2026-03-16 06:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd709296f8c5c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add category_id column to products table
    op.add_column('products', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_products_category_id', 'products', 'categories', ['category_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key constraint and category_id column
    op.drop_constraint('fk_products_category_id', 'products', type_='foreignkey')
    op.drop_column('products', 'category_id')
