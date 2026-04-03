# Marketplace Schema Migration Guide

Đã thêm các bảng và trường mới vào schema database để hỗ trợ marketplace đầy đủ tính năng.

## Các Thay Đổi Chính

### 1. Multi-Seller Infrastructure
- **stores**: Cửa hàng/chi nhánh của seller
- **addresses**, **provinces**, **districts**, **wards**: Hệ thống địa chỉ chuẩn hóa
- **order_packages**: Hỗ trợ multi-seller trong một đơn hàng
- Cập nhật `orders`, `order_items` với các trường multi-seller

### 2. Product Variants & Inventory
- **product_variants**: Biến thể sản phẩm (size, màu, trọng lượng)
- **product_options**, **product_option_values**: Tùy chọn và giá trị
- **inventory_movements**: Lịch sử xuất nhập kho
- **stock_reservations**: Giữ hàng tạm thời
- Cập nhật `products` với SKU, slug, weight, dimensions, VAT

### 3. Product Media
- **product_media**: Quản lý ảnh/video sản phẩm (thay thế JSON)

### 4. Payment Gateway
- **payment_providers**: Nhà cung cấp cổng thanh toán
- **payment_methods**: Các phương thức thanh toán
- **order_adjustments**: Điều chỉnh đơn hàng (thuế, phí, giảm giá)
- Cập nhật `payments` với gateway integration fields

### 5. Promotions
- **promotion_usages**: Theo dõi sử dụng mã khuyến mãi
- **order_promotions**: Liên kết đơn hàng với khuyến mãi
- Cập nhật `promotions` với applicable scope

### 6. Shipping
- **shipping_rates**: Bảng giá vận chuyển
- **shipping_services**: Các dịch vụ vận chuyển
- Cập nhật `shipments` với COD, shipper info, dimensions

### 7. Reviews & Ratings
- **review_images**: Hình ảnh đính kèm đánh giá
- Cập nhật `reviews` với order verification, moderation, unique constraint

### 8. Returns
- Cập nhật `return_requests` với item-level returns, refund info

### 9. Settlement
- **settlement_items**: Chi tiết đối soát theo đơn hàng

### 10. RBAC
- **permissions**: Quyền hạn chi tiết
- **role_permissions**: Liên kết role với permission

### 11. Database Constraints
- Thêm Foreign Keys: `categories.parent_id`, `complaints.order_id`
- Thêm indexes cho performance trên các cột quan trọng

### 12. Seller Profile
- Cập nhật `seller_profiles` với tax_id, slug, shop contact

## Cách Chạy Migration

### Bước 1: Cài đặt dependencies
```bash
pip install alembic
```

### Bước 2: Tạo migration file
```bash
# Từ thư mục root của project
alembic revision --autogenerate -m "add_marketplace_schema_enhancements"
```

### Bước 3: Review migration file
Kiểm tra file migration được tạo trong `alembic/versions/` để đảm bảo nó đúng.

### Bước 4: Chạy migration
```bash
# Apply migration lên database
alembic upgrade head
```

### Bước 5: Rollback (nếu cần)
```bash
# Rollback về version trước đó
alembic downgrade -1
```

## Lưu Ý Quan Trọng

### 1. Backup Database
**QUAN TRỌNG**: Backup database trước khi chạy migration!
```bash
# PostgreSQL
pg_dump -U username -d database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# MySQL
mysqldump -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Foreign Key Constraints
Các bảng mới có nhiều foreign key constraints. Đảm bảo:
- Dữ liệu hiện có không vi phạm constraints
- Migration có thể cần thêm `nullable=True` cho một số FK ban đầu

### 3. Data Migration
Sau khi tạo bảng mới, bạn có thể cần migrate dữ liệu hiện có:

#### Migrate images từ JSON sang product_media:
```python
# Script migrate images
from app.models import Product, ProductMedia
import json

products = session.query(Product).filter(Product.images.isnot(None)).all()
for product in products:
    if product.images:
        images = json.loads(product.images)
        for idx, img_url in enumerate(images):
            media = ProductMedia(
                product_id=product.id,
                media_type="IMAGE",
                url=img_url,
                sort_order=idx,
                is_primary=(idx == 0)
            )
            session.add(media)
session.commit()
```

### 4. Indexes
Migration sẽ tự động tạo indexes cho:
- Foreign keys
- Các cột thường dùng để query (status, created_at, etc.)

### 5. Testing
Sau khi chạy migration, test các chức năng chính:
- Tạo/đọc products
- Tạo orders
- Payment flow
- Review system

## Các Bước Tiếp Theo

### 1. Seed Data
Cần seed data cho các bảng mới:

```python
# provinces, districts, wards
# Có thể import từ https://provinces.open-api.vn/

# payment_providers
providers = [
    {"name": "VNPay", "code": "VNPAY", "is_active": True},
    {"name": "MoMo", "code": "MOMO", "is_active": True},
    {"name": "ZaloPay", "code": "ZALOPAY", "is_active": True},
]

# payment_methods
methods = [
    {"name": "COD", "code": "COD", "is_active": True},
    {"name": "Chuyển khoản", "code": "BANK_TRANSFER", "is_active": True},
]

# permissions
permissions = [
    {"name": "Tạo sản phẩm", "code": "product.create", "module": "product"},
    {"name": "Xem đơn hàng", "code": "order.view", "module": "order"},
    # ... thêm các permissions khác
]
```

### 2. Update API Schemas
Cập nhật Pydantic schemas để support các trường mới:
- `app/schemas/product.py`: Thêm SKU, slug, weight, dimensions
- `app/schemas/order.py`: Thêm currency, channel, package support
- `app/schemas/payment.py`: Thêm gateway fields
- etc.

### 3. Update API Endpoints
Cập nhật các endpoints để sử dụng models mới:
- Product variants endpoints
- Multi-seller cart/checkout
- Promotion usage tracking
- Review với moderation

### 4. Update Business Logic
- Implement inventory reservation khi checkout
- Implement promotion usage tracking
- Implement multi-seller order splitting
- Implement review moderation workflow

## Troubleshooting

### Migration fails với "relation already exists"
```bash
# Đánh dấu migration đã chạy mà không thực thi
alembic stamp head
```

### Migration fails với foreign key constraint
Có thể cần:
1. Thêm data vào bảng parent trước
2. Hoặc set `nullable=True` tạm thời cho FK

### Performance issues sau migration
Chạy `VACUUM ANALYZE` (PostgreSQL) hoặc `OPTIMIZE TABLE` (MySQL) sau migration:
```sql
-- PostgreSQL
VACUUM ANALYZE;

-- MySQL
OPTIMIZE TABLE table_name;
```

## Liên Hệ

Nếu gặp vấn đề khi chạy migration, vui lòng liên hệ dev team.
