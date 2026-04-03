# PHÂN TÍCH CẤU TRÚC API VÀ PHÂN QUYỀN HỆ THỐNG

**Ngày phân tích:** 2026-04-03
**Tổng số API:** 173 endpoints (không tính `/` và `/health`)
**Mục đích:** Phân loại API theo 3 nhóm người dùng (Buyer/Mobile, Seller/Web, Admin/Web), kiểm tra phân quyền giữa Seller và Admin, xác định các vấn đề về permission

---

## MỤC LỤC

1. [Tổng Quan Hệ Thống Phân Quyền](#1-tổng-quan-hệ-thống-phân-quyền)
2. [Phân Loại API Theo Nhóm Người Dùng](#2-phân-loại-api-theo-nhóm-người-dùng)
3. [Các Vấn Đề Phân Quyền Nghiêm Trọng](#3-các-vấn-đề-phân-quyền-nghiêm-trọng)
4. [Đánh Giá Tính Phù Hợp Cho E-commerce Marketplace](#4-đánh-giá-tính-phù-hợp-cho-e-commerce-marketplace)
5. [Khuyến Nghị](#5-khuyến-nghị)

---

## 1. TỔNG QUAN HỆ THỐNG PHÂN QUYỀN

### 1.1. Cơ Chế Xác Thực (Authentication)

- **File chính:** `/app/api/v1/auth.py`
- **Phương thức:** Bearer Token (JWT)
- **Dependencies:**
  - `get_current_user(token)` - Bắt buộc phải đăng nhập, trả về User object
  - `get_current_user_optional()` - Không bắt buộc đăng nhập, trả về User hoặc None (dùng cho public endpoints)

### 1.2. Cơ Chế Phân Quyền (Authorization)

#### Cấu Trúc Database
```
users table:
  - type: String - Giá trị: "admin", "producer", "seller", "consumer", "content_manager"

roles table:
  - Tồn tại nhưng KHÔNG được sử dụng trong authorization

permissions table:
  - Tồn tại nhưng KHÔNG được sử dụng trong authorization

role_permissions, user_roles:
  - Các bảng liên kết tồn tại nhưng KHÔNG được kiểm tra tại các API endpoints
```

#### Phương Thức Kiểm Tra Quyền

**HỆ THỐNG HIỆN TẠI: Type-based Simple Check**

- **KHÔNG có** decorator-based permission system
- **KHÔNG có** middleware RBAC
- **KHÔNG sử dụng** bảng `roles`, `permissions`, `role_permissions`, `user_roles`
- Chỉ kiểm tra trực tiếp: `if current_user.type != "admin":`
- Một số file có helper function: `_require_seller()`, `_require_admin()` nhưng không được tái sử dụng

**Ví dụ kiểm tra quyền:**
```python
# Pattern 1: Inline check
if current_user.type != "admin":
    raise HTTPException(status_code=403, detail="Admin only")

# Pattern 2: Helper function (chỉ có ở 3 files)
def _require_seller(user: User):
    if user.type not in {"producer", "seller", "admin"}:
        raise HTTPException(status_code=403)
```

### 1.3. Định Nghĩa User Types

| User Type | Mô Tả | Quyền Hiện Tại |
|-----------|-------|----------------|
| **admin** | Quản trị viên hệ thống | Toàn quyền: quản lý users, duyệt nội dung, xem analytics, quản lý seller, thao tác với mọi đơn hàng |
| **producer** | Nhà sản xuất nông nghiệp | Bán sản phẩm, quản lý shop, tạo bài viết, quản lý đơn hàng của shop |
| **seller** | Người bán (alias của producer) | Giống hệt producer, không có sự khác biệt trong code |
| **consumer** | Người mua/khách hàng | Duyệt sản phẩm, đặt hàng, xem đơn hàng của mình |
| **content_manager** | Quản lý nội dung | Chỉ có quyền duyệt products/content, KHÔNG có quyền admin khác (triển khai chưa nhất quán) |

---

## 2. PHÂN LOẠI API THEO NHÓM NGƯỜI DÙNG

### 2.1. NHÓM BUYER/MOBILE (Consumer - App Di Động)

**File chính:** `/app/api/v1/mobile_app.py`

#### A. Public Endpoints (Không cần đăng nhập)

| Endpoint | Method | Mô Tả |
|----------|--------|-------|
| `/api/mobile/posts` | GET | Xem danh sách bài viết đã duyệt |
| `/api/mobile/posts/{id}` | GET | Xem chi tiết bài viết |
| `/api/mobile/products` | GET | Duyệt danh sách sản phẩm |
| `/api/mobile/products/{id}` | GET | Xem chi tiết sản phẩm |

#### B. Authenticated Endpoints (Cần đăng nhập - Consumer)

| Endpoint | Method | Mô Tả | Vấn Đề |
|----------|--------|-------|--------|
| `/api/mobile/checkout` | POST | Tạo đơn hàng | ✅ OK |
| `/api/mobile/orders/my` | GET | Xem đơn hàng của tôi | ✅ OK |
| `/api/mobile/orders/my/{id}` | GET | Chi tiết đơn hàng | ✅ OK |
| `/api/mobile/profile` | GET/PUT | Quản lý profile | ✅ OK |
| `/api/mobile/posts/my` | GET | Xem bài viết của tôi | ⚠️ Consumer có nên tạo post? |
| `/api/mobile/posts/my` | POST | Tạo bài viết | ⚠️ Consumer có nên tạo post? |
| `/api/mobile/posts/my/{id}` | PUT/DELETE | Sửa/xóa bài viết | ⚠️ Consumer có nên tạo post? |

#### C. Shopping Flow (Cart, Orders, Reviews)

| Module | Endpoints | User Type | Trạng Thái |
|--------|-----------|-----------|------------|
| **cart** | `/api/cart/*` | Authenticated (any) | ✅ OK - dành cho consumer |
| **reviews** | `/api/reviews` (POST) | Authenticated (any) | ✅ OK |
| **reviews** | `/api/reviews/product/{id}` (GET) | Authenticated (any) | ✅ OK - nên là public |
| **returns** | `/api/returns` (POST) | Authenticated | ✅ OK |
| **returns** | `/api/returns/my` (GET) | Authenticated | ✅ OK |

---

### 2.2. NHÓM SELLER/WEB DASHBOARD (Producer/Seller - Web Portal)

**File chính:** `/app/api/v1/seller.py`

#### A. Seller Dashboard & Stats

| Endpoint | Method | Permission Check | Admin Access? |
|----------|--------|------------------|---------------|
| `/api/seller/dashboard` | GET | `_require_seller()` | ✅ YES - Admin có thể truy cập |
| `/api/seller/products` | GET | `_require_seller()` | ✅ YES |
| `/api/seller/orders` | GET | `_require_seller()` | ✅ YES |
| `/api/seller/profile` | GET/PUT | `_require_seller()` | ✅ YES |

**Logic `_require_seller()`:**
```python
allowed_types = {"producer", "seller", "admin"}  # Line 55
```
➡️ **Admin có toàn quyền truy cập mọi endpoint seller!**

#### B. Product Management (Seller)

| Endpoint | Method | Permission | Owner Check |
|----------|--------|------------|-------------|
| `/api/seller/products` | POST | Seller only | Auto-assign `producer_id = current_user.id` |
| `/api/seller/products/{id}` | PUT | Seller only | ✅ Kiểm tra ownership: `product.producer_id == user.id` |
| `/api/seller/products/{id}` | DELETE | Seller only | ✅ Kiểm tra ownership |
| `/api/seller/products/{id}/stock` | PUT | Seller only | ✅ Cập nhật tồn kho của mình |

#### C. Order Management (Seller)

| Endpoint | Method | Chức Năng | Permission |
|----------|--------|-----------|------------|
| `/api/seller/orders` | GET | Xem đơn hàng của shop | Chỉ orders có `seller_id == user.id` |
| `/api/seller/orders/{id}/confirm` | PUT | Xác nhận đơn hàng | Seller của đơn đó |
| `/api/seller/orders/{id}/reject` | PUT | Từ chối/hủy đơn | Seller của đơn đó |
| `/api/seller/orders/{id}/ship` | PUT | Chuyển sang Đang giao hàng | Seller của đơn đó |

#### D. Content Management (Seller)

| Resource | Endpoints | Permission |
|----------|-----------|------------|
| **Posts** | `/api/seller/posts/*` | Producer/Seller/Admin |
| **Contracts** | `/api/seller/contracts/*` | Producer/Seller/Admin |
| **Returns** | `/api/seller/returns/*` | Seller xử lý returns của shop |

#### E. Seller Onboarding

| Endpoint | Method | Chức Năng | User Type |
|----------|--------|-----------|-----------|
| `/api/seller/register` | POST | Đăng ký hồ sơ seller | Producer/Seller |
| `/api/seller/verification-status` | GET | Xem trạng thái xác minh | Producer/Seller |
| `/api/seller/applications` | GET | Admin xem hồ sơ chờ duyệt | **Admin only** |
| `/api/seller/verify/{user_id}` | PUT | Admin duyệt/từ chối hồ sơ | **Admin only** |

#### F. Settlement & Payouts

| Endpoint | Method | User Type | Chức Năng |
|----------|--------|-----------|-----------|
| `/api/settlement/wallet` | GET | Seller | Xem ví của mình |
| `/api/settlement/history` | GET | Seller | Lịch sử kỳ đối soát |
| `/api/settlement/payouts` | GET | Seller | Lịch sử chi trả |
| `/api/settlement/create` | POST | Admin | Tạo kỳ đối soát cho seller |
| `/api/settlement/{id}/approve` | POST | Admin | Duyệt kỳ đối soát |
| `/api/settlement/{id}/payout` | POST | Admin | Chi trả cho seller |

---

### 2.3. NHÓM ADMIN/WEB DASHBOARD (Quản Trị Viên)

#### A. User Management (CRITICAL - NO PERMISSION CHECK!)

| Endpoint | Method | Permission Check | ⚠️ VẤN ĐỀ |
|----------|--------|------------------|----------|
| `/api/users` | GET | ❌ NONE | **ANY authenticated user có thể xem list users!** |
| `/api/users` | POST | ❌ NONE | **ANY authenticated user có thể tạo user!** |
| `/api/users/{id}` | GET/PUT/DELETE | ❌ NONE | **ANY authenticated user có thể sửa/xóa user!** |
| `/api/users/{id}/activate` | PUT | ❌ NONE | **ANY authenticated user có thể activate/deactivate!** |
| `/api/users/{id}/roles` | GET/POST | ❌ NONE | **ANY authenticated user có thể gán roles!** |

**File:** `/app/api/v1/users.py` - Lines 49-287

#### B. Role & Permission Management

| Endpoint | Method | Permission Check | Admin Only? |
|----------|--------|------------------|-------------|
| `/api/admin/roles` | GET/POST | ❌ NONE | Có prefix `/admin/` nhưng không check |
| `/api/admin/roles/{id}` | PUT/DELETE | ❌ NONE | Có prefix `/admin/` nhưng không check |
| `/api/permissions` | GET/POST/PUT/DELETE | ❌ NONE (if exists) | Chưa rõ - table tồn tại nhưng không được dùng |

#### C. Dashboard & Analytics (CRITICAL - NO PERMISSION CHECK!)

| Endpoint | Method | Permission Check | ⚠️ VẤN ĐỀ |
|----------|--------|------------------|----------|
| `/api/dashboard/overview` | GET | ❌ NONE | **ANY authenticated user xem được tổng quan doanh thu!** |
| `/api/dashboard/revenue` | GET | ❌ NONE | **ANY authenticated user xem được revenue stats!** |
| `/api/dashboard/users` | GET | ❌ NONE | **ANY authenticated user xem được user stats!** |
| `/api/dashboard/products` | GET | ❌ NONE | **ANY authenticated user xem được product stats!** |
| `/api/dashboard/orders` | GET | ❌ NONE | **ANY authenticated user xem được order stats!** |
| `/api/stats/categories` | GET | ❌ NONE | **Tương tự - stats APIs không có permission check** |
| `/api/stats/consumers` | GET | ❌ NONE | |
| `/api/stats/producers` | GET | ❌ NONE | |
| `/api/stats/regions` | GET | ❌ NONE | |
| `/api/stats/trending` | GET | ❌ NONE | |

**File:** `/app/api/v1/dashboard.py` - Lines 50-289
**File:** `/app/api/v1/stats.py`

#### D. Content Approval (Admin + Content Manager)

| Endpoint | Method | Allowed Types | Ghi Chú |
|----------|--------|---------------|---------|
| `/api/products/{id}/approve` | POST | `admin` OR `content_manager` | Line 328 in products.py |
| `/api/content/{id}/approve` | POST | `admin` OR `content_manager` | Line 277 in content.py |

#### E. Order Management (Admin)

| Endpoint | Method | Permission | Chức Năng |
|----------|--------|------------|-----------|
| `/api/orders` | GET | Role-based filtering | Admin xem tất cả, Seller xem của shop, Consumer xem của mình |
| `/api/orders` | POST | Admin only | Tạo đơn hàng thủ công (line 334 in orders.py) |
| `/api/orders/{id}` | DELETE | Admin only | Xóa đơn hàng (line 415) |
| `/api/orders/{id}/status` | PUT | Role-based | Consumer chỉ cancel, Seller update đơn của shop, Admin update tất cả |

**File:** `/app/api/v1/orders.py`

#### F. Promotion Management

| Endpoint | Method | Permission Check | Admin Only? |
|----------|--------|------------------|-------------|
| `/api/promotions` | GET | ✅ Admin check | YES - line 214 |
| `/api/promotions` | POST | ✅ Admin check | YES - line 214 |
| `/api/promotions/{id}` | PUT/DELETE | ✅ Admin check | YES - line 254, 278 |
| `/api/promotions/public` | GET | None (public) | Anyone |
| `/api/promotions/{id}` | GET | ✅ Admin check | YES |

**File:** `/app/api/v1/promotions.py`

#### G. Returns & Complaints Management

| Endpoint | Method | Permission | User Type |
|----------|--------|------------|-----------|
| `/api/returns` | GET | Admin check | Admin xem tất cả returns |
| `/api/returns/{id}/approve` | PUT | Admin check | Admin duyệt return |
| `/api/returns/{id}/reject` | PUT | Admin check | Admin từ chối |
| `/api/returns/{id}/received` | PUT | Admin check | Admin xác nhận đã nhận hàng trả về |
| `/api/complaints/complaints/{id}/handle` | PUT | Admin check (line 183) | Admin xử lý complaint |
| `/api/complaints/complaints/{id}` | DELETE | Admin check | Admin xóa complaint |

#### H. Other Admin Functions

| Module | Endpoints | Permission | Chức Năng |
|--------|-----------|------------|-----------|
| **Categories** | `/api/categories` (POST/PUT/DELETE) | ❌ NONE | Nên là Admin only |
| **Regions** | `/api/regions` (POST/PUT/DELETE) | ❌ NONE | Nên là Admin only |
| **Organizations** | `/api/org` (all) | ❌ NONE | Không rõ - nên có permission check |
| **Contracts** | `/api/contracts` (all) | ❌ NONE | Mixed - admin và seller đều dùng |
| **Media** | `/api/medias` (all) | ❌ NONE | Nên có role check |
| **Payments** | `/api/payments/config/*` | ❌ NONE | Admin config phí, chu kỳ thanh toán - CRITICAL! |
| **Traceability** | `/api/traceability/certificates/{id}/verify` | ✅ Admin check | Admin xác minh chứng nhận |

---

### 2.4. MIXED/SHARED ENDPOINTS

#### A. Products API (`/app/api/v1/products.py`)

| Endpoint | Method | Permission Logic |
|----------|--------|------------------|
| `/api/products` | GET | Public (optional auth) - Anyone can browse |
| `/api/products/{id}` | GET | Public (optional auth) - Anyone can view |
| `/api/products` | POST | **Mixed:** Admin tạo cho bất kỳ producer nào (respects `producer_id`), Producer/Seller tự động gán `producer_id = current_user.id` |
| `/api/products/{id}` | PUT | **Mixed:** Admin update bất kỳ product nào, Producer/Seller chỉ update product của mình (ownership check - line 251-256) |
| `/api/products/{id}` | DELETE | **Mixed:** Admin xóa bất kỳ, Producer/Seller xóa của mình |
| `/api/products/{id}/approve` | POST | Admin hoặc Content Manager (line 328) |
| `/api/products/{id}/label` | PUT | ❌ NONE - ai cũng có thể update label? |

#### B. Content/Posts API (`/app/api/v1/content.py`)

| Endpoint | Method | Permission Logic |
|----------|--------|------------------|
| `/api/content` | GET | Public (optional auth) |
| `/api/content/{id}` | GET | Public (optional auth) |
| `/api/content` | POST | Authenticated - Producer creates |
| `/api/content/{id}` | PUT/DELETE | Producer owns OR Admin |
| `/api/content/{id}/approve` | POST | Admin OR Content Manager |

#### C. Orders API - Role-Based Filtering

**GET `/api/orders`** - Lines 95-103:
```python
if user.type == "consumer":
    query = query.filter(Order.customer_id == user.id)  # Chỉ xem đơn của mình
elif user.type in {"producer", "seller"}:
    query = query.filter(Order.seller_id == user.id)    # Chỉ xem đơn của shop
# Admin: không filter, xem tất cả
```

**PUT `/api/orders/{id}/status`** - Lines 226-235:
```python
if user.type == "consumer":
    if new_status != "CANCELLED":
        raise HTTPException(403, "Consumer chỉ có thể hủy đơn")
elif user.type in {"producer", "seller"}:
    if order.seller_id != user.id:
        raise HTTPException(403, "Không phải đơn của bạn")
# Admin: không check, update được tất cả
```

---

## 3. CÁC VẤN ĐỀ PHÂN QUYỀN NGHIÊM TRỌNG

### 🔴 CRITICAL (Phải sửa ngay)

#### 1. User Management API - KHÔNG CÓ PERMISSION CHECK
**File:** `/app/api/v1/users.py` (Lines 49-287)

**Tác động:**
- ❌ Bất kỳ user nào đã login (kể cả consumer) có thể:
  - Xem danh sách tất cả users trong hệ thống
  - Tạo user mới với bất kỳ type nào (admin, producer, seller, consumer)
  - Cập nhật thông tin bất kỳ user nào
  - Xóa bất kỳ user nào
  - Activate/deactivate user
  - Gán roles cho user
- ❌ Consumer có thể tự nâng cấp mình thành admin
- ❌ Seller có thể xóa admin hoặc competitor

**Rủi ro:** NGHIÊM TRỌNG - Mất toàn quyền kiểm soát hệ thống

**Khuyến nghị:** Thêm check `if current_user.type != "admin": raise HTTPException(403)` vào TẤT CẢ endpoints trong file này

---

#### 2. Dashboard & Analytics API - KHÔNG CÓ PERMISSION CHECK
**File:** `/app/api/v1/dashboard.py` (Lines 50-289)
**File:** `/app/api/v1/stats.py`

**Tác động:**
- ❌ Bất kỳ user nào đã login có thể xem:
  - Tổng doanh thu của toàn hệ thống
  - Số lượng users, orders, products
  - Revenue breakdown theo thời gian
  - Consumer/Producer statistics
  - Category/Region stats
- ❌ Seller có thể xem doanh thu của competitor
- ❌ Consumer có thể xem toàn bộ business metrics

**Rủi ro:** NGHIÊM TRỌNG - Lộ thông tin kinh doanh nhạy cảm

**Khuyến nghị:**
- Dashboard overview, revenue, users stats → Admin only
- Seller stats → Có thể cho phép seller xem stats của chính mình (đã có `/api/seller/dashboard`)
- Public stats (trending, categories) → Có thể giữ public

---

#### 3. Payment Configuration API - KHÔNG CÓ PERMISSION CHECK
**File:** `/app/api/v1/payments.py`

**Endpoints nguy hiểm:**
- `PUT /api/payments/config/cycle` - Cập nhật chu kỳ thanh toán
- `PUT /api/payments/config/fee` - Cập nhật phí platform
- `POST /api/payments/refund` - Xử lý hoàn tiền

**Tác động:**
- ❌ Seller có thể tự giảm phí platform
- ❌ Seller có thể tự refund cho khách hàng của competitor
- ❌ Consumer có thể thay đổi cấu hình thanh toán

**Rủi ro:** NGHIÊM TRỌNG - Tổn thất tài chính

**Khuyến nghị:** Admin only cho tất cả config endpoints

---

### 🟠 HIGH PRIORITY (Nên sửa sớm)

#### 4. Categories & Regions Management - Không Có Permission Check
**Files:**
- `/app/api/v1/categories.py` - POST, PUT, DELETE
- `/app/api/v1/regions.py` - POST, PUT, DELETE

**Tác động:**
- ❌ Bất kỳ user nào có thể tạo/sửa/xóa categories
- ❌ Seller có thể xóa category của competitor để làm mất sản phẩm
- ❌ Consumer có thể phá hoại cấu trúc danh mục

**Khuyến nghị:** Admin only cho POST/PUT/DELETE, GET có thể public

---

#### 5. Product Label Update - Không Có Permission Check
**File:** `/app/api/v1/products.py` - Line 373

**Endpoint:** `PUT /api/products/{id}/label`

**Tác động:**
- ❌ Bất kỳ ai có thể gán label "HOT", "BEST_SELLER", "TRENDING" cho sản phẩm bất kỳ
- ❌ Seller có thể tự gán badge cho sản phẩm của mình
- ❌ Competitor có thể gỡ badge của sản phẩm khác

**Khuyến nghị:** Admin only hoặc auto-assign based on sales data

---

#### 6. Admin Có Toàn Quyền Truy Cập Seller Portal
**File:** `/app/api/v1/seller.py` - Line 55

```python
allowed_types = {"producer", "seller", "admin"}
```

**Phân tích:**
- ✅ **Có thể là INTENTIONAL:** Admin cần xem được seller dashboard để support
- ⚠️ **Vấn đề:** Tạo sự mơ hồ - nên dùng `/seller/*` hay `/admin/seller/*` để quản lý seller?
- ⚠️ **Vấn đề:** Admin có thể vô tình thao tác trên seller portal thay vì admin panel

**Khuyến nghị:**
- **Option 1 (Recommended):** Tách riêng:
  - `/api/seller/*` - CHỈ cho seller (producer/seller types)
  - `/api/admin/sellers/*` - Admin xem/quản lý sellers
- **Option 2:** Giữ nguyên nhưng thêm query param `?as_role=admin` để phân biệt context

---

#### 7. Organizations API - Không Rõ Permission Logic
**File:** `/app/api/v1/organizations.py`

**Endpoints:** `/api/org/*` - ALL endpoints không có permission check

**Vấn đề:**
- Không rõ Organizations là gì trong context marketplace
- Không rõ ai có quyền tạo/quản lý organizations
- Không có ownership check khi update/delete

**Khuyến nghị:**
- Làm rõ use case của Organizations
- Thêm permission check và ownership validation

---

### 🟡 MEDIUM PRIORITY (Có thể cải thiện)

#### 8. Consumer Có Thể Tạo Posts
**File:** `/app/api/v1/mobile_app.py` - Lines 186-286

**Endpoints:**
- `POST /api/mobile/posts/my` - Tạo bài viết
- `PUT /api/mobile/posts/my/{id}` - Sửa bài viết
- `DELETE /api/mobile/posts/my/{id}` - Xóa bài viết

**Vấn đề:**
- ⚠️ Consumer (người mua) có thể tạo posts/content
- Không rõ: Consumer có nên được tạo content marketing?
- Hay chỉ Producer/Seller mới được tạo posts?

**Khuyến nghị:**
- Làm rõ business logic: Consumer có được phép tạo posts/reviews không?
- Nếu không: Thêm check `if user.type not in {"producer", "seller"}: raise HTTPException(403)`
- Nếu có: Cân nhắc moderation cho consumer posts

---

#### 9. Reviews API - GET Nên Là Public
**File:** `/app/api/v1/reviews.py`

**Endpoint:** `GET /api/reviews/product/{product_id}`

**Hiện tại:** Requires authentication

**Vấn đề:**
- Reviews của sản phẩm nên là public để người chưa đăng nhập có thể xem
- Cản trở UX khi browse sản phẩm

**Khuyến nghị:** Chuyển sang `get_current_user_optional()` hoặc public endpoint

---

#### 10. Roles API - Có Prefix `/admin/` Nhưng Không Check Permission
**File:** `/app/api/v1/roles.py`

**Endpoints:** `/api/admin/roles/*`

**Vấn đề:**
- Có prefix `/admin/` nhưng không có admin check trong code
- Bất kỳ user nào cũng có thể tạo/sửa/xóa roles

**Khuyến nghị:** Thêm admin check cho consistency

---

#### 11. Settlement APIs - Phân Quyền Chưa Rõ Ràng
**File:** `/app/api/v1/settlement.py`

**Vấn đề:**
- `/api/settlement/create` - Line 316: Có admin check ✅
- `/api/settlement/{id}/approve` - Line 316: Có admin check ✅
- `/api/settlement/{id}/payout` - Line 316: Có admin check ✅
- `/api/settlement/wallet` - Line 39-41: Seller check ✅
- `/api/settlement/history` - ❌ KHÔNG có permission check
- `/api/settlement/payouts` - ❌ KHÔNG có permission check

**Rủi ro:**
- Seller có thể xem history/payouts của seller khác
- Consumer có thể xem settlement data

**Khuyến nghị:**
- Filter by `seller_id == current_user.id` cho seller
- Admin có thể xem tất cả

---

### 🟢 LOW PRIORITY (Nhỏ nhưng cần lưu ý)

#### 12. Permission System Không Được Sử Dụng
**Database:** Tables `permissions`, `role_permissions`, `user_roles` tồn tại nhưng không được dùng

**Vấn đề:**
- Frontend có thể expect role-based permissions
- Hiện tại chỉ check `user.type` (hardcoded)
- Không linh hoạt khi muốn thêm custom roles

**Khuyến nghị:**
- **Short-term:** Document rõ hệ thống hiện tại dùng `user.type`, không dùng roles table
- **Long-term:** Migrate sang proper RBAC system

---

#### 13. Không Có Audit Trail Cho Authorization
**Vấn đề:**
- Không log khi user bị từ chối quyền (403)
- Không log khi admin thực hiện sensitive actions
- Khó trace lại khi có security incident

**Khuyến nghị:**
- Thêm audit logging cho:
  - Failed authorization attempts
  - Admin actions (user management, approvals, config changes)
  - Sensitive data access (dashboard, analytics)

---

#### 14. Helper Functions Không Được Tái Sử Dụng
**Vấn đề:**
- Chỉ 3 files định nghĩa `_require_admin()`, `_require_seller()`
- Mỗi file tự định nghĩa lại
- Không consistent

**Khuyến nghị:**
- Tạo `/app/core/permissions.py` với centralized helpers:
  ```python
  def require_admin(user: User):
      if user.type != "admin":
          raise HTTPException(403, "Admin only")

  def require_seller(user: User):
      if user.type not in {"producer", "seller"}:
          raise HTTPException(403, "Seller only")

  def require_seller_or_admin(user: User):
      if user.type not in {"producer", "seller", "admin"}:
          raise HTTPException(403)
  ```

---

#### 15. Optional Auth Không Nhất Quán
**Vấn đề:**
- Một số endpoints dùng `get_current_user_optional()` (products, content)
- Một số dùng `get_current_user()` (orders, seller)
- Không có guideline khi nào dùng cái nào

**Khuyến nghị:**
- Document clear rules:
  - Public browsing → `optional`
  - User-specific data → `required`
  - Personalized content (optional login benefits) → `optional`

---

## 4. ĐÁNH GIÁ TÍNH PHÙ HỢP CHO E-COMMERCE MARKETPLACE

### 4.1. Điểm Mạnh

✅ **Phân Tách Seller Portal Tốt**
- Có riêng `/api/seller/*` prefix cho seller operations
- Ownership checks cho products, orders khá tốt
- Seller onboarding workflow rõ ràng

✅ **Role-Based Filtering Đúng Đắn Ở Orders API**
- Consumer chỉ thấy đơn của mình
- Seller chỉ thấy đơn của shop
- Admin thấy tất cả
- Pattern này NÊN áp dụng cho các endpoints khác

✅ **Settlement System Có Cơ Bản**
- Có workflow đối soát: create → approve → payout
- Seller xem được wallet, history, payouts của mình

✅ **Multi-Seller Support Structure**
- Database schema hỗ trợ tốt (Store, OrderPackage, Settlement)
- API có phân biệt seller_id, store_id

---

### 4.2. Điểm Yếu Nghiêm Trọng

❌ **KHÔNG CÓ PERMISSION CHECK CHO ADMIN ENDPOINTS**
- User management, Dashboard, Stats APIs hoàn toàn mở
- Đây là lỗ hổng bảo mật NGHIÊM TRỌNG
- Không phù hợp cho production marketplace

❌ **KHÔNG SỬ DỤNG HỆ THỐNG RBAC**
- Có database schema cho roles/permissions nhưng không dùng
- Chỉ hardcode check `user.type`
- Không linh hoạt khi scale

❌ **ADMIN VÀ SELLER ROUTES BỊ TRỘN LẪN**
- Admin có thể access seller portal
- Không rõ ràng endpoint nào cho ai
- Dễ confuse khi develop và maintain

❌ **THIẾU AUDIT TRAIL**
- Không log authorization failures
- Không trace admin actions
- Khó compliance với regulations (GDPR, PCI-DSS)

---

### 4.3. So Sánh Với Best Practices Marketplace

| Feature | Best Practice | Hệ Thống Hiện Tại | Gap |
|---------|---------------|-------------------|-----|
| **User Management** | Admin only, audit log | ❌ No permission check | CRITICAL |
| **Dashboard/Analytics** | Admin/Seller own data | ❌ No permission check | CRITICAL |
| **Seller Isolation** | Strict ownership checks | ✅ Good for products/orders | Some gaps in settlements |
| **RBAC System** | Flexible role-based | ❌ Hardcoded type check | Need migration |
| **Audit Trail** | All sensitive actions | ❌ No logging | Compliance risk |
| **API Versioning** | `/v1/`, `/v2/` | ✅ Has `/api/v1/` | Good |
| **Rate Limiting** | Per user type | ❓ Unknown | Need to check |
| **Webhooks Security** | Signature verification | ⚠️ Has for GHN shipping | Need for payments |

---

### 4.4. Phù Hợp Cho Các Use Case Marketplace?

#### ✅ Phù Hợp:
1. **Multi-seller product listing** - Good structure
2. **Order management per seller** - Good isolation
3. **Seller onboarding & verification** - Clear workflow
4. **Basic settlement** - Has foundation

#### ⚠️ Cần Cải Thiện:
1. **Admin operations security** - CRITICAL gaps
2. **Seller analytics** - No proper seller-only dashboards
3. **Commission/fee management** - Config APIs not protected
4. **Dispute resolution** - Complaints handling OK, but no escalation workflow

#### ❌ Chưa Đủ:
1. **Advanced RBAC** - No custom roles (e.g., "seller_support", "finance_team")
2. **Multi-store per seller** - Database has `stores` table but APIs don't use it
3. **Seller subscription tiers** - No tiering system
4. **Advanced analytics** - Seller competitor analysis, market insights

---

## 5. KHUYẾN NGHỊ

### 5.1. HÀNH ĐỘNG NGAY (Critical - 1-2 Days)

#### A. Fix User Management API Security
**File:** `/app/api/v1/users.py`

**Thêm vào đầu mỗi endpoint:**
```python
if current_user.type != "admin":
    raise HTTPException(status_code=403, detail="Admin access required")
```

**Endpoints cần fix:**
- Lines 49-287: TẤT CẢ endpoints trong file này

---

#### B. Fix Dashboard/Stats API Security
**File:** `/app/api/v1/dashboard.py`, `/app/api/v1/stats.py`

**Pattern:**
```python
# Admin-only endpoints
if current_user.type != "admin":
    raise HTTPException(status_code=403, detail="Admin access required")

# OR Public stats (trending, categories)
# Use get_current_user_optional() và không filter
```

**Decision needed:**
- Dashboard overview, revenue, users → Admin only
- Trending, categories stats → Có thể public
- Seller đã có `/api/seller/dashboard` riêng

---

#### C. Fix Payment Config API Security
**File:** `/app/api/v1/payments.py`

**Endpoints cần fix:**
- `PUT /api/payments/config/cycle` → Admin only
- `PUT /api/payments/config/fee` → Admin only
- `POST /api/payments/refund` → Admin only (hoặc có approval workflow)

---

### 5.2. NGẮN HẠN (High Priority - 1 Week)

#### D. Centralize Permission Helpers
**Tạo file:** `/app/core/permissions.py`

```python
from fastapi import HTTPException
from app.models.user import User

def require_admin(user: User):
    """Requires user type to be admin"""
    if user.type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

def require_seller(user: User):
    """Requires user type to be producer or seller (NOT admin)"""
    if user.type not in {"producer", "seller"}:
        raise HTTPException(
            status_code=403,
            detail="Seller access required"
        )

def require_seller_or_admin(user: User):
    """Allows admin to access seller endpoints for support"""
    if user.type not in {"producer", "seller", "admin"}:
        raise HTTPException(
            status_code=403,
            detail="Seller or admin access required"
        )

def require_consumer(user: User):
    """Requires user type to be consumer"""
    if user.type != "consumer":
        raise HTTPException(
            status_code=403,
            detail="Consumer access required"
        )

def check_ownership(resource_user_id: int, current_user: User, allow_admin: bool = True):
    """Check if user owns the resource"""
    is_owner = resource_user_id == current_user.id
    is_admin = current_user.type == "admin" and allow_admin

    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this resource"
        )
```

**Sau đó refactor tất cả các file API để dùng helpers này.**

---

#### E. Fix Categories & Regions Management
**Files:** `/app/api/v1/categories.py`, `/app/api/v1/regions.py`

**Pattern:**
- GET → Public (optional auth)
- POST/PUT/DELETE → Admin only

---

#### F. Review Product Label Update
**File:** `/app/api/v1/products.py` - Line 373

**Options:**
1. **Admin only** - Manual labeling by admin
2. **Auto-assign** - Based on sales data, views, ratings
3. **Remove endpoint** - Labels managed internally only

---

#### G. Clarify Admin Access To Seller Portal
**Decision needed:**

**Option 1: Tách riêng (Recommended)**
```
/api/seller/*           → Seller ONLY (producer, seller types)
/api/admin/sellers/*    → Admin view/manage sellers
```

**Option 2: Query param**
```
/api/seller/dashboard?as_role=admin  → Admin viewing seller dashboard
/api/seller/dashboard                → Seller viewing own dashboard
```

**Option 3: Giữ nguyên**
- Document rõ: Admin có full access seller portal for support purposes

---

### 5.3. TRUNG HẠN (Medium Priority - 2-4 Weeks)

#### H. Implement Proper RBAC System

**Phase 1: Use Existing Tables**
- Migrate từ `user.type` check sang `user.roles` check
- Sử dụng bảng `permissions`, `role_permissions`, `user_roles` đã tồn tại
- Tạo decorator: `@require_permission("product.create")`

**Phase 2: Granular Permissions**
```
Modules:
- product.view, product.create, product.update, product.delete, product.approve
- order.view, order.create, order.update, order.cancel
- user.view, user.create, user.update, user.delete
- dashboard.view, analytics.view
- settlement.create, settlement.approve, settlement.payout
```

**Phase 3: Custom Roles**
```
admin → All permissions
seller → product.*, order.view (own), settlement.view (own)
consumer → order.create, order.view (own), review.create
content_manager → product.approve, content.approve
finance_team → settlement.*, payment.config.*
support_team → user.view, order.view
```

---

#### I. Add Audit Logging

**Tạo table:** `audit_logs`
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action VARCHAR(100),  -- 'user.create', 'order.update', etc.
    resource_type VARCHAR(50),  -- 'User', 'Order', 'Product'
    resource_id INT,
    old_value JSONB,  -- Before change
    new_value JSONB,  -- After change
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Log events:**
- Admin actions: user CRUD, approvals, config changes
- Authorization failures (403)
- Sensitive data access (dashboard, analytics)
- Payment/settlement operations

---

#### J. Review & Document All APIs

**Tạo file:** `API_PERMISSION_MATRIX.md`

| Endpoint | Method | User Types | Permission | Ownership Check | Notes |
|----------|--------|------------|------------|-----------------|-------|
| `/api/users` | GET | admin | user.view | N/A | List all users |
| `/api/products` | POST | admin, seller | product.create | Auto-assign producer_id for seller | |
| ... | ... | ... | ... | ... | ... |

---

### 5.4. DÀI HẠN (Long Term - 1-3 Months)

#### K. Multi-Store Support
**Database có `stores` table nhưng APIs chưa dùng**

**Cần implement:**
- `/api/seller/stores` - CRUD stores
- `/api/seller/stores/{id}/products` - Products per store
- `/api/seller/stores/{id}/settings` - Store configuration
- Filter orders by store_id

---

#### L. Advanced Seller Features
1. **Seller Tiers/Subscriptions**
   - Basic, Pro, Enterprise tiers
   - Different commission rates
   - Feature access based on tier

2. **Seller Analytics Dashboard**
   - Sales reports
   - Customer insights
   - Competitor benchmarking (anonymized)
   - Market trends

3. **Seller Marketing Tools**
   - Create promotions (currently admin only)
   - Run ads (new feature)
   - Email campaigns

---

#### M. Enhanced Security
1. **Rate Limiting**
   - Per user type (consumer: 100 req/min, seller: 500, admin: 1000)
   - Per endpoint (expensive operations lower limit)

2. **IP Whitelisting For Admin**
   - Admin panel chỉ access từ office IPs
   - Or require 2FA for admin operations

3. **Webhook Signature Verification**
   - VNPAY IPN ✅ đã có
   - Momo, ZaloPay webhooks cần thêm
   - Shipping webhooks (GHN) ✅ đã có

4. **Data Encryption**
   - Payment configs (api_key, merchant_id) → encrypt at rest
   - Sensitive user data (GDPR compliance)

---

#### N. API Gateway & Microservices (Optional)
**Nếu scale lớn:**
- Tách thành microservices:
  - User Service
  - Product Service
  - Order Service
  - Payment Service
  - Seller Service
- API Gateway handle:
  - Authentication
  - Rate limiting
  - Request routing
  - Response aggregation

---

## KẾT LUẬN

### Tình Trạng Hiện Tại
Hệ thống có **cấu trúc tốt cho multi-seller marketplace** (database schema, API separation), nhưng có **các lỗ hổng bảo mật NGHIÊM TRỌNG** ở phân quyền:
- User management API hoàn toàn mở
- Dashboard/Analytics API không có permission check
- Payment config API không được bảo vệ

### Mức Độ Sẵn Sàng Cho Production
- **Database Schema:** 8/10 ✅ Good foundation
- **API Structure:** 7/10 ✅ Clear separation, good organization
- **Permission System:** 2/10 ❌ CRITICAL gaps
- **Security:** 3/10 ❌ Major vulnerabilities
- **Audit/Compliance:** 1/10 ❌ No logging

**Overall: 4/10 - KHÔNG SẴN SÀNG cho production marketplace**

### Hành Động Ưu Tiên
1. **NGAY (1-2 days):** Fix user management, dashboard, payment config APIs
2. **TUẦN 1:** Centralize permission helpers, fix categories/regions
3. **TUẦN 2-4:** Implement proper RBAC, add audit logging
4. **THÁNG 2-3:** Multi-store support, advanced seller features

### Timeline Đề Xuất
- **Sprint 1 (2 weeks):** Fix all CRITICAL security issues
- **Sprint 2 (2 weeks):** Implement RBAC system
- **Sprint 3 (2 weeks):** Audit logging & documentation
- **Sprint 4+ (ongoing):** Advanced features & scaling

---

**Prepared by:** Claude Code Agent
**Date:** 2026-04-03
**Version:** 1.0
