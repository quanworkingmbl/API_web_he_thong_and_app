# 📱 API Documentation – Mobile App

> **Base URL**: `https://api.quancmsbe.site/api`  
> **Auth Header**: `Authorization: Bearer <JWT_TOKEN>`  
> **Secret Header**: `X-Quan-Secret: <API_SECRET>`

---

## 📋 Mục lục

| # | Module | Prefix | Loại |
|---|--------|--------|------|
| 1 | [Authentication](#1-authentication) | `/api/auth` | 🌐 Dùng chung |
| 2 | [Bài đăng (Seller)](#2-bài-đăng-seller) | `/api/seller/posts` | 🌐 Dùng chung |
| 3 | [Sản phẩm](#3-sản-phẩm) | `/api/mobile/products`, `/api/seller/products` | 📱/🌐 |
| 4 | [Giỏ hàng & Checkout](#4-giỏ-hàng--checkout) | `/api/mobile/cart`, `/api/mobile/checkout` | 📱 Riêng mobile |
| 5 | [Đơn hàng](#5-đơn-hàng) | `/api/mobile/orders/my` | 📱 Riêng mobile |
| 6 | [Đánh giá sản phẩm](#6-đánh-giá-sản-phẩm) | `/api/reviews` | 🌐 Dùng chung |
| 7 | [Hợp đồng quảng cáo](#7-hợp-đồng-quảng-cáo) | `/api/seller/contracts` | 🌐 Dùng chung |
| 8 | [Yêu cầu đổi trả](#8-yêu-cầu-đổi-trả) | `/api/returns` | 🌐 Dùng chung |
| 9 | [Khuyến mãi](#9-khuyến-mãi) | `/api/promotions` | 🌐 Dùng chung |
| 10 | [Thanh toán](#10-thanh-toán) | `/api/payments` | 🌐 Dùng chung |
| 11 | [Hồ sơ cá nhân](#11-hồ-sơ-cá-nhân) | `/api/mobile/profile` | 📱 Riêng mobile |
| 12 | [Upload Media](#12-upload-media) | `/api/medias/uploads` | 🌐 Dùng chung |
| 13 | [Thông báo Mobile](#13-thông-báo-mobile) | `/api/mobile/notifications` | 📱 Riêng mobile |
| 14 | [Vùng & Sổ địa chỉ Mobile](#14-vùng--sổ-địa-chỉ-mobile) | `/api/mobile/regions`, `/api/mobile/addresses` | 📱 Riêng mobile |

---

## 🔑 Quy ước chung

| Ký hiệu | Ý nghĩa |
|---------|---------|
| 📱 **Riêng mobile** | Endpoint tối ưu cho app, prefix `/api/mobile/` |
| 🌐 **Dùng chung** | Endpoint dùng chung với web admin/seller panel |

### Response chuẩn
```json
{
  "success": true,
  "message": "...",
  "data": { ... },
  "meta": { "total": 100, "page": 1, "limit": 20, "total_pages": 5 }
}
```

---

## 1. Authentication

> **Prefix**: `/api/auth` | 🌐 **Dùng chung**  
> **File**: `app/api/v1/auth.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `POST` | `/api/auth/login` | ❌ | Đăng nhập → nhận access_token + refresh_token |
| `POST` | `/api/auth/refresh` | ❌ | Làm mới access_token khi hết hạn |
| `GET` | `/api/auth/me` | ✅ | Lấy thông tin user đang đăng nhập (kèm profile tóm tắt: SĐT + địa chỉ mặc định) |
| `GET` | `/api/auth/profile` | ✅ | Profile dùng chung cho Web/App (đầy đủ phone + address + tỉnh/quận/phường) |
| `PUT` | `/api/auth/profile` | ✅ | Cập nhật profile dùng chung |
| `PUT` | `/api/auth/change-password` | ✅ | Đổi mật khẩu |

### POST `/api/auth/login`
```json
// Request
{
  "email": "seller@example.com",
  "password": "StrongPass123"
}

// Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "seller@example.com",
    "name": "Nguyễn Văn A",
    "type": "seller"
  }
}
```

> `access_token` hết hạn sau **30 phút** → gọi `/auth/refresh` để lấy mới.  
> Lưu cả 2 token vào secure storage của app.

### GET `/api/auth/profile`
```json
{
  "success": true,
  "message": "Lấy thông tin profile thành công",
  "data": {
    "id": 12,
    "email": "bao1@gmail.com",
    "name": "Vuong Quoc Bao",
    "gender": "male",
    "type": "consumer",
    "phone": "0123456789",
    "address": "123 Trần Hưng Đạo",
    "province_name": "Hồ Chí Minh",
    "district_name": "Quận 5",
    "ward_name": "Phường 04",
    "full_address": "123 Trần Hưng Đạo, Phường 04, Quận 5, Hồ Chí Minh",
    "primary_address": {
      "id": 101,
      "recipient_name": "Vương Quốc Bảo",
      "phone": "0123456789",
      "province_code": "79",
      "province_name": "Hồ Chí Minh",
      "district_code": "775",
      "district_name": "Quận 5",
      "ward_code": "27196",
      "ward_name": "Phường 04",
      "address_line": "123 Trần Hưng Đạo",
      "full_address": "123 Trần Hưng Đạo, Phường 04, Quận 5, Hồ Chí Minh",
      "is_default": true
    }
  }
}
```

### PUT `/api/auth/profile`
```json
{
  "name": "Vương Quốc Bảo",
  "gender": "male",
  "phone": "0123456789",
  "address_line": "123 Trần Hưng Đạo",
  "province_code": "79",
  "district_code": "775",
  "ward_code": "27196"
}
```

### POST `/api/auth/refresh`
```json
// Request
{ "refresh_token": "eyJ..." }

// Response
{ "access_token": "eyJ...", "token_type": "bearer" }
```

### PUT `/api/auth/change-password`
```json
{
  "old_password": "OldPass123",
  "new_password": "NewPass456"
}
```

---

## 2. Bài đăng (Seller)

> **Prefix**: `/api/seller/posts` | 🌐 **Dùng chung**  
> **File**: `app/api/v1/seller.py`  
> **Quyền**: Seller/Producer đã KYC

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/seller/posts` | ✅ | Xem danh sách bài đăng của seller |
| `POST` | `/api/seller/posts` | ✅ | Tạo bài đăng mới |
| `PUT` | `/api/seller/posts/{post_id}` | ✅ | Cập nhật bài đăng |
| `DELETE` | `/api/seller/posts/{post_id}` | ✅ | Xóa bài đăng |

### GET `/api/seller/posts`
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `status` | string | PENDING \| APPROVED \| REJECTED |
| `page` / `limit` | int | Phân trang |

### POST `/api/seller/posts` – Tạo bài đăng

#### Bảng field

| Field | Type | Bắt buộc | Validation | Mô tả |
|-------|------|----------|------------|-------|
| `title` | string | ✅ | 2–255 ký tự | Tiêu đề bài đăng |
| `content` | string | ❌ | — | Nội dung bài đăng |
| `content_type` | string | ❌ | `POST` \| `PRODUCT_DESCRIPTION` \| `NEWS` \| `ANNOUNCEMENT` | Mặc định: `POST` |
| `product_id` | integer | ❌ | ID sản phẩm hợp lệ | Liên kết sản phẩm |
| `images` | string | ❌ | JSON string của array URL | Ảnh bài đăng |
| `videos` | string | ❌ | JSON string của array URL | Video bài đăng |

#### Request body mẫu (đầy đủ)
```json
{
  "title": "Giới thiệu Gạo ST25 chính hãng",
  "content": "Gạo ST25 được trồng tại Sóc Trăng, nổi tiếng thơm ngon...",
  "content_type": "POST",
  "product_id": 1,
  "images": "[\"https://s3.amazonaws.com/bucket/image1.jpg\", \"https://s3.amazonaws.com/bucket/image2.jpg\"]",
  "videos": null
}
```

#### Request body tối giản (chỉ bắt buộc)
```json
{
  "title": "Giới thiệu Gạo ST25 chính hãng"
}
```

> [!IMPORTANT]
> **`images` và `videos` phải là JSON string, KHÔNG phải array.**  
> ✅ Đúng: `"images": "[\"https://url.com/img.jpg\"]"` (string chứa JSON)  
> ❌ Sai: `"images": ["https://url.com/img.jpg"]` (array trực tiếp → 422)

> [!NOTE]
> **`content_type`** phải là một trong 4 giá trị UPPERCASE: `POST`, `PRODUCT_DESCRIPTION`, `NEWS`, `ANNOUNCEMENT`.  
> Gửi sai giá trị (ví dụ `"post"` thường thường) → 422.

> Upload ảnh trước qua `/api/medias/uploads` → lấy `url` → ghép thành JSON string → điền vào `images`.  
> Bài đăng sau khi tạo → status `PENDING`, cần Admin duyệt. Sửa nội dung → reset về `PENDING`.

---

## 3. Sản phẩm

> **File**: `app/api/v1/seller.py`, `app/api/v1/mobile_app.py`

### Seller quản lý sản phẩm | 🌐 Dùng chung

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/seller/products` | ✅ | Xem danh sách SP của seller |
| `POST` | `/api/seller/products` | ✅ | Tạo sản phẩm mới (KYC required) |
| `PUT` | `/api/seller/products/{product_id}` | ✅ | Cập nhật sản phẩm |
| `DELETE` | `/api/seller/products/{product_id}` | ✅ | Xóa sản phẩm |

### Consumer xem sản phẩm | 📱 Riêng mobile

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/mobile/home` | ❌ | Trang chủ tổng hợp (categories, featured, promotions) |
| `GET` | `/api/mobile/products` | ❌ | Danh sách SP công khai (đã duyệt) |
| `GET` | `/api/mobile/products/{product_id}` | ❌ | Chi tiết SP (kèm variants, nguồn gốc) |
| `GET` | `/api/mobile/shops/{seller_id}` | ❌ | Trang cửa hàng và sản phẩm của seller |

### GET `/api/mobile/products` – Lọc sản phẩm
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `seller_id` | int | Lọc theo cửa hàng |
| `category_id` | int | Lọc theo danh mục |
| `label` | string | NORMAL \| OCOP \| ORGANIC \| GEOGRAPHICAL_INDICATION |
| `search` | string | Tìm theo tên sản phẩm |
| `min_price` / `max_price` | decimal | Khoảng giá |
| `sort_by` | string | `price_asc` \| `price_desc` \| `newest` \| `rating` |
| `page` / `limit` | int | Phân trang |

### POST `/api/seller/products` – Tạo sản phẩm
```json
{
  "name": "Gạo ST25 Sóc Trăng",
  "description": "Gạo thơm đặc sản...",
  "category_id": 1,
  "region_id": 3,
  "price": 85000,
  "stock_quantity": 500,
  "unit": "kg",
  "images": "[\"https://s3.amazonaws.com/...\"]"
}
```

> Seller phải **KYC verified** mới tạo được SP. Sản phẩm tạo → `PENDING` → Admin duyệt → `APPROVED` mới hiển thị công khai.

---

## 4. Giỏ hàng & Checkout

> **Prefix**: `/api/mobile/cart`, `/api/mobile/checkout` | 📱 **Riêng mobile**  
> **File**: `app/api/v1/mobile_app.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/mobile/cart` | ✅ | Xem giỏ hàng hiện tại |
| `POST` | `/api/mobile/cart/items` | ✅ | Thêm sản phẩm vào giỏ |
| `PUT` | `/api/mobile/cart/items/{item_id}` | ✅ | Cập nhật số lượng |
| `DELETE` | `/api/mobile/cart/items/{item_id}` | ✅ | Xóa sản phẩm khỏi giỏ |
| `DELETE` | `/api/mobile/cart` | ✅ | Xóa toàn bộ giỏ hàng |
| `POST` | `/api/mobile/checkout` | ✅ | Đặt hàng từ giỏ hàng |

### POST `/api/mobile/cart/items` – Thêm vào giỏ
```json
{
  "product_id": 1,
  "quantity": 2,
  "variant_id": null    // null nếu SP không có biến thể
}
```

### GET `/api/mobile/cart` – Response giỏ hàng
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "variant_id": null,
        "seller_id": 3,
        "seller_name": "Nông trại A",
        "product_name": "Gạo ST25",
        "product_image": "https://...",
        "unit_label": "1kg",
        "location_label": "Gạo đặc sản",
        "unit_price": "85000",
        "quantity": 2,
        "subtotal": "170000",
        "stock_quantity": 498,
        "is_active": true
      }
    ],
    "total_items": 1,
    "subtotal": "170000",
    "shipping_fee": "30000",
    "discount_amount": "0",
    "total_amount": "200000",
    "updated_at": "2026-04-15T03:41:19.019877"
  }
}
```

### Trường trả về của `data.items[]` trong giỏ hàng

| Field | Type | Mô tả hiển thị |
|-------|------|----------------|
| `id` | int | ID item giỏ hàng |
| `product_id` | int | ID sản phẩm |
| `variant_id` | int/null | ID biến thể (nếu có) |
| `seller_id` | int | ID người bán |
| `seller_name` | string | Tên cửa hàng hiển thị |
| `product_name` | string | Tên sản phẩm |
| `product_image` | string/null | Ảnh đại diện |
| `unit_label` | string | Đơn vị hiển thị |
| `location_label` | string | Nhãn khu vực/danh mục hiển thị |
| `unit_price` | string(number) | Đơn giá |
| `quantity` | int | Số lượng |
| `subtotal` | string(number) | Thành tiền dòng |
| `stock_quantity` | int | Tồn kho khả dụng |
| `is_active` | bool | Trạng thái còn bán |

### POST `/api/mobile/checkout` – Đặt hàng
```json
// Request
{
  "customer_name": "Nguyễn Văn A",
  "customer_phone": "0909123456",
  "customer_email": "a@gmail.com",
  "shipping_address": "123 Nguyễn Huệ, Q1, TP.HCM",
  "shipping_province": "79",
  "shipping_district": "760",
  "shipping_ward": "26734",
  "seller_id": 3,
  "payment_method": "COD",          // COD | BANK_TRANSFER | MOMO | VNPAY | ZALOPAY | PLATFORM_CREDITS
  "customer_note": "Giao giờ hành chính",
  "coupon_code": "SUMMER2026",      // optional
  "items": [
    { "product_id": 1, "quantity": 2, "variant_id": null },
    { "product_id": 4, "quantity": 1, "variant_id": 11 }
  ]
}

// Response (COD)
{
  "success": true,
  "data": {
    "order_id": 1,
    "order_number": "ORD-2026-001",
    "seller_id": 3,
    "total_amount": "170000",
    "discount_amount": "10000",
    "applied_promotion": {
      "id": 12,
      "code": "SUMMER2026",
      "name": "Giảm giá mùa hè",
      "auto_applied": false
    },
    "status": "PENDING",
    "payment_method": "COD"
  }
}
```

### Trường trả về trong `data` khi checkout thành công

| Field | Type | Mô tả hiển thị |
|-------|------|----------------|
| `order_id` | int | ID đơn hàng |
| `order_number` | string | Mã đơn |
| `seller_id` | int | ID người bán |
| `total_amount` | string(number) | Tổng tiền sau phí/giảm |
| `discount_amount` | string(number) | Giá trị giảm giá áp dụng |
| `applied_promotion` | object/null | Mã giảm giá thực tế áp dụng |
| `status` | string | Trạng thái đơn ban đầu (`PENDING`) |
| `payment_method` | string | Phương thức thanh toán |

> **Luồng checkout**:
> 1. **Kiểu A**: giỏ hàng chỉ được chứa sản phẩm của **1 seller**
> 2. Nếu có nhiều seller trong payload `items` → trả lỗi `400`
> 3. Nếu client gửi `seller_id` nhưng không khớp dữ liệu item → trả lỗi `400`
> 4. Kiểm tra & trừ tồn kho (có row-level locking tránh race condition)
> 5. Áp mã khuyến mãi nếu có
> 6. Tạo **một** đơn hàng duy nhất cho seller đó

---

## 5. Đơn hàng

> **Prefix**: `/api/mobile/orders/my` | 📱 **Riêng mobile**  
> **File**: `app/api/v1/mobile_app.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/mobile/orders/my` | ✅ | Danh sách đơn hàng của tôi |
| `GET` | `/api/mobile/orders/my/{order_id}` | ✅ | Chi tiết đơn hàng |
| `GET` | `/api/mobile/orders/my/{order_id}/timeline` | ✅ | Timeline trạng thái đơn hàng |
| `POST` | `/api/mobile/orders/my/{order_id}/confirm-received` | ✅ | Xác nhận đã nhận hàng |
| `PUT` | `/api/mobile/orders/my/{order_id}/cancel` | ✅ | Hủy đơn hàng |

### GET `/api/mobile/orders/my`
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `status` | string | PENDING \| CONFIRMED \| PROCESSING \| SHIPPING \| DELIVERED \| CANCELLED |
| `page` / `limit` | int | Phân trang |

### Trường trả về chính trong `GET /api/mobile/orders/my` (`data[]`)

| Field | Type | Mô tả hiển thị |
|-------|------|----------------|
| `id` | int | ID đơn |
| `order_number` | string | Mã đơn |
| `seller_name` | string/null | Tên shop |
| `total_amount` | string(number) | Tổng tiền |
| `status` | string | Trạng thái đơn |
| `payment_method` | string | Phương thức thanh toán |
| `payment_status` | string | Trạng thái thanh toán |
| `item_count` | int | Tổng số dòng sản phẩm |
| `first_item_image` | string/null | Ảnh dòng đầu tiên |
| `items` | array | Danh sách item tóm tắt của đơn |
| `created_at` | datetime string | Thời điểm tạo |

### Trường trả về chính trong `GET /api/mobile/orders/my/{order_id}` (`data`)

| Field | Type | Mô tả hiển thị |
|-------|------|----------------|
| `id`, `order_number`, `seller_id`, `seller_name` | mixed | Định danh đơn/nhà bán |
| `subtotal`, `shipping_fee`, `discount_amount`, `total_amount` | string(number) | Khối thanh toán |
| `status`, `payment_method`, `payment_status` | string | Trạng thái đơn/thanh toán |
| `shipping_address`, `customer_note`, `coupon_code` | string/null | Thông tin giao hàng |
| `can_cancel`, `can_review` | bool | Cờ khả năng thao tác UI |
| `created_at`, `confirmed_at`, `shipped_at`, `delivered_at` | datetime string/null | Mốc thời gian |
| `items` | array | Danh sách item chi tiết |
| `timeline` | array | Lịch sử chuyển trạng thái |
| `shipment` | object/null | Tracking và đơn vị vận chuyển |

### POST `/api/mobile/orders/my/{order_id}/confirm-received`

```json
// Request (optional)
{
  "note": "Đã nhận đủ hàng"
}

// Response
{
  "success": true,
  "message": "Đã xác nhận nhận hàng. Cảm ơn bạn!",
  "order_id": 1,
  "new_status": "DELIVERED",
  "payment_status": "PAID",
  "can_review": true
}
```

### PUT `/api/mobile/orders/my/{order_id}/cancel` – Hủy đơn
```json
{
  "cancel_reason": "Tôi muốn đổi sản phẩm khác"
}
```

> Chỉ hủy được khi đơn đang `PENDING` hoặc `CONFIRMED`. Tồn kho tự động hoàn lại sau khi hủy.

---

## 6. Đánh giá sản phẩm

> **Prefix**: `/api/reviews` | 🌐 **Dùng chung**  
> **File**: `app/api/v1/reviews.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/reviews/product/{product_id}` | ❌ | Xem đánh giá sản phẩm (public) |
| `POST` | `/api/reviews` | ✅ | Tạo đánh giá |
| `PUT` | `/api/reviews/{review_id}` | ✅ | Cập nhật đánh giá |
| `DELETE` | `/api/reviews/{review_id}` | ✅ | Xóa đánh giá |

### POST `/api/reviews` – Tạo đánh giá
```json
{
  "product_id": 1,
  "order_id": 5,     // bắt buộc – đơn phải ở trạng thái DELIVERED
  "rating": 5,        // 1-5 sao
  "comment": "Sản phẩm rất tốt!"
}
```

### GET `/api/reviews/product/{product_id}` – Xem đánh giá
```json
{
  "data": {
    "stats": {
      "total_reviews": 42,
      "avg_rating": 4.7,
      "rating_distribution": { "5": 30, "4": 8, "3": 3, "2": 1, "1": 0 }
    },
    "reviews": [
      { "reviewer_name": "N***n", "rating": 5, "comment": "...", "created_at": "..." }
    ]
  }
}
```

> Điều kiện tạo đánh giá: đơn hàng phải `DELIVERED`. Mỗi user chỉ đánh giá **1 lần/sản phẩm**.

---

## 7. Hợp đồng quảng cáo

> **Prefix**: `/api/seller/contracts` | 🌐 **Dùng chung**  
> **File**: `app/api/v1/seller.py`  
> **Quyền**: Seller

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/seller/contracts` | ✅ | Xem danh sách hợp đồng |
| `POST` | `/api/seller/contracts` | ✅ | Tạo hợp đồng mới |
| `PUT` | `/api/seller/contracts/{contract_id}` | ✅ | Cập nhật (chỉ khi DRAFT) |
| `DELETE` | `/api/seller/contracts/{contract_id}` | ✅ | Xóa (chỉ khi DRAFT) |

### POST `/api/seller/contracts` – Tạo hợp đồng
```json
{
  "contract_number": "QC-2026-001",
  "contract_type": "ADVERTISING",       // ADVERTISING | PARTNERSHIP | DISTRIBUTION | OTHER
  "start_date": "2026-05-01T00:00:00",
  "end_date": "2026-07-31T23:59:59",
  "amount": 5000000,
  "terms": "Điều khoản hợp đồng..."
}
```

> Hợp đồng tạo → status `DRAFT`, Admin duyệt → `ACTIVE`. Chỉ sửa/xóa khi còn `DRAFT`.

---

## 8. Yêu cầu đổi trả

> **Prefix**: `/api/returns` | 🌐 **Dùng chung**  
> **File**: `app/api/v1/returns.py`  
> **Quyền**: Consumer

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/returns/my` | ✅ | Danh sách yêu cầu của tôi |
| `POST` | `/api/returns` | ✅ | Tạo yêu cầu đổi/trả |
| `PUT` | `/api/returns/{return_id}/cancel` | ✅ | Hủy yêu cầu (khi còn PENDING) |

### GET `/api/returns/my`
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `status` | string | PENDING \| APPROVED \| REJECTED \| RECEIVED \| CANCELLED |
| `page` / `limit` | int | Phân trang |

### POST `/api/returns` – Tạo yêu cầu đổi/trả
```json
{
  "order_id": 5,
  "return_type": "RETURN",      // RETURN | EXCHANGE
  "reason": "Sản phẩm bị lỗi, không đúng mô tả",
  "images": "[\"https://s3.amazonaws.com/evidence.jpg\"]"
}
```

> Điều kiện: đơn hàng phải ở trạng thái `DELIVERED`. Không tạo trùng nếu đã có yêu cầu `PENDING`/`APPROVED`.

---

## 9. Khuyến mãi

> **Prefix**: `/api/promotions`, `/api/mobile/promotions` | 🌐/📱  
> **File**: `app/api/v1/promotions.py`, `app/api/v1/mobile_app.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/promotions/public` | ❌ | Xem mã khuyến mãi công khai đang hoạt động |
| `POST` | `/api/mobile/promotions/apply` | ✅ | Validate mã và tính số tiền được giảm ngay tại checkout |

### GET `/api/promotions/public`
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `search` | string | Tìm theo code hoặc tên |
| `page` / `limit` | int | Phân trang |

```json
// Response
{
  "data": [
    {
      "id": 1,
      "code": "SUMMER2026",
      "name": "Khuyến mãi mùa hè",
      "promotion_type": "PERCENTAGE",
      "discount_value": "20",
      "min_order_amount": "200000",
      "max_discount_amount": "50000",
      "end_date": "2026-06-30T23:59:59"
    }
  ]
}
```

### POST `/api/mobile/promotions/apply`

```json
// Request
{
  "coupon_code": "SUMMER2026",
  "subtotal": 250000,
  "seller_id": 3,
  "product_ids": [1, 4],
  "category_ids": [2]
}

// Response success
{
  "success": true,
  "data": {
    "valid": true,
    "promotion_id": 12,
    "promotion_name": "Giảm giá mùa hè",
    "promotion_type": "PERCENTAGE",
    "applicable_to": "SELLER",
    "discount_amount": "20000",
    "new_subtotal": "230000",
    "message": "Áp mã thành công: Giảm 20,000đ"
  }
}
```

> Áp dụng mã KM khi checkout: điền `coupon_code` vào body của `POST /api/mobile/checkout`.

---

## 10. Thanh toán

> **Prefix**: `/api/payments` | 🌐 **Dùng chung**  
> **File**: `app/api/v1/payments.py`  
> **Tích hợp**: VNPAY

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/payments` | ✅ | Xem lịch sử giao dịch |
| `POST` | `/api/payments/create` | ✅ | Tạo link thanh toán VNPAY |
| `GET` | `/api/payments/vnpay-return` | ❌ | VNPAY redirect về sau khi thanh toán |

### GET `/api/payments` – Lịch sử giao dịch
| Query Param | Type | Mô tả |
|-------------|------|--------|
| `status` | string | PENDING \| SUCCESS \| FAILED \| REFUNDED |
| `page` / `limit` | int | Phân trang |

> Consumer chỉ xem được lịch sử của mình.

### POST `/api/payments/create` – Tạo link VNPAY
```json
// Request
{
  "order_id": 1,
  "payment_method": "VNPAY"
}

// Response
{
  "payment_url": "https://sandbox.vnpayment.vn/...",
  "payment_id": 1,
  "txn_ref": "TXN_1_1712345678"
}
```

> Luồng: Lấy `payment_url` → mở **WebView** hoặc **in-app browser** → user thanh toán → VNPAY redirect về `/api/payments/vnpay-return` → cập nhật trạng thái đơn.

---

## 11. Hồ sơ cá nhân

> **Prefix**: `/api/mobile/profile` | 📱 **Riêng mobile**  
> **File**: `app/api/v1/mobile_app.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/mobile/profile` | ✅ | Xem thông tin cá nhân |
| `PUT` | `/api/mobile/profile` | ✅ | Cập nhật thông tin cá nhân |

### GET `/api/mobile/profile`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "seller@example.com",
    "name": "Nguyễn Văn A",
    "type": "seller",
    "gender": "male",
    "activated": 1,
    "created_at": "2026-01-01T00:00:00",
    "phone": "0909123456",
    "address": "123 Nguyễn Huệ",
    "province_name": "TP Hồ Chí Minh",
    "district_name": "Quận 1",
    "ward_name": "Phường Bến Nghé",
    "full_address": "123 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP Hồ Chí Minh",
    "primary_address": {
      "id": 10,
      "recipient_name": "Nguyễn Văn A",
      "phone": "0909123456",
      "province_code": "79",
      "province_name": "TP Hồ Chí Minh",
      "district_code": "760",
      "district_name": "Quận 1",
      "ward_code": "26734",
      "ward_name": "Phường Bến Nghé",
      "address_line": "123 Nguyễn Huệ",
      "full_address": "123 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP Hồ Chí Minh",
      "is_default": true
    },
    "addresses": [
      {
        "id": 10,
        "recipient_name": "Nguyễn Văn A",
        "phone": "0909123456",
        "province_code": "79",
        "province_name": "TP Hồ Chí Minh",
        "district_code": "760",
        "district_name": "Quận 1",
        "ward_code": "26734",
        "ward_name": "Phường Bến Nghé",
        "address_line": "123 Nguyễn Huệ",
        "full_address": "123 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP Hồ Chí Minh",
        "is_default": true
      }
    ],
    "order_stats": {
      "total": 15,
      "pending": 2,
      "delivered": 10
    }
  }
}
```

### PUT `/api/mobile/profile` – Cập nhật
```json
{
  "name": "Nguyễn Văn B",
  "gender": "female"
}
```

### Trường trả về profile (`data`)

| Field | Type | Mô tả hiển thị |
|-------|------|----------------|
| `id`, `email`, `name`, `type`, `gender`, `activated`, `created_at` | mixed | Thông tin tài khoản |
| `phone`, `address`, `province_name`, `district_name`, `ward_name`, `full_address` | mixed | Thông tin liên hệ + địa chỉ mặc định để hiển thị nhanh |
| `primary_address` | object/null | Địa chỉ mặc định chi tiết (nếu có) |
| `addresses` | array | Danh sách địa chỉ đã lưu (đầy đủ tên tỉnh/quận/phường) |
| `order_stats.total` | int | Tổng số đơn |
| `order_stats.pending` | int | Số đơn đang chờ xử lý |
| `order_stats.delivered` | int | Số đơn đã giao |

---

## 12. Upload Media

> **Prefix**: `/api/medias/uploads` | 🌐 **Dùng chung**  
> **File**: `app/api/v1/media.py`  
> **Storage**: AWS S3

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `POST` | `/api/medias/uploads` | ✅ | Upload ảnh/video lên S3 |

- **Content-Type**: `multipart/form-data`
- **Field**: `file`
- **Allowed types**: `image/jpeg`, `image/png`, `image/webp`, `video/mp4`
- **Max size**: 10 MB

```json
// Response
{
  "success": true,
  "id": 1,
  "url": "https://bucket.s3.amazonaws.com/uuid.jpg",
  "file_type": "image",
  "file_size": 524288
}
```

> **Luồng upload**: Gọi `POST /api/medias/uploads` → lấy `url` → điền vào `images`/`videos` khi tạo bài đăng hoặc sản phẩm.

---

## 13. Thông báo Mobile

> **Prefix**: `/api/mobile/notifications` | 📱 **Riêng mobile**  
> **File**: `app/api/v1/mobile_app.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/mobile/notifications` | ✅ | Lấy danh sách thông báo theo lịch sử trạng thái đơn hàng |

### GET `/api/mobile/notifications`

| Query Param | Type | Mô tả |
|-------------|------|--------|
| `page` | int | Trang hiện tại (>= 1) |
| `limit` | int | Số bản ghi/trang (1-50) |

### Trường trả về trong `data[]`

| Field | Type | Mô tả hiển thị |
|-------|------|----------------|
| `id` | int | ID log thông báo |
| `category` | string | Nhóm thông báo (`ORDER`) |
| `title` | string | Tiêu đề thông báo |
| `message` | string | Nội dung thông báo |
| `order_id` | int | ID đơn liên quan |
| `order_number` | string | Mã đơn liên quan |
| `status` | string | Trạng thái đơn (`PENDING`, `SHIPPING`, ...) |
| `status_label` | string | Nhãn tiếng Việt của trạng thái |
| `created_at` | datetime string | Thời điểm phát sinh |
| `unread` | bool | Cờ chưa đọc (hiện backend trả `false`) |

---

## 14. Vùng & Sổ địa chỉ Mobile

> **Prefix**: `/api/mobile/regions`, `/api/mobile/addresses` | 📱 **Riêng mobile**  
> **File**: `app/api/v1/mobile_app.py`

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| `GET` | `/api/mobile/regions/provinces` | ❌ | Danh sách tỉnh/thành |
| `GET` | `/api/mobile/regions/districts` | ❌ | Danh sách quận/huyện theo tỉnh |
| `GET` | `/api/mobile/regions/wards` | ❌ | Danh sách phường/xã theo quận |
| `GET` | `/api/mobile/addresses` | ✅ | Lấy sổ địa chỉ của user |
| `POST` | `/api/mobile/addresses` | ✅ | Tạo địa chỉ mới |
| `PUT` | `/api/mobile/addresses/{address_id}` | ✅ | Cập nhật địa chỉ |
| `DELETE` | `/api/mobile/addresses/{address_id}` | ✅ | Xóa địa chỉ |

### Trường trả về của region lookup

| Endpoint | Trường trong mỗi phần tử `data[]` |
|----------|------------------------------------|
| `/api/mobile/regions/provinces` | `code`, `name` |
| `/api/mobile/regions/districts` | `code`, `name`, `province_code` |
| `/api/mobile/regions/wards` | `code`, `name`, `district_code` |

### Trường trả về của `addresses`

| Field | Type | Mô tả hiển thị |
|-------|------|----------------|
| `id` | int | ID địa chỉ |
| `recipient_name` | string | Người nhận |
| `phone` | string | SĐT nhận hàng |
| `province_code`, `province_name` | string | Mã và tên tỉnh/thành |
| `district_code`, `district_name` | string | Mã và tên quận/huyện |
| `ward_code`, `ward_name` | string | Mã và tên phường/xã |
| `address_line` | string | Địa chỉ chi tiết |
| `full_address` | string | Địa chỉ ghép đầy đủ để hiển thị |
| `is_default` | bool | Cờ địa chỉ mặc định |

---

## 📊 Bảng tổng hợp – Tất cả API mobile

| Method | Endpoint | Auth | Loại | Mô tả |
|--------|----------|------|------|--------|
| `POST` | `/api/auth/login` | ❌ | 🌐 | Đăng nhập |
| `POST` | `/api/auth/refresh` | ❌ | 🌐 | Làm mới token |
| `GET` | `/api/auth/me` | ✅ | 🌐 | Thông tin user |
| `GET` | `/api/auth/profile` | ✅ | 🌐 | Profile dùng chung |
| `PUT` | `/api/auth/profile` | ✅ | 🌐 | Cập nhật profile dùng chung |
| `PUT` | `/api/auth/change-password` | ✅ | 🌐 | Đổi mật khẩu |
| `GET` | `/api/seller/posts` | ✅ | 🌐 | Danh sách bài đăng |
| `POST` | `/api/seller/posts` | ✅ | 🌐 | Tạo bài đăng |
| `PUT` | `/api/seller/posts/{id}` | ✅ | 🌐 | Sửa bài đăng |
| `DELETE` | `/api/seller/posts/{id}` | ✅ | 🌐 | Xóa bài đăng |
| `GET` | `/api/mobile/products` | ❌ | 📱 | Danh sách SP (consumer) |
| `GET` | `/api/mobile/products/{id}` | ❌ | 📱 | Chi tiết SP |
| `GET` | `/api/mobile/categories` | ❌ | 📱 | Danh mục |
| `GET` | `/api/seller/products` | ✅ | 🌐 | Danh sách SP (seller) |
| `POST` | `/api/seller/products` | ✅ | 🌐 | Tạo SP |
| `PUT` | `/api/seller/products/{id}` | ✅ | 🌐 | Sửa SP |
| `DELETE` | `/api/seller/products/{id}` | ✅ | 🌐 | Xóa SP |
| `GET` | `/api/mobile/cart` | ✅ | 📱 | Xem giỏ hàng |
| `POST` | `/api/mobile/cart/add` | ✅ | 📱 | Thêm vào giỏ |
| `PUT` | `/api/mobile/cart/update/{id}` | ✅ | 📱 | Cập nhật số lượng |
| `DELETE` | `/api/mobile/cart/remove/{id}` | ✅ | 📱 | Xóa SP khỏi giỏ |
| `DELETE` | `/api/cart` | ✅ | 🌐 | Xóa toàn bộ giỏ |
| `POST` | `/api/mobile/checkout` | ✅ | 📱 | Đặt hàng |
| `GET` | `/api/mobile/orders/my` | ✅ | 📱 | Danh sách đơn hàng |
| `GET` | `/api/mobile/orders/my/{id}` | ✅ | 📱 | Chi tiết đơn |
| `PUT` | `/api/mobile/orders/my/{id}/cancel` | ✅ | 📱 | Hủy đơn |
| `GET` | `/api/reviews/product/{id}` | ❌ | 🌐 | Xem đánh giá SP |
| `POST` | `/api/reviews` | ✅ | 🌐 | Tạo đánh giá |
| `PUT` | `/api/reviews/{id}` | ✅ | 🌐 | Sửa đánh giá |
| `DELETE` | `/api/reviews/{id}` | ✅ | 🌐 | Xóa đánh giá |
| `GET` | `/api/seller/contracts` | ✅ | 🌐 | Danh sách hợp đồng QC |
| `POST` | `/api/seller/contracts` | ✅ | 🌐 | Tạo hợp đồng QC |
| `PUT` | `/api/seller/contracts/{id}` | ✅ | 🌐 | Sửa hợp đồng QC |
| `DELETE` | `/api/seller/contracts/{id}` | ✅ | 🌐 | Xóa hợp đồng QC |
| `GET` | `/api/returns/my` | ✅ | 🌐 | Danh sách yêu cầu đổi trả |
| `POST` | `/api/returns` | ✅ | 🌐 | Tạo yêu cầu đổi trả |
| `PUT` | `/api/returns/{id}/cancel` | ✅ | 🌐 | Hủy yêu cầu |
| `GET` | `/api/promotions/public` | ❌ | 🌐 | Mã khuyến mãi |
| `GET` | `/api/payments` | ✅ | 🌐 | Lịch sử giao dịch |
| `POST` | `/api/payments/create` | ✅ | 🌐 | Tạo link VNPAY |
| `GET` | `/api/payments/vnpay-return` | ❌ | 🌐 | VNPAY callback |
| `GET` | `/api/mobile/profile` | ✅ | 📱 | Xem hồ sơ |
| `PUT` | `/api/mobile/profile` | ✅ | 📱 | Cập nhật hồ sơ |
| `POST` | `/api/medias/uploads` | ✅ | 🌐 | Upload ảnh/video |
