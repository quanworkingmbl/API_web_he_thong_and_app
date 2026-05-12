-- patch_vat.sql
-- Thêm cột vat_amount vào bảng orders để track tổng VAT của đơn hàng

ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS vat_amount NUMERIC(10, 2) NOT NULL DEFAULT 0;

-- Cập nhật công thức: seller_amount mới sẽ = subtotal - platform_fee - vat_amount
-- Đơn cũ giữ nguyên seller_amount (VAT = 0, tức exempt), chỉ đơn mới được tính VAT.

COMMENT ON COLUMN orders.vat_amount IS
  'Tổng VAT của đơn hàng – tính từ vat_rate của từng sản phẩm (VAT included trong giá niêm yết). Nền tảng giữ VAT để nộp thuế thay seller.';
