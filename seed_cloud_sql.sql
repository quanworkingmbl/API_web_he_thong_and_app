-- ============================================================
-- SEED DATA cho CMS Cloud SQL
-- Chạy SAU KHI init_db.sql đã tạo xong các bảng
-- Password cho tất cả user: "password123"
-- Hash: $2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO
-- ============================================================

-- ── 1. ROLES ─────────────────────────────────────────────────
INSERT INTO roles (id, role_name, description) VALUES
(1, 'admin',           'Quản trị viên hệ thống'),
(2, 'content_manager', 'Quản lý nội dung'),
(3, 'seller',          'Người bán hàng'),
(4, 'customer',        'Khách hàng')
ON CONFLICT (id) DO NOTHING;

-- ── 2. USERS ─────────────────────────────────────────────────
-- Lưu ý: cột "status" là ENUM userstatus ('ACTIVE','SUSPENDED','BANNED')
INSERT INTO users (id, email, password_hash, name, gender, activated, type, status) VALUES
(1, 'admin@example.com',     '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Quản trị viên',  'male',   1, 'admin',           'ACTIVE'),
(2, 'content@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Nguyễn Văn An',  'male',   1, 'content_manager', 'ACTIVE'),
(3, 'seller1@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Trần Thị Bình',  'female', 1, 'seller',          'ACTIVE'),
(4, 'seller2@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Lê Văn Cường',   'male',   1, 'seller',          'ACTIVE'),
(5, 'customer1@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Hoàng Văn Em',   'male',   1, 'customer',        'ACTIVE'),
(6, 'customer2@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Đỗ Thị Phương',  'female', 1, 'customer',        'ACTIVE')
ON CONFLICT (id) DO NOTHING;

-- ── 3. USER_ROLES ────────────────────────────────────────────
-- Bảng user_roles có PRIMARY KEY (id), không có UNIQUE constraint trên (user_id, role_id)
-- nên dùng ON CONFLICT (id) DO NOTHING
INSERT INTO user_roles (id, user_id, role_id) VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 3),
(4, 4, 3),
(5, 5, 4),
(6, 6, 4)
ON CONFLICT (id) DO NOTHING;

-- ── 4. ORGANIZATIONS ─────────────────────────────────────────
INSERT INTO organizations (id, name, description) VALUES
(1, 'Nông trại Sạch Việt', 'Tổ chức nông sản sạch'),
(2, 'Hợp tác xã Xanh',     'HTX nông nghiệp xanh')
ON CONFLICT (id) DO NOTHING;

-- ── 5. CATEGORIES ────────────────────────────────────────────
INSERT INTO categories (id, name, slug, description, is_active) VALUES
(1, 'Rau củ quả',          'rau-cu-qua',        'Rau củ quả tươi sạch',          TRUE),
(2, 'Trái cây',            'trai-cay',           'Trái cây tươi các loại',         TRUE),
(3, 'Gạo & Ngũ cốc',      'gao-ngu-coc',        'Gạo, nếp và các loại ngũ cốc',  TRUE),
(4, 'Thực phẩm chế biến', 'thuc-pham-che-bien', 'Sản phẩm đã chế biến sẵn',      TRUE)
ON CONFLICT (id) DO NOTHING;

-- ── 6. PRODUCTS ──────────────────────────────────────────────
-- Schema thực tế: producer_id (FK -> users), category_id, status (ENUM productstatus), label (ENUM productlabel)
-- KHÔNG có: stock_quantity, seller_id, is_active (những cột này không tồn tại trong schema migration)
INSERT INTO products (id, name, description, price, producer_id, category_id, status, images) VALUES
(1, 'Rau muống sạch',    'Rau muống trồng hữu cơ, không thuốc trừ sâu',      15000, 3, 1, 'APPROVED', '["https://storage.googleapis.com/mbl-cms-media-bucket/sample/rau-muong.jpg"]'),
(2, 'Cà chua bi đỏ',    'Cà chua bi đỏ trồng trong nhà kính',               25000, 3, 1, 'APPROVED', '["https://storage.googleapis.com/mbl-cms-media-bucket/sample/ca-chua.jpg"]'),
(3, 'Xoài cát Hòa Lộc', 'Xoài cát Hòa Lộc ngọt thơm, đặc sản Tiền Giang', 45000, 4, 2, 'APPROVED', '["https://storage.googleapis.com/mbl-cms-media-bucket/sample/xoai.jpg"]'),
(4, 'Gạo ST25',          'Gạo ST25 - gạo ngon nhất thế giới',                35000, 4, 3, 'APPROVED', '["https://storage.googleapis.com/mbl-cms-media-bucket/sample/gao-st25.jpg"]'),
(5, 'Dưa hấu không hạt','Dưa hấu không hạt, ngọt mát',                     30000, 3, 2, 'APPROVED', '["https://storage.googleapis.com/mbl-cms-media-bucket/sample/dua-hau.jpg"]')
ON CONFLICT (id) DO NOTHING;

-- ── 7. SELLER_PROFILES ───────────────────────────────────────
INSERT INTO seller_profiles (id, user_id, business_name, business_type, verification_status) VALUES
(1, 3, 'Nông trại Bình An', 'HOUSEHOLD', 'VERIFIED'),
(2, 4, 'Vườn Rau Xanh',    'HOUSEHOLD', 'VERIFIED')
ON CONFLICT (id) DO NOTHING;

-- ── 8. SELLER_WALLETS ────────────────────────────────────────
INSERT INTO seller_wallets (id, seller_id, pending_balance, available_balance, total_withdrawn) VALUES
(1, 3, 0.00, 500000.00, 0.00),
(2, 4, 0.00, 750000.00, 0.00)
ON CONFLICT (id) DO NOTHING;

-- ── 9. CARTS ─────────────────────────────────────────────────
INSERT INTO carts (id, user_id) VALUES
(1, 5),
(2, 6)
ON CONFLICT (id) DO NOTHING;

-- ── 10. ORDERS ───────────────────────────────────────────────
-- Schema yêu cầu: subtotal, shipping_fee, discount_amount, total_amount,
--   platform_fee_percentage, platform_fee_amount, seller_amount đều NOT NULL
INSERT INTO orders (
    id, order_number, customer_id, seller_id, status,
    customer_name, customer_phone,
    shipping_address,
    payment_method, payment_status,
    subtotal, shipping_fee, discount_amount, total_amount,
    platform_fee_percentage, platform_fee_amount, seller_amount
) VALUES
(1, 'ORD-202605-001', 5, 3, 'DELIVERED',
    'Hoàng Văn Em',  '0901234567',
    'Số 10 Ngõ 5, Phố Huế, Hà Nội',
    'COD', 'PAID',
    115000, 0, 0, 115000,
    5.00, 5750, 109250),
(2, 'ORD-202605-002', 6, 4, 'PENDING',
    'Đỗ Thị Phương', '0912345678',
    'Số 20 Đường Lê Lợi, TP.HCM',
    'BANK_TRANSFER', 'PENDING',
    75000, 0, 0, 75000,
    5.00, 3750, 71250)
ON CONFLICT (id) DO NOTHING;

-- ── 11. ORDER_ITEMS ──────────────────────────────────────────
INSERT INTO order_items (id, order_id, product_id, product_name, quantity, unit_price, total_price) VALUES
(1, 1, 1, 'Rau muống sạch',    2, 15000, 30000),
(2, 1, 2, 'Cà chua bi đỏ',    1, 25000, 25000),
(3, 1, 4, 'Gạo ST25',          1, 35000, 35000),
(4, 2, 3, 'Xoài cát Hòa Lộc', 1, 45000, 45000),
(5, 2, 5, 'Dưa hấu không hạt',1, 30000, 30000)
ON CONFLICT (id) DO NOTHING;

-- ── 12. CONTENTS (Bài viết) ──────────────────────────────────
INSERT INTO contents (id, title, content, content_type, author_id, status, is_active, images) VALUES
(1, 'Bí quyết trồng rau sạch tại nhà',
   'Trồng rau sạch tại nhà không khó nếu bạn biết cách chọn đất và phân bón phù hợp. Bài viết chia sẻ kinh nghiệm 5 năm làm nông nghiệp hữu cơ.',
   'POST', 3, 'APPROVED', TRUE, '["https://storage.googleapis.com/mbl-cms-media-bucket/sample/rau-muong.jpg"]'),
(2, 'Vì sao nên chọn gạo ST25?',
   'Gạo ST25 được vinh danh là gạo ngon nhất thế giới năm 2019. Tìm hiểu về quy trình canh tác đặc biệt tạo nên hạt gạo thơm ngon này.',
   'POST', 4, 'APPROVED', TRUE, '["https://storage.googleapis.com/mbl-cms-media-bucket/sample/gao-st25.jpg"]')
ON CONFLICT (id) DO NOTHING;

-- ── 13. Reset sequences ───────────────────────────────────────
SELECT setval('roles_id_seq',         (SELECT MAX(id) FROM roles),          TRUE);
SELECT setval('users_id_seq',         (SELECT MAX(id) FROM users),          TRUE);
SELECT setval('user_roles_id_seq',    (SELECT MAX(id) FROM user_roles),     TRUE);
SELECT setval('organizations_id_seq', (SELECT MAX(id) FROM organizations),  TRUE);
SELECT setval('categories_id_seq',    (SELECT MAX(id) FROM categories),     TRUE);
SELECT setval('products_id_seq',      (SELECT MAX(id) FROM products),       TRUE);
SELECT setval('seller_profiles_id_seq',(SELECT MAX(id) FROM seller_profiles),TRUE);
SELECT setval('seller_wallets_id_seq',(SELECT MAX(id) FROM seller_wallets), TRUE);
SELECT setval('carts_id_seq',         (SELECT MAX(id) FROM carts),          TRUE);
SELECT setval('orders_id_seq',        (SELECT MAX(id) FROM orders),         TRUE);
SELECT setval('order_items_id_seq',   (SELECT MAX(id) FROM order_items),    TRUE);
SELECT setval('contents_id_seq',      (SELECT MAX(id) FROM contents),       TRUE);

-- ============================================================
-- DONE! Seed data inserted successfully.
-- Login: admin@example.com / password123
-- ============================================================
