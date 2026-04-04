# Tổng Quan Schema Database Marketplace

## Models Mới Đã Thêm

### 1. Multi-Seller & Store Management
| Model | File | Mô tả |
|-------|------|-------|
| Store | `store.py` | Cửa hàng/chi nhánh của seller |
| OrderPackage | `order_package.py` | Sub-order theo seller |

### 2. Address System
| Model | File | Mô tả |
|-------|------|-------|
| Province | `address.py` | Tỉnh/Thành phố |
| District | `address.py` | Quận/Huyện |
| Ward | `address.py` | Phường/Xã |
| Address | `address.py` | Sổ địa chỉ người dùng |

### 3. Product Variants & Inventory
| Model | File | Mô tả |
|-------|------|-------|
| ProductVariant | `product_variant.py` | Biến thể sản phẩm |
| ProductOption | `product_variant.py` | Tùy chọn (Màu, Size) |
| ProductOptionValue | `product_variant.py` | Giá trị tùy chọn |
| InventoryMovement | `product_variant.py` | Lịch sử xuất nhập kho |
| StockReservation | `product_variant.py` | Giữ hàng tạm thời |

### 4. Product Media
| Model | File | Mô tả |
|-------|------|-------|
| ProductMedia | `product_media.py` | Ảnh/video sản phẩm |

### 5. Payment Gateway
| Model | File | Mô tả |
|-------|------|-------|
| PaymentProvider | `payment_method.py` | Nhà cung cấp thanh toán |
| PaymentMethodType | `payment_method.py` | Phương thức thanh toán |
| OrderAdjustment | `payment_method.py` | Điều chỉnh đơn hàng |

### 6. Promotions
| Model | File | Mô tả |
|-------|------|-------|
| PromotionUsage | `promotion_usage.py` | Theo dõi sử dụng mã |
| OrderPromotion | `promotion_usage.py` | Liên kết đơn-mã |

### 7. Shipping
| Model | File | Mô tả |
|-------|------|-------|
| ShippingRate | `shipping_service.py` | Bảng giá vận chuyển |
| ShippingServiceType | `shipping_service.py` | Dịch vụ vận chuyển |

### 8. Reviews
| Model | File | Mô tả |
|-------|------|-------|
| ReviewImage | `review_image.py` | Hình ảnh đánh giá |

### 9. Settlement
| Model | File | Mô tả |
|-------|------|-------|
| SettlementItem | `settlement_item.py` | Chi tiết đối soát |

### 10. RBAC
| Model | File | Mô tả |
|-------|------|-------|
| Permission | `permission.py` | Quyền hạn |
| RolePermission | `permission.py` | Role-Permission mapping |

## Models Đã Cập Nhật

### Product (`product.py`)
**Trường mới:**
- `store_id`: FK đến stores
- `sku`: Mã SKU (nullable vì có variants)
- `slug`: URL-friendly identifier
- `weight`: Trọng lượng (gram)
- `dimensions`: Kích thước (JSON)
- `unit`: Đơn vị tính
- `vat_rate`: Thuế VAT
- `published_at`, `unpublished_at`: Lên lịch hiển thị
- `seo_title`, `seo_description`, `seo_keywords`: SEO

**Indexes mới:** `producer_id`, `category_id`, `status`, `is_active`, `store_id`, `sku`, `slug`

### Order (`order.py`)
**Trường mới:**
- `currency`: Tiền tệ (VND, USD)
- `channel`: Kênh bán (WEB, MOBILE_APP)
- `coupon_code`: Mã coupon đã dùng
- `tax_breakdown`: Chi tiết thuế (JSON)
- `fee_breakdown`: Chi tiết phí (JSON)

### OrderItem (`order.py`)
**Trường mới:**
- `seller_id`: Seller của item này
- `store_id`: Store của item này
- `package_id`: OrderPackage nếu multi-seller
- `variant_id`: ProductVariant nếu có
- `tax_amount`: Thuế của item
- `discount_amount`: Giảm giá của item
- `tracking_code`: Mã vận đơn riêng

**Indexes mới:** `order_id`, `product_id`, `seller_id`, `store_id`, `package_id`, `variant_id`

### Payment (`payment.py`)
**Trường mới:**
- `payment_method_id`: FK đến payment_methods
- `gateway_transaction_id`: Mã giao dịch gateway
- `payment_channel`: card, bank, wallet
- `currency`: Tiền tệ
- `card_brand`: Visa, Mastercard
- `bank_code`: Mã ngân hàng
- `failure_code`, `failure_message`: Lỗi
- `gateway_response`: Response đầy đủ (JSON)

**Indexes mới:** `order_id`, `customer_id`, `seller_id`, `payment_method_id`, `gateway_transaction_id`, `status`

### Promotion (`promotion.py`)
**Trường mới:**
- `applicable_to`: ALL/SELLER/PRODUCT/CATEGORY
- `seller_id`: Nếu riêng seller
- `applicable_product_ids`: Sản phẩm áp dụng (JSON)
- `applicable_category_ids`: Danh mục áp dụng (JSON)
- `user_conditions`: Điều kiện user (JSON)
- `usage_limit_per_user`: Giới hạn per user

**Indexes mới:** `seller_id`, `status`

### Shipment (`shipment.py`)
**Trường mới:**
- `service_code`: EXPRESS, STANDARD
- `shipper_name`, `shipper_phone`: Thông tin shipper
- `cod_amount`: Thu hộ COD
- `width`, `height`, `length`: Kích thước kiện
- `insurance_value`: Giá trị bảo hiểm
- `from_address_id`, `to_address_id`: FK addresses
- `webhook_signature`: Validate callback

**Indexes mới:** `order_id`, `tracking_code`, `status`

### ReturnRequest (`return_request.py`)
**Trường mới:**
- `order_item_id`: FK order_items
- `refund_amount`: Số tiền hoàn
- `refund_method`: ORIGINAL/BANK_TRANSFER/WALLET
- `seller_return_address_id`: Địa chỉ trả hàng
- `return_shipping_code`: Mã vận đơn trả
- `approved_by`, `approved_at`: Phê duyệt

**Indexes mới:** `order_id`, `user_id`, `order_item_id`, `status`

### Review (`complaint.py`)
**Trường mới:**
- `order_item_id`: Xác minh mua hàng
- `seller_rating`: Đánh giá seller
- `moderation_status`: PENDING/APPROVED/REJECTED
- `moderated_by`, `moderated_at`: Kiểm duyệt
- `moderation_note`: Ghi chú kiểm duyệt

**Constraints mới:**
- UniqueConstraint(user_id, product_id)

**Indexes mới:** `product_id`, `user_id`, `order_item_id`, `moderation_status`

**Relationships mới:** `images` (ReviewImage)

### SellerProfile (`seller_profile.py`)
**Trường mới:**
- `slug`: URL cửa hàng
- `shop_phone`, `shop_email`: Liên hệ shop
- `pickup_address_id`: Địa chỉ lấy hàng
- `tax_id`: Mã số thuế
- `business_registration_number`: Số ĐKKD

**Indexes mới:** `user_id`, `slug`, `tax_id`, `verification_status`

### Category (`category.py`)
**Trường cập nhật:**
- `parent_id`: Thêm ForeignKey constraint

**Indexes mới:** `parent_id`

**Relationships mới:** `parent`, `subcategories`

### Complaint (`complaint.py`)
**Trường cập nhật:**
- `order_id`: Thêm ForeignKey constraint

**Indexes mới:** `product_id`, `order_id`, `user_id`, `complaint_type`, `status`

**Relationships mới:** `order`

## Tổng Số Thay Đổi

- **Bảng mới**: 21 bảng
- **Bảng cập nhật**: 10 bảng
- **Trường mới**: ~80 trường
- **Foreign Keys mới**: ~30 FKs
- **Indexes mới**: ~50 indexes
- **Relationships mới**: ~40 relationships

## Enums Mới

- `AddressType`: SHIPPING, BILLING
- `OrderPackageStatus`: PENDING, CONFIRMED, PROCESSING, SHIPPING, DELIVERED, CANCELLED, REFUNDED
- `MovementType`: IN, OUT, ADJUSTMENT
- `ReservationStatus`: ACTIVE, RELEASED, FULFILLED
- `MediaType`: IMAGE, VIDEO
- `ModerationStatus`: PENDING, APPROVED, REJECTED

## Mapping với Yêu Cầu Gốc

### ✅ Các bảng đã thêm theo yêu cầu:
1. ✅ stores/seller_branches
2. ✅ addresses + bảng địa giới hành chính
3. ✅ product_variants + product_options
4. ✅ inventory_movements + stock_reservations
5. ✅ order_sellers/order_packages
6. ✅ order_adjustments
7. ✅ payment_methods + payment_providers
8. ✅ promotion_usages + order_promotions
9. ✅ product_media
10. ✅ permissions + role_permissions
11. ✅ review_images
12. ✅ shipping_rates + shipping_services
13. ✅ settlement_items

### ✅ Các trường đã thêm theo yêu cầu:
1. ✅ Products: SKU, slug, weight, dimensions, VAT, unit, store_id, published_at, SEO
2. ✅ Orders: currency, channel, coupon_code, tax_breakdown, fee_breakdown
3. ✅ OrderItems: seller_id, store_id, variant_id, tax_amount, discount_amount, tracking_code
4. ✅ Payments: gateway fields, currency, card_brand, bank_code, failure handling
5. ✅ Shipments: COD, shipper info, dimensions, service_code, webhook
6. ✅ SellerProfiles: tax_id, slug, shop contact, pickup_address_id
7. ✅ Promotions: applicable scope, user conditions, per-user limit
8. ✅ ReturnRequests: item-level, refund info, seller address
9. ✅ Reviews: order verification, moderation, seller_rating

### ✅ Constraints & Indexes:
1. ✅ categories.parent_id FK
2. ✅ complaints.order_id FK
3. ✅ Indexes trên FK chính
4. ✅ Unique constraints cho reviews

## Lưu Ý Khi Sử Dụng

1. **Multi-Seller Orders**: Sử dụng `OrderPackage` để split orders theo seller
2. **Inventory**: Sử dụng `StockReservation` khi checkout để tránh oversell
3. **Product Variants**: Nếu sản phẩm có variants, tồn kho nên track ở `ProductVariant`
4. **Promotions**: Track usage qua `PromotionUsage` để enforce limits
5. **Reviews**: Verify purchase qua `order_item_id` trước khi cho review
6. **Addresses**: Sử dụng địa chỉ chuẩn hóa với province/district/ward codes
7. **Payments**: Lưu `gateway_transaction_id` để reconcile với gateway
8. **Shipping**: Validate webhook callbacks bằng `webhook_signature`
