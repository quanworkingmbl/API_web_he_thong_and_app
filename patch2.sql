-- ============================================================
-- PATCH 2 - Remaining 42 missing columns
-- Paste vào Cloud SQL Studio rồi bấm Run
-- ============================================================

ALTER TABLE payment_providers ADD COLUMN IF NOT EXISTS api_endpoint TEXT;
ALTER TABLE payment_providers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

ALTER TABLE permissions ADD COLUMN IF NOT EXISTS code VARCHAR(100);
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS module VARCHAR(100);
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

ALTER TABLE provinces ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE districts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE wards ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS provider VARCHAR(50);
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS service_code VARCHAR(50);
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS origin_province VARCHAR(20);
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS destination_province VARCHAR(20);
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS base_rate NUMERIC(10,2) DEFAULT 0;
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS per_kg_rate NUMERIC(10,2) DEFAULT 0;
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS sla_days INTEGER;
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE shipping_rates ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

ALTER TABLE shipping_services ADD COLUMN IF NOT EXISTS service_code VARCHAR(50);
ALTER TABLE shipping_services ADD COLUMN IF NOT EXISTS service_name VARCHAR(255);
ALTER TABLE shipping_services ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE shipping_services ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

ALTER TABLE role_permissions ADD COLUMN IF NOT EXISTS role_id INTEGER;

ALTER TABLE order_adjustments ADD COLUMN IF NOT EXISTS created_by INTEGER;
ALTER TABLE order_promotions ADD COLUMN IF NOT EXISTS seller_id INTEGER;
ALTER TABLE promotion_usages ADD COLUMN IF NOT EXISTS discount_amount NUMERIC(12,2) DEFAULT 0;

ALTER TABLE product_options ADD COLUMN IF NOT EXISTS option_name VARCHAR(100);

ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS variant_id INTEGER;
ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS reference_type VARCHAR(50);
ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS reference_id INTEGER;
ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE inventory_movements ADD COLUMN IF NOT EXISTS created_by INTEGER;

ALTER TABLE product_media ADD COLUMN IF NOT EXISTS variant_id INTEGER;
ALTER TABLE product_media ADD COLUMN IF NOT EXISTS url TEXT;
ALTER TABLE product_media ADD COLUMN IF NOT EXISTS alt_text VARCHAR(255);
ALTER TABLE product_media ADD COLUMN IF NOT EXISTS is_primary BOOLEAN DEFAULT FALSE;

ALTER TABLE product_option_values ADD COLUMN IF NOT EXISTS variant_id INTEGER;
ALTER TABLE product_option_values ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

ALTER TABLE stock_reservations ADD COLUMN IF NOT EXISTS variant_id INTEGER;
ALTER TABLE stock_reservations ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'ACTIVE';
ALTER TABLE stock_reservations ADD COLUMN IF NOT EXISTS reserved_at TIMESTAMP DEFAULT NOW();
ALTER TABLE stock_reservations ADD COLUMN IF NOT EXISTS released_at TIMESTAMP;

SELECT 'PATCH 2 APPLIED SUCCESSFULLY' AS status;
