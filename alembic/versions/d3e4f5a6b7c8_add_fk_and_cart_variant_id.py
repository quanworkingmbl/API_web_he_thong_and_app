"""add_fk_store_variant_cart_and_cleanup_orphans

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-04-05

- Thêm cart_items.variant_id (FK product_variants)
- Gắn FK: products.store_id, order_items (store_id, package_id, variant_id),
  payments.payment_method_id, seller_profiles.pickup_address_id
- Xóa tham chiếu orphan trước khi tạo FK (SET NULL logic đã có ở model)
"""

from alembic import op
import sqlalchemy as sa


revision = "d3e4f5a6b7c8"
down_revision = "c2d3e4f5a6b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # --- cart_items.variant_id ---
    op.add_column(
        "cart_items",
        sa.Column("variant_id", sa.Integer(), nullable=True),
    )
    op.create_index(op.f("ix_cart_items_variant_id"), "cart_items", ["variant_id"], unique=False)

    # --- Dọn orphan trước khi ALTER ---
    conn.execute(
        sa.text("""
            UPDATE products SET store_id = NULL
            WHERE store_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM stores s WHERE s.id = products.store_id);
        """)
    )
    conn.execute(
        sa.text("""
            UPDATE order_items SET store_id = NULL
            WHERE store_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM stores s WHERE s.id = order_items.store_id);
        """)
    )
    conn.execute(
        sa.text("""
            UPDATE order_items SET package_id = NULL
            WHERE package_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM order_packages p WHERE p.id = order_items.package_id);
        """)
    )
    conn.execute(
        sa.text("""
            UPDATE order_items SET variant_id = NULL
            WHERE variant_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM product_variants v WHERE v.id = order_items.variant_id);
        """)
    )
    conn.execute(
        sa.text("""
            UPDATE payments SET payment_method_id = NULL
            WHERE payment_method_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM payment_methods pm WHERE pm.id = payments.payment_method_id);
        """)
    )
    conn.execute(
        sa.text("""
            UPDATE seller_profiles SET pickup_address_id = NULL
            WHERE pickup_address_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM addresses a WHERE a.id = seller_profiles.pickup_address_id);
        """)
    )

    # --- Foreign keys ---
    op.create_foreign_key(
        "fk_products_store_id",
        "products",
        "stores",
        ["store_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_order_items_store_id",
        "order_items",
        "stores",
        ["store_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_order_items_package_id",
        "order_items",
        "order_packages",
        ["package_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_order_items_variant_id",
        "order_items",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_payments_payment_method_id",
        "payments",
        "payment_methods",
        ["payment_method_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_seller_profiles_pickup_address_id",
        "seller_profiles",
        "addresses",
        ["pickup_address_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_cart_items_variant_id",
        "cart_items",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_cart_items_variant_id", "cart_items", type_="foreignkey")
    op.drop_constraint("fk_seller_profiles_pickup_address_id", "seller_profiles", type_="foreignkey")
    op.drop_constraint("fk_payments_payment_method_id", "payments", type_="foreignkey")
    op.drop_constraint("fk_order_items_variant_id", "order_items", type_="foreignkey")
    op.drop_constraint("fk_order_items_package_id", "order_items", type_="foreignkey")
    op.drop_constraint("fk_order_items_store_id", "order_items", type_="foreignkey")
    op.drop_constraint("fk_products_store_id", "products", type_="foreignkey")

    op.drop_index(op.f("ix_cart_items_variant_id"), table_name="cart_items")
    op.drop_column("cart_items", "variant_id")
