-- ============================================================
-- Patch: Thêm các cột còn thiếu trong bảng orders
-- Áp dụng cho Cloud SQL production khi có missing columns
-- ============================================================

-- Thêm wallet_credited nếu chưa có
ALTER TABLE orders ADD COLUMN IF NOT EXISTS wallet_credited BOOLEAN NOT NULL DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS ix_orders_wallet_credited ON orders(wallet_credited);

-- Thêm các cột liên quan đến settlement nếu chưa có (từ patch trước có thể còn thiếu)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS seller_amount NUMERIC(12,2);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS platform_fee NUMERIC(12,2);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS settlement_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE orders ADD COLUMN IF NOT EXISTS settled_at TIMESTAMP WITH TIME ZONE;

-- ============================================================
-- Kiểm tra kết quả
-- ============================================================
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'orders'
  AND column_name IN ('wallet_credited', 'seller_amount', 'platform_fee', 'settlement_status', 'settled_at')
ORDER BY column_name;
