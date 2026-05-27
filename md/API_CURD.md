# 📘 API Documentation – CMS Hệ Thống & App

> **Base URL**: `https://api.quancmsbe.site/api`  
> **Prefix chung**: Tất cả endpoint đều bắt đầu bằng `/api/...`  
> **Auth Header**: `Authorization: Bearer <JWT_TOKEN>`  
> **Secret Header**: `X-Quan-Secret: <API_SECRET>` (bắt buộc cho mọi request)

---

## 📋 Mục lục

| # | Module | Prefix | Mô tả |
|---|--------|--------|--------|
| 1 | [Authentication](#1-authentication) | `/api/auth` | Đăng ký, đăng nhập, quản lý token |
| 2 | [Users](#2-users) | `/api/users` | Quản lý người dùng (Admin) |
| 3 | [Roles](#3-roles) | `/api/admin/roles` | Quản lý vai trò (Admin) |
| 4 | [Categories](#4-categories) | `/api/categories` | Quản lý danh mục sản phẩm |
| 5 | [Regions](#5-regions) | `/api/regions` | Quản lý vùng miền |
| 6 | [Products](#6-products) | `/api/products` | Quản lý sản phẩm & biến thể |
| 7 | [Cart](#7-cart) | `/api/cart` | Giỏ hàng |
| 8 | [Orders](#8-orders) | `/api/orders` | Quản lý đơn hàng (Admin/Seller) |
| 9 | [Payments](#9-payments) | `/api/payments` | Thanh toán VNPAY, IPN, hoàn tiền |
| 10 | [Shipping](#10-shipping) | `/api/shipping` | Vận chuyển GHN |
| 11 | [Reviews](#11-reviews) | `/api/reviews` | Đánh giá sản phẩm |
| 12 | [Returns](#12-returns) | `/api/returns` | Đổi/trả hàng |
| 13 | [Complaints](#13-complaints) | `/api/complaints` | Khiếu nại & hỗ trợ |
| 14 | [Content](#14-content) | `/api/content` | Quản lý nội dung/bài đăng |
| 15 | [Media](#15-media) | `/api/medias` | Upload/quản lý media (AWS S3) |
| 16 | [Seller](#16-seller) | `/api/seller` | Dashboard & quản lý seller |
| 17 | [Seller Onboarding](#17-seller-onboarding) | `/api/seller` | Đăng ký kinh doanh & KYC |
| 18 | [Settlement](#18-settlement) | `/api/settlement` | Đối soát & chi trả cho seller |
| 19 | [Traceability](#19-traceability) | `/api/traceability` | Truy xuất nguồn gốc & chứng nhận |
| 20 | [Promotions](#20-promotions) | `/api/promotions` | Mã khuyến mãi / Coupon |
| 21 | [Mobile App](#21-mobile-app) | `/api/mobile` | API cho ứng dụng di động |

---

## 🔑 Quy ước chung

### Roles (vai trò)
| Role | Mô tả |
|------|--------|
| `admin` | Quản trị viên – toàn quyền |
| `content_manager` | Quản lý nội dung |
| `producer` / `seller` | Người bán hàng |
| `consumer` | Khách hàng / người mua |
| `guest` | Chưa đăng nhập (public endpoint) |

### Response chuẩn
```json
{
  "success": true,
  "message": "...",
  "data": { ... },
  "meta": { "total": 100, "page": 1, "limit": 20, "total_pages": 5 }
}
```

### Pagination
Hầu hết các endpoint GET danh sách đều hỗ trợ:
- `page` (int, default=1) – Trang hiện tại
- `limit` (int, default=20) – Số bản ghi mỗi trang

---

## 1. Authentication

> **Prefix**: `/api/auth`  
> **File**: `app/api/v1/auth.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `POST` | `/register` | ❌ | Đăng ký tài khoản mới |
| `POST` | `/login` | ❌ | Đăng nhập → trả access_token + refresh_token |
| `POST` | `/refresh` | ❌ | Làm mới access_token bằng refresh_token |
| `GET` | `/me` | ✅ | Lấy thông tin user hiện tại |
| `PUT` | `/change-password` | ✅ | Đổi mật khẩu |

### POST `/register`
**Mục đích**: Tạo tài khoản mới. Mặc định `type = "consumer"`, `activated = 1`.

```json
// Request Body
{
  "email": "user@example.com",
  "password": "StrongPass123",
  "name": "Nguyễn Văn A",
  "gender": "male"          // optional
}
```

### POST `/login`
**Mục đích**: Xác thực email+password → trả JWT token.

```json
// Request Body
{
  "email": "user@example.com",
  "password": "StrongPass123"
}

// Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "name": "...", "type": "consumer" }
}
```

> ⚡ **Lưu ý**: Hệ thống kiểm tra trạng thái user (`BANNED`, `SUSPENDED`) khi đăng nhập. User bị BANNED không thể đăng nhập. User SUSPENDED sẽ tự mở khóa sau `status_expire_at`.

### POST `/refresh`
**Mục đích**: Dùng `refresh_token` để lấy `access_token` mới khi token cũ hết hạn.

### GET `/me`
**Mục đích**: Lấy thông tin profile của user đang đăng nhập.

### PUT `/change-password`
```json
{
  "old_password": "OldPass123",
  "new_password": "NewPass456"
}
```

---

## 2. Users

> **Prefix**: `/api/users`  
> **File**: `app/api/v1/users.py`  
> **Quyền**: Chỉ admin (kiểm tra qua `check_user_manage_access`)

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ | Admin | Danh sách user (phân trang, tìm kiếm) |
| `POST` | `/` | ✅ | Admin | Tạo user mới |
| `GET` | `/{user_id}` | ✅ | Admin | Xem chi tiết user |
| `PUT` | `/{user_id}` | ✅ | Admin | Cập nhật user |
| `DELETE` | `/{user_id}` | ✅ | Admin | Soft delete user |
| `PUT` | `/{user_id}/activate` | ✅ | Admin | Kích hoạt / vô hiệu hóa |
| `PUT` | `/{user_id}/status` | ✅ | Admin | Đổi trạng thái (ACTIVE/SUSPENDED/BANNED) |
| `POST` | `/{user_id}/roles` | ✅ | Admin | Gán roles cho user |
| `GET` | `/{user_id}/roles` | ✅ | Admin | Xem roles của user |

### GET `/` – Danh sách user
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `model` | string | Filter theo `type` (admin, consumer, seller...) |
| `activated` | int | 0 hoặc 1 |
| `search` | string | Tìm theo name hoặc email |
| `page` | int | Trang |
| `limit` | int | Số bản ghi (max 500) |

### PUT `/{user_id}/status` – Quản lý trạng thái
```json
{
  "status": "SUSPENDED",           // ACTIVE | SUSPENDED | BANNED
  "status_reason": "Vi phạm chính sách",
  "status_expire_at": "2026-05-01T00:00:00"  // bắt buộc khi SUSPENDED
}
```

> ⚡ **Logic**: Không cho phép admin tự ban/suspend chính mình. SUSPENDED bắt buộc có `status_expire_at`. BANNED là vĩnh viễn.

---

## 3. Roles

> **Prefix**: `/api/admin/roles`  
> **File**: `app/api/v1/roles.py`  
> **Quyền**: Chỉ admin (kiểm tra qua `check_role_manage_access`)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/` | ✅ | Danh sách roles |
| `POST` | `/` | ✅ | Tạo role mới |
| `PUT` | `/{role_id}` | ✅ | Cập nhật role |
| `DELETE` | `/{role_id}` | ✅ | Xóa role |

### POST `/` – Tạo role
```json
{
  "role_name": "content_moderator",
  "description": "Moderator nội dung"
}
```

---

## 4. Categories

> **Prefix**: `/api/categories`  
> **File**: `app/api/v1/categories.py`  
> **Quyền**: GET = cần auth, CUD = admin (kiểm tra qua `check_category_manage_access`)

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ | All | Danh sách danh mục (phân trang, lọc) |
| `GET` | `/{category_id}` | ✅ | All | Chi tiết danh mục |
| `POST` | `/` | ✅ | Admin | Tạo danh mục mới |
| `PUT` | `/{category_id}` | ✅ | Admin | Cập nhật danh mục |
| `DELETE` | `/{category_id}` | ✅ | Admin | Xóa danh mục |

### GET `/` – Lọc danh mục
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `is_active` | bool | Lọc trạng thái hoạt động |
| `parent_id` | int | Lọc theo danh mục cha |
| `search` | string | Tìm theo tên |

### POST `/` – Tạo danh mục
```json
{
  "name": "Thực phẩm sạch",
  "description": "Sản phẩm nông sản sạch",
  "icon": "🌿",
  "image": "https://...",
  "parent_id": null,        // danh mục gốc
  "order": 1,
  "is_active": true
}
```

> ⚡ **Logic**: Slug tự động sinh từ name. Không xóa được nếu còn danh mục con. Không cho phép parent_id = chính nó.

---

## 5. Regions

> **Prefix**: `/api/regions`  
> **File**: `app/api/v1/regions.py`  
> **Quyền**: GET = cần auth, CUD = admin (`check_region_manage_access`)

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ | All | Danh sách vùng miền |
| `GET` | `/{region_id}` | ✅ | All | Chi tiết vùng |
| `POST` | `/` | ✅ | Admin | Tạo vùng mới |
| `PUT` | `/{region_id}` | ✅ | Admin | Cập nhật vùng |
| `DELETE` | `/{region_id}` | ✅ | Admin | Xóa vùng |

```json
// POST /
{
  "name": "Đồng bằng sông Cửu Long",
  "description": "Vùng nông nghiệp trọng điểm",
  "image": "https://...",
  "latitude": "10.0451",
  "longitude": "105.7468",
  "order": 1,
  "is_active": true
}
```

---

## 6. Products

> **Prefix**: `/api/products`  
> **File**: `app/api/v1/products.py`  
> **Quyền**: Phức tạp – phân quyền theo role và quy trình duyệt KYC

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ Optional | All | Danh sách sản phẩm |
| `GET` | `/{product_id}` | ✅ Optional | All | Chi tiết sản phẩm |
| `POST` | `/` | ✅ | Seller/Admin | Tạo sản phẩm mới |
| `PUT` | `/{product_id}` | ✅ | Owner/Admin | Cập nhật sản phẩm |
| `DELETE` | `/{product_id}` | ✅ | Owner/Admin | Soft delete (is_active=false) |
| `POST` | `/{product_id}/approve` | ✅ | Admin | Duyệt/từ chối sản phẩm |
| `PUT` | `/{product_id}/label` | ✅ | Admin | Gắn nhãn (NORMAL/OCOP/ORGANIC...) |
| `GET` | `/{product_id}/variants` | ✅ Optional | All | Danh sách biến thể |
| `POST` | `/{product_id}/variants` | ✅ | Seller/Admin | Thêm biến thể |
| `PUT` | `/{product_id}/variants/{variant_id}` | ✅ | Seller/Admin | Cập nhật biến thể |
| `DELETE` | `/{product_id}/variants/{variant_id}` | ✅ | Seller/Admin | Xóa biến thể |

### GET `/` – Danh sách sản phẩm
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `status` | string | PENDING, APPROVED, REJECTED |
| `category_id` | int | Lọc theo danh mục |
| `region_id` | int | Lọc theo vùng miền |
| `label` | string | NORMAL, OCOP, ORGANIC, GEOGRAPHICAL_INDICATION |
| `search` | string | Tìm theo tên |
| `min_price` / `max_price` | decimal | Khoảng giá |
| `include_inactive` | bool | Admin hiển thị SP đã xóa |

### POST `/` – Tạo sản phẩm
```json
{
  "name": "Gạo ST25",
  "description": "Gạo thơm đặc sản Sóc Trăng...",
  "category_id": 1,
  "region_id": 3,
  "price": 85000,
  "stock_quantity": 500,
  "unit": "kg",
  "images": "[\"https://...\"]",
  "videos": "[\"https://...\"]"
}
```

> ⚡ **Quy trình duyệt**: Seller tạo SP → status = `PENDING` → Admin duyệt (`APPROVED`) hoặc từ chối (`REJECTED`). Seller phải **KYC verified** mới được tạo SP. Khi seller sửa nội dung → reset về `PENDING`.

### POST `/{product_id}/approve` – Duyệt sản phẩm
```json
{
  "status": "APPROVED",   // hoặc "REJECTED"
  "notes": "Sản phẩm đạt chuẩn",
  "label": "OCOP"         // optional – gắn nhãn khi duyệt
}
```

### Biến thể sản phẩm (Variants)
```json
// POST /{product_id}/variants
{
  "variant_name": "Gói 5kg",
  "sku": "ST25-5KG",
  "price": 400000,
  "stock_quantity": 100,
  "weight": "5kg",
  "attributes": "{\"weight\":\"5kg\"}"
}
```

---

## 7. Cart

> **Prefix**: `/api/cart`  
> **File**: `app/api/v1/cart.py`  
> **Quyền**: Tất cả user đã đăng nhập

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/` | ✅ | Xem giỏ hàng hiện tại |
| `POST` | `/items` | ✅ | Thêm sản phẩm vào giỏ |
| `PUT` | `/items/{item_id}` | ✅ | Cập nhật số lượng |
| `DELETE` | `/items/{item_id}` | ✅ | Xóa sản phẩm khỏi giỏ |
| `DELETE` | `/` | ✅ | Xóa toàn bộ giỏ hàng |

### POST `/items` – Thêm vào giỏ
```json
{
  "product_id": 1,
  "quantity": 2,
  "variant_id": null    // optional – nếu sản phẩm có biến thể
}
```

> ⚡ **Logic**: 
> - Chỉ thêm được SP đã `APPROVED` và `is_active = true`
> - Nếu cùng product+variant đã có → cộng dồn số lượng
> - Tự động validate tồn kho trước khi thêm
> - Unit price lấy từ variant (nếu có) hoặc product.price

### GET `/` – Response giỏ hàng
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 5,
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "variant_id": null,
        "product_name": "Gạo ST25",
        "product_image": "https://...",
        "unit_price": 85000,
        "quantity": 2,
        "subtotal": 170000,
        "stock_quantity": 498
      }
    ],
    "total_items": 1,
    "total_amount": 170000
  }
}
```

---

## 8. Orders

> **Prefix**: `/api/orders`  
> **File**: `app/api/v1/orders.py`  
> **Quyền**: Admin + Seller (xem đơn của store mình) + Consumer (xem đơn của mình)

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ | Admin/Seller | Danh sách đơn hàng |
| `GET` | `/{order_id}` | ✅ | Admin/Seller/Owner | Chi tiết đơn hàng |
| `PUT` | `/{order_id}/status` | ✅ | Admin/Seller | Cập nhật trạng thái đơn |

### GET `/` – Danh sách đơn hàng
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `status` | string | PENDING, CONFIRMED, PROCESSING, SHIPPING, DELIVERED, CANCELLED, REFUNDED |
| `payment_status` | string | UNPAID, PAID, REFUNDED |
| `search` | string | Tìm theo order_number |
| `customer_id` | int | Lọc theo khách hàng |

> ⚡ **Phân quyền dữ liệu**: 
> - `admin` → xem tất cả đơn
> - `seller/producer` → chỉ xem đơn của store mình (`seller_id = current_user.id`)
> - `consumer` → chỉ xem đơn của mình

### PUT `/{order_id}/status` – State Machine

```json
{
  "status": "CONFIRMED",
  "note": "Xác nhận đơn hàng"
}
```

**Bảng chuyển trạng thái hợp lệ**:

| Từ trạng thái | → Trạng thái mới | Ai được phép |
|---------------|-------------------|--------------|
| `PENDING` | `CONFIRMED` | seller, admin |
| `PENDING` | `CANCELLED` | consumer, admin |
| `CONFIRMED` | `PROCESSING` | seller, admin |
| `CONFIRMED` | `CANCELLED` | consumer, admin |
| `PROCESSING` | `SHIPPING` | seller, admin |
| `SHIPPING` | `DELIVERED` | admin, system (webhook) |
| `DELIVERED` | `REFUNDED` | admin |

> ⚡ **Business Logic**: 
> - Mỗi lần chuyển trạng thái → ghi `OrderStatusLog` (audit trail)
> - Khi CANCELLED → hoàn tồn kho tự động
> - Khi DELIVERED + COD → tự động set `payment_status = PAID`
> - `payment_status` tự động cập nhật theo `resolve_payment_status()`

---

## 9. Payments

> **Prefix**: `/api/payments`  
> **File**: `app/api/v1/payments.py`  
> **Tích hợp**: VNPAY Gateway

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/` | ✅ | Danh sách payments (phân quyền) |
| `GET` | `/{payment_id}` | ✅ | Chi tiết payment |
| `POST` | `/create` | ✅ | Tạo payment URL (VNPAY) |
| `GET` | `/vnpay-return` | ❌ | VNPAY redirect callback |
| `POST` | `/vnpay-ipn` | ❌ | VNPAY server-to-server callback |
| `POST` | `/{payment_id}/refund` | ✅ | Hoàn tiền |
| `GET` | `/revenue` | ✅ | Thống kê doanh thu |

### POST `/create` – Tạo link thanh toán VNPAY
```json
{
  "order_id": 1,
  "payment_method": "VNPAY"    // VNPAY | COD
}
```

**Response**:
```json
{
  "success": true,
  "payment_url": "https://sandbox.vnpayment.vn/paymentv2/...",
  "payment_id": 1,
  "txn_ref": "TXN_1_1712345678"
}
```

### GET `/vnpay-return`
**Mục đích**: VNPAY redirect user về sau khi thanh toán. Xác minh checksum, cập nhật trạng thái.

### POST `/vnpay-ipn`
**Mục đích**: VNPAY gọi server-to-server để xác nhận giao dịch. 
- Kiểm tra checksum
- Kiểm tra idempotency (không xử lý trùng)
- Kiểm tra amount khớp
- Cập nhật `Payment.status`, `Order.payment_status`
- Lưu `transaction_no`, `response_code`, `bank_code`

### POST `/{payment_id}/refund` – Hoàn tiền
```json
{
  "amount": 85000,       // số tiền hoàn (≤ collected_amount)
  "reason": "Khách đổi ý"
}
```

> ⚡ **Logic hoàn tiền**:
> - Chỉ admin mới được hoàn tiền
> - Kiểm tra `amount ≤ collected_amount - refunded_amount`
> - Tạo refund transaction record
> - Cập nhật `order.payment_status = REFUNDED`
> - Cập nhật `payment.refunded_amount`
> - **Hiện tại mock gateway** – chưa gọi VNPAY Refund API thực

### GET `/revenue` – Thống kê doanh thu
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `from_date` | datetime | Ngày bắt đầu |
| `to_date` | datetime | Ngày kết thúc |
| `seller_id` | int | Lọc theo seller (admin) |

---

## 10. Shipping

> **Prefix**: `/api/shipping`  
> **File**: `app/api/v1/shipping.py`  
> **Tích hợp**: GHN (Giao Hàng Nhanh)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `POST` | `/fee` | ✅ | Tính phí vận chuyển |
| `POST` | `/create` | ✅ | Tạo vận đơn GHN |
| `GET` | `/{shipment_id}/track` | ✅ | Tra cứu trạng thái vận đơn |
| `GET` | `/order/{order_id}` | ✅ | Xem vận đơn theo order_id |
| `POST` | `/webhook` | ❌ | GHN webhook callback |

### POST `/fee` – Tính phí vận chuyển
```json
{
  "to_district_id": 1442,          // Mã quận/huyện GHN
  "to_ward_code": "20808",         // Mã phường/xã GHN
  "weight": 500,                   // gram
  "from_district_id": 1454         // default: quận gửi
}
```

### POST `/create` – Tạo vận đơn
```json
{
  "order_id": 1,
  "weight": 500,
  "to_district_id": 1442,
  "to_ward_code": "20808",
  "note": "Giao giờ hành chính"
}
```

> ⚡ **Logic**: 
> - Chỉ seller sở hữu đơn hoặc admin mới được tạo vận đơn
> - Tự động chuyển order sang `SHIPPING`
> - Ghi audit log
> - Nếu GHN API lỗi → vẫn tạo shipment record với phí mặc định

### POST `/webhook` – GHN Webhook
**Mục đích**: GHN gọi khi trạng thái vận đơn thay đổi. Tự động cập nhật:
- `delivered` → `Order.status = DELIVERED`, auto set payment_status cho COD
- `returned` → `Order.status = REFUNDED`
- `delivering` / `picked` → `Order.status = SHIPPING`

---

## 11. Reviews

> **Prefix**: `/api/reviews`  
> **File**: `app/api/v1/reviews.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `POST` | `/` | ✅ | Tạo đánh giá sản phẩm |
| `GET` | `/product/{product_id}` | ❌ | Xem đánh giá (public) |
| `PUT` | `/{review_id}` | ✅ | Cập nhật đánh giá của mình |
| `DELETE` | `/{review_id}` | ✅ | Xóa đánh giá của mình |

### POST `/` – Tạo đánh giá
```json
{
  "product_id": 1,
  "order_id": 5,       // phải có đơn DELIVERED chứa SP này
  "rating": 5,          // 1-5 sao
  "comment": "Sản phẩm rất tốt"
}
```

> ⚡ **Logic**: Phải có đơn hàng `DELIVERED` mới được đánh giá. Mỗi user chỉ đánh giá 1 lần/sản phẩm.

### GET `/product/{product_id}` – Xem đánh giá (Public)
**Response bao gồm**:
- Thống kê: tổng reviews, điểm TB, phân bố 1-5 sao
- Danh sách reviews với tên ẩn (privacy: `N***n`)

---

## 12. Returns

> **Prefix**: `/api/returns`  
> **File**: `app/api/v1/returns.py`

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `POST` | `/` | ✅ | Consumer | Tạo yêu cầu đổi/trả |
| `GET` | `/my` | ✅ | Consumer | Xem yêu cầu của mình |
| `PUT` | `/{return_id}/cancel` | ✅ | Consumer | Hủy yêu cầu (khi PENDING) |
| `GET` | `/` | ✅ | Admin | Xem tất cả yêu cầu |
| `PUT` | `/{return_id}/approve` | ✅ | Admin | Duyệt yêu cầu |
| `PUT` | `/{return_id}/reject` | ✅ | Admin | Từ chối yêu cầu |
| `PUT` | `/{return_id}/received` | ✅ | Admin | Đánh dấu đã nhận hàng trả |

### POST `/` – Tạo yêu cầu đổi/trả
```json
{
  "order_id": 5,
  "return_type": "RETURN",     // RETURN | EXCHANGE
  "reason": "Sản phẩm bị lỗi, không đúng mô tả trên website",
  "images": "[\"https://...\"]"
}
```

> ⚡ **State Machine**: `PENDING` → `APPROVED` → `RECEIVED` → (hoàn tiền/đổi hàng)  
> **Logic**: Chỉ tạo khi đơn `DELIVERED`. Không tạo trùng (kiểm tra PENDING/APPROVED).

---

## 13. Complaints

> **Prefix**: `/api/complaints`  
> **File**: `app/api/v1/complaints.py`

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ | All (phân quyền) | Danh sách khiếu nại |
| `POST` | `/` | ✅ | Consumer | Tạo khiếu nại mới |
| `GET` | `/{complaint_id}` | ✅ | Owner/Admin | Chi tiết khiếu nại |
| `PUT` | `/{complaint_id}/status` | ✅ | Admin/CS | Cập nhật trạng thái |
| `POST` | `/{complaint_id}/assign` | ✅ | Admin | Phân công CS xử lý |
| `POST` | `/{complaint_id}/threads` | ✅ | Owner/Admin/CS | Thêm comment |
| `GET` | `/{complaint_id}/threads` | ✅ | Owner/Admin/CS | Xem thread comments |

### POST `/` – Tạo khiếu nại
```json
{
  "order_id": 5,
  "type": "PRODUCT_QUALITY",     // ORDER_ISSUE, PRODUCT_QUALITY, DELIVERY, PAYMENT, OTHER
  "title": "Sản phẩm không đúng mô tả",
  "description": "Gạo bị ẩm mốc, không đúng hình ảnh...",
  "evidence_urls": "[\"https://...\"]"
}
```

### PUT `/{complaint_id}/status` – Cập nhật trạng thái
```json
{
  "status": "IN_PROGRESS",    // OPEN, IN_PROGRESS, WAITING_CUSTOMER, RESOLVED, CLOSED
  "note": "Đang liên hệ seller xác minh"
}
```

### POST `/{complaint_id}/threads` – Thread trả lời
```json
{
  "message": "Chúng tôi đã liên hệ seller...",
  "attachments": "[\"https://...\"]"
}
```

> ⚡ **SLA Tracking**: Hệ thống theo dõi SLA (`sla_deadline`). `complaint_status_logs` ghi lại mọi thay đổi trạng thái. Thread cho phép trao đổi 2 chiều giữa consumer ↔ CS/Admin.

---

## 14. Content

> **Prefix**: `/api/content`  
> **File**: `app/api/v1/content.py`

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ Optional | All (phân quyền) | Danh sách nội dung |
| `GET` | `/{content_id}` | ✅ Optional | All | Chi tiết nội dung |
| `POST` | `/` | ✅ | Seller/Admin | Tạo nội dung mới |
| `PUT` | `/{content_id}` | ✅ | Owner/Admin/CM | Cập nhật nội dung |
| `DELETE` | `/{content_id}` | ✅ | Owner/Admin/CM | Soft delete |
| `PUT` | `/{content_id}/restore` | ✅ | Admin/CM | Khôi phục nội dung |
| `POST` | `/{content_id}/approve` | ✅ | Admin/CM | Duyệt/từ chối nội dung |
| `GET` | `/{content_id}/audit-logs` | ✅ | Admin/CM | Xem audit log |

### POST `/` – Tạo nội dung
```json
{
  "title": "Bài viết giới thiệu Gạo ST25",
  "content": "Gạo ST25 là giống gạo thơm nổi tiếng...",  // ≥ 30 ký tự
  "content_type": "POST",         // POST | PRODUCT_DESCRIPTION | NEWS | ANNOUNCEMENT
  "author_id": 3,
  "product_id": 1,                // optional
  "images": "[\"https://...\"]",  // ≥ 1 media file
  "videos": null
}
```

> ⚡ **Quy trình**:
> - Seller phải KYC verified mới được tạo
> - Tạo xong → `PENDING` → Admin/CM duyệt
> - Sửa nội dung (trừ admin) → reset về `PENDING`
> - Mọi hành động ghi audit log (`ContentAuditLog`)
> - Validate: nội dung ≥ 30 ký tự, ≥ 1 ảnh/video

### Phân quyền xem content:
| Role | Nhìn thấy |
|------|-----------|
| Admin/CM | Tất cả (kể cả inactive nếu `include_inactive=true`) |
| Seller | Bài của mình (mọi status) + bài APPROVED công khai |
| Consumer/Guest | Chỉ APPROVED + is_active |

---

## 15. Media

> **Prefix**: `/api/medias`  
> **File**: `app/api/v1/media.py`  
> **Storage**: AWS S3

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/` | ✅ | Danh sách media |
| `GET` | `/{media_id}` | ✅ | Chi tiết media |
| `POST` | `/uploads` | ✅ | Upload file lên S3 |
| `DELETE` | `/{media_id}` | ✅ | Xóa media (S3 + DB) |

### POST `/uploads` – Upload file
- **Content-Type**: `multipart/form-data`
- **Field**: `file` (UploadFile)
- **Allowed types**: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `video/mp4`, `video/quicktime`
- **Max size**: 10 MB

**Response**:
```json
{
  "success": true,
  "id": 1,
  "filename": "product.jpg",
  "url": "https://bucket.s3.region.amazonaws.com/uuid.jpg",
  "file_type": "image",
  "file_size": 524288
}
```

> ⚡ Dùng `url` trả về gán vào trường `images`/`videos` của Product/Content.

---

## 16. Seller

> **Prefix**: `/api/seller`  
> **File**: `app/api/v1/seller.py`  
> **Quyền**: Chỉ seller/producer/admin

### Dashboard
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/dashboard` | ✅ | Tổng quan: doanh thu, đơn, SP |
| `GET` | `/revenue` | ✅ | Chi tiết doanh thu |
| `GET` | `/analytics` | ✅ | Top SP, rating TB |

### Quản lý đơn hàng Seller
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/orders` | ✅ | Danh sách đơn hàng của seller |
| `GET` | `/orders/{order_id}` | ✅ | Chi tiết đơn |
| `PUT` | `/orders/{order_id}/status` | ✅ | Cập nhật trạng thái (state machine) |

### Quản lý sản phẩm Seller
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/products` | ✅ | Danh sách SP của seller |
| `POST` | `/products` | ✅ | Tạo SP mới (KYC required) |
| `PUT` | `/products/{product_id}` | ✅ | Cập nhật SP (reset → PENDING) |
| `DELETE` | `/products/{product_id}` | ✅ | Xóa SP |

### Quản lý bài đăng Seller
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/posts` | ✅ | Danh sách bài đăng |
| `POST` | `/posts` | ✅ | Tạo bài đăng (chờ duyệt) |
| `PUT` | `/posts/{post_id}` | ✅ | Cập nhật bài đăng |
| `DELETE` | `/posts/{post_id}` | ✅ | Xóa bài đăng |

### Hợp đồng quảng cáo
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/contracts` | ✅ | Danh sách hợp đồng QC |
| `POST` | `/contracts` | ✅ | Tạo hợp đồng (DRAFT) |
| `PUT` | `/contracts/{contract_id}` | ✅ | Cập nhật (chỉ DRAFT) |
| `DELETE` | `/contracts/{contract_id}` | ✅ | Xóa (chỉ DRAFT) |

### Yêu cầu đổi trả (Seller view)
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/returns` | ✅ | Xem yêu cầu đổi trả thuộc đơn seller |
| `PUT` | `/returns/{return_id}` | ✅ | Seller ACCEPT/REJECT yêu cầu |

---

## 17. Seller Onboarding

> **Prefix**: `/api/seller` (cùng prefix với Seller)  
> **File**: `app/api/v1/seller_onboarding.py`

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `POST` | `/register` | ✅ | Seller | Nộp hồ sơ kinh doanh |
| `GET` | `/verification-status` | ✅ | Seller | Xem trạng thái xét duyệt |
| `PUT` | `/verify/{user_id}` | ✅ | Admin | Duyệt / từ chối hồ sơ |
| `GET` | `/applications` | ✅ | Admin | Xem danh sách hồ sơ chờ |

### POST `/register` – Nộp hồ sơ KYC
```json
{
  "business_name": "Hợp tác xã Nông sản Sạch",
  "business_type": "COOPERATIVE",     // INDIVIDUAL | HOUSEHOLD | COOPERATIVE | COMPANY
  "description": "...",
  "address": "...",
  "id_card_number": "079123456789",
  "id_card_front_url": "https://...",
  "id_card_back_url": "https://...",
  "business_license_url": "https://...",
  "bank_name": "Vietcombank",
  "bank_account_number": "0123456789",
  "bank_account_name": "NGUYEN VAN A"
}
```

### PUT `/verify/{user_id}` – Admin duyệt KYC
```json
{
  "status": "VERIFIED",          // VERIFIED | REJECTED
  "rejection_reason": null       // bắt buộc khi REJECTED
}
```

> ⚡ **Logic**: Khi `VERIFIED` → `user.activated = 1` (cho phép bán hàng). Nếu nộp lại → reset về `PENDING`.

---

## 18. Settlement

> **Prefix**: `/api/settlement`  
> **File**: `app/api/v1/settlement.py`

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/wallet` | ✅ | Seller | Xem ví (pending/available/withdrawn) |
| `GET` | `/history` | ✅ | Seller/Admin | Lịch sử kỳ đối soát |
| `POST` | `/create` | ✅ | Admin | Tạo kỳ đối soát cho seller |
| `POST` | `/{settlement_id}/approve` | ✅ | Admin | Duyệt kỳ đối soát |
| `POST` | `/{settlement_id}/payout` | ✅ | Admin | Chi trả cho seller |
| `GET` | `/payouts` | ✅ | Seller/Admin | Lịch sử chi trả |

### POST `/create` – Tạo kỳ đối soát
```json
{
  "seller_id": 3,
  "period_start": "2026-03-01T00:00:00",
  "period_end": "2026-03-31T23:59:59",
  "note": "Đối soát tháng 3/2026"
}
```

> ⚡ **Quy trình đối soát**:
> 1. Admin tạo kỳ → tự động tổng hợp đơn DELIVERED trong kỳ → tính `total_amount`, `platform_fee`, `seller_amount`
> 2. `seller_amount` cộng vào `pending_balance` của ví
> 3. Admin duyệt → chuyển `pending` → `available`
> 4. Admin chi trả → trừ `available`, cộng `total_withdrawn`, tạo payout record

### GET `/wallet` – Xem ví
```json
{
  "success": true,
  "data": {
    "seller_id": 3,
    "pending_balance": "500000",
    "available_balance": "2000000",
    "total_withdrawn": "5000000"
  }
}
```

---

## 19. Traceability

> **Prefix**: `/api/traceability`  
> **File**: `app/api/v1/traceability.py`

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `POST` | `/certificates` | ✅ | Seller | Thêm chứng nhận cho SP |
| `GET` | `/certificates/product/{product_id}` | ❌ | Public | Xem chứng nhận đã xác minh |
| `PUT` | `/certificates/{cert_id}/verify` | ✅ | Admin | Xác minh/từ chối chứng nhận |
| `POST` | `/origins` | ✅ | Seller | Khai báo nguồn gốc SP |
| `GET` | `/origins/product/{product_id}` | ❌ | Public | Xem nguồn gốc SP |
| `GET` | `/product/{product_id}` | ❌ | Public | Xem tất cả (origin + certs + SP info) |

### POST `/certificates` – Thêm chứng nhận
```json
{
  "product_id": 1,
  "certificate_name": "Chứng nhận OCOP 4 sao",
  "certificate_number": "OCOP-2026-001",
  "issued_by": "Sở NN&PTNT Sóc Trăng",
  "issue_date": "2026-01-15",
  "expiry_date": "2028-01-15",
  "document_url": "https://..."
}
```

### POST `/origins` – Khai báo nguồn gốc
```json
{
  "product_id": 1,
  "village_name": "Ấp Mỹ Phước, xã Mỹ Xuyên",
  "region_id": 3,
  "producer_name": "HTX Nông sản Sóc Trăng",
  "batch_number": "LOT-2026-03-001",
  "production_date": "2026-03-01",
  "expiry_date": "2027-03-01",
  "ingredients": "Lúa ST25, nước sạch",
  "process_summary": "Thu hoạch → xay xát → đóng gói → kiểm định"
}
```

> ⚡ Mỗi SP chỉ có 1 origin record. Nếu đã tồn tại → cập nhật. Chứng nhận cần admin xác minh (`PENDING → VERIFIED`). Public endpoint chỉ hiển thị chứng nhận đã `VERIFIED`.

---

## 20. Promotions

> **Prefix**: `/api/promotions`  
> **File**: `app/api/v1/promotions.py`

| Method | Endpoint | Auth | Quyền | Mô tả |
|--------|----------|------|-------|--------|
| `GET` | `/` | ✅ | Admin | Danh sách mã KM |
| `GET` | `/public` | ✅ Optional | All | Xem mã KM công khai đang hoạt động |
| `GET` | `/{promotion_id}` | ✅ | Admin | Chi tiết mã KM |
| `POST` | `/` | ✅ | Admin | Tạo mã KM mới |
| `PUT` | `/{promotion_id}` | ✅ | Admin | Cập nhật mã KM |
| `DELETE` | `/{promotion_id}` | ✅ | Admin | Xóa mã KM |

### POST `/` – Tạo mã khuyến mãi
```json
{
  "code": "SUMMER2026",
  "name": "Khuyến mãi mùa hè",
  "description": "Giảm 20% đơn từ 200k",
  "promotion_type": "PERCENTAGE",         // PERCENTAGE | FIXED_AMOUNT
  "discount_value": 20,                   // 20% hoặc 20000 VND
  "min_order_amount": 200000,
  "max_discount_amount": 50000,           // optional: giới hạn số tiền giảm tối đa
  "usage_limit": 100,                     // optional: giới hạn lượt dùng
  "start_date": "2026-06-01T00:00:00",
  "end_date": "2026-06-30T23:59:59",
  "is_public": true
}
```

> ⚡ Code tự động uppercase. `end_date > start_date`. Public endpoint chỉ hiển thị mã `ACTIVE`, `is_public=true`, trong thời hạn.

---

## 21. Mobile App

> **Prefix**: `/api/mobile`  
> **File**: `app/api/v1/mobile_app.py`  
> **Mục đích**: API tối ưu cho ứng dụng di động

### Trang chủ & Sản phẩm
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/home` | ❌ | Trang chủ: banner, SP nổi bật, danh mục |
| `GET` | `/products` | ❌ | Tìm kiếm & lọc SP |
| `GET` | `/products/{product_id}` | ❌ | Chi tiết SP (kèm variants, origin) |
| `GET` | `/categories` | ❌ | Danh sách danh mục active |

### Giỏ hàng & Đặt hàng
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/cart` | ✅ | Xem giỏ hàng |
| `POST` | `/cart/add` | ✅ | Thêm SP vào giỏ |
| `PUT` | `/cart/update/{item_id}` | ✅ | Cập nhật số lượng |
| `DELETE` | `/cart/remove/{item_id}` | ✅ | Xóa SP khỏi giỏ |
| `POST` | `/checkout` | ✅ | **Đặt hàng** (core flow) |

### Đơn hàng Consumer
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/orders/my` | ✅ | Danh sách đơn hàng của tôi |
| `GET` | `/orders/my/{order_id}` | ✅ | Chi tiết đơn hàng |
| `PUT` | `/orders/my/{order_id}/cancel` | ✅ | Hủy đơn hàng |

### Profile
| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/profile` | ✅ | Xem profile |
| `PUT` | `/profile` | ✅ | Cập nhật profile |

### POST `/checkout` – Đặt hàng (⚡ Critical Flow)
```json
{
  "shipping_address": "123 Nguyễn Huệ, Q1, TP.HCM",
  "payment_method": "VNPAY",         // VNPAY | COD
  "customer_note": "Giao giờ hành chính",
  "promotion_code": "SUMMER2026"     // optional
}
```

> ⚡ **Business Logic quan trọng**:
> 1. Lấy giỏ hàng → nhóm theo seller → tạo Order riêng cho mỗi seller
> 2. **Row-level locking** (`SELECT FOR UPDATE`) trên sản phẩm để tránh race condition
> 3. Validate tồn kho trước khi trừ
> 4. Tính phí: `subtotal` + `shipping_fee` + `platform_fee` - `discount` = `total_amount`
> 5. Sinh `order_number` duy nhất
> 6. Tạo `OrderItem` cho từng line
> 7. Xóa giỏ hàng sau khi đặt thành công
> 8. Nếu VNPAY → tạo Payment + trả payment_url
> 9. Nếu COD → trả kết quả trực tiếp

### PUT `/orders/my/{order_id}/cancel` – Hủy đơn
```json
{
  "cancel_reason": "Tôi muốn đổi sản phẩm khác"   // optional
}
```

> ⚡ Chỉ hủy khi `PENDING` hoặc `CONFIRMED`. Tự động hoàn tồn kho. Ghi audit log.

---

## 📊 Bảng tổng hợp Permission Matrix

| Hành động | Guest | Consumer | Seller | Admin |
|-----------|-------|----------|--------|-------|
| Xem SP public | ✅ | ✅ | ✅ | ✅ |
| Tạo SP | ❌ | ❌ | ✅ (KYC) | ✅ |
| Duyệt SP | ❌ | ❌ | ❌ | ✅ |
| Đặt hàng | ❌ | ✅ | ✅ | ✅ |
| Xem đơn hàng | ❌ | Đơn mình | Đơn store | Tất cả |
| Cập nhật trạng thái đơn | ❌ | Cancel only | CONFIRMED→SHIPPING | Tất cả |
| Thanh toán | ❌ | ✅ | ❌ | ✅ |
| Hoàn tiền | ❌ | ❌ | ❌ | ✅ |
| Đánh giá SP | ❌ | ✅ (DELIVERED) | ❌ | ❌ |
| Khiếu nại | ❌ | ✅ | ❌ | ✅ |
| Quản lý user | ❌ | ❌ | ❌ | ✅ |
| Upload media | ❌ | ✅ | ✅ | ✅ |
| Đối soát | ❌ | ❌ | Xem ví | ✅ |

---

## 🔄 State Machine Summary

### Order Status
```
PENDING → CONFIRMED → PROCESSING → SHIPPING → DELIVERED
    ↓         ↓
 CANCELLED  CANCELLED                          → REFUNDED
```

### Payment Status
```
UNPAID → PAID → REFUNDED
```

### Product Status
```
PENDING → APPROVED
    ↓
 REJECTED → PENDING (khi sửa lại)
```

### Return Status
```
PENDING → APPROVED → RECEIVED → (hoàn tiền/đổi hàng)
    ↓         ↓
 CANCELLED  REJECTED
```

### Complaint Status
```
OPEN → IN_PROGRESS → WAITING_CUSTOMER → RESOLVED → CLOSED
```

### Settlement Status
```
PENDING → APPROVED → COMPLETED (sau khi payout)
```

### Content Status
```
PENDING → APPROVED
    ↓
 REJECTED → PENDING (khi sửa lại)
```

---

## 🛡️ Security Notes

1. **API Secret**: Mọi request phải có `X-Quan-Secret` header (trừ `/docs`, `/health`)
2. **JWT Auth**: Bearer token trong `Authorization` header, expires 30 phút
3. **Refresh Token**: Dùng để lấy access_token mới, expires 7 ngày
4. **Row-level Locking**: Checkout dùng `SELECT FOR UPDATE` tránh race condition
5. **Idempotency**: VNPAY IPN kiểm tra giao dịch trùng lặp
6. **Ownership Check**: Consumer chỉ xem/sửa data của mình, Seller chỉ xem data store mình
7. **KYC Gate**: Seller phải verified KYC trước khi tạo sản phẩm/nội dung
8. **Soft Delete**: Hầu hết entity dùng `is_active` / `deleted_at` thay vì xóa vĩnh viễn
9. **Audit Trail**: Mọi thay đổi trạng thái quan trọng đều ghi log
