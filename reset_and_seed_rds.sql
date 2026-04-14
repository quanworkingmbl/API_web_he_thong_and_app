-- ============================================================================
-- RESET & SEED DATABASE - PostgreSQL RDS AWS
-- Cập nhật: 2026-04-09 – Tích hợp đầy đủ schema mới:
--   Order Security, Complaint Management, Payment Management,
--   Cart Variant, User Status, Content Audit, Refresh Token, AI tables
--
-- CÁCH DÙNG: Chạy TOÀN BỘ file này trong pgAdmin / DBeaver
--   File tự tạo enum/bảng mới nếu chưa có (idempotent schema)
-- ============================================================================


-- ############################################################################
-- BƯỚC 1: TRUNCATE DỮ LIỆU CŨ (giữ cấu trúc bảng)
-- Truncate động: chỉ truncate các bảng đang tồn tại để tránh lỗi khi schema thiếu
-- ############################################################################

DO $$
DECLARE
    table_list TEXT[] := ARRAY[
        'ai_moderation_logs',
        'ai_generation_cache',
        'ai_cost_logs',
        'product_embeddings',
        'refresh_tokens',
        'payment_audit_logs',
        'complaint_status_logs',
        'complaint_comments',
        'content_audit_logs',
        'product_price_logs',
        'order_status_logs',
        'return_requests',
        'product_origins',
        'product_certificates',
        'payouts',
        'settlements',
        'seller_wallets',
        'payment_transactions',
        'payments',
        'shipments',
        'complaints',
        'order_items',
        'orders',
        'cart_items',
        'carts',
        'promotions',
        'reviews',
        'product_approvals',
        'product_media',
        'contents',
        'partner_contracts',
        'seller_profiles',
        'user_roles',
        'user_organizations',
        'products',
        'categories',
        'regions',
        'medias',
        'users',
        'roles',
        'organizations'
    ];
    existing_tables TEXT;
BEGIN
    SELECT string_agg(format('%I', t), ', ')
    INTO existing_tables
    FROM unnest(table_list) AS t
    WHERE to_regclass(format('public.%I', t)) IS NOT NULL;

    IF existing_tables IS NOT NULL THEN
        EXECUTE 'TRUNCATE TABLE ' || existing_tables || ' RESTART IDENTITY CASCADE';
    END IF;
END $$;


-- ############################################################################
-- BƯỚC 1.5: ĐẢM BẢO ENUM TYPES & SCHEMA MỚI (idempotent)
-- ############################################################################

DO $$ BEGIN
    CREATE TYPE complaintcategory AS ENUM
        ('DELIVERY','QUALITY','REFUND','FRAUD','SERVICE','OTHER');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE complaintpriority AS ENUM
        ('LOW','MEDIUM','HIGH','URGENT');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE commentrole AS ENUM
        ('buyer','seller','admin','system');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE originstatus AS ENUM
        ('PENDING','VERIFIED','REJECTED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'PARTIAL_REFUNDED';
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE userstatus AS ENUM
        ('ACTIVE','SUSPENDED','BANNED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE contentauditaction AS ENUM
        ('CREATE','UPDATE','APPROVE','REJECT','DELETE','RESTORE');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- Cột mới cho users
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS status          userstatus NOT NULL DEFAULT 'ACTIVE',
    ADD COLUMN IF NOT EXISTS status_reason   TEXT,
    ADD COLUMN IF NOT EXISTS status_expire_at TIMESTAMPTZ;

-- Cột mới cho contents
ALTER TABLE contents
    ADD COLUMN IF NOT EXISTS is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at      TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by      INTEGER,
    ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_contents_deleted_by'
    ) THEN
        ALTER TABLE contents
        ADD CONSTRAINT fk_contents_deleted_by
        FOREIGN KEY (deleted_by)
        REFERENCES users(id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_contents_is_active ON contents (is_active);

CREATE TABLE IF NOT EXISTS content_audit_logs (
    id         SERIAL PRIMARY KEY,
    content_id INTEGER NOT NULL REFERENCES contents(id),
    action     contentauditaction NOT NULL,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    notes      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_content_audit_logs_id ON content_audit_logs (id);
CREATE INDEX IF NOT EXISTS ix_content_audit_logs_content_id ON content_audit_logs (content_id);

CREATE TABLE IF NOT EXISTS product_price_logs (
    id         SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    old_price  NUMERIC(15,2) NOT NULL,
    new_price  NUMERIC(15,2) NOT NULL,
    changed_by INTEGER NOT NULL REFERENCES users(id),
    reason     TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_product_price_logs_id ON product_price_logs (id);
CREATE INDEX IF NOT EXISTS ix_product_price_logs_product_id ON product_price_logs (product_id);

-- Cột/FK mới cho cart_items.variant_id
ALTER TABLE cart_items
    ADD COLUMN IF NOT EXISTS variant_id INTEGER;
CREATE INDEX IF NOT EXISTS ix_cart_items_variant_id ON cart_items (variant_id);

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'cart_items'
          AND column_name = 'variant_id'
    )
    AND EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'product_variants'
    )
    AND NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_cart_items_variant_id'
    )
    THEN
        ALTER TABLE cart_items
        ADD CONSTRAINT fk_cart_items_variant_id
        FOREIGN KEY (variant_id)
        REFERENCES product_variants(id)
        ON DELETE SET NULL;
    END IF;
END $$;

-- Bảng mới cho auth refresh token
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id                    SERIAL PRIMARY KEY,
    user_id               INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jti                   VARCHAR(64) NOT NULL UNIQUE,
    family_id             VARCHAR(64) NOT NULL,
    token_hash            VARCHAR(128) NOT NULL UNIQUE,
    expires_at            TIMESTAMPTZ NOT NULL,
    revoked_at            TIMESTAMPTZ,
    replaced_by_jti       VARCHAR(64),
    created_by_ip         VARCHAR(64),
    created_by_user_agent VARCHAR(512),
    revoked_reason        TEXT,
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_id ON refresh_tokens (id);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_family_id ON refresh_tokens (family_id);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_expires_at ON refresh_tokens (expires_at);

-- Bảng AI
CREATE TABLE IF NOT EXISTS ai_moderation_logs (
    id                 SERIAL PRIMARY KEY,
    product_id         INTEGER REFERENCES products(id),
    content_id         INTEGER REFERENCES contents(id),
    rule_engine_result VARCHAR(20),
    rule_engine_flags  TEXT,
    model_used         VARCHAR(100) NOT NULL,
    ai_decision        VARCHAR(20) NOT NULL,
    ai_confidence      DOUBLE PRECISION,
    ai_reasons         TEXT,
    ai_flags           TEXT,
    escalated          BOOLEAN DEFAULT FALSE,
    escalation_reason  VARCHAR(200),
    processing_time_ms INTEGER,
    input_tokens       INTEGER DEFAULT 0,
    output_tokens      INTEGER DEFAULT 0,
    estimated_cost_usd DOUBLE PRECISION DEFAULT 0.0,
    raw_response       TEXT,
    created_at         TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_ai_moderation_logs_id ON ai_moderation_logs (id);
CREATE INDEX IF NOT EXISTS ix_ai_moderation_logs_product_id ON ai_moderation_logs (product_id);
CREATE INDEX IF NOT EXISTS ix_ai_moderation_logs_content_id ON ai_moderation_logs (content_id);

CREATE TABLE IF NOT EXISTS ai_generation_cache (
    id          SERIAL PRIMARY KEY,
    input_hash  VARCHAR(64) NOT NULL UNIQUE,
    task_type   VARCHAR(30) NOT NULL,
    model_used  VARCHAR(100),
    input_text  TEXT,
    output_text TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    expires_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_ai_generation_cache_id ON ai_generation_cache (id);
CREATE INDEX IF NOT EXISTS ix_ai_generation_cache_input_hash ON ai_generation_cache (input_hash);
CREATE INDEX IF NOT EXISTS ix_ai_generation_cache_expires_at ON ai_generation_cache (expires_at);

CREATE TABLE IF NOT EXISTS ai_cost_logs (
    id                  SERIAL PRIMARY KEY,
    log_date            DATE NOT NULL,
    model_id            VARCHAR(100) NOT NULL,
    task_type           VARCHAR(30) NOT NULL,
    request_count       INTEGER DEFAULT 0,
    total_input_tokens  INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    total_cost_usd      DOUBLE PRECISION DEFAULT 0.0,
    CONSTRAINT uq_cost_date_model_task UNIQUE (log_date, model_id, task_type)
);
CREATE INDEX IF NOT EXISTS ix_ai_cost_logs_id ON ai_cost_logs (id);
CREATE INDEX IF NOT EXISTS ix_ai_cost_logs_log_date ON ai_cost_logs (log_date);

CREATE TABLE IF NOT EXISTS product_embeddings (
    id               SERIAL PRIMARY KEY,
    product_id       INTEGER NOT NULL UNIQUE REFERENCES products(id),
    embedding_text   TEXT,
    embedding_vector TEXT,
    vector_dimension INTEGER,
    model_version    VARCHAR(100),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_product_embeddings_id ON product_embeddings (id);
CREATE INDEX IF NOT EXISTS ix_product_embeddings_product_id ON product_embeddings (product_id);

-- Cột mới cho orders
ALTER TABLE orders ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
CREATE INDEX IF NOT EXISTS ix_orders_is_active ON orders (is_active);

-- Cột mới cho complaints
ALTER TABLE complaints
    ADD COLUMN IF NOT EXISTS category        complaintcategory NOT NULL DEFAULT 'OTHER',
    ADD COLUMN IF NOT EXISTS priority        complaintpriority NOT NULL DEFAULT 'MEDIUM',
    ADD COLUMN IF NOT EXISTS images          TEXT,
    ADD COLUMN IF NOT EXISTS resolution_type VARCHAR(30),
    ADD COLUMN IF NOT EXISTS return_request_id INTEGER REFERENCES return_requests(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS assigned_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS first_response_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS resolved_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS closed_at         TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS ix_complaints_category ON complaints (category);
CREATE INDEX IF NOT EXISTS ix_complaints_priority ON complaints (priority);

-- Cột mới cho payments
ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS vnpay_transaction_no VARCHAR(100),
    ADD COLUMN IF NOT EXISTS vnpay_response_code  VARCHAR(10),
    ADD COLUMN IF NOT EXISTS vnpay_bank_code       VARCHAR(20),
    ADD COLUMN IF NOT EXISTS amount_from_gateway   NUMERIC(15,2),
    ADD COLUMN IF NOT EXISTS amount_mismatch       BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS refunded_amount       NUMERIC(15,2),
    ADD COLUMN IF NOT EXISTS refund_note           TEXT,
    ADD COLUMN IF NOT EXISTS refunded_at           TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS ix_payments_vnpay_transaction_no ON payments (vnpay_transaction_no);

-- Cột mới cho payment_transactions
ALTER TABLE payment_transactions ADD COLUMN IF NOT EXISTS gateway_ref VARCHAR(255);

-- Cột mới cho product_origins (duyệt nguồn gốc)
ALTER TABLE product_origins
    ADD COLUMN IF NOT EXISTS verification_status originstatus NOT NULL DEFAULT 'PENDING',
    ADD COLUMN IF NOT EXISTS verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Bảng mới
CREATE TABLE IF NOT EXISTS order_status_logs (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    actor_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
    role       VARCHAR(30),
    note       TEXT,
    timestamp  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_order_status_logs_id       ON order_status_logs (id);
CREATE INDEX IF NOT EXISTS ix_order_status_logs_order_id ON order_status_logs (order_id);

CREATE TABLE IF NOT EXISTS complaint_comments (
    id           SERIAL PRIMARY KEY,
    complaint_id INTEGER NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    author_id    INTEGER NOT NULL REFERENCES users(id)     ON DELETE SET NULL,
    role         commentrole NOT NULL,
    message      TEXT NOT NULL,
    attachments  TEXT,
    is_internal  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_complaint_comments_id           ON complaint_comments (id);
CREATE INDEX IF NOT EXISTS ix_complaint_comments_complaint_id ON complaint_comments (complaint_id);

CREATE TABLE IF NOT EXISTS complaint_status_logs (
    id           SERIAL PRIMARY KEY,
    complaint_id INTEGER NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    old_status   VARCHAR(30),
    new_status   VARCHAR(30) NOT NULL,
    actor_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    note         TEXT,
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_complaint_status_logs_id           ON complaint_status_logs (id);
CREATE INDEX IF NOT EXISTS ix_complaint_status_logs_complaint_id ON complaint_status_logs (complaint_id);

CREATE TABLE IF NOT EXISTS payment_audit_logs (
    id         SERIAL PRIMARY KEY,
    payment_id INTEGER REFERENCES payments(id) ON DELETE SET NULL,
    action     VARCHAR(50) NOT NULL,
    actor_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
    amount     NUMERIC(15,2),
    note       TEXT,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    timestamp  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_payment_audit_logs_id         ON payment_audit_logs (id);
CREATE INDEX IF NOT EXISTS ix_payment_audit_logs_payment_id ON payment_audit_logs (payment_id);


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
-- Columns: id, email, password_hash, name, gender, activated, type,
--   status, status_reason, status_expire_at
-- ============================================================================
INSERT INTO users (id, email, password_hash, name, gender, activated, type, status, status_reason, status_expire_at) VALUES
(1, 'admin@example.com',     '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Quản trị viên', 'male',   1, 'admin',           'ACTIVE',    NULL,                                          NULL),
(2, 'content@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Nguyễn Văn An', 'male',   1, 'content_manager', 'ACTIVE',    NULL,                                          NULL),
(3, 'seller1@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Trần Thị Bình', 'female', 1, 'seller',          'ACTIVE',    NULL,                                          NULL),
(4, 'seller2@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Lê Văn Cường',  'male',   1, 'seller',          'ACTIVE',    NULL,                                          NULL),
(5, 'seller3@example.com',   '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Phạm Thị Dung', 'female', 1, 'seller',          'SUSPENDED', 'Chưa hoàn tất hồ sơ xác minh cửa hàng',       NOW() + INTERVAL '7 days'),
(6, 'customer1@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Hoàng Văn Em',  'male',   1, 'customer',        'ACTIVE',    NULL,                                          NULL),
(7, 'customer2@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Đỗ Thị Phương', 'female', 1, 'customer',        'ACTIVE',    NULL,                                          NULL),
(8, 'customer3@example.com', '$2b$12$n4piNSOxGuKKshPXAe4VwuBWA92k0NNwKExGm4nbCYRg/IOwSz3gO', 'Vũ Minh Quân',  'male',   1, 'customer',        'BANNED',    'Vi phạm chính sách đánh giá spam',             NULL);

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
    confirmed_at, shipped_at, delivered_at, created_at, is_active) VALUES
(1, 'ORD-2026-001', 6, 'Hoàng Văn Em',  '0912345678', 'customer1@example.com',
    '123 Đường ABC, Phường Hàng Bạc', 'Hà Nội',      'Hoàn Kiếm',    'Hàng Bạc',
    3, 60000.00, 25000.00, 0.00, 85000.00, 5.00, 4250.00, 80750.00,
    'DELIVERED', 'COD', 'paid', 'VND',
    NOW()-INTERVAL '5 days', NOW()-INTERVAL '4 days', NOW()-INTERVAL '2 days', NOW()-INTERVAL '6 days', TRUE),
(2, 'ORD-2026-002', 7, 'Đỗ Thị Phương', '0987654321', 'customer2@example.com',
    '456 Đường DEF, Phường Bến Nghé', 'Hồ Chí Minh', 'Quận 1',       'Bến Nghé',
    4, 350000.00, 30000.00, 10000.00, 370000.00, 5.00, 18500.00, 351500.00,
    'SHIPPING', 'BANK_TRANSFER', 'paid', 'VND',
    NOW()-INTERVAL '3 days', NOW()-INTERVAL '2 days', NULL, NOW()-INTERVAL '4 days', TRUE),
(3, 'ORD-2026-003', 6, 'Hoàng Văn Em',  '0912345678', 'customer1@example.com',
    '123 Đường ABC, Phường Hàng Bạc', 'Hà Nội',      'Hoàn Kiếm',    'Hàng Bạc',
    5, 450000.00, 25000.00, 0.00, 475000.00, 5.00, 23750.00, 451250.00,
    'PROCESSING', 'MOMO', 'paid', 'VND',
    NOW()-INTERVAL '1 day', NULL, NULL, NOW()-INTERVAL '2 days', TRUE),
(4, 'ORD-2026-004', 8, 'Vũ Minh Quân',  '0901234567', 'customer3@example.com',
    '789 Đường GHI, Phường Mỹ An',   'Đà Nẵng',     'Ngũ Hành Sơn', 'Mỹ An',
    3, 215000.00, 20000.00, 0.00, 235000.00, 5.00, 11750.00, 223250.00,
    'CONFIRMED', 'VNPAY', 'paid', 'VND',
    NOW(), NULL, NULL, NOW()-INTERVAL '12 hours', TRUE),
(5, 'ORD-2026-005', 7, 'Đỗ Thị Phương', '0987654321', 'customer2@example.com',
    '456 Đường DEF, Phường Bến Nghé', 'Hồ Chí Minh', 'Quận 1',       'Bến Nghé',
    4, 280000.00, 30000.00, 0.00, 310000.00, 5.00, 15500.00, 294500.00,
    'PENDING', 'COD', 'unpaid', 'VND',
    NULL, NULL, NULL, NOW()-INTERVAL '3 hours', TRUE);

-- ============================================================================
-- 12b. ORDER_STATUS_LOGS
-- ============================================================================
INSERT INTO order_status_logs (order_id, old_status, new_status, actor_id, role, note, timestamp) VALUES
(1, NULL,         'PENDING',    6, 'consumer', 'Đặt hàng qua mobile app. Phương thức: COD',              NOW()-INTERVAL '6 days'),
(1, 'PENDING',    'CONFIRMED',  3, 'seller',   'Seller xác nhận đơn hàng',                               NOW()-INTERVAL '5 days 22 hours'),
(1, 'CONFIRMED',  'PROCESSING', 3, 'seller',   'Đang chuẩn bị hàng',                                    NOW()-INTERVAL '5 days 20 hours'),
(1, 'PROCESSING', 'SHIPPING',   3, 'seller',   'Tạo vận đơn GHN, tracking: GHN-VN-7654321',             NOW()-INTERVAL '4 days'),
(1, 'SHIPPING',   'DELIVERED',  NULL,'system', 'Cập nhật tự động từ GHN webhook',                        NOW()-INTERVAL '2 days'),
(2, NULL,         'PENDING',    7, 'consumer', 'Đặt hàng qua mobile app. Phương thức: BANK_TRANSFER',    NOW()-INTERVAL '4 days'),
(2, 'PENDING',    'CONFIRMED',  4, 'seller',   'Seller xác nhận đơn hàng',                               NOW()-INTERVAL '3 days 20 hours'),
(2, 'CONFIRMED',  'SHIPPING',   4, 'seller',   'Tạo vận đơn GHTK, tracking: GHTK-VN-8765432',           NOW()-INTERVAL '2 days'),
(3, NULL,         'PENDING',    6, 'consumer', 'Đặt hàng qua mobile app. Phương thức: MOMO',             NOW()-INTERVAL '2 days'),
(3, 'PENDING',    'CONFIRMED',  5, 'seller',   'Seller xác nhận đơn hàng',                               NOW()-INTERVAL '1 day 20 hours'),
(3, 'CONFIRMED',  'PROCESSING', 5, 'seller',   'Đang chuẩn bị hàng',                                    NOW()-INTERVAL '1 day'),
(4, NULL,         'PENDING',    8, 'consumer', 'Đặt hàng qua mobile app. Phương thức: VNPAY',            NOW()-INTERVAL '12 hours'),
(4, 'PENDING',    'CONFIRMED',  3, 'seller',   'Seller xác nhận đơn hàng',                               NOW()-INTERVAL '11 hours'),
(5, NULL,         'PENDING',    7, 'consumer', 'Đặt hàng qua mobile app. Phương thức: COD',              NOW()-INTERVAL '3 hours');

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
    platform_fee_percentage, platform_fee_amount, seller_amount, status, payment_cycle,
    vnpay_transaction_no, vnpay_response_code, vnpay_bank_code, amount_from_gateway, amount_mismatch,
    refunded_amount, refund_note, refunded_at) VALUES
(1, 1, 6, 3,  85000.00, 'VND', 5.00,  4250.00,  80750.00, 'PARTIAL_REFUNDED', 'WEEKLY',  NULL, NULL, NULL, NULL, FALSE, 30000.00, 'Hoàn tiền một phần do yêu cầu trả hàng RR-001', NOW()-INTERVAL '1 day'),
(2, 2, 7, 4, 370000.00, 'VND', 5.00, 18500.00, 351500.00, 'COMPLETED',        'WEEKLY',  NULL, NULL, NULL, NULL, FALSE, NULL,     NULL,                                         NULL),
(3, 3, 6, 5, 475000.00, 'VND', 5.00, 23750.00, 451250.00, 'PENDING',          'MONTHLY', NULL, NULL, NULL, NULL, FALSE, NULL,     NULL,                                         NULL),
(4, 4, 8, 3, 235000.00, 'VND', 5.00, 11750.00, 223250.00, 'COMPLETED', 'WEEKLY',
    'VNP-TXN-20260405-004', '00', 'NCB', 235000.00, FALSE, NULL, NULL, NULL);

-- ============================================================================
-- 15. PAYMENT_TRANSACTIONS
-- Columns: payment_id, transaction_type, amount, status, notes, created_at
-- ============================================================================
INSERT INTO payment_transactions (payment_id, transaction_type, amount, status, notes, gateway_ref, created_at) VALUES
(1, 'payment',  85000.00, 'COMPLETED', 'Thanh toán COD đơn ORD-2026-001',          NULL,                    NOW()-INTERVAL '2 days'),
(2, 'payment', 370000.00, 'COMPLETED', 'Thanh toán chuyển khoản đơn ORD-2026-002', NULL,                    NOW()-INTERVAL '2 days'),
(3, 'payment', 475000.00, 'PENDING',   'Thanh toán MoMo đơn ORD-2026-003',         NULL,                    NOW()),
(4, 'payment', 235000.00, 'COMPLETED', 'Thanh toán VNPay đơn ORD-2026-004',        'VNP-TXN-20260405-004', NOW());

-- ============================================================================
-- 15b. PAYMENT_AUDIT_LOGS
-- ============================================================================
INSERT INTO payment_audit_logs (payment_id, action, actor_id, amount, note, ip_address, timestamp) VALUES
(1,    'IPN_RECEIVED',  NULL, 85000.00,  'COD thu tiền khi giao hàng. GHN webhook DELIVERED.',              NULL,            NOW()-INTERVAL '2 days'),
(1,    'REFUND_PROCESSED', 2, 30000.00,  'Hoàn tiền một phần theo yêu cầu trả hàng #1',                     '10.10.10.10',   NOW()-INTERVAL '1 day 2 hours'),
(2,    'IPN_RECEIVED',  NULL, 370000.00, 'BANK_TRANSFER xác nhận. txn=BANK-TXN-002, bank=BIDV',             NULL,            NOW()-INTERVAL '2 days'),
(4,    'VNPAY_RETURN',  NULL, 235000.00, 'return url. code=00, mismatch=False. txn=VNP-TXN-20260405-004',   '192.168.1.100', NOW()),
(4,    'IPN_RECEIVED',  NULL, 235000.00, 'txn=VNP-TXN-20260405-004, code=00, bank=NCB',                     NULL,            NOW()),
(NULL, 'CONFIG_FEE',    1,    NULL,      'Set platform fee = 5%',                                            '127.0.0.1',    NOW()-INTERVAL '60 days'),
(NULL, 'CONFIG_CYCLE',  1,    NULL,      'Set payment cycle = WEEKLY',                                       '127.0.0.1',    NOW()-INTERVAL '60 days');

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
    category, priority, title, description, images, status, handled_by, resolution, resolution_type,
    assigned_at, first_response_at, resolved_at, closed_at) VALUES
(7, NULL, 6, 'PRODUCT_QUALITY',
    'QUALITY', 'MEDIUM',
    'Sản phẩm giỏ đan tre chưa được duyệt',
    'Tôi muốn mua giỏ đan tre nhưng sản phẩm chưa được duyệt để đặt hàng',
    '["https://cdn.local/complaints/cp-001-1.jpg"]',
    'RESOLVED', 2, 'Đã liên hệ người bán để bổ sung ảnh và hoàn thiện thông tin', 'SELLER_COORDINATION',
    NOW()-INTERVAL '8 days', NOW()-INTERVAL '7 days', NOW()-INTERVAL '6 days', NOW()-INTERVAL '5 days'),
(NULL, 2, 7, 'DELIVERY',
    'DELIVERY', 'HIGH',
    'Đơn hàng giao chậm hơn dự kiến',
    'Đơn ORD-2026-002 đã 2 ngày chưa thấy cập nhật trạng thái vận chuyển',
    '["https://cdn.local/complaints/cp-002-1.jpg","https://cdn.local/complaints/cp-002-2.jpg"]',
    'IN_PROGRESS', 2, NULL, 'CARRIER_ESCALATION',
    NOW()-INTERVAL '2 days', NOW()-INTERVAL '1 day', NULL, NULL);

-- ============================================================================
-- 17b. COMPLAINT_COMMENTS & COMPLAINT_STATUS_LOGS
-- ============================================================================
INSERT INTO complaint_comments (complaint_id, author_id, role, message, is_internal, created_at) VALUES
(1, 6, 'buyer',  'Tôi muốn mua giỏ đan tre nhưng thấy sản phẩm chưa được duyệt. Khi nào có thể mua?', FALSE, NOW()-INTERVAL '8 days'),
(1, 2, 'admin',  'Chúng tôi đã liên hệ với người bán và yêu cầu bổ sung ảnh sản phẩm.',               FALSE, NOW()-INTERVAL '7 days'),
(1, 2, 'admin',  '[Ghi chú nội bộ] Seller5 đã được nhắc nhở. Hạn bổ sung: 3 ngày.',                   TRUE,  NOW()-INTERVAL '7 days'),
(1, 6, 'buyer',  'Cảm ơn, tôi sẽ chờ thêm.',                                                          FALSE, NOW()-INTERVAL '6 days'),
(2, 7, 'buyer',  'Đơn ORD-2026-002 giao từ 2 ngày trước mà vẫn chưa đến. Tracking: GHTK-VN-8765432.', FALSE, NOW()-INTERVAL '2 days'),
(2, 2, 'admin',  'Chúng tôi đã liên hệ GHTK để kiểm tra. Hàng đang trên đường, giao ngày mai.',        FALSE, NOW()-INTERVAL '1 day'),
(2, 4, 'seller', 'Xin lỗi vì sự chậm trễ. Hàng tôi đã bàn giao cho GHTK đúng hạn.',                  FALSE, NOW()-INTERVAL '1 day'),
(2, 2, 'admin',  '[Ghi chú nội bộ] Lỗi từ GHTK, không phải seller.',                                  TRUE,  NOW()-INTERVAL '20 hours');

INSERT INTO complaint_status_logs (complaint_id, old_status, new_status, actor_id, note, timestamp) VALUES
(1, NULL,           'PENDING',     6, 'Khiếu nại được tạo mới',                              NOW()-INTERVAL '8 days'),
(1, 'PENDING',      'ASSIGNED',    2, 'Giao cho user #2 (Nguyễn Văn An)',                    NOW()-INTERVAL '8 days'),
(1, 'ASSIGNED',     'IN_PROGRESS', 2, 'Tự động IN_PROGRESS khi CS phản hồi lần đầu',         NOW()-INTERVAL '7 days'),
(1, 'IN_PROGRESS',  'RESOLVED',    2, 'Đã liên hệ người bán bổ sung ảnh',                   NOW()-INTERVAL '6 days'),
(2, NULL,           'PENDING',     7, 'Khiếu nại được tạo mới',                              NOW()-INTERVAL '2 days'),
(2, 'PENDING',      'ASSIGNED',    2, 'Giao cho user #2 (Nguyễn Văn An)',                    NOW()-INTERVAL '2 days'),
(2, 'ASSIGNED',     'IN_PROGRESS', 2, 'Tự động IN_PROGRESS khi CS phản hồi lần đầu',         NOW()-INTERVAL '1 day');

-- ============================================================================
-- 18. CONTENTS
-- ============================================================================
INSERT INTO contents (id, title, content, content_type, author_id, product_id,
    status, approved_by, approved_at, is_active, deleted_at, deleted_by, rejection_reason) VALUES
(1, 'Hướng dẫn chọn rau sạch',
    'Bài viết hướng dẫn cách nhận biết và chọn rau sạch an toàn...',
    'ARTICLE', 3, 1, 'APPROVED', 2, NOW()-INTERVAL '10 days', TRUE,  NULL,                 NULL, NULL),
(2, 'Giới thiệu gốm Bát Tràng',
    'Bài viết về nghề làm gốm truyền thống Bát Tràng, lịch sử hơn 500 năm...',
    'ARTICLE', 4, 5, 'APPROVED', 2, NOW()-INTERVAL '8 days',  TRUE,  NULL,                 NULL, NULL),
(3, 'Video quy trình sản xuất khăn thêu',
    'Video giới thiệu quy trình thêu tay truyền thống của nghệ nhân Huế...',
    'VIDEO', 5, 8, 'REJECTED', NULL, NULL, TRUE,  NULL,                 NULL, 'Thiếu thông tin bản quyền hình ảnh/video.'),
(4, 'Câu chuyện của người nông dân',
    'Hành trình khởi nghiệp từ cánh đồng của chị Trần Thị Bình...',
    'ARTICLE', 2, NULL, 'APPROVED', 1, NOW()-INTERVAL '5 days', FALSE, NOW()-INTERVAL '1 day', 1,    NULL);

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

INSERT INTO cart_items (cart_id, product_id, variant_id, quantity, unit_price) VALUES
(1, 3,  NULL, 2,  50000.00),
(1, 10, NULL, 1, 250000.00),
(2, 5,  NULL, 1, 350000.00),
(2, 6,  NULL, 2, 280000.00),
(3, 1,  NULL, 3,  25000.00),
(3, 9,  NULL, 1, 180000.00);

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

-- Liên kết complaint đã xử lý với yêu cầu trả hàng
UPDATE complaints
SET return_request_id = 1
WHERE id = 1;

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
    batch_number, production_date, expiry_date, ingredients, process_summary,
    verification_status, verified_by, verified_at, rejection_reason) VALUES
(1, 1,  'Thôn Tân Lập, Đan Phượng', 1, 'Hộ nông dân Trần Thị Bình',
    'LOT-RAU-2026-001',  '2026-03-28', '2026-04-03',
    'Rau cải xanh 100% tự nhiên, không thuốc trừ sâu',
    'Gieo hạt → Bón phân hữu cơ → Thu hoạch → Rửa sạch → Đóng gói',
    'VERIFIED', 1, NOW()-INTERVAL '12 days', NULL),
(2, 3,  'Vùng cam Hà Giang', 1, 'HTX Nông nghiệp Hà Giang',
    'LOT-CAM-2026-012',  '2026-03-10', '2026-04-10',
    'Cam sành nguyên chất, không chất bảo quản',
    'Thu hoạch → Phân loại → Rửa sạch → Đóng thùng → Vận chuyển lạnh',
    'VERIFIED', 2, NOW()-INTERVAL '10 days', NULL),
(3, 5,  'Làng nghề Bát Tràng', 1, 'Gia đình nghệ nhân Lê Văn Cường',
    'LOT-GOM-2026-005',  '2026-02-15', NULL,
    'Đất sét Bát Tràng, men sứ tự nhiên',
    'Lấy đất → Nhào nặn → Tạo hình → Phơi khô → Tráng men → Nung 1200°C → Kiểm tra',
    'VERIFIED', 1, NOW()-INTERVAL '9 days', NULL),
(4, 10, 'Đảo Phú Quốc', 3, 'Cơ sở sản xuất tiêu Phú Quốc',
    'LOT-TIEU-2026-003', '2026-01-05', '2028-01-04',
    'Tiêu đen Phú Quốc hạt nguyên, không phụ gia',
    'Thu hoạch → Phơi nắng 5–7 ngày → Sàng lọc → Đóng gói hút chân không',
    'PENDING', NULL, NULL, NULL);

-- ============================================================================
-- 28. CONTENT_AUDIT_LOGS
-- ============================================================================
INSERT INTO content_audit_logs (id, content_id, action, user_id, old_status, new_status, notes, created_at) VALUES
(1, 1, 'CREATE',  3, NULL,      'PENDING',  'Seller tạo bài viết ban đầu',                              NOW()-INTERVAL '11 days'),
(2, 1, 'APPROVE', 2, 'PENDING', 'APPROVED', 'Duyệt bài viết hướng dẫn rau sạch',                        NOW()-INTERVAL '10 days'),
(3, 3, 'CREATE',  5, NULL,      'PENDING',  'Tạo nội dung video giới thiệu quy trình',                  NOW()-INTERVAL '3 days'),
(4, 3, 'REJECT',  2, 'PENDING', 'REJECTED', 'Thiếu giấy tờ bản quyền hình ảnh trong video',             NOW()-INTERVAL '2 days'),
(5, 4, 'DELETE',  1, 'APPROVED','APPROVED', 'Ẩn tạm nội dung để chỉnh sửa thông tin tác giả',           NOW()-INTERVAL '1 day');

-- ============================================================================
-- 29. PRODUCT_PRICE_LOGS
-- ============================================================================
INSERT INTO product_price_logs (id, product_id, old_price, new_price, changed_by, reason, created_at) VALUES
(1, 4,  110000.00, 120000.00, 1, 'Điều chỉnh giá theo mùa vụ xoài',                 NOW()-INTERVAL '15 days'),
(2, 6,  260000.00, 280000.00, 4, 'Cập nhật chi phí nguyên liệu gốm',                 NOW()-INTERVAL '9 days'),
(3, 10, 240000.00, 250000.00, 2, 'Điều chỉnh theo biến động nguồn cung hồ tiêu',     NOW()-INTERVAL '4 days');

-- ============================================================================
-- 30. REFRESH_TOKENS
-- ============================================================================
INSERT INTO refresh_tokens (
    id, user_id, jti, family_id, token_hash, expires_at,
    revoked_at, replaced_by_jti, created_by_ip, created_by_user_agent,
    revoked_reason, created_at, updated_at
) VALUES
(1, 6, 'jti_u6_fam1_0001', 'fam_u6_2026_04',
    '9f6d1d4d9f7bbac9b7a3fd4a8a7f9f12901a30f95e5b6c2f31dbf6f24fce0011',
    NOW() + INTERVAL '20 days', NULL, NULL, '171.244.1.10', 'iOSApp/1.4.2', NULL,
    NOW()-INTERVAL '1 day', NOW()-INTERVAL '1 day'),
(2, 6, 'jti_u6_fam1_0000', 'fam_u6_2026_04',
    'e1adff4beea24bb3e1b1f9f80447f2d060f37d7a7d49651d283f2d4f7b430022',
    NOW() + INTERVAL '10 days', NOW()-INTERVAL '2 days', 'jti_u6_fam1_0001', '171.244.1.10', 'iOSApp/1.4.1', 'ROTATED',
    NOW()-INTERVAL '6 days', NOW()-INTERVAL '2 days'),
(3, 7, 'jti_u7_fam1_0001', 'fam_u7_2026_04',
    'd2bc1a3e4d8f7aa29a50f0b7e6c65ed9090ecb8e83c23a8f35c7ec6d1810a033',
    NOW() + INTERVAL '25 days', NULL, NULL, '203.113.8.15', 'AndroidApp/2.0.0', NULL,
    NOW()-INTERVAL '8 hours', NOW()-INTERVAL '8 hours');

-- ============================================================================
-- 31. AI_MODERATION_LOGS
-- ============================================================================
INSERT INTO ai_moderation_logs (
    id, product_id, content_id, rule_engine_result, rule_engine_flags,
    model_used, ai_decision, ai_confidence, ai_reasons, ai_flags,
    escalated, escalation_reason, processing_time_ms,
    input_tokens, output_tokens, estimated_cost_usd, raw_response, created_at
) VALUES
(1, 7, NULL, 'FLAGGED', 'missing_product_images',
    'gpt-4o-mini', 'REVIEW', 0.82, 'Thiếu ảnh minh họa sản phẩm tối thiểu', 'image_missing',
    TRUE, 'Cần duyệt thủ công bởi content_manager', 612,
    820, 156, 0.0042, '{"decision":"REVIEW","reason":"missing images"}', NOW()-INTERVAL '7 days'),
(2, NULL, 3, 'FLAGGED', 'copyright_risk',
    'gpt-4o-mini', 'REJECT', 0.91, 'Nghi ngờ vi phạm bản quyền tư liệu video', 'copyright',
    TRUE, 'Yêu cầu người đăng bổ sung bằng chứng bản quyền', 734,
    1040, 201, 0.0061, '{"decision":"REJECT","reason":"copyright risk"}', NOW()-INTERVAL '2 days'),
(3, 1, NULL, 'PASS', NULL,
    'gpt-4o-mini', 'APPROVE', 0.97, 'Mô tả sản phẩm hợp lệ, không phát hiện rủi ro', NULL,
    FALSE, NULL, 401,
    560, 98, 0.0026, '{"decision":"APPROVE"}', NOW()-INTERVAL '10 days');

-- ============================================================================
-- 32. AI_GENERATION_CACHE
-- ============================================================================
INSERT INTO ai_generation_cache (id, input_hash, task_type, model_used, input_text, output_text, created_at, expires_at) VALUES
(1, 'a5a4559b7f7f8f62e0e84f985fd3f7f3a2b98d1d08aa5c96f0d3a0c7c2f10001', 'PRODUCT_SUMMARY', 'gpt-4o-mini',
    'Rau cải xanh hữu cơ, không thuốc trừ sâu, thu hoạch trong ngày',
    'Rau cải xanh hữu cơ tươi sạch, an toàn cho bữa cơm gia đình.', NOW()-INTERVAL '4 days', NOW()+INTERVAL '3 days'),
(2, 'b3b7f994f02f90a3de66d9c3ca0d9d2ab5e06d89c5b99cc4a61ea90ec7810002', 'SEO_TITLE', 'gpt-4o-mini',
    'Bình gốm Bát Tràng thủ công cao cấp',
    'Bình gốm Bát Tràng thủ công: Tinh hoa gốm Việt cho không gian sống', NOW()-INTERVAL '2 days', NOW()+INTERVAL '5 days');

-- ============================================================================
-- 33. AI_COST_LOGS
-- ============================================================================
INSERT INTO ai_cost_logs (id, log_date, model_id, task_type, request_count, total_input_tokens, total_output_tokens, total_cost_usd) VALUES
(1, CURRENT_DATE - 2, 'gpt-4o-mini', 'MODERATION',       32, 28450, 5410, 0.2184),
(2, CURRENT_DATE - 1, 'gpt-4o-mini', 'PRODUCT_SUMMARY',  18, 13220, 3780, 0.1241),
(3, CURRENT_DATE - 1, 'gpt-4o-mini', 'SEO_TITLE',        11,  4210,  980, 0.0395);

-- ============================================================================
-- 34. PRODUCT_EMBEDDINGS
-- ============================================================================
INSERT INTO product_embeddings (id, product_id, embedding_text, embedding_vector, vector_dimension, model_version, created_at, updated_at) VALUES
(1, 1,  'Rau cải xanh hữu cơ tươi sạch không thuốc trừ sâu', '[0.012,0.155,0.447,0.083,0.390,0.221,0.064,0.118]', 8, 'text-embedding-3-small@2026-03', NOW()-INTERVAL '10 days', NOW()-INTERVAL '10 days'),
(2, 5,  'Bình gốm Bát Tràng thủ công truyền thống cao cấp',  '[0.332,0.071,0.214,0.455,0.102,0.184,0.290,0.016]', 8, 'text-embedding-3-small@2026-03', NOW()-INTERVAL '8 days',  NOW()-INTERVAL '8 days'),
(3, 10, 'Tiêu đen Phú Quốc nguyên hạt thơm nồng tự nhiên',   '[0.087,0.241,0.301,0.094,0.510,0.068,0.132,0.225]', 8, 'text-embedding-3-small@2026-03', NOW()-INTERVAL '4 days',  NOW()-INTERVAL '4 days');

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
SELECT setval('content_audit_logs_id_seq',   (SELECT MAX(id) FROM content_audit_logs));
SELECT setval('product_price_logs_id_seq',   (SELECT MAX(id) FROM product_price_logs));
SELECT setval('refresh_tokens_id_seq',       (SELECT MAX(id) FROM refresh_tokens));
SELECT setval('ai_moderation_logs_id_seq',   (SELECT MAX(id) FROM ai_moderation_logs));
SELECT setval('ai_generation_cache_id_seq',  (SELECT MAX(id) FROM ai_generation_cache));
SELECT setval('ai_cost_logs_id_seq',         (SELECT MAX(id) FROM ai_cost_logs));
SELECT setval('product_embeddings_id_seq',   (SELECT MAX(id) FROM product_embeddings));
SELECT setval('order_status_logs_id_seq',    (SELECT MAX(id) FROM order_status_logs));
SELECT setval('complaint_comments_id_seq',   (SELECT MAX(id) FROM complaint_comments));
SELECT setval('complaint_status_logs_id_seq',(SELECT MAX(id) FROM complaint_status_logs));
SELECT setval('payment_audit_logs_id_seq',   (SELECT MAX(id) FROM payment_audit_logs));

-- ============================================================================
-- HOÀN TẤT
-- ============================================================================
SELECT 'Database reset & seed HOÀN TẤT! (tích hợp đầy đủ schema mới)' AS result;
