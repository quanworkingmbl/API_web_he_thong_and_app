-- ============================================================
-- PATCH 2: Thêm cột còn thiếu cho payments, returns, users
-- Chạy trong Cloud SQL Studio (database: postgres)
-- ============================================================

-- ── PAYMENTS: cột model có nhưng DB chưa có ──
ALTER TABLE payments ADD COLUMN IF NOT EXISTS gateway_transaction_id VARCHAR(255);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS payment_channel VARCHAR(50);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'VND' NOT NULL;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS amount_from_gateway NUMERIC(15,2);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS amount_mismatch BOOLEAN DEFAULT false NOT NULL;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS card_brand VARCHAR(50);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS bank_code VARCHAR(50);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS failure_code VARCHAR(50);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS failure_message TEXT;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS gateway_response TEXT;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS refunded_amount NUMERIC(15,2);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS refund_note TEXT;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS refunded_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS ix_payments_gateway_transaction_id ON payments (gateway_transaction_id);

-- ── RETURN_REQUESTS: cột model có nhưng DB chưa có ──
ALTER TABLE return_requests ADD COLUMN IF NOT EXISTS order_item_id INTEGER REFERENCES order_items(id) ON DELETE SET NULL;
ALTER TABLE return_requests ADD COLUMN IF NOT EXISTS refund_amount VARCHAR(20);
ALTER TABLE return_requests ADD COLUMN IF NOT EXISTS refund_method VARCHAR(50);
ALTER TABLE return_requests ADD COLUMN IF NOT EXISTS seller_return_address_id INTEGER;
ALTER TABLE return_requests ADD COLUMN IF NOT EXISTS return_shipping_code VARCHAR(100);
ALTER TABLE return_requests ADD COLUMN IF NOT EXISTS approved_by INTEGER REFERENCES users(id);
ALTER TABLE return_requests ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS ix_return_requests_order_item_id ON return_requests (order_item_id);

-- ── USERS: kiểm tra cột date_of_birth, fcm_token, avatar_url ──
-- (Đã thêm qua init_db.sql migrations k5l6m7n8o9p0, p1q2r3s4t5u6, q2r3s4t5u6v7)
-- Thêm lại an toàn nếu chưa có
ALTER TABLE users ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS fcm_token VARCHAR(512);
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(512);

-- ── PRODUCTS: soft delete support ──
-- Model dùng is_active để ẩn sản phẩm (soft delete)
-- Đảm bảo cột tồn tại (đã thêm trong patch 1, chạy lại an toàn)
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL;
ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0 NOT NULL;

-- ── ORDERS: is_active soft delete ──
-- (Đã có trong init_db.sql migration a0b1c2d3e4f5)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL;
CREATE INDEX IF NOT EXISTS ix_orders_is_active ON orders (is_active);

-- ── SETTLEMENT ITEMS TABLE (cần cho payments/reconciliation) ──
CREATE TABLE IF NOT EXISTS settlement_items (
    id SERIAL NOT NULL,
    settlement_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    order_item_id INTEGER,
    seller_amount NUMERIC(15,2) NOT NULL,
    platform_fee NUMERIC(15,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY(settlement_id) REFERENCES settlements(id) ON DELETE CASCADE,
    FOREIGN KEY(order_id) REFERENCES orders(id)
);
CREATE INDEX IF NOT EXISTS ix_settlement_items_id ON settlement_items (id);
CREATE INDEX IF NOT EXISTS ix_settlement_items_settlement_id ON settlement_items (settlement_id);

-- ============================================================
-- DONE! Patch 2 applied.
-- ============================================================
