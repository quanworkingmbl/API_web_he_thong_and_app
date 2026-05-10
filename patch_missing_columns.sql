-- ============================================================
-- PATCH: Thêm các cột còn thiếu vào schema hiện tại
-- Chạy SAU KHI init_db.sql đã thành công
-- Dùng IF NOT EXISTS để an toàn khi chạy lại
-- ============================================================

-- ── PRODUCTS: Các cột model Python yêu cầu nhưng chưa có trong DB ──

-- Đổi tên producer_id → seller_id (nếu cần)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='products' AND column_name='producer_id'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='products' AND column_name='seller_id'
    ) THEN
        ALTER TABLE products RENAME COLUMN producer_id TO seller_id;
    END IF;
END $$;

-- seller_id index
CREATE INDEX IF NOT EXISTS ix_products_seller_id ON products (seller_id);

-- Tạo bảng stores (nếu chưa có) - cần thiết cho FK
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL NOT NULL,
    seller_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    logo_url TEXT,
    banner_url TEXT,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(seller_id) REFERENCES users (id)
);
CREATE INDEX IF NOT EXISTS ix_stores_id ON stores (id);

-- store_id trên products
ALTER TABLE products ADD COLUMN IF NOT EXISTS store_id INTEGER REFERENCES stores(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_products_store_id ON products (store_id);

-- SKU, slug cho products
ALTER TABLE products ADD COLUMN IF NOT EXISTS sku VARCHAR(100) UNIQUE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS slug VARCHAR(255) UNIQUE;
CREATE INDEX IF NOT EXISTS ix_products_sku ON products (sku);
CREATE INDEX IF NOT EXISTS ix_products_slug ON products (slug);

-- Physical properties
ALTER TABLE products ADD COLUMN IF NOT EXISTS weight INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS dimensions TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS unit VARCHAR(20);

-- Tax
ALTER TABLE products ADD COLUMN IF NOT EXISTS vat_rate NUMERIC(5,2);

-- Visibility
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL;
ALTER TABLE products ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS unpublished_at TIMESTAMP WITH TIME ZONE;

-- Stock quantity
ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0 NOT NULL;

CREATE INDEX IF NOT EXISTS ix_products_is_active ON products (is_active);

-- ── ADDRESSES TABLE (cần cho seller_profiles.pickup_address_id) ──
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL NOT NULL,
    user_id INTEGER,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    address_line TEXT NOT NULL,
    ward VARCHAR(100),
    ward_code VARCHAR(20),
    district VARCHAR(100),
    district_code VARCHAR(20),
    province VARCHAR(100),
    province_code VARCHAR(20),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_addresses_id ON addresses (id);
CREATE INDEX IF NOT EXISTS ix_addresses_user_id ON addresses (user_id);

-- seller_profiles: pickup_address_id
ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS pickup_address_id INTEGER REFERENCES addresses(id) ON DELETE SET NULL;

-- ── ORDER_ITEMS: store_id, package_id, variant_id ──

-- Bảng order_packages
CREATE TABLE IF NOT EXISTS order_packages (
    id SERIAL NOT NULL,
    order_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    store_id INTEGER,
    subtotal NUMERIC(15,2) NOT NULL,
    shipping_fee NUMERIC(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(30),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(seller_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS ix_order_packages_id ON order_packages (id);

ALTER TABLE order_items ADD COLUMN IF NOT EXISTS store_id INTEGER REFERENCES stores(id) ON DELETE SET NULL;
ALTER TABLE order_items ADD COLUMN IF NOT EXISTS package_id INTEGER REFERENCES order_packages(id) ON DELETE SET NULL;

-- ── PRODUCT_VARIANTS TABLE ──
DO $$ BEGIN
    CREATE TYPE variantstatus AS ENUM ('ACTIVE', 'INACTIVE', 'OUT_OF_STOCK');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS product_variants (
    id SERIAL NOT NULL,
    product_id INTEGER NOT NULL,
    sku VARCHAR(100) UNIQUE,
    name VARCHAR(255),
    price NUMERIC(15,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0 NOT NULL,
    attributes TEXT,
    images TEXT,
    is_active BOOLEAN DEFAULT true NOT NULL,
    weight INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_product_variants_id ON product_variants (id);
CREATE INDEX IF NOT EXISTS ix_product_variants_product_id ON product_variants (product_id);

-- variant_id trên order_items và cart_items
ALTER TABLE order_items ADD COLUMN IF NOT EXISTS variant_id INTEGER REFERENCES product_variants(id) ON DELETE SET NULL;
-- cart_items đã có variant_id từ migration d3e4f5a6b7c8, thêm FK nếu chưa có
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_cart_items_variant_id'
    ) THEN
        ALTER TABLE cart_items ADD CONSTRAINT fk_cart_items_variant_id
            FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ── PAYMENT_METHODS TABLE ──
CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    config TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_payment_methods_id ON payment_methods (id);

-- payments: payment_method_id
ALTER TABLE payments ADD COLUMN IF NOT EXISTS payment_method_id INTEGER REFERENCES payment_methods(id) ON DELETE SET NULL;

-- ── REVIEWS: thêm cột còn thiếu ──
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS order_item_id INTEGER;
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS images TEXT;
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;

-- ============================================================
-- DONE! Patch applied successfully.
-- ============================================================
