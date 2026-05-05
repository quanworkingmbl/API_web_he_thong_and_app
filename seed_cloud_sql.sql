-- ============================================================================
-- SEED DATA - Cloud SQL PostgreSQL (Google Cloud)
-- Chạy file này sau khi Alembic migrate xong (tables đã tồn tại)
-- Password tất cả users: "password123"
-- ============================================================================

-- ############################################################################
-- 1. ORGANIZATIONS
-- ############################################################################
INSERT INTO organizations (id, name, description) VALUES
(1, 'Hợp tác xã Nông nghiệp Hà Nội',     'HTX chuyên sản xuất nông sản sạch tại Hà Nội'),
(2, 'Làng nghề truyền thống Bát Tràng',    'Làng nghề gốm sứ truyền thống Bát Tràng'),
(3, 'Hội nông dân Đà Nẵng',                'Tổ chức hỗ trợ nông dân phát triển sản xuất'),
(4, 'Hiệp hội Thủ công mỹ nghệ Việt Nam', 'Hiệp hội quản lý và phát triển nghề thủ công mỹ nghệ')
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 2. ROLES
-- ############################################################################
INSERT INTO roles (id, role_name, description) VALUES
(1, 'admin',           'Quản trị viên hệ thống'),
(2, 'content_manager', 'Quản lý nội dung'),
(3, 'seller',          'Người bán hàng/Nhà sản xuất'),
(4, 'customer',        'Khách hàng')
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 3. USERS  (password: "password123")
-- ############################################################################
INSERT INTO users (id, email, password_hash, name, gender, activated, type, status) VALUES
(1, 'admin@example.com',     '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Quản trị viên', 'male',   1, 'admin',           'ACTIVE'),
(2, 'content@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Nguyễn Văn An', 'male',   1, 'content_manager', 'ACTIVE'),
(3, 'seller1@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Trần Thị Bình', 'female', 1, 'seller',          'ACTIVE'),
(4, 'seller2@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Lê Văn Cường',  'male',   1, 'seller',          'ACTIVE'),
(5, 'customer1@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Hoàng Văn Em',  'male',   1, 'customer',        'ACTIVE'),
(6, 'customer2@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Đỗ Thị Phương', 'female', 1, 'customer',        'ACTIVE')
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 4. USER_ROLES
-- ############################################################################
INSERT INTO user_roles (user_id, role_id) VALUES
(1,1),(2,2),(3,3),(4,3),(5,4),(6,4)
ON CONFLICT DO NOTHING;

-- ############################################################################
-- 5. USER_ORGANIZATIONS
-- ############################################################################
INSERT INTO user_organizations (user_id, organization_id) VALUES
(3,1),(4,2)
ON CONFLICT DO NOTHING;

-- ############################################################################
-- 6. CATEGORIES
-- ############################################################################
INSERT INTO categories (id, name, slug, description, icon, parent_id, "order", is_active) VALUES
(1, 'Rau củ quả',       'rau-cu-qua',       'Rau củ quả tươi sạch',                    'leaf',     NULL, 1, true),
(2, 'Trái cây',         'trai-cay',         'Các loại trái cây tươi ngon',             'apple',    NULL, 2, true),
(3, 'Thủ công mỹ nghệ', 'thu-cong-my-nghe', 'Sản phẩm thủ công mỹ nghệ truyền thống', 'scissors', NULL, 3, true),
(4, 'Nông sản khô',     'nong-san-kho',     'Nông sản đã qua chế biến, sấy khô',       'package',  NULL, 4, true),
(5, 'Gia vị',           'gia-vi',           'Các loại gia vị phục vụ nấu ăn',          'coffee',   NULL, 5, true),
(6, 'Gốm sứ',           'gom-su',           'Sản phẩm gốm sứ thủ công',                'coffee',   3,    1, true)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 7. REGIONS
-- ############################################################################
INSERT INTO regions (id, name, slug, description, latitude, longitude, "order", is_active) VALUES
(1, 'Hà Nội',      'ha-noi',      'Thủ đô Hà Nội',         '21.0285', '105.8542', 1, true),
(2, 'Đà Nẵng',     'da-nang',     'Thành phố Đà Nẵng',     '16.0544', '108.2022', 2, true),
(3, 'Hồ Chí Minh', 'ho-chi-minh','Thành phố Hồ Chí Minh', '10.8231', '106.6297', 3, true),
(4, 'Huế',         'hue',         'Thành phố Huế',          '16.4637', '107.5909', 4, true)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 8. PRODUCTS
-- ############################################################################
INSERT INTO products (id, name, description, price, producer_id, category_id, status, label, is_active, stock_quantity) VALUES
(1,  'Rau cải xanh hữu cơ',   'Rau cải xanh trồng hữu cơ, không thuốc trừ sâu',       25000.00,  3, 1, 'APPROVED', 'CLEAN_AGRICULTURE', true, 100),
(2,  'Cà chua bi Đà Lạt',     'Cà chua bi Đà Lạt ngọt tự nhiên, giàu vitamin C',        35000.00,  3, 1, 'APPROVED', 'CLEAN_AGRICULTURE', true, 80),
(3,  'Cam sành Hà Giang',     'Cam sành Hà Giang ngọt thanh, ít hạt',                   50000.00,  3, 2, 'APPROVED', 'OCOP',              true, 200),
(4,  'Xoài cát Hòa Lộc',      'Xoài cát Hòa Lộc thơm ngon đặc sản Tiền Giang',        120000.00,  3, 2, 'APPROVED', 'OCOP',              true, 50),
(5,  'Bình gốm Bát Tràng',    'Bình gốm thủ công từ làng nghề Bát Tràng',              350000.00,  4, 6, 'APPROVED', 'TRADITIONAL_CRAFT', true, 30),
(6,  'Chén trà gốm xanh',     'Bộ chén trà gốm xanh thủ công, họa tiết hoa sen',       280000.00,  4, 6, 'APPROVED', 'TRADITIONAL_CRAFT', true, 45),
(7,  'Nấm hương khô Đà Lạt',  'Nấm hương Đà Lạt sấy khô tự nhiên, giàu dinh dưỡng',  180000.00,  3, 4, 'APPROVED', 'CLEAN_AGRICULTURE', true, 60),
(8,  'Tiêu đen Phú Quốc',     'Tiêu đen hạt nguyên chất Phú Quốc',                     250000.00,  4, 5, 'APPROVED', 'OCOP',              true, 40),
(9,  'Khăn thêu tay Huế',     'Khăn thêu tay Huế, họa tiết tinh xảo, thích hợp làm quà', 450000.00, 3, 3, 'APPROVED', 'TRADITIONAL_CRAFT', true, 15),
(10, 'Giỏ đan tre',           'Giỏ đan tre thủ công tinh xảo, bền đẹp',                150000.00,  4, 3, 'PENDING',  'TRADITIONAL_CRAFT', true, 25)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 9. PRODUCT_APPROVALS
-- ############################################################################
INSERT INTO product_approvals (product_id, approver_id, status, notes, checked_description, checked_price, checked_images) VALUES
(1, 2, 'APPROVED', 'Sản phẩm đạt chuẩn',             true, true, true),
(2, 2, 'APPROVED', 'Chất lượng tốt',                  true, true, true),
(3, 2, 'APPROVED', 'Đạt chuẩn OCOP',                  true, true, true),
(4, 1, 'APPROVED', 'Sản phẩm cao cấp',                true, true, true),
(5, 2, 'APPROVED', 'Thủ công mỹ nghệ chất lượng',     true, true, true),
(6, 2, 'APPROVED', 'Gốm sứ đẹp',                      true, true, true),
(7, 2, 'APPROVED', 'Nông sản khô đảm bảo chất lượng', true, true, true),
(8, 2, 'APPROVED', 'Gia vị đặc sản Phú Quốc',         true, true, true),
(9, 1, 'APPROVED', 'Thêu tay tinh xảo',               true, true, true),
(10,2, 'PENDING',  'Chờ bổ sung thêm ảnh sản phẩm',   true, true, false)
ON CONFLICT (product_id) DO NOTHING;

-- ############################################################################
-- 10. SELLER_PROFILES
-- ############################################################################
INSERT INTO seller_profiles (id, user_id, business_name, business_type, description, address,
    id_card_number, bank_name, bank_account_number, bank_account_name,
    verification_status, verified_by, verified_at) VALUES
(1, 3, 'Cơ sở nông sản sạch Trần Thị Bình', 'INDIVIDUAL',
    'Chuyên cung cấp rau củ quả hữu cơ, trái cây sạch tại Hà Nội',
    'Thôn Tân Lập, xã Đan Phượng, Hà Nội',
    '036123456789', 'Vietcombank', '0071004321001', 'TRAN THI BINH',
    'VERIFIED', 1, NOW() - INTERVAL '30 days'),
(2, 4, 'Làng gốm Bát Tràng – Lê Văn Cường', 'HOUSEHOLD',
    'Gia đình 3 đời làm gốm sứ truyền thống tại làng Bát Tràng',
    'Số 12, ngõ 5, Làng Bát Tràng, Gia Lâm, Hà Nội',
    '001234567890', 'BIDV', '31410001234567', 'LE VAN CUONG',
    'VERIFIED', 1, NOW() - INTERVAL '20 days')
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 11. REVIEWS
-- ############################################################################
INSERT INTO reviews (product_id, user_id, rating, comment, created_at) VALUES
(1, 5, 5, 'Rau rất tươi và sạch, giao hàng nhanh!',           NOW() - INTERVAL '10 days'),
(2, 5, 5, 'Cà chua ngọt, con nhà tôi rất thích',               NOW() - INTERVAL '12 days'),
(3, 6, 5, 'Cam ngọt thanh, rất ngon, giá hợp lý',              NOW() - INTERVAL '7 days'),
(4, 5, 5, 'Xoài thơm ngon, đúng chuẩn Hòa Lộc',                NOW() - INTERVAL '5 days'),
(5, 6, 4, 'Bình gốm đẹp, giá hơi cao',                         NOW() - INTERVAL '3 days'),
(7, 5, 4, 'Nấm khô thơm ngon, sẽ mua lại',                     NOW() - INTERVAL '2 days'),
(8, 6, 5, 'Tiêu Phú Quốc thơm đúng chuẩn',                    NOW() - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- ############################################################################
-- 12. ORDERS + ORDER_ITEMS
-- ############################################################################
INSERT INTO orders (id, order_number, customer_id, customer_name, customer_phone, customer_email,
    shipping_address, shipping_province, shipping_district, shipping_ward,
    seller_id, subtotal, shipping_fee, discount_amount, total_amount,
    platform_fee_percentage, platform_fee_amount, seller_amount,
    status, payment_method, payment_status, currency,
    confirmed_at, shipped_at, delivered_at, created_at, is_active) VALUES
(1, 'ORD-2026-001', 5, 'Hoàng Văn Em', '0912345678', 'customer1@example.com',
    '123 Đường ABC, Phường Hàng Bạc', 'Hà Nội', 'Hoàn Kiếm', 'Hàng Bạc',
    3, 60000.00, 25000.00, 0.00, 85000.00, 5.00, 4250.00, 80750.00,
    'DELIVERED', 'COD', 'paid', 'VND',
    NOW()-INTERVAL '5 days', NOW()-INTERVAL '4 days', NOW()-INTERVAL '2 days', NOW()-INTERVAL '6 days', TRUE),
(2, 'ORD-2026-002', 6, 'Đỗ Thị Phương', '0987654321', 'customer2@example.com',
    '456 Đường DEF, Phường Bến Nghé', 'Hồ Chí Minh', 'Quận 1', 'Bến Nghé',
    4, 350000.00, 30000.00, 0.00, 380000.00, 5.00, 19000.00, 361000.00,
    'SHIPPING', 'BANK_TRANSFER', 'paid', 'VND',
    NOW()-INTERVAL '3 days', NOW()-INTERVAL '2 days', NULL, NOW()-INTERVAL '4 days', TRUE),
(3, 'ORD-2026-003', 5, 'Hoàng Văn Em', '0912345678', 'customer1@example.com',
    '123 Đường ABC, Phường Hàng Bạc', 'Hà Nội', 'Hoàn Kiếm', 'Hàng Bạc',
    3, 215000.00, 20000.00, 0.00, 235000.00, 5.00, 11750.00, 223250.00,
    'CONFIRMED', 'COD', 'unpaid', 'VND',
    NOW()-INTERVAL '1 day', NULL, NULL, NOW()-INTERVAL '2 days', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, total_price, tax_amount, discount_amount, created_at) VALUES
(1, 1, 'Rau cải xanh hữu cơ', 25000.00, 2,  50000.00, 0.00, 0.00, NOW()-INTERVAL '6 days'),
(1, 2, 'Cà chua bi Đà Lạt',   35000.00, 1,  35000.00, 0.00, 0.00, NOW()-INTERVAL '6 days'),
(2, 5, 'Bình gốm Bát Tràng', 350000.00, 1, 350000.00, 0.00, 0.00, NOW()-INTERVAL '4 days'),
(3, 7, 'Nấm hương khô Đà Lạt',180000.00,1, 180000.00, 0.00, 0.00, NOW()-INTERVAL '2 days'),
(3, 2, 'Cà chua bi Đà Lạt',   35000.00, 1,  35000.00, 0.00, 0.00, NOW()-INTERVAL '2 days')
ON CONFLICT DO NOTHING;

-- ############################################################################
-- 13. PAYMENTS
-- ############################################################################
INSERT INTO payments (id, order_id, customer_id, seller_id, amount, currency,
    platform_fee_percentage, platform_fee_amount, seller_amount, status, payment_cycle,
    amount_mismatch) VALUES
(1, 1, 5, 3,  85000.00, 'VND', 5.00,  4250.00,  80750.00, 'COMPLETED', 'WEEKLY',  FALSE),
(2, 2, 6, 4, 380000.00, 'VND', 5.00, 19000.00, 361000.00, 'COMPLETED', 'WEEKLY',  FALSE),
(3, 3, 5, 3, 235000.00, 'VND', 5.00, 11750.00, 223250.00, 'PENDING',   'MONTHLY', FALSE)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 14. CONTENTS
-- ############################################################################
INSERT INTO contents (id, title, content, content_type, author_id, product_id,
    status, approved_by, approved_at, is_active) VALUES
(1, 'Hướng dẫn chọn rau sạch',
    'Bài viết hướng dẫn cách nhận biết và chọn rau sạch an toàn cho gia đình...',
    'ARTICLE', 3, 1, 'APPROVED', 2, NOW()-INTERVAL '10 days', TRUE),
(2, 'Giới thiệu gốm Bát Tràng',
    'Bài viết về nghề làm gốm truyền thống Bát Tràng, lịch sử hơn 500 năm...',
    'ARTICLE', 4, 5, 'APPROVED', 2, NOW()-INTERVAL '8 days', TRUE),
(3, 'Câu chuyện người nông dân',
    'Hành trình khởi nghiệp từ cánh đồng của chị Trần Thị Bình...',
    'ARTICLE', 2, NULL, 'APPROVED', 1, NOW()-INTERVAL '5 days', TRUE)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 15. PROMOTIONS
-- ############################################################################
INSERT INTO promotions (id, code, name, description, promotion_type, discount_value,
    min_order_amount, max_discount_amount, usage_limit, used_count,
    start_date, end_date, status, is_public, created_by) VALUES
(1, 'WELCOME10', 'Giảm 10% đơn đầu tiên',
    'Mã giảm 10% cho khách mới, đơn từ 100.000đ',
    'PERCENTAGE', 10.00, 100000.00, 50000.00, 500, 0,
    NOW()-INTERVAL '30 days', NOW()+INTERVAL '60 days', 'ACTIVE', true, 1),
(2, 'FREESHIP', 'Miễn phí vận chuyển',
    'Miễn phí vận chuyển cho đơn từ 200.000đ',
    'FIXED_AMOUNT', 30000.00, 200000.00, NULL, 200, 0,
    NOW()-INTERVAL '15 days', NOW()+INTERVAL '30 days', 'ACTIVE', true, 1)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 16. CARTS & CART_ITEMS
-- ############################################################################
INSERT INTO carts (id, user_id) VALUES (1,5),(2,6)
ON CONFLICT (id) DO NOTHING;

INSERT INTO cart_items (cart_id, product_id, quantity, unit_price) VALUES
(1, 3,  2,  50000.00),
(1, 8,  1, 250000.00),
(2, 5,  1, 350000.00)
ON CONFLICT DO NOTHING;

-- ############################################################################
-- 17. SHIPMENTS
-- ############################################################################
INSERT INTO shipments (id, order_id, provider, tracking_code, provider_order_code,
    status, fee, weight, estimated_delivery, actual_delivery, from_address, to_address) VALUES
(1, 1, 'GHN',  'GHN-VN-001', 'GHN-ORDER-001', 'DELIVERED',  25000.00, 800,
    NOW()-INTERVAL '3 days', NOW()-INTERVAL '2 days',
    'Thôn Tân Lập, Đan Phượng, Hà Nội', '123 Đường ABC, Hàng Bạc, Hà Nội'),
(2, 2, 'GHTK', 'GHTK-VN-002','GHTK-ORDER-002','IN_TRANSIT', 30000.00, 3500,
    NOW()+INTERVAL '1 day', NULL,
    'Làng Bát Tràng, Gia Lâm, Hà Nội', '456 Đường DEF, Bến Nghé, Q1, TP.HCM')
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 18. SELLER_WALLETS
-- ############################################################################
INSERT INTO seller_wallets (id, seller_id, pending_balance, available_balance, total_withdrawn) VALUES
(1, 3, 223250.00, 80750.00, 0.00),
(2, 4, 361000.00,     0.00, 0.00)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- 19. PARTNER_CONTRACTS
-- ############################################################################
INSERT INTO partner_contracts (id, contract_number, partner_id, contract_type,
    start_date, end_date, amount, status, terms, created_by) VALUES
(1, 'CTR-2026-001', 3, 'SELLER_AGREEMENT',
    NOW()-INTERVAL '60 days', NOW()+INTERVAL '1 year', 1000000.00, 'ACTIVE',
    'Hợp đồng hợp tác bán nông sản sạch trên nền tảng', 1),
(2, 'CTR-2026-002', 4, 'SELLER_AGREEMENT',
    NOW()-INTERVAL '45 days', NOW()+INTERVAL '1 year', 1500000.00, 'ACTIVE',
    'Hợp đồng bán sản phẩm gốm sứ Bát Tràng', 1)
ON CONFLICT (id) DO NOTHING;

-- ############################################################################
-- RESET SEQUENCES
-- ############################################################################
SELECT setval('organizations_id_seq',     (SELECT COALESCE(MAX(id),1) FROM organizations));
SELECT setval('roles_id_seq',             (SELECT COALESCE(MAX(id),1) FROM roles));
SELECT setval('users_id_seq',             (SELECT COALESCE(MAX(id),1) FROM users));
SELECT setval('categories_id_seq',        (SELECT COALESCE(MAX(id),1) FROM categories));
SELECT setval('regions_id_seq',           (SELECT COALESCE(MAX(id),1) FROM regions));
SELECT setval('products_id_seq',          (SELECT COALESCE(MAX(id),1) FROM products));
SELECT setval('orders_id_seq',            (SELECT COALESCE(MAX(id),1) FROM orders));
SELECT setval('payments_id_seq',          (SELECT COALESCE(MAX(id),1) FROM payments));
SELECT setval('contents_id_seq',          (SELECT COALESCE(MAX(id),1) FROM contents));
SELECT setval('seller_profiles_id_seq',   (SELECT COALESCE(MAX(id),1) FROM seller_profiles));
SELECT setval('carts_id_seq',             (SELECT COALESCE(MAX(id),1) FROM carts));
SELECT setval('promotions_id_seq',        (SELECT COALESCE(MAX(id),1) FROM promotions));
SELECT setval('shipments_id_seq',         (SELECT COALESCE(MAX(id),1) FROM shipments));
SELECT setval('seller_wallets_id_seq',    (SELECT COALESCE(MAX(id),1) FROM seller_wallets));
SELECT setval('partner_contracts_id_seq', (SELECT COALESCE(MAX(id),1) FROM partner_contracts));

SELECT 'Seed data Cloud SQL HOÀN TẤT!' AS result;
