-- ============================================================
-- PATCH 3: Fix lỗi 500 trên GCP Cloud Run
-- Nguyên nhân: Model Python có các cột chưa tồn tại trong Cloud SQL
--
-- Các lỗi đang gặp:
--   1. psycopg2.errors.UndefinedColumn: column promotions.applicable_to
--   2. psycopg2.errors.UndefinedColumn: column orders.currency
--   3. psycopg2.errors.UndefinedColumn: column orders.wallet_credited
--
-- CÁCH CHẠY:
--   Vào GCP Console → Cloud SQL Studio → chọn database → chạy script này
-- ============================================================

-- ── 1. PROMOTIONS: thêm các cột còn thiếu ──────────────────────
-- applicable_to: xác định phạm vi áp dụng khuyến mãi (ALL/SELLER/PRODUCT/CATEGORY)
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS applicable_to VARCHAR(50) DEFAULT 'ALL';

-- seller_id cho promotions (nếu chưa có - promotion dành riêng cho 1 seller)
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS seller_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_promotions_seller_id ON promotions (seller_id);

-- applicable_product_ids: JSON array các product_id được áp dụng
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS applicable_product_ids TEXT;

-- applicable_category_ids: JSON array các category_id được áp dụng
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS applicable_category_ids TEXT;

-- user_conditions: JSON điều kiện người dùng (first_order, min_purchases, v.v.)
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS user_conditions TEXT;

-- is_public: hiển thị cho consumer hay không
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT true;

-- created_by: admin/seller tạo promotion
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- usage_limit_per_user: giới hạn dùng mỗi người
ALTER TABLE promotions ADD COLUMN IF NOT EXISTS usage_limit_per_user INTEGER;

-- ── 2. ORDERS: thêm các cột còn thiếu ──────────────────────────
-- currency: đơn vị tiền tệ (VND, USD, ...)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'VND' NOT NULL;

-- wallet_credited: flag chống double-credit tiền vào ví seller
ALTER TABLE orders ADD COLUMN IF NOT EXISTS wallet_credited BOOLEAN DEFAULT false NOT NULL;
CREATE INDEX IF NOT EXISTS ix_orders_wallet_credited ON orders (wallet_credited);

-- channel: kênh đặt hàng (WEB, MOBILE_APP, THIRD_PARTY)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS channel VARCHAR(50);

-- coupon_code: mã coupon đã sử dụng
ALTER TABLE orders ADD COLUMN IF NOT EXISTS coupon_code VARCHAR(50);

-- tax_breakdown: JSON breakdown của thuế
ALTER TABLE orders ADD COLUMN IF NOT EXISTS tax_breakdown TEXT;

-- fee_breakdown: JSON breakdown của phí
ALTER TABLE orders ADD COLUMN IF NOT EXISTS fee_breakdown TEXT;

-- ── 3. Kiểm tra kết quả ────────────────────────────────────────
-- Sau khi chạy, verify bằng các lệnh sau:
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'promotions' ORDER BY column_name;
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'orders' ORDER BY column_name;

-- ============================================================
-- DONE! Patch 3 applied. Restart Cloud Run service nếu cần.
-- ============================================================
