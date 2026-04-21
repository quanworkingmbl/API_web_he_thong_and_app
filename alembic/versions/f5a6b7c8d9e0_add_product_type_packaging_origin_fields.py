"""add_product_type_packaging_approved_at_origin_fields

Revision ID: f5a6b7c8d9e0
Revises: b82aa2f98076
Create Date: 2026-04-13 17:00:00.000000

Changes:
- products: add product_type, packaging_type, approved_at; drop seo_title, seo_description, seo_keywords; change label to enum
- product_approvals: add checked_traceability
- product_origins: add facility_name, usage_instructions, storage_instructions, warnings; add unique constraint
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f5a6b7c8d9e0'
down_revision = 'b82aa2f98076'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── products table ────────────────────────────────────────────────────────

    # 1. Thêm product_type_enum và cột product_type
    product_type_enum = sa.Enum('AGRICULTURAL', 'HANDICRAFT', name='product_type_enum')
    product_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('products', sa.Column('product_type', product_type_enum, nullable=True))
    op.create_index('ix_products_product_type', 'products', ['product_type'])

    # 2. Thêm packaging_type
    op.add_column('products', sa.Column('packaging_type', sa.String(50), nullable=True))

    # 3. Thêm approved_at
    op.add_column('products', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))

    # 4. Xóa SEO fields (không cần nữa)
    try:
        op.drop_column('products', 'seo_title')
    except Exception:
        pass
    try:
        op.drop_column('products', 'seo_description')
    except Exception:
        pass
    try:
        op.drop_column('products', 'seo_keywords')
    except Exception:
        pass

    # 5. Migrate label column: String(50) → Enum
    # Tạo enum type trước (PostgreSQL), sau đó alter column
    # Vì có thể có data cũ, dùng USING cast
    try:
        # Tạo enum type mới
        label_enum = sa.Enum(
            'CLEAN_AGRICULTURE', 'TRADITIONAL_CRAFT', 'OCOP',
            name='productlabel'
        )
        label_enum.create(op.get_bind(), checkfirst=True)
        # Alter column (PostgreSQL)
        op.execute("""
            ALTER TABLE products 
            ALTER COLUMN label TYPE productlabel 
            USING label::productlabel
        """)
    except Exception:
        # MySQL / SQLite: ignore, String vẫn hoạt động với enum values
        pass

    # ── product_approvals table ───────────────────────────────────────────────
    op.add_column(
        'product_approvals',
        sa.Column('checked_traceability', sa.Boolean(), nullable=False, server_default='false')
    )

    # ── product_origins table ─────────────────────────────────────────────────
    op.add_column('product_origins', sa.Column('facility_name', sa.String(255), nullable=True))
    op.add_column('product_origins', sa.Column('usage_instructions', sa.Text(), nullable=True))
    op.add_column('product_origins', sa.Column('storage_instructions', sa.Text(), nullable=True))
    op.add_column('product_origins', sa.Column('warnings', sa.Text(), nullable=True))

    # Thêm unique constraint product_id (1 product → 1 origin)
    try:
        op.create_unique_constraint('uq_product_origins_product_id', 'product_origins', ['product_id'])
    except Exception:
        pass  # Đã có unique từ trước


def downgrade() -> None:
    # ── product_origins table ─────────────────────────────────────────────────
    try:
        op.drop_constraint('uq_product_origins_product_id', 'product_origins', type_='unique')
    except Exception:
        pass
    op.drop_column('product_origins', 'warnings')
    op.drop_column('product_origins', 'storage_instructions')
    op.drop_column('product_origins', 'usage_instructions')
    op.drop_column('product_origins', 'facility_name')

    # ── product_approvals table ───────────────────────────────────────────────
    op.drop_column('product_approvals', 'checked_traceability')

    # ── products table ────────────────────────────────────────────────────────
    op.add_column('products', sa.Column('seo_title', sa.String(255), nullable=True))
    op.add_column('products', sa.Column('seo_description', sa.Text(), nullable=True))
    op.add_column('products', sa.Column('seo_keywords', sa.Text(), nullable=True))

    op.drop_column('products', 'approved_at')
    op.drop_column('products', 'packaging_type')

    try:
        op.drop_index('ix_products_product_type', 'products')
    except Exception:
        pass
    op.drop_column('products', 'product_type')

    try:
        op.execute("DROP TYPE IF EXISTS product_type_enum")
    except Exception:
        pass
