BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 16e7f7b9034c

CREATE TABLE organizations (
    id SERIAL NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_organizations_id ON organizations (id);

CREATE TYPE permissiontype AS ENUM ('CATALOGUE', 'MENU');

CREATE TABLE permissions (
    id SERIAL NOT NULL, 
    parent_id INTEGER, 
    name VARCHAR(255) NOT NULL, 
    label VARCHAR(255) NOT NULL, 
    type permissiontype NOT NULL, 
    route VARCHAR(255), 
    status VARCHAR(50), 
    "order" INTEGER, 
    icon VARCHAR(255), 
    component VARCHAR(255), 
    hide BOOLEAN, 
    hide_tab BOOLEAN, 
    frame_src VARCHAR(500), 
    new_feature BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(parent_id) REFERENCES permissions (id), 
    UNIQUE (name)
);

CREATE INDEX ix_permissions_id ON permissions (id);

CREATE TABLE roles (
    id SERIAL NOT NULL, 
    role_name VARCHAR(255) NOT NULL, 
    description TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    UNIQUE (role_name)
);

CREATE INDEX ix_roles_id ON roles (id);

CREATE TABLE users (
    id SERIAL NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    gender VARCHAR(50), 
    activated INTEGER, 
    type VARCHAR(50), 
    created_by VARCHAR(255), 
    updated_by VARCHAR(255), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    deleted_by VARCHAR(255), 
    deleted_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_id ON users (id);

CREATE TABLE medias (
    id SERIAL NOT NULL, 
    filename VARCHAR(255) NOT NULL, 
    file_path VARCHAR(500) NOT NULL, 
    file_type VARCHAR(100), 
    file_size INTEGER, 
    mime_type VARCHAR(100), 
    uploaded_by INTEGER, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(uploaded_by) REFERENCES users (id)
);

CREATE INDEX ix_medias_id ON medias (id);

CREATE TYPE contractstatus AS ENUM ('DRAFT', 'ACTIVE', 'EXPIRED', 'CANCELLED');

CREATE TABLE partner_contracts (
    id SERIAL NOT NULL, 
    contract_number VARCHAR(100) NOT NULL, 
    partner_id INTEGER NOT NULL, 
    contract_type VARCHAR(50) NOT NULL, 
    start_date TIMESTAMP WITH TIME ZONE NOT NULL, 
    end_date TIMESTAMP WITH TIME ZONE, 
    amount NUMERIC(10, 2), 
    status contractstatus, 
    terms TEXT, 
    created_by INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(created_by) REFERENCES users (id), 
    FOREIGN KEY(partner_id) REFERENCES users (id), 
    UNIQUE (contract_number)
);

CREATE INDEX ix_partner_contracts_id ON partner_contracts (id);

CREATE TYPE paymentstatus AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED');

CREATE TYPE paymentcycle AS ENUM ('WEEKLY', 'MONTHLY');

CREATE TABLE payments (
    id SERIAL NOT NULL, 
    order_id INTEGER NOT NULL, 
    customer_id INTEGER NOT NULL, 
    seller_id INTEGER NOT NULL, 
    amount NUMERIC(10, 2) NOT NULL, 
    platform_fee_percentage NUMERIC(5, 2), 
    platform_fee_amount NUMERIC(10, 2) NOT NULL, 
    seller_amount NUMERIC(10, 2) NOT NULL, 
    status paymentstatus, 
    payment_cycle paymentcycle, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(customer_id) REFERENCES users (id), 
    FOREIGN KEY(seller_id) REFERENCES users (id)
);

CREATE INDEX ix_payments_id ON payments (id);

CREATE TYPE productstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

CREATE TABLE products (
    id SERIAL NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    price NUMERIC(10, 2) NOT NULL, 
    producer_id INTEGER NOT NULL, 
    status productstatus, 
    label VARCHAR(50), 
    images TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(producer_id) REFERENCES users (id)
);

CREATE INDEX ix_products_id ON products (id);

CREATE TABLE role_permissions (
    id SERIAL NOT NULL, 
    role_id INTEGER NOT NULL, 
    permission_id INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(permission_id) REFERENCES permissions (id), 
    FOREIGN KEY(role_id) REFERENCES roles (id)
);

CREATE INDEX ix_role_permissions_id ON role_permissions (id);

CREATE TABLE user_organizations (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    organization_id INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_user_organizations_id ON user_organizations (id);

CREATE TABLE user_roles (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    role_id INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(role_id) REFERENCES roles (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_user_roles_id ON user_roles (id);

CREATE TYPE complaintstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'RESOLVED', 'CLOSED');

CREATE TABLE complaints (
    id SERIAL NOT NULL, 
    product_id INTEGER, 
    order_id INTEGER, 
    user_id INTEGER NOT NULL, 
    complaint_type VARCHAR(50) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    description TEXT NOT NULL, 
    status complaintstatus, 
    handled_by INTEGER, 
    resolution TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(handled_by) REFERENCES users (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_complaints_id ON complaints (id);

CREATE TYPE contentstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

CREATE TABLE contents (
    id SERIAL NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    content TEXT, 
    content_type VARCHAR(50) NOT NULL, 
    author_id INTEGER NOT NULL, 
    product_id INTEGER, 
    status contentstatus, 
    images TEXT, 
    videos TEXT, 
    approved_by INTEGER, 
    approved_at TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(approved_by) REFERENCES users (id), 
    FOREIGN KEY(author_id) REFERENCES users (id), 
    FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_contents_id ON contents (id);

CREATE TABLE payment_transactions (
    id SERIAL NOT NULL, 
    payment_id INTEGER NOT NULL, 
    transaction_type VARCHAR(50) NOT NULL, 
    amount NUMERIC(10, 2) NOT NULL, 
    status paymentstatus NOT NULL, 
    notes TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(payment_id) REFERENCES payments (id)
);

CREATE INDEX ix_payment_transactions_id ON payment_transactions (id);

CREATE TABLE product_approvals (
    id SERIAL NOT NULL, 
    product_id INTEGER NOT NULL, 
    approver_id INTEGER NOT NULL, 
    status productstatus NOT NULL, 
    notes TEXT, 
    checked_description BOOLEAN, 
    checked_price BOOLEAN, 
    checked_images BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(approver_id) REFERENCES users (id), 
    FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_product_approvals_id ON product_approvals (id);

CREATE TABLE reviews (
    id SERIAL NOT NULL, 
    product_id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL, 
    rating INTEGER NOT NULL, 
    comment TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_reviews_id ON reviews (id);

INSERT INTO alembic_version (version_num) VALUES ('16e7f7b9034c') RETURNING alembic_version.version_num;

-- Running upgrade 16e7f7b9034c -> b7c8d9e0f1a2

UPDATE alembic_version SET version_num='b7c8d9e0f1a2' WHERE alembic_version.version_num = '16e7f7b9034c';

-- Running upgrade 16e7f7b9034c -> d709296f8c5c

CREATE TABLE categories (
    id SERIAL NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    slug VARCHAR(255) NOT NULL, 
    description TEXT, 
    icon VARCHAR(100), 
    image TEXT, 
    parent_id INTEGER, 
    "order" INTEGER, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE INDEX ix_categories_id ON categories (id);

CREATE UNIQUE INDEX ix_categories_slug ON categories (slug);

CREATE TABLE regions (
    id SERIAL NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    slug VARCHAR(255) NOT NULL, 
    description TEXT, 
    image TEXT, 
    latitude VARCHAR(50), 
    longitude VARCHAR(50), 
    "order" INTEGER, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE INDEX ix_regions_id ON regions (id);

CREATE UNIQUE INDEX ix_regions_slug ON regions (slug);

CREATE TYPE orderstatus AS ENUM ('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPING', 'DELIVERED', 'CANCELLED', 'REFUNDED');

CREATE TYPE paymentmethod AS ENUM ('COD', 'BANK_TRANSFER', 'MOMO', 'VNPAY', 'ZALOPAY');

CREATE TABLE orders (
    id SERIAL NOT NULL, 
    order_number VARCHAR(50) NOT NULL, 
    customer_id INTEGER NOT NULL, 
    customer_name VARCHAR(255) NOT NULL, 
    customer_phone VARCHAR(20) NOT NULL, 
    customer_email VARCHAR(255), 
    shipping_address TEXT NOT NULL, 
    shipping_province VARCHAR(100), 
    shipping_district VARCHAR(100), 
    shipping_ward VARCHAR(100), 
    seller_id INTEGER NOT NULL, 
    subtotal NUMERIC(15, 2) NOT NULL, 
    shipping_fee NUMERIC(10, 2) NOT NULL, 
    discount_amount NUMERIC(10, 2) NOT NULL, 
    total_amount NUMERIC(15, 2) NOT NULL, 
    platform_fee_percentage NUMERIC(5, 2) NOT NULL, 
    platform_fee_amount NUMERIC(10, 2) NOT NULL, 
    seller_amount NUMERIC(15, 2) NOT NULL, 
    status orderstatus, 
    payment_method paymentmethod, 
    payment_status VARCHAR(20), 
    customer_note TEXT, 
    seller_note TEXT, 
    admin_note TEXT, 
    cancel_reason TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    confirmed_at TIMESTAMP WITH TIME ZONE, 
    shipped_at TIMESTAMP WITH TIME ZONE, 
    delivered_at TIMESTAMP WITH TIME ZONE, 
    cancelled_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(customer_id) REFERENCES users (id), 
    FOREIGN KEY(seller_id) REFERENCES users (id)
);

CREATE INDEX ix_orders_id ON orders (id);

CREATE UNIQUE INDEX ix_orders_order_number ON orders (order_number);

CREATE TABLE order_items (
    id SERIAL NOT NULL, 
    order_id INTEGER NOT NULL, 
    product_id INTEGER NOT NULL, 
    product_name VARCHAR(255) NOT NULL, 
    product_image TEXT, 
    unit_price NUMERIC(15, 2) NOT NULL, 
    quantity INTEGER NOT NULL, 
    total_price NUMERIC(15, 2) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_order_items_id ON order_items (id);

INSERT INTO alembic_version (version_num) VALUES ('d709296f8c5c') RETURNING alembic_version.version_num;

-- Running upgrade d709296f8c5c -> a1b2c3d4e5f6

ALTER TABLE products ADD COLUMN category_id INTEGER;

ALTER TABLE products ADD CONSTRAINT fk_products_category_id FOREIGN KEY(category_id) REFERENCES categories (id);

UPDATE alembic_version SET version_num='a1b2c3d4e5f6' WHERE alembic_version.version_num = 'd709296f8c5c';

-- Running upgrade a1b2c3d4e5f6, b7c8d9e0f1a2 -> 944b201b5ae7

DELETE FROM alembic_version WHERE alembic_version.version_num = 'a1b2c3d4e5f6';

UPDATE alembic_version SET version_num='944b201b5ae7' WHERE alembic_version.version_num = 'b7c8d9e0f1a2';

-- Running upgrade 944b201b5ae7 -> b82aa2f98076

CREATE TYPE promotiontype AS ENUM ('PERCENTAGE', 'FIXED_AMOUNT');

CREATE TYPE promotionstatus AS ENUM ('ACTIVE', 'INACTIVE', 'EXPIRED');

CREATE TABLE promotions (
    id SERIAL NOT NULL, 
    code VARCHAR(50) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    promotion_type promotiontype NOT NULL, 
    discount_value NUMERIC(12, 2) NOT NULL, 
    min_order_amount NUMERIC(12, 2), 
    max_discount_amount NUMERIC(12, 2), 
    usage_limit INTEGER, 
    used_count INTEGER, 
    start_date TIMESTAMP WITH TIME ZONE NOT NULL, 
    end_date TIMESTAMP WITH TIME ZONE NOT NULL, 
    status promotionstatus, 
    is_public BOOLEAN, 
    created_by INTEGER, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_promotions_code ON promotions (code);

CREATE INDEX ix_promotions_id ON promotions (id);

CREATE TABLE carts (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id), 
    UNIQUE (user_id)
);

CREATE INDEX ix_carts_id ON carts (id);

CREATE TYPE businesstype AS ENUM ('INDIVIDUAL', 'HOUSEHOLD', 'COOPERATIVE', 'COMPANY');

CREATE TYPE verificationstatus AS ENUM ('PENDING', 'VERIFIED', 'REJECTED');

CREATE TABLE seller_profiles (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    business_name VARCHAR(255) NOT NULL, 
    business_type businesstype, 
    description TEXT, 
    address TEXT, 
    id_card_number VARCHAR(20), 
    id_card_front_url TEXT, 
    id_card_back_url TEXT, 
    business_license_url TEXT, 
    bank_name VARCHAR(255), 
    bank_account_number VARCHAR(50), 
    bank_account_name VARCHAR(255), 
    verification_status verificationstatus, 
    verified_by INTEGER, 
    verified_at TIMESTAMP WITH TIME ZONE, 
    rejection_reason TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id), 
    FOREIGN KEY(verified_by) REFERENCES users (id), 
    UNIQUE (user_id)
);

CREATE INDEX ix_seller_profiles_id ON seller_profiles (id);

CREATE TABLE seller_wallets (
    id SERIAL NOT NULL, 
    seller_id INTEGER NOT NULL, 
    pending_balance NUMERIC(15, 2) NOT NULL, 
    available_balance NUMERIC(15, 2) NOT NULL, 
    total_withdrawn NUMERIC(15, 2) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(seller_id) REFERENCES users (id), 
    UNIQUE (seller_id)
);

CREATE INDEX ix_seller_wallets_id ON seller_wallets (id);

CREATE TYPE settlementstatus AS ENUM ('PENDING', 'APPROVED', 'COMPLETED');

CREATE TABLE settlements (
    id SERIAL NOT NULL, 
    seller_id INTEGER NOT NULL, 
    period_start TIMESTAMP WITH TIME ZONE NOT NULL, 
    period_end TIMESTAMP WITH TIME ZONE NOT NULL, 
    total_orders INTEGER NOT NULL, 
    total_amount NUMERIC(15, 2) NOT NULL, 
    total_platform_fee NUMERIC(15, 2) NOT NULL, 
    total_seller_amount NUMERIC(15, 2) NOT NULL, 
    status settlementstatus, 
    approved_by INTEGER, 
    approved_at TIMESTAMP WITH TIME ZONE, 
    note TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(approved_by) REFERENCES users (id), 
    FOREIGN KEY(seller_id) REFERENCES users (id)
);

CREATE INDEX ix_settlements_id ON settlements (id);

CREATE TABLE cart_items (
    id SERIAL NOT NULL, 
    cart_id INTEGER NOT NULL, 
    product_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL, 
    unit_price NUMERIC(15, 2) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(cart_id) REFERENCES carts (id), 
    FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE INDEX ix_cart_items_id ON cart_items (id);

CREATE TYPE payoutstatus AS ENUM ('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED');

CREATE TABLE payouts (
    id SERIAL NOT NULL, 
    seller_id INTEGER NOT NULL, 
    settlement_id INTEGER, 
    amount NUMERIC(15, 2) NOT NULL, 
    bank_name VARCHAR(255), 
    bank_account_number VARCHAR(50), 
    bank_account_name VARCHAR(255), 
    status payoutstatus, 
    transaction_ref VARCHAR(255), 
    note TEXT, 
    processed_by INTEGER, 
    processed_at TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(processed_by) REFERENCES users (id), 
    FOREIGN KEY(seller_id) REFERENCES users (id), 
    FOREIGN KEY(settlement_id) REFERENCES settlements (id)
);

CREATE INDEX ix_payouts_id ON payouts (id);

CREATE TYPE certificatestatus AS ENUM ('PENDING', 'VERIFIED', 'REJECTED', 'EXPIRED');

CREATE TABLE product_certificates (
    id SERIAL NOT NULL, 
    product_id INTEGER NOT NULL, 
    certificate_name VARCHAR(255) NOT NULL, 
    certificate_number VARCHAR(100), 
    issued_by VARCHAR(255), 
    issue_date DATE, 
    expiry_date DATE, 
    document_url TEXT, 
    verification_status certificatestatus, 
    verified_by INTEGER, 
    verified_at TIMESTAMP WITH TIME ZONE, 
    rejection_reason TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    FOREIGN KEY(verified_by) REFERENCES users (id)
);

CREATE INDEX ix_product_certificates_id ON product_certificates (id);

CREATE TABLE product_origins (
    id SERIAL NOT NULL, 
    product_id INTEGER NOT NULL, 
    village_name VARCHAR(255), 
    region_id INTEGER, 
    producer_name VARCHAR(255), 
    batch_number VARCHAR(100), 
    production_date DATE, 
    expiry_date DATE, 
    ingredients TEXT, 
    process_summary TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    FOREIGN KEY(region_id) REFERENCES regions (id)
);

CREATE INDEX ix_product_origins_id ON product_origins (id);

CREATE TYPE returntype AS ENUM ('RETURN', 'EXCHANGE');

CREATE TYPE returnstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'RECEIVED', 'REFUNDED', 'EXCHANGED');

CREATE TABLE return_requests (
    id SERIAL NOT NULL, 
    order_id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL, 
    return_type returntype NOT NULL, 
    reason TEXT NOT NULL, 
    images TEXT, 
    status returnstatus, 
    admin_note TEXT, 
    handled_by INTEGER, 
    handled_at TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(handled_by) REFERENCES users (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_return_requests_id ON return_requests (id);

CREATE TYPE shippingprovider AS ENUM ('GHN', 'GHTK', 'VNPOST', 'MANUAL');

CREATE TYPE shipmentstatus AS ENUM ('PENDING', 'CREATED', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED', 'FAILED', 'RETURNED');

CREATE TABLE shipments (
    id SERIAL NOT NULL, 
    order_id INTEGER NOT NULL, 
    provider shippingprovider, 
    tracking_code VARCHAR(100), 
    provider_order_code VARCHAR(100), 
    status shipmentstatus, 
    fee NUMERIC(10, 2), 
    weight INTEGER, 
    estimated_delivery TIMESTAMP WITH TIME ZONE, 
    actual_delivery TIMESTAMP WITH TIME ZONE, 
    from_address TEXT, 
    to_address TEXT, 
    note TEXT, 
    tracking_detail TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(order_id) REFERENCES orders (id), 
    UNIQUE (order_id)
);

CREATE INDEX ix_shipments_id ON shipments (id);

CREATE INDEX ix_shipments_tracking_code ON shipments (tracking_code);

DROP INDEX ix_role_permissions_id;

DROP TABLE role_permissions;

DROP INDEX ix_permissions_id;

DROP TABLE permissions;

ALTER TABLE payments ADD FOREIGN KEY(order_id) REFERENCES orders (id);

UPDATE alembic_version SET version_num='b82aa2f98076' WHERE alembic_version.version_num = '944b201b5ae7';

-- Running upgrade 944b201b5ae7 -> c9d8e7f6a5b4

CREATE TYPE userstatus AS ENUM ('ACTIVE', 'SUSPENDED', 'BANNED');

ALTER TABLE users ADD COLUMN status userstatus DEFAULT 'ACTIVE' NOT NULL;

ALTER TABLE users ADD COLUMN status_reason TEXT;

ALTER TABLE users ADD COLUMN status_expire_at TIMESTAMP WITH TIME ZONE;

INSERT INTO alembic_version (version_num) VALUES ('c9d8e7f6a5b4') RETURNING alembic_version.version_num;

-- Running upgrade c9d8e7f6a5b4 -> d1e2f3a4b5c6

CREATE TABLE product_price_logs (
    id SERIAL NOT NULL, 
    product_id INTEGER NOT NULL, 
    old_price NUMERIC(15, 2) NOT NULL, 
    new_price NUMERIC(15, 2) NOT NULL, 
    changed_by INTEGER NOT NULL, 
    reason TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    FOREIGN KEY(changed_by) REFERENCES users (id)
);

CREATE INDEX ix_product_price_logs_id ON product_price_logs (id);

CREATE INDEX ix_product_price_logs_product_id ON product_price_logs (product_id);

UPDATE alembic_version SET version_num='d1e2f3a4b5c6' WHERE alembic_version.version_num = 'c9d8e7f6a5b4';

-- Running upgrade d1e2f3a4b5c6 -> e2f3a4b5c6d7

ALTER TABLE contents ADD COLUMN is_active BOOLEAN DEFAULT '1' NOT NULL;

ALTER TABLE contents ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE contents ADD COLUMN deleted_by INTEGER;

ALTER TABLE contents ADD COLUMN rejection_reason TEXT;

ALTER TABLE contents ADD CONSTRAINT fk_contents_deleted_by FOREIGN KEY(deleted_by) REFERENCES users (id);

CREATE INDEX ix_contents_is_active ON contents (is_active);

CREATE TYPE contentauditaction AS ENUM ('CREATE', 'UPDATE', 'APPROVE', 'REJECT', 'DELETE', 'RESTORE');

CREATE TABLE content_audit_logs (
    id SERIAL NOT NULL, 
    content_id INTEGER NOT NULL, 
    action contentauditaction NOT NULL, 
    user_id INTEGER NOT NULL, 
    old_status VARCHAR(20), 
    new_status VARCHAR(20), 
    notes TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(content_id) REFERENCES contents (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_content_audit_logs_id ON content_audit_logs (id);

CREATE INDEX ix_content_audit_logs_content_id ON content_audit_logs (content_id);

UPDATE alembic_version SET version_num='e2f3a4b5c6d7' WHERE alembic_version.version_num = 'd1e2f3a4b5c6';

-- Running upgrade b82aa2f98076, e2f3a4b5c6d7 -> f1a2b3c4d5e6

DELETE FROM alembic_version WHERE alembic_version.version_num = 'b82aa2f98076';

UPDATE alembic_version SET version_num='f1a2b3c4d5e6' WHERE alembic_version.version_num = 'e2f3a4b5c6d7';

-- Running upgrade f1a2b3c4d5e6 -> a0b1c2d3e4f5

ALTER TABLE orders ADD COLUMN is_active BOOLEAN DEFAULT true NOT NULL;

CREATE INDEX ix_orders_is_active ON orders (is_active);

CREATE TABLE order_status_logs (
    id SERIAL NOT NULL, 
    order_id INTEGER NOT NULL, 
    old_status VARCHAR(30), 
    new_status VARCHAR(30) NOT NULL, 
    actor_id INTEGER, 
    role VARCHAR(30), 
    note TEXT, 
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE SET NULL, 
    FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE
);

CREATE INDEX ix_order_status_logs_id ON order_status_logs (id);

CREATE INDEX ix_order_status_logs_order_id ON order_status_logs (order_id);

UPDATE alembic_version SET version_num='a0b1c2d3e4f5' WHERE alembic_version.version_num = 'f1a2b3c4d5e6';

-- Running upgrade a0b1c2d3e4f5 -> b1c2d3e4f5a6

DO $$ BEGIN
            CREATE TYPE complaintcategory AS ENUM
                ('DELIVERY','QUALITY','REFUND','FRAUD','SERVICE','OTHER');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;;

DO $$ BEGIN
            CREATE TYPE complaintpriority AS ENUM
                ('LOW','MEDIUM','HIGH','URGENT');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;;

DO $$ BEGIN
            CREATE TYPE commentrole AS ENUM
                ('buyer','seller','admin','system');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;;

ALTER TABLE complaints ADD COLUMN category complaintcategory DEFAULT 'OTHER' NOT NULL;

ALTER TABLE complaints ADD COLUMN priority complaintpriority DEFAULT 'MEDIUM' NOT NULL;

ALTER TABLE complaints ADD COLUMN images TEXT;

ALTER TABLE complaints ADD COLUMN resolution_type VARCHAR(30);

ALTER TABLE complaints ADD COLUMN return_request_id INTEGER;

ALTER TABLE complaints ADD COLUMN assigned_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE complaints ADD COLUMN first_response_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE complaints ADD COLUMN resolved_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE complaints ADD COLUMN closed_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX ix_complaints_category ON complaints (category);

CREATE INDEX ix_complaints_priority ON complaints (priority);

ALTER TABLE complaints ADD CONSTRAINT fk_complaints_return_request_id FOREIGN KEY(return_request_id) REFERENCES return_requests (id) ON DELETE SET NULL;

-- commentrole already created above via DO $$ block

CREATE TABLE complaint_comments (
    id SERIAL NOT NULL, 
    complaint_id INTEGER NOT NULL, 
    author_id INTEGER NOT NULL, 
    role commentrole NOT NULL, 
    message TEXT NOT NULL, 
    attachments TEXT, 
    is_internal BOOLEAN DEFAULT false NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(complaint_id) REFERENCES complaints (id) ON DELETE CASCADE, 
    FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_complaint_comments_id ON complaint_comments (id);

CREATE INDEX ix_complaint_comments_complaint_id ON complaint_comments (complaint_id);

CREATE TABLE complaint_status_logs (
    id SERIAL NOT NULL, 
    complaint_id INTEGER NOT NULL, 
    old_status VARCHAR(30), 
    new_status VARCHAR(30) NOT NULL, 
    actor_id INTEGER, 
    note TEXT, 
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(complaint_id) REFERENCES complaints (id) ON DELETE CASCADE, 
    FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_complaint_status_logs_id ON complaint_status_logs (id);

CREATE INDEX ix_complaint_status_logs_complaint_id ON complaint_status_logs (complaint_id);

UPDATE alembic_version SET version_num='b1c2d3e4f5a6' WHERE alembic_version.version_num = 'a0b1c2d3e4f5';

-- Running upgrade b1c2d3e4f5a6 -> c2d3e4f5a6b7

DO $$ BEGIN
            ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'PARTIAL_REFUNDED';
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;;

ALTER TABLE payments ADD COLUMN vnpay_transaction_no VARCHAR(100);

ALTER TABLE payments ADD COLUMN vnpay_response_code VARCHAR(10);

ALTER TABLE payments ADD COLUMN vnpay_bank_code VARCHAR(20);

ALTER TABLE payments ADD COLUMN amount_from_gateway NUMERIC(15, 2);

ALTER TABLE payments ADD COLUMN amount_mismatch BOOLEAN DEFAULT false NOT NULL;

ALTER TABLE payments ADD COLUMN refunded_amount NUMERIC(15, 2);

ALTER TABLE payments ADD COLUMN refund_note TEXT;

ALTER TABLE payments ADD COLUMN refunded_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX ix_payments_vnpay_transaction_no ON payments (vnpay_transaction_no);

ALTER TABLE payment_transactions ADD COLUMN gateway_ref VARCHAR(255);

CREATE TABLE payment_audit_logs (
    id SERIAL NOT NULL, 
    payment_id INTEGER, 
    action VARCHAR(50) NOT NULL, 
    actor_id INTEGER, 
    amount NUMERIC(15, 2), 
    note TEXT, 
    ip_address VARCHAR(50), 
    user_agent VARCHAR(500), 
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(payment_id) REFERENCES payments (id) ON DELETE SET NULL, 
    FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_payment_audit_logs_id ON payment_audit_logs (id);

CREATE INDEX ix_payment_audit_logs_payment_id ON payment_audit_logs (payment_id);

UPDATE alembic_version SET version_num='c2d3e4f5a6b7' WHERE alembic_version.version_num = 'b1c2d3e4f5a6';

-- Running upgrade c2d3e4f5a6b7 -> d3e4f5a6b7c8

ALTER TABLE cart_items ADD COLUMN variant_id INTEGER;

CREATE INDEX ix_cart_items_variant_id ON cart_items (variant_id);

-- (orphan cleanup skipped — fresh DB, no legacy data)

-- SKIPPED: bảng stores, order_packages, product_variants, payment_methods, addresses
-- chưa được tạo trong schema này nên các FK dưới đây bị bỏ qua để tránh lỗi.
-- ALTER TABLE products ADD CONSTRAINT fk_products_store_id FOREIGN KEY(store_id) REFERENCES stores (id) ON DELETE SET NULL;
-- ALTER TABLE order_items ADD CONSTRAINT fk_order_items_store_id FOREIGN KEY(store_id) REFERENCES stores (id) ON DELETE SET NULL;
-- ALTER TABLE order_items ADD CONSTRAINT fk_order_items_package_id FOREIGN KEY(package_id) REFERENCES order_packages (id) ON DELETE SET NULL;
-- ALTER TABLE order_items ADD CONSTRAINT fk_order_items_variant_id FOREIGN KEY(variant_id) REFERENCES product_variants (id) ON DELETE SET NULL;
-- ALTER TABLE payments ADD CONSTRAINT fk_payments_payment_method_id FOREIGN KEY(payment_method_id) REFERENCES payment_methods (id) ON DELETE SET NULL;
-- ALTER TABLE seller_profiles ADD CONSTRAINT fk_seller_profiles_pickup_address_id FOREIGN KEY(pickup_address_id) REFERENCES addresses (id) ON DELETE SET NULL;
-- ALTER TABLE cart_items ADD CONSTRAINT fk_cart_items_variant_id FOREIGN KEY(variant_id) REFERENCES product_variants (id) ON DELETE SET NULL;

UPDATE alembic_version SET version_num='d3e4f5a6b7c8' WHERE alembic_version.version_num = 'c2d3e4f5a6b7';

-- Running upgrade d3e4f5a6b7c8 -> e7f8a9b0c1d2

CREATE TYPE originstatus AS ENUM ('PENDING', 'VERIFIED', 'REJECTED');

ALTER TABLE product_origins ADD COLUMN verification_status originstatus DEFAULT 'PENDING';

ALTER TABLE product_origins ADD COLUMN verified_by INTEGER;

ALTER TABLE product_origins ADD COLUMN verified_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE product_origins ADD COLUMN rejection_reason TEXT;

ALTER TABLE product_origins ADD CONSTRAINT fk_product_origins_verified_by_users FOREIGN KEY(verified_by) REFERENCES users (id);

UPDATE product_origins SET verification_status = 'VERIFIED' WHERE verification_status IS NULL;

UPDATE alembic_version SET version_num='e7f8a9b0c1d2' WHERE alembic_version.version_num = 'd3e4f5a6b7c8';

-- Running upgrade e7f8a9b0c1d2 -> f4a5b6c7d8e9

CREATE TABLE refresh_tokens (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    jti VARCHAR(64) NOT NULL, 
    family_id VARCHAR(64) NOT NULL, 
    token_hash VARCHAR(128) NOT NULL, 
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    revoked_at TIMESTAMP WITH TIME ZONE, 
    replaced_by_jti VARCHAR(64), 
    created_by_ip VARCHAR(64), 
    created_by_user_agent VARCHAR(512), 
    revoked_reason TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
    UNIQUE (jti), 
    UNIQUE (token_hash)
);

CREATE INDEX ix_refresh_tokens_expires_at ON refresh_tokens (expires_at);

CREATE INDEX ix_refresh_tokens_family_id ON refresh_tokens (family_id);

CREATE INDEX ix_refresh_tokens_id ON refresh_tokens (id);

CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id);

UPDATE alembic_version SET version_num='f4a5b6c7d8e9' WHERE alembic_version.version_num = 'e7f8a9b0c1d2';

-- Running upgrade  -> ai_001_add_tables

CREATE TABLE ai_moderation_logs (
    id SERIAL NOT NULL, 
    product_id INTEGER, 
    content_id INTEGER, 
    rule_engine_result VARCHAR(20), 
    rule_engine_flags TEXT, 
    model_used VARCHAR(100) NOT NULL, 
    ai_decision VARCHAR(20) NOT NULL, 
    ai_confidence FLOAT, 
    ai_reasons TEXT, 
    ai_flags TEXT, 
    escalated BOOLEAN, 
    escalation_reason VARCHAR(200), 
    processing_time_ms INTEGER, 
    input_tokens INTEGER, 
    output_tokens INTEGER, 
    estimated_cost_usd FLOAT, 
    raw_response TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    FOREIGN KEY(content_id) REFERENCES contents (id)
);

CREATE INDEX ix_ai_moderation_logs_id ON ai_moderation_logs (id);

CREATE INDEX ix_ai_moderation_logs_product_id ON ai_moderation_logs (product_id);

CREATE INDEX ix_ai_moderation_logs_content_id ON ai_moderation_logs (content_id);

CREATE TABLE ai_generation_cache (
    id SERIAL NOT NULL, 
    input_hash VARCHAR(64) NOT NULL, 
    task_type VARCHAR(30) NOT NULL, 
    model_used VARCHAR(100), 
    input_text TEXT, 
    output_text TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    expires_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    UNIQUE (input_hash)
);

CREATE INDEX ix_ai_generation_cache_id ON ai_generation_cache (id);

CREATE INDEX ix_ai_generation_cache_input_hash ON ai_generation_cache (input_hash);

CREATE INDEX ix_ai_generation_cache_expires_at ON ai_generation_cache (expires_at);

CREATE TABLE ai_cost_logs (
    id SERIAL NOT NULL, 
    log_date DATE NOT NULL, 
    model_id VARCHAR(100) NOT NULL, 
    task_type VARCHAR(30) NOT NULL, 
    request_count INTEGER, 
    total_input_tokens INTEGER, 
    total_output_tokens INTEGER, 
    total_cost_usd FLOAT, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_cost_date_model_task UNIQUE (log_date, model_id, task_type)
);

CREATE INDEX ix_ai_cost_logs_id ON ai_cost_logs (id);

CREATE INDEX ix_ai_cost_logs_log_date ON ai_cost_logs (log_date);

CREATE TABLE product_embeddings (
    id SERIAL NOT NULL, 
    product_id INTEGER NOT NULL, 
    embedding_text TEXT, 
    embedding_vector TEXT, 
    vector_dimension INTEGER, 
    model_version VARCHAR(100), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(product_id) REFERENCES products (id), 
    UNIQUE (product_id)
);

CREATE INDEX ix_product_embeddings_id ON product_embeddings (id);

CREATE INDEX ix_product_embeddings_product_id ON product_embeddings (product_id);

INSERT INTO alembic_version (version_num) VALUES ('ai_001_add_tables') RETURNING alembic_version.version_num;

-- Running upgrade ai_001_add_tables, f4a5b6c7d8e9 -> 1d50cbd85214

DELETE FROM alembic_version WHERE alembic_version.version_num = 'ai_001_add_tables';

UPDATE alembic_version SET version_num='1d50cbd85214' WHERE alembic_version.version_num = 'f4a5b6c7d8e9';

-- Running upgrade 1d50cbd85214 -> g1h2i3j4k5l6

ALTER TABLE seller_profiles ADD COLUMN business_registration_cert_url TEXT;

COMMENT ON COLUMN seller_profiles.business_registration_cert_url IS 'Giấy CN Đăng ký Kinh doanh – bản sao công chứng';

ALTER TABLE seller_profiles ADD COLUMN food_safety_cert_url TEXT;

COMMENT ON COLUMN seller_profiles.food_safety_cert_url IS 'Giấy CN Cơ sở đủ điều kiện An toàn thực phẩm';

UPDATE alembic_version SET version_num='g1h2i3j4k5l6' WHERE alembic_version.version_num = '1d50cbd85214';

-- Running upgrade b82aa2f98076 -> f5a6b7c8d9e0

CREATE TYPE product_type_enum AS ENUM ('AGRICULTURAL', 'HANDICRAFT');

ALTER TABLE products ADD COLUMN product_type product_type_enum;

CREATE INDEX ix_products_product_type ON products (product_type);

ALTER TABLE products ADD COLUMN packaging_type VARCHAR(50);

ALTER TABLE products ADD COLUMN approved_at TIMESTAMP WITH TIME ZONE;

-- SKIPPED: seo_title, seo_description, seo_keywords chưa bao giờ được ADD trong schema này.
-- ALTER TABLE products DROP COLUMN seo_title;
-- ALTER TABLE products DROP COLUMN seo_description;
-- ALTER TABLE products DROP COLUMN seo_keywords;

CREATE TYPE productlabel AS ENUM ('CLEAN_AGRICULTURE', 'TRADITIONAL_CRAFT', 'OCOP');

ALTER TABLE products 
            ALTER COLUMN label TYPE productlabel 
            USING label::productlabel;

ALTER TABLE product_approvals ADD COLUMN checked_traceability BOOLEAN DEFAULT 'false' NOT NULL;

ALTER TABLE product_origins ADD COLUMN facility_name VARCHAR(255);

ALTER TABLE product_origins ADD COLUMN usage_instructions TEXT;

ALTER TABLE product_origins ADD COLUMN storage_instructions TEXT;

ALTER TABLE product_origins ADD COLUMN warnings TEXT;

ALTER TABLE product_origins ADD CONSTRAINT uq_product_origins_product_id UNIQUE (product_id);

INSERT INTO alembic_version (version_num) VALUES ('f5a6b7c8d9e0') RETURNING alembic_version.version_num;

-- Running upgrade f5a6b7c8d9e0 -> i3j4k5l6m7n8

ALTER TABLE product_origins ADD COLUMN images TEXT;

UPDATE alembic_version SET version_num='i3j4k5l6m7n8' WHERE alembic_version.version_num = 'f5a6b7c8d9e0';

-- Running upgrade i3j4k5l6m7n8 -> j4k5l6m7n8o9

ALTER TABLE products ADD COLUMN videos TEXT;

UPDATE alembic_version SET version_num='j4k5l6m7n8o9' WHERE alembic_version.version_num = 'i3j4k5l6m7n8';

-- Running upgrade j4k5l6m7n8o9 -> k5l6m7n8o9p0

ALTER TABLE users ADD COLUMN date_of_birth DATE;

UPDATE alembic_version SET version_num='k5l6m7n8o9p0' WHERE alembic_version.version_num = 'j4k5l6m7n8o9';

-- Running upgrade k5l6m7n8o9p0 -> l6m7n8o9p0q1

-- SKIPPED: bảng addresses chưa được tạo trong schema này.
-- ALTER TABLE addresses ALTER COLUMN province_code DROP NOT NULL;
-- ALTER TABLE addresses ALTER COLUMN district_code DROP NOT NULL;
-- ALTER TABLE addresses ALTER COLUMN ward_code DROP NOT NULL;

UPDATE alembic_version SET version_num='l6m7n8o9p0q1' WHERE alembic_version.version_num = 'k5l6m7n8o9p0';

-- Running upgrade f5a6b7c8d9e0, g1h2i3j4k5l6 -> h2i3j4k5l6m7

UPDATE alembic_version SET version_num='h2i3j4k5l6m7' WHERE alembic_version.version_num = 'g1h2i3j4k5l6';

-- Running upgrade h2i3j4k5l6m7, l6m7n8o9p0q1 -> n2o3p4q5r6s7

DELETE FROM alembic_version WHERE alembic_version.version_num = 'h2i3j4k5l6m7';

UPDATE alembic_version SET version_num='n2o3p4q5r6s7' WHERE alembic_version.version_num = 'l6m7n8o9p0q1';

-- Running upgrade n2o3p4q5r6s7 -> m1n2o3p4q5r6

CREATE TABLE notifications (
    id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    category VARCHAR(20) DEFAULT 'SYSTEM' NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    message TEXT NOT NULL, 
    action_url VARCHAR(500), 
    ref_type VARCHAR(50), 
    ref_id INTEGER, 
    is_read BOOLEAN DEFAULT false NOT NULL, 
    read_at TIMESTAMP WITHOUT TIME ZONE, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user_id ON notifications (user_id);

CREATE INDEX idx_notifications_user_unread ON notifications (user_id, is_read);

CREATE INDEX idx_notifications_created_at ON notifications (created_at);

CREATE INDEX idx_notifications_ref ON notifications (ref_type, ref_id);

UPDATE alembic_version SET version_num='m1n2o3p4q5r6' WHERE alembic_version.version_num = 'n2o3p4q5r6s7';

-- Running upgrade m1n2o3p4q5r6 -> p1q2r3s4t5u6

ALTER TABLE users ADD COLUMN fcm_token VARCHAR(512);

COMMENT ON COLUMN users.fcm_token IS 'Firebase Cloud Messaging device token';

UPDATE alembic_version SET version_num='p1q2r3s4t5u6' WHERE alembic_version.version_num = 'm1n2o3p4q5r6';

-- Running upgrade p1q2r3s4t5u6 -> q2r3s4t5u6v7

ALTER TABLE users ADD COLUMN avatar_url VARCHAR(512);

COMMENT ON COLUMN users.avatar_url IS 'URL ảnh đại diện user lưu trên Supabase Storage';

UPDATE alembic_version SET version_num='q2r3s4t5u6v7' WHERE alembic_version.version_num = 'p1q2r3s4t5u6';

-- Running upgrade q2r3s4t5u6v7 -> r3s4t5u6v7w8

ALTER TYPE paymentmethod ADD VALUE IF NOT EXISTS 'PLATFORM_CREDITS';

UPDATE alembic_version SET version_num='r3s4t5u6v7w8' WHERE alembic_version.version_num = 'q2r3s4t5u6v7';

COMMIT;

