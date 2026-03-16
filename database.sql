-- ============================================================================
-- DATABASE SAMPLE DATA FOR API_WEB_HE_THONG_AND_APP
-- ============================================================================
-- Note: Tables with image fields (medias, contents, regions, categories, products)
-- should have images manually added by the user
-- ============================================================================

-- Clear existing data (in reverse order of dependencies)
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM reviews;
DELETE FROM product_approvals;
DELETE FROM complaints;
DELETE FROM contents;
DELETE FROM payment_transactions;
DELETE FROM payments;
DELETE FROM partner_contracts;
DELETE FROM user_roles;
DELETE FROM user_organizations;
DELETE FROM role_permissions;
DELETE FROM products;
DELETE FROM categories;
DELETE FROM regions;
DELETE FROM medias;
DELETE FROM users;
DELETE FROM roles;
DELETE FROM permissions;
DELETE FROM organizations;

-- ============================================================================
-- 1. ORGANIZATIONS
-- ============================================================================
INSERT INTO organizations (id, name, description, created_at) VALUES
(1, 'Hợp tác xã Nông nghiệp Hà Nội', 'Hợp tác xã chuyên sản xuất nông sản sạch tại Hà Nội', NOW()),
(2, 'Làng nghề truyền thống Bát Tràng', 'Làng nghề gốm sứ truyền thống Bát Tràng', NOW()),
(3, 'Hội nông dân Đà Nẵng', 'Tổ chức hỗ trợ nông dân phát triển sản xuất', NOW()),
(4, 'Hiệp hội Thủ công mỹ nghệ Việt Nam', 'Hiệp hội quản lý và phát triển nghề thủ công mỹ nghệ', NOW());

-- ============================================================================
-- 2. ROLES
-- ============================================================================
INSERT INTO roles (id, role_name, description, created_at) VALUES
(1, 'admin', 'Quản trị viên hệ thống', NOW()),
(2, 'content_manager', 'Quản lý nội dung', NOW()),
(3, 'seller', 'Người bán hàng/Nhà sản xuất', NOW()),
(4, 'customer', 'Khách hàng', NOW());

-- ============================================================================
-- 3. PERMISSIONS
-- ============================================================================
INSERT INTO permissions (id, parent_id, name, label, type, route, status, "order", icon, component, hide, hide_tab, new_feature, created_at) VALUES
(1, NULL, 'dashboard', 'Tổng quan', 'MENU', '/dashboard', 'active', 1, 'dashboard', 'Dashboard', false, false, false, NOW()),
(2, NULL, 'products', 'Quản lý sản phẩm', 'CATALOGUE', NULL, 'active', 2, 'shopping', NULL, false, false, false, NOW()),
(3, 2, 'products.list', 'Danh sách sản phẩm', 'MENU', '/products', 'active', 1, 'list', 'ProductList', false, false, false, NOW()),
(4, 2, 'products.create', 'Tạo sản phẩm', 'MENU', '/products/create', 'active', 2, 'plus', 'ProductCreate', false, false, false, NOW()),
(5, 2, 'products.approve', 'Duyệt sản phẩm', 'MENU', '/products/approve', 'active', 3, 'check', 'ProductApprove', false, false, false, NOW()),
(6, NULL, 'orders', 'Quản lý đơn hàng', 'MENU', '/orders', 'active', 3, 'shopping-cart', 'Orders', false, false, false, NOW()),
(7, NULL, 'categories', 'Danh mục sản phẩm', 'MENU', '/categories', 'active', 4, 'tags', 'Categories', false, false, false, NOW()),
(8, NULL, 'users', 'Quản lý người dùng', 'MENU', '/users', 'active', 5, 'users', 'Users', false, false, false, NOW()),
(9, NULL, 'contents', 'Quản lý nội dung', 'MENU', '/contents', 'active', 6, 'file-text', 'Contents', false, false, false, NOW()),
(10, NULL, 'reports', 'Báo cáo thống kê', 'MENU', '/reports', 'active', 7, 'bar-chart', 'Reports', false, false, false, NOW());

-- ============================================================================
-- 4. ROLE_PERMISSIONS
-- ============================================================================
INSERT INTO role_permissions (role_id, permission_id, created_at) VALUES
(1,1,NOW()),(1,2,NOW()),(1,3,NOW()),(1,4,NOW()),(1,5,NOW()),
(1,6,NOW()),(1,7,NOW()),(1,8,NOW()),(1,9,NOW()),(1,10,NOW());

INSERT INTO role_permissions (role_id, permission_id, created_at) VALUES
(2,1,NOW()),(2,2,NOW()),(2,3,NOW()),(2,5,NOW()),(2,9,NOW());

INSERT INTO role_permissions (role_id, permission_id, created_at) VALUES
(3,1,NOW()),(3,2,NOW()),(3,3,NOW()),(3,4,NOW()),(3,6,NOW());

INSERT INTO role_permissions (role_id, permission_id, created_at) VALUES
(4,1,NOW()),(4,3,NOW()),(4,6,NOW());

-- ============================================================================
-- 5. USERS
-- ============================================================================
INSERT INTO users (id, email, password_hash, name, gender, activated, type, created_at) VALUES
(1,'admin@example.com','$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO','Quản trị viên','male',1,'admin',NOW()),
(2,'content@example.com','$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO','Nguyễn Văn A','male',1,'content_manager',NOW()),
(3,'seller1@example.com','$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO','Trần Thị B','female',1,'seller',NOW()),
(4,'seller2@example.com','$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO','Lê Văn C','male',1,'seller',NOW()),
(5,'seller3@example.com','$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO','Phạm Thị D','female',1,'seller',NOW()),
(6,'customer1@example.com','$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO','Hoàng Văn E','male',1,'customer',NOW()),
(7,'customer2@example.com','$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO','Đỗ Thị F','female',1,'customer',NOW());

-- ============================================================================
-- 6. USER_ROLES
-- ============================================================================
INSERT INTO user_roles (user_id, role_id, created_at) VALUES
(1,1,NOW()),(2,2,NOW()),(3,3,NOW()),(4,3,NOW()),(5,3,NOW()),(6,4,NOW()),(7,4,NOW());

-- ============================================================================
-- 7. USER_ORGANIZATIONS
-- ============================================================================
INSERT INTO user_organizations (user_id, organization_id, created_at) VALUES
(3,1,NOW()),(4,2,NOW()),(5,3,NOW());

-- ============================================================================
-- 8. CATEGORIES
-- ============================================================================
INSERT INTO categories (id,name,slug,description,icon,parent_id,"order",is_active,created_at) VALUES
(1,'Rau củ quả','rau-cu-qua','Các loại rau củ quả tươi sạch','leaf',NULL,1,true,NOW()),
(2,'Trái cây','trai-cay','Các loại trái cây tươi ngon','apple',NULL,2,true,NOW()),
(3,'Thủ công mỹ nghệ','thu-cong-my-nghe','Sản phẩm thủ công mỹ nghệ truyền thống','scissors',NULL,3,true,NOW()),
(4,'Nông sản khô','nong-san-kho','Các loại nông sản đã qua chế biến, sấy khô','package',NULL,4,true,NOW()),
(5,'Gia vị','gia-vi','Các loại gia vị phục vụ nấu ăn','coffee',NULL,5,true,NOW()),
(6,'Gốm sứ','gom-su','Sản phẩm gốm sứ thủ công','coffee',3,1,true,NOW()),
(7,'Đan lát','dan-lat','Sản phẩm đan lát truyền thống','gift',3,2,true,NOW()),
(8,'Thêu tay','theu-tay','Sản phẩm thêu tay tinh xảo','heart',3,3,true,NOW());

-- ============================================================================
-- 9. REGIONS
-- ============================================================================
INSERT INTO regions (id,name,slug,description,latitude,longitude,"order",is_active,created_at) VALUES
(1,'Hà Nội','ha-noi','Thủ đô Hà Nội','21.0285','105.8542',1,true,NOW()),
(2,'Đà Nẵng','da-nang','Thành phố Đà Nẵng','16.0544','108.2022',2,true,NOW()),
(3,'Hồ Chí Minh','ho-chi-minh','Thành phố Hồ Chí Minh','10.8231','106.6297',3,true,NOW()),
(4,'Huế','hue','Thành phố Huế','16.4637','107.5909',4,true,NOW()),
(5,'Hội An','hoi-an','Phố cổ Hội An','15.8801','108.3380',5,true,NOW());

-- ============================================================================
-- 10. PRODUCTS
-- ============================================================================
INSERT INTO products (id,name,description,price,producer_id,category_id,status,label,created_at) VALUES
(1,'Rau cải xanh hữu cơ','Rau cải xanh trồng theo phương pháp hữu cơ, không sử dụng thuốc trừ sâu',25000.00,3,1,'APPROVED','CLEAN_AGRICULTURE',NOW()),
(2,'Cà chua bi Đà Lạt','Cà chua bi Đà Lạt ngọt tự nhiên, giàu vitamin',35000.00,3,1,'APPROVED','CLEAN_AGRICULTURE',NOW()),
(3,'Cam sành Hà Giang','Cam sành Hà Giang ngọt thanh, ít hạt',50000.00,3,2,'APPROVED','OCOP',NOW()),
(4,'Xoài cát Hòa Lộc','Xoài cát Hòa Lộc thơm ngon đặc sản Tiền Giang',120000.00,3,2,'APPROVED','OCOP',NOW()),
(5,'Bình gốm Bát Tràng','Bình gốm thủ công từ làng nghề Bát Tràng',350000.00,4,6,'APPROVED','TRADITIONAL_CRAFT',NOW()),
(6,'Chén trà gốm xanh','Bộ chén trà gốm xanh thủ công, họa tiết hoa sen',280000.00,4,6,'APPROVED','TRADITIONAL_CRAFT',NOW()),
(7,'Giỏ đan tre truyền thống','Giỏ đan tre thủ công tinh xảo',150000.00,5,7,'PENDING','TRADITIONAL_CRAFT',NOW()),
(8,'Khăn thêu tay Huế','Khăn thêu tay truyền thống của Huế, họa tiết tinh xảo',450000.00,5,8,'APPROVED','TRADITIONAL_CRAFT',NOW()),
(9,'Nấm hương khô Đà Lạt','Nấm hương Đà Lạt sấy khô tự nhiên',180000.00,3,4,'APPROVED','CLEAN_AGRICULTURE',NOW()),
(10,'Tiêu đen Phú Quốc','Tiêu đen hạt nguyên chất Phú Quốc',250000.00,4,5,'APPROVED','OCOP',NOW());

-- ============================================================================
-- 11. PRODUCT_APPROVALS
-- ============================================================================
INSERT INTO product_approvals (product_id, approver_id, status, notes, checked_description, checked_price, checked_images, created_at) VALUES
(1, 2, 'APPROVED', 'Sản phẩm đạt chuẩn, mô tả chi tiết', true, true, true, NOW()),
(2, 2, 'APPROVED', 'Sản phẩm chất lượng tốt', true, true, true, NOW()),
(3, 2, 'APPROVED', 'Đặc sản vùng miền, đạt chuẩn OCOP', true, true, true, NOW()),
(4, 1, 'APPROVED', 'Sản phẩm cao cấp, giá hợp lý', true, true, true, NOW()),
(5, 2, 'APPROVED', 'Sản phẩm thủ công mỹ nghệ chất lượng', true, true, true, NOW()),
(6, 2, 'APPROVED', 'Gốm sứ đẹp, giá cạnh tranh', true, true, true, NOW()),
(8, 1, 'APPROVED', 'Thêu tay tinh xảo', true, true, true, NOW()),
(9, 2, 'APPROVED', 'Nông sản khô đảm bảo chất lượng', true, true, true, NOW()),
(10, 2, 'APPROVED', 'Gia vị đặc sản Phú Quốc', true, true, true, NOW());

-- ============================================================================
-- 12. REVIEWS
-- ============================================================================
INSERT INTO reviews (product_id, user_id, rating, comment, created_at) VALUES
(1, 6, 5, 'Rau rất tươi và sạch, giao hàng nhanh!', NOW()),
(1, 7, 4, 'Chất lượng tốt, sẽ mua tiếp', NOW()),
(2, 6, 5, 'Cà chua ngọt lắm, con nhà tôi rất thích', NOW()),
(3, 7, 5, 'Cam ngọt thanh, rất ngon', NOW()),
(4, 6, 5, 'Xoài thơm ngon, đúng chuẩn Hòa Lộc', NOW()),
(5, 7, 4, 'Bình gốm đẹp, chất lượng tốt nhưng giá hơi cao', NOW()),
(6, 6, 5, 'Chén trà rất đẹp, thích hợp làm quà tặng', NOW()),
(8, 7, 5, 'Thêu tay rất tinh xảo, đáng đồng tiền bát gạo', NOW());

-- ============================================================================
-- 13. ORDERS
-- ============================================================================
INSERT INTO orders (id, order_number, customer_id, customer_name, customer_phone, customer_email, shipping_address, shipping_province, shipping_district, shipping_ward, seller_id, subtotal, shipping_fee, discount_amount, total_amount, platform_fee_percentage, platform_fee_amount, seller_amount, status, payment_method, payment_status, created_at) VALUES
(1, 'ORD-2026-001', 6, 'Hoàng Văn E', '0912345678', 'customer1@example.com', '123 Đường ABC, Phường XYZ', 'Hà Nội', 'Hoàn Kiếm', 'Hàng Bạc', 3, 60000.00, 25000.00, 0.00, 85000.00, 5.00, 4250.00, 80750.00, 'DELIVERED', 'COD', 'paid', NOW()),
(2, 'ORD-2026-002', 7, 'Đỗ Thị F', '0987654321', 'customer2@example.com', '456 Đường DEF, Phường UVW', 'Hồ Chí Minh', 'Quận 1', 'Bến Nghé', 4, 350000.00, 30000.00, 10000.00, 370000.00, 5.00, 18500.00, 351500.00, 'SHIPPING', 'BANK_TRANSFER', 'paid', NOW()),
(3, 'ORD-2026-003', 6, 'Hoàng Văn E', '0912345678', 'customer1@example.com', '123 Đường ABC, Phường XYZ', 'Hà Nội', 'Hoàn Kiếm', 'Hàng Bạc', 5, 450000.00, 25000.00, 0.00, 475000.00, 5.00, 23750.00, 451250.00, 'PROCESSING', 'MOMO', 'paid', NOW());

-- ============================================================================
-- 14. ORDER_ITEMS
-- ============================================================================
INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, total_price, created_at) VALUES
(1, 1, 'Rau cải xanh hữu cơ', 25000.00, 2, 50000.00, NOW()),
(1, 2, 'Cà chua bi Đà Lạt', 35000.00, 1, 35000.00, NOW() - INTERVAL '1 minute'),
(2, 5, 'Bình gốm Bát Tràng', 350000.00, 1, 350000.00, NOW()),
(3, 8, 'Khăn thêu tay Huế', 450000.00, 1, 450000.00, NOW());

-- ============================================================================
-- 15. PAYMENTS
-- ============================================================================
INSERT INTO payments (id, order_id, customer_id, seller_id, amount, platform_fee_percentage, platform_fee_amount, seller_amount, status, payment_cycle, created_at) VALUES
(1, 1, 6, 3, 85000.00, 5.00, 4250.00, 80750.00, 'COMPLETED', 'WEEKLY', NOW()),
(2, 2, 7, 4, 370000.00, 5.00, 18500.00, 351500.00, 'COMPLETED', 'WEEKLY', NOW()),
(3, 3, 6, 5, 475000.00, 5.00, 23750.00, 451250.00, 'PENDING', 'MONTHLY', NOW());

-- ============================================================================
-- 16. PAYMENT_TRANSACTIONS
-- ============================================================================
INSERT INTO payment_transactions (payment_id, transaction_type, amount, status, notes, created_at) VALUES
(1, 'payment', 85000.00, 'COMPLETED', 'Thanh toán COD đơn hàng ORD-2026-001', NOW()),
(2, 'payment', 370000.00, 'COMPLETED', 'Thanh toán chuyển khoản đơn hàng ORD-2026-002', NOW()),
(3, 'payment', 475000.00, 'PENDING', 'Thanh toán MoMo đơn hàng ORD-2026-003', NOW());

-- ============================================================================
-- 17. PARTNER_CONTRACTS
-- ============================================================================
INSERT INTO partner_contracts (id, contract_number, partner_id, contract_type, start_date, end_date, amount, status, terms, created_by, created_at) VALUES
(1, 'CTR-2026-001', 3, 'SELLER_AGREEMENT', NOW(), NOW() + INTERVAL '1 year', 1000000.00, 'ACTIVE', 'Hợp đồng hợp tác bán hàng trên nền tảng, cam kết đảm bảo chất lượng sản phẩm', 1, NOW()),
(2, 'CTR-2026-002', 4, 'SELLER_AGREEMENT', NOW(), NOW() + INTERVAL '1 year', 1500000.00, 'ACTIVE', 'Hợp đồng bán sản phẩm thủ công mỹ nghệ', 1, NOW()),
(3, 'CTR-2026-003', 5, 'SELLER_AGREEMENT', NOW(), NOW() + INTERVAL '6 months', 800000.00, 'ACTIVE', 'Hợp đồng thử nghiệm 6 tháng', 1, NOW());

-- ============================================================================
-- 18. COMPLAINTS
-- ============================================================================
INSERT INTO complaints (product_id, order_id, user_id, complaint_type, title, description, status, handled_by, resolution, created_at) VALUES
(7, NULL, 6, 'PRODUCT_QUALITY', 'Sản phẩm giỏ đan tre chưa được duyệt', 'Tôi muốn mua sản phẩm giỏ đan tre nhưng sản phẩm chưa được duyệt', 'RESOLVED', 2, 'Đã liên hệ với người bán để hoàn thiện thông tin sản phẩm', NOW());

-- ============================================================================
-- 19. CONTENTS
-- ============================================================================
INSERT INTO contents (id, title, content, content_type, author_id, product_id, status, approved_by, approved_at, created_at) VALUES
(1, 'Hướng dẫn chọn rau sạch', 'Bài viết hướng dẫn cách nhận biết và chọn rau sạch an toàn cho sức khỏe...', 'ARTICLE', 3, 1, 'APPROVED', 2, NOW(), NOW()),
(2, 'Giới thiệu gốm Bát Tràng', 'Bài viết giới thiệu về nghề làm gốm truyền thống Bát Tràng...', 'ARTICLE', 4, 5, 'APPROVED', 2, NOW(), NOW()),
(3, 'Video quy trình sản xuất khăn thêu', 'Video giới thiệu quy trình thêu tay truyền thống...', 'VIDEO', 5, 8, 'PENDING', NULL, NULL, NOW());

-- ============================================================================
-- 20. MEDIAS
-- ============================================================================
-- NOTE: This table stores media files - please manually upload and add file information
-- Example structure (not inserting data as files need to be physically uploaded):
-- INSERT INTO medias (filename, file_path, file_type, file_size, mime_type, uploaded_by, created_at) VALUES
-- ('product1.jpg', '/uploads/products/product1.jpg', 'image', 245678, 'image/jpeg', 3, NOW());

-- ============================================================================
-- Reset sequences (for PostgreSQL)
-- ============================================================================
SELECT setval('organizations_id_seq', (SELECT MAX(id) FROM organizations));
SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));
SELECT setval('permissions_id_seq', (SELECT MAX(id) FROM permissions));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('regions_id_seq', (SELECT MAX(id) FROM regions));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));
SELECT setval('payments_id_seq', (SELECT MAX(id) FROM payments));
SELECT setval('partner_contracts_id_seq', (SELECT MAX(id) FROM partner_contracts));
SELECT setval('complaints_id_seq', (SELECT MAX(id) FROM complaints));
SELECT setval('contents_id_seq', (SELECT MAX(id) FROM contents));
