-- ============================================================================
-- RESET & SEED DATABASE - PostgreSQL RDS AWS
-- Cập nhật: 2026-04-05 – Khớp với schema thực tế (alembic models)
--
-- CÁCH DÙNG (sau khi alembic upgrade head đã chạy xong):
--   Chạy TOÀN BỘ file này trong pgAdmin / DBeaver
--   (bảng đã tồn tại → chỉ cần TRUNCATE rồi INSERT)
-- ============================================================================


-- ############################################################################
-- BƯỚC 1: TRUNCATE DỮ LIỆU CŨ (giữ cấu trúc bảng)
-- ############################################################################

TRUNCATE TABLE
    return_requests,
    product_origins,
    product_certificates,
    payouts,
    settlements,
    seller_wallets,
    payment_transactions,
    payments,
    shipments,
    complaints,
    order_items,
    orders,
    cart_items,
    carts,
    promotions,
    reviews,
    product_approvals,
    product_media,
    contents,
    partner_contracts,
    seller_profiles,
    user_roles,
    user_organizations,
    products,
    categories,
    regions,
    medias,
    users,
    roles,
    organizations
RESTART IDENTITY CASCADE;


-- ############################################################################
-- BƯỚC 2: INSERT DỮ LIỆU MẪU
-- Password của tất cả users: "password123"
-- ############################################################################

-- ============================================================================
-- 1. ORGANIZATIONS
-- ============================================================================
INSERT INTO organizations (id, name, description) VALUES
(1, 'Hợp tác xã Nông nghiệp Hà Nội',     'HTX chuyên sản xuất nông sản sạch tại Hà Nội'),
(2, 'Làng nghề truyền thống Bát Tràng',    'Làng nghề gốm sứ truyền thống Bát Tràng'),
(3, 'Hội nông dân Đà Nẵng',                'Tổ chức hỗ trợ nông dân phát triển sản xuất'),
(4, 'Hiệp hội Thủ công mỹ nghệ Việt Nam', 'Hiệp hội quản lý và phát triển nghề thủ công mỹ nghệ');

-- ============================================================================
-- 2. ROLES
-- ============================================================================
INSERT INTO roles (id, role_name, description) VALUES
(1, 'admin',           'Quản trị viên hệ thống'),
(2, 'content_manager', 'Quản lý nội dung'),
(3, 'seller',          'Người bán hàng/Nhà sản xuất'),
(4, 'customer',        'Khách hàng');

-- ============================================================================
-- 3. USERS  (password: "password123")
-- Columns: id, email, password_hash, name, gender, activated, type
-- ============================================================================
INSERT INTO users (id, email, password_hash, name, gender, activated, type) VALUES
(1, 'admin@example.com',     '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Quản trị viên', 'male',   1, 'admin'),
(2, 'content@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Nguyễn Văn An', 'male',   1, 'content_manager'),
(3, 'seller1@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Trần Thị Bình', 'female', 1, 'seller'),
(4, 'seller2@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Lê Văn Cường',  'male',   1, 'seller'),
(5, 'seller3@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Phạm Thị Dung', 'female', 1, 'seller'),
(6, 'customer1@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Hoàng Văn Em',  'male',   1, 'customer'),
(7, 'customer2@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Đỗ Thị Phương', 'female', 1, 'customer'),
(8, 'customer3@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Vũ Minh Quân',  'male',   1, 'customer');

-- ============================================================================
-- 4. USER_ROLES
-- ============================================================================
INSERT INTO user_roles (user_id, role_id) VALUES
(1,1),(2,2),(3,3),(4,3),(5,3),(6,4),(7,4),(8,4);

-- ============================================================================
-- 5. USER_ORGANIZATIONS
-- ============================================================================
INSERT INTO user_organizations (user_id, organization_id) VALUES
(3,1),(4,2),(5,3);

-- ============================================================================
-- 6. CATEGORIES
-- Columns: id, name, slug, description, icon, parent_id, "order", is_active
-- ============================================================================
INSERT INTO categories (id, name, slug, description, icon, parent_id, "order", is_active) VALUES
(1, 'Rau củ quả',       'rau-cu-qua',       'Rau củ quả tươi sạch',                        'leaf',     NULL, 1, true),
(2, 'Trái cây',         'trai-cay',         'Các loại trái cây tươi ngon',                 'apple',    NULL, 2, true),
(3, 'Thủ công mỹ nghệ', 'thu-cong-my-nghe', 'Sản phẩm thủ công mỹ nghệ truyền thống',     'scissors', NULL, 3, true),
(4, 'Nông sản khô',     'nong-san-kho',     'Các loại nông sản đã qua chế biến, sấy khô', 'package',  NULL, 4, true),
(5, 'Gia vị',           'gia-vi',           'Các loại gia vị phục vụ nấu ăn',             'coffee',   NULL, 5, true),
(6, 'Gốm sứ',           'gom-su',           'Sản phẩm gốm sứ thủ công',                   'coffee',   3,    1, true),
(7, 'Đan lát',          'dan-lat',          'Sản phẩm đan lát truyền thống',               'gift',     3,    2, true),
(8, 'Thêu tay',         'theu-tay',         'Sản phẩm thêu tay tinh xảo',                  'heart',    3,    3, true);

-- ============================================================================
-- 7. REGIONS
-- Columns: id, name, slug, description, latitude, longitude, "order", is_active
-- ============================================================================
INSERT INTO regions (id, name, slug, description, latitude, longitude, "order", is_active) VALUES
(1, 'Hà Nội',      'ha-noi',      'Thủ đô Hà Nội',          '21.0285', '105.8542', 1, true),
(2, 'Đà Nẵng',     'da-nang',     'Thành phố Đà Nẵng',      '16.0544', '108.2022', 2, true),
(3, 'Hồ Chí Minh', 'ho-chi-minh', 'Thành phố Hồ Chí Minh',  '10.8231', '106.6297', 3, true),
(4, 'Huế',         'hue',         'Thành phố Huế',           '16.4637', '107.5909', 4, true),
(5, 'Hội An',      'hoi-an',      'Phố cổ Hội An',           '15.8801', '108.3380', 5, true);

-- ============================================================================
-- 8. PRODUCTS
-- Columns từ model: id, name, description, price, producer_id, category_id,
--   status (enum: PENDING/APPROVED/REJECTED), label (string), is_active,
--   stock_quantity, sku, slug, weight, images, created_at
-- ============================================================================
INSERT INTO products (id, name, description, price, producer_id, category_id, status, label, is_active, stock_quantity) VALUES
(1,  'Rau cải xanh hữu cơ',      'Rau cải xanh trồng hữu cơ, không thuốc trừ sâu',          25000.00, 3, 1, 'APPROVED', 'CLEAN_AGRICULTURE', true, 100),
(2,  'Cà chua bi Đà Lạt',        'Cà chua bi Đà Lạt ngọt tự nhiên, giàu vitamin C',           35000.00, 3, 1, 'APPROVED', 'CLEAN_AGRICULTURE', true, 80),
(3,  'Cam sành Hà Giang',        'Cam sành Hà Giang ngọt thanh, ít hạt',                      50000.00, 3, 2, 'APPROVED', 'OCOP',              true, 200),
(4,  'Xoài cát Hòa Lộc',         'Xoài cát Hòa Lộc thơm ngon đặc sản Tiền Giang',           120000.00, 3, 2, 'APPROVED', 'OCOP',              true, 50),
(5,  'Bình gốm Bát Tràng',       'Bình gốm thủ công từ làng nghề Bát Tràng',                 350000.00, 4, 6, 'APPROVED', 'TRADITIONAL_CRAFT', true, 30),
(6,  'Chén trà gốm xanh',        'Bộ chén trà gốm xanh thủ công, họa tiết hoa sen',          280000.00, 4, 6, 'APPROVED', 'TRADITIONAL_CRAFT', true, 45),
(7,  'Giỏ đan tre truyền thống', 'Giỏ đan tre thủ công tinh xảo, bền đẹp',                   150000.00, 5, 7, 'PENDING',  'TRADITIONAL_CRAFT', true, 25),
(8,  'Khăn thêu tay Huế',        'Khăn thêu tay Huế, họa tiết tinh xảo, thích hợp làm quà',  450000.00, 5, 8, 'APPROVED', 'TRADITIONAL_CRAFT', true, 15),
(9,  'Nấm hương khô Đà Lạt',     'Nấm hương Đà Lạt sấy khô tự nhiên, giàu dinh dưỡng',      180000.00, 3, 4, 'APPROVED', 'CLEAN_AGRICULTURE', true, 60),
(10, 'Tiêu đen Phú Quốc',        'Tiêu đen hạt nguyên chất Phú Quốc',                        250000.00, 4, 5, 'APPROVED', 'OCOP',              true, 40),
(11, 'Mắm ruốc Huế',             'Mắm ruốc Huế nguyên chất, công thức truyền thống',           90000.00, 5, 5, 'APPROVED', 'TRADITIONAL_CRAFT', true, 70),
(12, 'Đào sữa Mộc Châu',         'Đào sữa Mộc Châu tươi ngon, mọng nước',                     85000.00, 3, 2, 'PENDING',  'CLEAN_AGRICULTURE', true, 35);

-- ============================================================================
-- 9. PRODUCT_APPROVALS
-- Columns: product_id, approver_id, status, notes, checked_description, checked_price, checked_images
-- ============================================================================
INSERT INTO product_approvals (product_id, approver_id, status, notes, checked_description, checked_price, checked_images) VALUES
(1,  2, 'APPROVED', 'Sản phẩm đạt chuẩn, mô tả chi tiết',        true, true, true),
(2,  2, 'APPROVED', 'Sản phẩm chất lượng tốt',                    true, true, true),
(3,  2, 'APPROVED', 'Đặc sản vùng miền, đạt chuẩn OCOP',          true, true, true),
(4,  1, 'APPROVED', 'Sản phẩm cao cấp, giá hợp lý',               true, true, true),
(5,  2, 'APPROVED', 'Thủ công mỹ nghệ chất lượng',                true, true, true),
(6,  2, 'APPROVED', 'Gốm sứ đẹp, giá cạnh tranh',                 true, true, true),
(7,  2, 'PENDING',  'Chờ bổ sung thêm ảnh sản phẩm',              true, true, false),
(8,  1, 'APPROVED', 'Thêu tay tinh xảo, chất lượng xuất sắc',     true, true, true),
(9,  2, 'APPROVED', 'Nông sản khô đảm bảo chất lượng',            true, true, true),
(10, 2, 'APPROVED', 'Gia vị đặc sản Phú Quốc',                    true, true, true),
(11, 2, 'APPROVED', 'Mắm ruốc đúng vị truyền thống',              true, true, true);

-- ============================================================================
-- 10. SELLER_PROFILES
-- Columns từ model: id, user_id, business_name, business_type, description, address,
--   slug, shop_phone, shop_email, id_card_number,
--   bank_name, bank_account_number, bank_account_name,
--   verification_status, verified_by, verified_at
-- NOTE: Bỏ các cột không có trong model mới (không có id_card_front_url etc.)
-- ============================================================================
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
    'VERIFIED', 1, NOW() - INTERVAL '20 days'),
(3, 5, 'Xưởng thủ công Phạm Thị Dung', 'COOPERATIVE',
    'HTX sản xuất hàng thủ công mỹ nghệ truyền thống tại Đà Nẵng',
    'Khu công nghiệp An Don, Đà Nẵng',
    '023456789012', 'Techcombank', '19036543210123', 'PHAM THI DUNG',
    'PENDING', NULL, NULL);

-- ============================================================================
-- 11. REVIEWS
-- Columns: product_id, user_id, rating, comment, created_at
-- ============================================================================
INSERT INTO reviews (product_id, user_id, rating, comment, created_at) VALUES
(1,  6, 5, 'Rau rất tươi và sạch, giao hàng nhanh!',            NOW() - INTERVAL '10 days'),
(2,  6, 5, 'Cà chua ngọt, con nhà tôi rất thích',                NOW() - INTERVAL '12 days'),
(3,  7, 5, 'Cam ngọt thanh, rất ngon, giá hợp lý',               NOW() - INTERVAL '7 days'),
(4,  6, 5, 'Xoài thơm ngon, đúng chuẩn Hòa Lộc',                 NOW() - INTERVAL '5 days'),
(5,  7, 4, 'Bình gốm đẹp, chất lượng tốt nhưng giá hơi cao',    NOW() - INTERVAL '3 days'),
(6,  6, 5, 'Chén trà rất đẹp, thích hợp làm quà tặng',           NOW() - INTERVAL '6 days'),
(8,  7, 5, 'Thêu tay rất tinh xảo, đáng tiền',                   NOW() - INTERVAL '4 days'),
(9,  8, 4, 'Nấm khô thơm ngon, sẽ mua lại',                      NOW() - INTERVAL '2 days'),
(10, 6, 5, 'Tiêu Phú Quốc thơm đúng chuẩn, không lẫn tạp chất', NOW() - INTERVAL '1 day');

-- ============================================================================
-- 12. ORDERS
-- Columns từ model: id, order_number, customer_id, customer_name, customer_phone,
--   customer_email, shipping_address, shipping_province, shipping_district, shipping_ward,
--   seller_id, subtotal, shipping_fee, discount_amount, total_amount,
--   platform_fee_percentage, platform_fee_amount, seller_amount,
--   status (enum OrderStatus), payment_method (enum PaymentMethod),
--   payment_status, confirmed_at, shipped_at, delivered_at, created_at
-- ============================================================================
INSERT INTO orders (id, order_number, customer_id, customer_name, customer_phone, customer_email,
    shipping_address, shipping_province, shipping_district, shipping_ward,
    seller_id, subtotal, shipping_fee, discount_amount, total_amount,
    platform_fee_percentage, platform_fee_amount, seller_amount,
    status, payment_method, payment_status, currency,
    confirmed_at, shipped_at, delivered_at, created_at) VALUES
(1, 'ORD-2026-001', 6, 'Hoàng Văn Em',  '0912345678', 'customer1@example.com',
    '123 Đường ABC, Phường Hàng Bạc', 'Hà Nội',      'Hoàn Kiếm',    'Hàng Bạc',
    3, 60000.00, 25000.00, 0.00, 85000.00, 5.00, 4250.00, 80750.00,
    'DELIVERED', 'COD', 'paid', 'VND',
    NOW()-INTERVAL '5 days', NOW()-INTERVAL '4 days', NOW()-INTERVAL '2 days', NOW()-INTERVAL '6 days'),
(2, 'ORD-2026-002', 7, 'Đỗ Thị Phương', '0987654321', 'customer2@example.com',
    '456 Đường DEF, Phường Bến Nghé', 'Hồ Chí Minh', 'Quận 1',       'Bến Nghé',
    4, 350000.00, 30000.00, 10000.00, 370000.00, 5.00, 18500.00, 351500.00,
    'SHIPPING', 'BANK_TRANSFER', 'paid', 'VND',
    NOW()-INTERVAL '3 days', NOW()-INTERVAL '2 days', NULL, NOW()-INTERVAL '4 days'),
(3, 'ORD-2026-003', 6, 'Hoàng Văn Em',  '0912345678', 'customer1@example.com',
    '123 Đường ABC, Phường Hàng Bạc', 'Hà Nội',      'Hoàn Kiếm',    'Hàng Bạc',
    5, 450000.00, 25000.00, 0.00, 475000.00, 5.00, 23750.00, 451250.00,
    'PROCESSING', 'MOMO', 'paid', 'VND',
    NOW()-INTERVAL '1 day', NULL, NULL, NOW()-INTERVAL '2 days'),
(4, 'ORD-2026-004', 8, 'Vũ Minh Quân',  '0901234567', 'customer3@example.com',
    '789 Đường GHI, Phường Mỹ An',   'Đà Nẵng',     'Ngũ Hành Sơn', 'Mỹ An',
    3, 215000.00, 20000.00, 0.00, 235000.00, 5.00, 11750.00, 223250.00,
    'CONFIRMED', 'VNPAY', 'paid', 'VND',
    NOW(), NULL, NULL, NOW()-INTERVAL '12 hours'),
(5, 'ORD-2026-005', 7, 'Đỗ Thị Phương', '0987654321', 'customer2@example.com',
    '456 Đường DEF, Phường Bến Nghé', 'Hồ Chí Minh', 'Quận 1',       'Bến Nghé',
    4, 280000.00, 30000.00, 0.00, 310000.00, 5.00, 15500.00, 294500.00,
    'PENDING', 'COD', 'unpaid', 'VND',
    NULL, NULL, NULL, NOW()-INTERVAL '3 hours');

-- ============================================================================
-- 13. ORDER_ITEMS
-- Columns từ model: order_id, product_id, product_name, unit_price, quantity,
--   total_price, created_at
--   (các cột mới: seller_id, store_id, package_id, variant_id, product_image,
--    tax_amount, discount_amount, tracking_code → để NULL)
-- ============================================================================
INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, total_price, tax_amount, discount_amount, created_at) VALUES
(1, 1, 'Rau cải xanh hữu cơ',   25000.00, 2,  50000.00, 0.00, 0.00, NOW()-INTERVAL '6 days'),
(1, 2, 'Cà chua bi Đà Lạt',     35000.00, 1,  35000.00, 0.00, 0.00, NOW()-INTERVAL '6 days'),
(2, 5, 'Bình gốm Bát Tràng',   350000.00, 1, 350000.00, 0.00, 0.00, NOW()-INTERVAL '4 days'),
(3, 8, 'Khăn thêu tay Huế',    450000.00, 1, 450000.00, 0.00, 0.00, NOW()-INTERVAL '2 days'),
(4, 9, 'Nấm hương khô Đà Lạt', 180000.00, 1, 180000.00, 0.00, 0.00, NOW()-INTERVAL '12 hours'),
(4, 2, 'Cà chua bi Đà Lạt',     35000.00, 1,  35000.00, 0.00, 0.00, NOW()-INTERVAL '12 hours'),
(5, 6, 'Chén trà gốm xanh',    280000.00, 1, 280000.00, 0.00, 0.00, NOW()-INTERVAL '3 hours');

-- ============================================================================
-- 14. PAYMENTS
-- Columns từ model: id, order_id, customer_id, seller_id, amount,
--   platform_fee_percentage, platform_fee_amount, seller_amount,
--   status (enum: PENDING/COMPLETED/FAILED/REFUNDED),
--   payment_cycle (enum: WEEKLY/MONTHLY)
-- NOTE: Bỏ các cột cũ không dùng; payment_method_id để NULL
-- ============================================================================
INSERT INTO payments (id, order_id, customer_id, seller_id, amount, currency,
    platform_fee_percentage, platform_fee_amount, seller_amount, status, payment_cycle) VALUES
(1, 1, 6, 3,  85000.00, 'VND', 5.00,  4250.00,  80750.00, 'COMPLETED', 'WEEKLY'),
(2, 2, 7, 4, 370000.00, 'VND', 5.00, 18500.00, 351500.00, 'COMPLETED', 'WEEKLY'),
(3, 3, 6, 5, 475000.00, 'VND', 5.00, 23750.00, 451250.00, 'PENDING',   'MONTHLY'),
(4, 4, 8, 3, 235000.00, 'VND', 5.00, 11750.00, 223250.00, 'COMPLETED', 'WEEKLY');

-- ============================================================================
-- 15. PAYMENT_TRANSACTIONS
-- Columns: payment_id, transaction_type, amount, status, notes, created_at
-- ============================================================================
INSERT INTO payment_transactions (payment_id, transaction_type, amount, status, notes, created_at) VALUES
(1, 'payment',  85000.00, 'COMPLETED', 'Thanh toán COD đơn ORD-2026-001',          NOW()-INTERVAL '2 days'),
(2, 'payment', 370000.00, 'COMPLETED', 'Thanh toán chuyển khoản đơn ORD-2026-002', NOW()-INTERVAL '2 days'),
(3, 'payment', 475000.00, 'PENDING',   'Thanh toán MoMo đơn ORD-2026-003',         NOW()),
(4, 'payment', 235000.00, 'COMPLETED', 'Thanh toán VNPay đơn ORD-2026-004',        NOW());

-- ============================================================================
-- 16. PARTNER_CONTRACTS
-- ============================================================================
INSERT INTO partner_contracts (id, contract_number, partner_id, contract_type,
    start_date, end_date, amount, status, terms, created_by) VALUES
(1, 'CTR-2026-001', 3, 'SELLER_AGREEMENT',
    NOW()-INTERVAL '60 days', NOW()+INTERVAL '1 year', 1000000.00, 'ACTIVE',
    'Hợp đồng hợp tác bán nông sản sạch trên nền tảng', 1),
(2, 'CTR-2026-002', 4, 'SELLER_AGREEMENT',
    NOW()-INTERVAL '45 days', NOW()+INTERVAL '1 year', 1500000.00, 'ACTIVE',
    'Hợp đồng bán sản phẩm gốm sứ Bát Tràng', 1),
(3, 'CTR-2026-003', 5, 'SELLER_AGREEMENT',
    NOW()-INTERVAL '10 days', NOW()+INTERVAL '6 months', 800000.00, 'ACTIVE',
    'Hợp đồng thử nghiệm 6 tháng', 1);

-- ============================================================================
-- 17. COMPLAINTS
-- ============================================================================
INSERT INTO complaints (product_id, order_id, user_id, complaint_type,
    title, description, status, handled_by, resolution) VALUES
(7, NULL, 6, 'PRODUCT_QUALITY',
    'Sản phẩm giỏ đan tre chưa được duyệt',
    'Tôi muốn mua giỏ đan tre nhưng sản phẩm chưa được duyệt để đặt hàng',
    'RESOLVED', 2, 'Đã liên hệ người bán để bổ sung ảnh và hoàn thiện thông tin'),
(NULL, 2, 7, 'DELIVERY',
    'Đơn hàng giao chậm hơn dự kiến',
    'Đơn ORD-2026-002 đã 2 ngày chưa thấy cập nhật trạng thái vận chuyển',
    'IN_PROGRESS', 2, NULL);

-- ============================================================================
-- 18. CONTENTS
-- ============================================================================
INSERT INTO contents (id, title, content, content_type, author_id, product_id,
    status, approved_by, approved_at) VALUES
(1, 'Hướng dẫn chọn rau sạch',
    'Bài viết hướng dẫn cách nhận biết và chọn rau sạch an toàn...',
    'ARTICLE', 3, 1, 'APPROVED', 2, NOW()-INTERVAL '10 days'),
(2, 'Giới thiệu gốm Bát Tràng',
    'Bài viết về nghề làm gốm truyền thống Bát Tràng, lịch sử hơn 500 năm...',
    'ARTICLE', 4, 5, 'APPROVED', 2, NOW()-INTERVAL '8 days'),
(3, 'Video quy trình sản xuất khăn thêu',
    'Video giới thiệu quy trình thêu tay truyền thống của nghệ nhân Huế...',
    'VIDEO', 5, 8, 'PENDING', NULL, NULL),
(4, 'Câu chuyện của người nông dân',
    'Hành trình khởi nghiệp từ cánh đồng của chị Trần Thị Bình...',
    'ARTICLE', 2, NULL, 'APPROVED', 1, NOW()-INTERVAL '5 days');

-- ============================================================================
-- 19. PROMOTIONS
-- Columns từ model: id, code, name, description, promotion_type (enum),
--   discount_value, min_order_amount, max_discount_amount, usage_limit,
--   usage_limit_per_user, used_count, start_date, end_date,
--   status (enum), is_public, seller_id (nullable), created_by
-- ============================================================================
INSERT INTO promotions (id, code, name, description, promotion_type, discount_value,
    min_order_amount, max_discount_amount, usage_limit, used_count,
    start_date, end_date, status, is_public, created_by) VALUES
(1, 'WELCOME10', 'Giảm 10% đơn đầu tiên',
    'Mã giảm 10% cho khách mới, đơn từ 100.000đ',
    'PERCENTAGE', 10.00, 100000.00, 50000.00, 500, 87,
    NOW()-INTERVAL '30 days', NOW()+INTERVAL '60 days', 'ACTIVE', true, 1),
(2, 'FREESHIP', 'Miễn phí vận chuyển',
    'Miễn phí vận chuyển cho đơn từ 200.000đ',
    'FIXED_AMOUNT', 30000.00, 200000.00, NULL, 200, 43,
    NOW()-INTERVAL '15 days', NOW()+INTERVAL '30 days', 'ACTIVE', true, 1),
(3, 'OCOP20', 'Giảm 20% sản phẩm OCOP',
    'Ưu đãi 20% cho tất cả sản phẩm nhãn OCOP',
    'PERCENTAGE', 20.00, 150000.00, 100000.00, 100, 12,
    NOW()-INTERVAL '5 days', NOW()+INTERVAL '10 days', 'ACTIVE', true, 1),
(4, 'SUMMER50K', 'Giảm 50K mùa hè',
    'Giảm 50.000đ cho đơn từ 300.000đ',
    'FIXED_AMOUNT', 50000.00, 300000.00, NULL, 50, 50,
    NOW()-INTERVAL '60 days', NOW()-INTERVAL '1 day', 'EXPIRED', false, 1);

-- ============================================================================
-- 20. CARTS & CART_ITEMS
-- ============================================================================
INSERT INTO carts (id, user_id) VALUES (1,6),(2,7),(3,8);

INSERT INTO cart_items (cart_id, product_id, quantity, unit_price) VALUES
(1, 3,  2,  50000.00),
(1, 10, 1, 250000.00),
(2, 5,  1, 350000.00),
(2, 6,  2, 280000.00),
(3, 1,  3,  25000.00),
(3, 9,  1, 180000.00);

-- ============================================================================
-- 21. SHIPMENTS
-- Columns từ model: id, order_id, provider (enum), tracking_code,
--   provider_order_code, status (enum), fee, weight,
--   estimated_delivery, actual_delivery, from_address, to_address, note
-- ============================================================================
INSERT INTO shipments (id, order_id, provider, tracking_code, provider_order_code,
    status, fee, weight, estimated_delivery, actual_delivery,
    from_address, to_address, note) VALUES
(1, 1, 'GHN',    'GHN-VN-7654321',  'GHN-ORDER-001',  'DELIVERED',  25000.00, 800,
    NOW()-INTERVAL '3 days', NOW()-INTERVAL '2 days',
    'Thôn Tân Lập, xã Đan Phượng, Hà Nội', '123 Đường ABC, Phường Hàng Bạc, Hà Nội', NULL),
(2, 2, 'GHTK',   'GHTK-VN-8765432', 'GHTK-ORDER-002', 'IN_TRANSIT', 30000.00, 3500,
    NOW()+INTERVAL '1 day', NULL,
    'Số 12 Làng Bát Tràng, Gia Lâm, Hà Nội', '456 Đường DEF, Bến Nghé, Quận 1, TP.HCM',
    'Hàng gốm sứ, đóng gói bong bóng'),
(3, 3, 'MANUAL', NULL, NULL, 'PENDING', 25000.00, 500,
    NOW()+INTERVAL '3 days', NULL,
    'Khu công nghiệp An Don, Đà Nẵng', '123 Đường ABC, Phường Hàng Bạc, Hà Nội', 'Seller tự giao'),
(4, 4, 'GHN',    'GHN-VN-9876543',  'GHN-ORDER-004',  'CREATED',    20000.00, 600,
    NOW()+INTERVAL '2 days', NULL,
    'Thôn Tân Lập, xã Đan Phượng, Hà Nội', '789 Đường GHI, Phường Mỹ An, Đà Nẵng', NULL);

-- ============================================================================
-- 22. SELLER_WALLETS
-- ============================================================================
INSERT INTO seller_wallets (id, seller_id, pending_balance, available_balance, total_withdrawn) VALUES
(1, 3, 223250.00, 80750.00, 0.00),
(2, 4, 351500.00,     0.00, 0.00),
(3, 5, 451250.00,     0.00, 0.00);

-- ============================================================================
-- 23. SETTLEMENTS
-- ============================================================================
INSERT INTO settlements (id, seller_id, period_start, period_end,
    total_orders, total_amount, total_platform_fee, total_seller_amount,
    status, approved_by, approved_at, note) VALUES
(1, 3, NOW()-INTERVAL '14 days', NOW()-INTERVAL '7 days',
    2, 320000.00, 16000.00, 304000.00, 'COMPLETED', 1, NOW()-INTERVAL '6 days',
    'Đối soát tuần 1 tháng 3/2026 – seller Trần Thị Bình'),
(2, 4, NOW()-INTERVAL '14 days', NOW()-INTERVAL '7 days',
    1, 370000.00, 18500.00, 351500.00, 'APPROVED',  1, NOW()-INTERVAL '5 days',
    'Đối soát tuần 1 tháng 3/2026 – seller Lê Văn Cường'),
(3, 5, NOW()-INTERVAL '7 days',  NOW(),
    1, 475000.00, 23750.00, 451250.00, 'PENDING', NULL, NULL,
    'Đối soát tuần 2 tháng 3/2026 – seller Phạm Thị Dung');

-- ============================================================================
-- 24. PAYOUTS
-- ============================================================================
INSERT INTO payouts (id, seller_id, settlement_id, amount,
    bank_name, bank_account_number, bank_account_name,
    status, transaction_ref, note, processed_by, processed_at) VALUES
(1, 3, 1, 304000.00, 'Vietcombank', '0071004321001', 'TRAN THI BINH',
    'SUCCESS',    'VCB-TXN-20260324-001', 'Chi trả đối soát tuần 1/3/2026', 1, NOW()-INTERVAL '5 days'),
(2, 4, 2, 351500.00, 'BIDV', '31410001234567', 'LE VAN CUONG',
    'PROCESSING', 'BIDV-TXN-20260325-002', 'Chi trả đối soát tuần 1/3/2026', 1, NULL);

-- ============================================================================
-- 25. RETURN_REQUESTS
-- ============================================================================
INSERT INTO return_requests (id, order_id, user_id, return_type, reason, images,
    status, admin_note, handled_by, handled_at) VALUES
(1, 1, 6, 'RETURN',
    'Rau bị héo khi nhận, không đảm bảo chất lượng như mô tả', '[]',
    'REFUNDED', 'Đã xác minh và hoàn tiền cho khách trong 24h', 2, NOW()-INTERVAL '1 day');

-- ============================================================================
-- 26. PRODUCT_CERTIFICATES
-- ============================================================================
INSERT INTO product_certificates (id, product_id, certificate_name, certificate_number,
    issued_by, issue_date, expiry_date, verification_status, verified_by, verified_at) VALUES
(1, 3,  'OCOP 4 sao', 'OCOP-HG-2024-0123',
    'Sở NN & PTNT tỉnh Hà Giang',      '2024-01-15', '2026-01-14', 'VERIFIED', 1, NOW()-INTERVAL '20 days'),
(2, 4,  'VietGAP',    'VIETGAP-TG-2024-0456',
    'Cục Trồng trọt – Bộ Nông nghiệp', '2024-03-01', '2026-02-28', 'VERIFIED', 2, NOW()-INTERVAL '15 days'),
(3, 5,  'Chứng nhận làng nghề truyền thống', 'LN-BT-2023-0789',
    'Sở Công thương TP. Hà Nội',        '2023-06-10', '2027-06-09', 'VERIFIED', 1, NOW()-INTERVAL '30 days'),
(4, 10, 'OCOP 3 sao', 'OCOP-KG-2025-0321',
    'Sở NN & PTNT tỉnh Kiên Giang',     '2025-01-20', '2027-01-19', 'PENDING',  NULL, NULL);

-- ============================================================================
-- 27. PRODUCT_ORIGINS
-- ============================================================================
INSERT INTO product_origins (id, product_id, village_name, region_id, producer_name,
    batch_number, production_date, expiry_date, ingredients, process_summary) VALUES
(1, 1,  'Thôn Tân Lập, Đan Phượng', 1, 'Hộ nông dân Trần Thị Bình',
    'LOT-RAU-2026-001',  '2026-03-28', '2026-04-03',
    'Rau cải xanh 100% tự nhiên, không thuốc trừ sâu',
    'Gieo hạt → Bón phân hữu cơ → Thu hoạch → Rửa sạch → Đóng gói'),
(2, 3,  'Vùng cam Hà Giang', 1, 'HTX Nông nghiệp Hà Giang',
    'LOT-CAM-2026-012',  '2026-03-10', '2026-04-10',
    'Cam sành nguyên chất, không chất bảo quản',
    'Thu hoạch → Phân loại → Rửa sạch → Đóng thùng → Vận chuyển lạnh'),
(3, 5,  'Làng nghề Bát Tràng', 1, 'Gia đình nghệ nhân Lê Văn Cường',
    'LOT-GOM-2026-005',  '2026-02-15', NULL,
    'Đất sét Bát Tràng, men sứ tự nhiên',
    'Lấy đất → Nhào nặn → Tạo hình → Phơi khô → Tráng men → Nung 1200°C → Kiểm tra'),
(4, 10, 'Đảo Phú Quốc', 3, 'Cơ sở sản xuất tiêu Phú Quốc',
    'LOT-TIEU-2026-003', '2026-01-05', '2028-01-04',
    'Tiêu đen Phú Quốc hạt nguyên, không phụ gia',
    'Thu hoạch → Phơi nắng 5–7 ngày → Sàng lọc → Đóng gói hút chân không');

-- ============================================================================
-- RESET SEQUENCES (đồng bộ lại auto-increment)
-- ============================================================================
SELECT setval('organizations_id_seq',        (SELECT MAX(id) FROM organizations));
SELECT setval('roles_id_seq',                (SELECT MAX(id) FROM roles));
SELECT setval('users_id_seq',                (SELECT MAX(id) FROM users));
SELECT setval('categories_id_seq',           (SELECT MAX(id) FROM categories));
SELECT setval('regions_id_seq',              (SELECT MAX(id) FROM regions));
SELECT setval('products_id_seq',             (SELECT MAX(id) FROM products));
SELECT setval('orders_id_seq',               (SELECT MAX(id) FROM orders));
SELECT setval('payments_id_seq',             (SELECT MAX(id) FROM payments));
SELECT setval('partner_contracts_id_seq',    (SELECT MAX(id) FROM partner_contracts));
SELECT setval('complaints_id_seq',           (SELECT MAX(id) FROM complaints));
SELECT setval('contents_id_seq',             (SELECT MAX(id) FROM contents));
SELECT setval('seller_profiles_id_seq',      (SELECT MAX(id) FROM seller_profiles));
SELECT setval('carts_id_seq',                (SELECT MAX(id) FROM carts));
SELECT setval('promotions_id_seq',           (SELECT MAX(id) FROM promotions));
SELECT setval('shipments_id_seq',            (SELECT MAX(id) FROM shipments));
SELECT setval('seller_wallets_id_seq',       (SELECT MAX(id) FROM seller_wallets));
SELECT setval('settlements_id_seq',          (SELECT MAX(id) FROM settlements));
SELECT setval('payouts_id_seq',              (SELECT MAX(id) FROM payouts));
SELECT setval('return_requests_id_seq',      (SELECT MAX(id) FROM return_requests));
SELECT setval('product_certificates_id_seq', (SELECT MAX(id) FROM product_certificates));
SELECT setval('product_origins_id_seq',      (SELECT MAX(id) FROM product_origins));

-- ============================================================================
-- HOÀN TẤT
-- ============================================================================
SELECT 'Database reset & seed HOÀN TẤT!' AS result;
