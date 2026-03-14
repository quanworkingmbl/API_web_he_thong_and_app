# 📘 Tài Liệu API - CMS Nông Sản & Thương Mại Điện Tử

> **Base URL:** `http://localhost:8000`  
> **API Prefix:** `/api`  
> **Authentication:** Bearer Token (JWT)  
> **Framework:** FastAPI + Python  
> **Database:** PostgreSQL (Supabase)

---

## 📑 Mục Lục

1. [Authentication](#1-authentication)
2. [Users - Quản lý người dùng](#2-users---quản-lý-người-dùng)
3. [Roles - Quản lý vai trò](#3-roles---quản-lý-vai-trò)
4. [Permissions - Quản lý quyền hạn](#4-permissions---quản-lý-quyền-hạn)
5. [Products - Quản lý sản phẩm](#5-products---quản-lý-sản-phẩm)
6. [Orders - Quản lý đơn hàng](#6-orders---quản-lý-đơn-hàng)
7. [Payments - Quản lý thanh toán](#7-payments---quản-lý-thanh-toán)
8. [Content - Quản lý nội dung](#8-content---quản-lý-nội-dung)
9. [Complaints - Khiếu nại & Đánh giá](#9-complaints---khiếu-nại--đánh-giá)
10. [Contracts - Hợp đồng đối tác](#10-contracts---hợp-đồng-đối-tác)
11. [Categories - Danh mục sản phẩm](#11-categories---danh-mục-sản-phẩm)
12. [Regions - Vùng địa lý](#12-regions---vùng-địa-lý)
13. [Organizations - Tổ chức / HTX](#13-organizations---tổ-chức--htx)
14. [Media - Upload file](#14-media---upload-file)
15. [Dashboard - Thống kê tổng quan](#15-dashboard---thống-kê-tổng-quan)
16. [Statistics - Thống kê chi tiết](#16-statistics---thống-kê-chi-tiết)
17. [Mobile App - API dành cho mobile](#17-mobile-app---api-dành-cho-mobile)

---

## 🔑 Hướng Dẫn Authentication

Hầu hết các API yêu cầu Bearer Token trong header:

```
Authorization: Bearer <your_token>
```

**Quy trình xác thực:**
1. Gọi `POST /api/auth/register` để đăng ký tài khoản
2. Gọi `POST /api/auth/login` để lấy `api_token`
3. Dùng token đó trong header `Authorization: Bearer <token>` cho các request tiếp theo

---

## 1. Authentication

### 1.1 Register User

**Method:** `POST`  
**URL:** `http://localhost:8000/api/auth/register`  
**Auth:** ❌ Không cần

**Mô tả:**  
Đăng ký tài khoản người dùng mới vào hệ thống. Tài khoản được tự động kích hoạt sau khi đăng ký.

**Use case:**  
Người dùng mới (nông dân, hợp tác xã, người tiêu dùng) tạo tài khoản để sử dụng hệ thống. Sau khi đăng ký, họ có thể đăng nhập và sử dụng các chức năng tương ứng với loại tài khoản.

**Liên kết với API khác:**
- Login API (`POST /api/auth/login`)
- Get Profile API (`GET /api/auth/me`)

---

**Headers**

```
Content-Type: application/json
accept: */*
```

---

**Request Body**

```json
{
  "email": "nguyen.van.a@gmail.com",
  "password": "password123",
  "name": "Nguyễn Văn A",
  "gender": "male",
  "type": "producer"
}
```

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `email` | string | ✅ | Email hợp lệ, duy nhất trong hệ thống |
| `password` | string | ✅ | Tối thiểu 8 ký tự |
| `name` | string | ✅ | Họ tên, 2–255 ký tự |
| `gender` | string | ❌ | `male` / `female` / `other` |
| `type` | string | ❌ | `consumer` (mặc định) / `producer` / `admin` |

---

**Example Response** `201 Created`

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 42,
    "email": "nguyen.van.a@gmail.com",
    "name": "Nguyễn Văn A",
    "type": "producer"
  }
}
```

**Error Response** `400 Bad Request`

```json
{
  "detail": "Email already registered"
}
```

---

### 1.2 Login

**Method:** `POST`  
**URL:** `http://localhost:8000/api/auth/login`  
**Auth:** ❌ Không cần

**Mô tả:**  
Đăng nhập bằng email và mật khẩu, nhận về JWT Bearer Token dùng cho các request tiếp theo.

**Use case:**  
Người dùng đăng nhập vào web admin hoặc mobile app. Token nhận được có thời hạn (mặc định 30 phút) và cần được lưu phía client để gửi trong header của các request tiếp theo.

**Liên kết với API khác:**
- Register API
- Refresh Token API
- Tất cả các API yêu cầu xác thực

---

**Headers**

```
Content-Type: application/json
accept: */*
```

---

**Request Body**

```json
{
  "email": "nguyen.van.a@gmail.com",
  "password": "password123",
  "recaptcha": null
}
```

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `email` | string | ✅ | Email đã đăng ký |
| `password` | string | ✅ | Mật khẩu |
| `recaptcha` | string | ❌ | Token reCAPTCHA (tuỳ chọn) |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_at": "2025-01-15T10:30:00Z",
    "user": {
      "id": 42,
      "email": "nguyen.van.a@gmail.com",
      "name": "Nguyễn Văn A",
      "type": "producer"
    }
  }
}
```

**Error Response** `401 Unauthorized`

```json
{
  "detail": "Incorrect email or password"
}
```

---

### 1.3 Get Current User Info

**Method:** `GET`  
**URL:** `http://localhost:8000/api/auth/me`  
**Auth:** ✅ Bearer Token bắt buộc

**Mô tả:**  
Lấy thông tin chi tiết của người dùng đang đăng nhập, bao gồm roles và permissions được gán.

**Use case:**  
Sau khi đăng nhập, frontend gọi API này để lấy thông tin user (họ tên, loại tài khoản, quyền hạn) nhằm hiển thị menu và phân quyền giao diện phù hợp.

**Liên kết với API khác:**
- Roles API
- Permissions API

---

**Headers**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
accept: */*
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "data": {
    "id": 42,
    "email": "nguyen.van.a@gmail.com",
    "name": "Nguyễn Văn A",
    "gender": "male",
    "activated": 1,
    "type": "producer",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": null,
    "deleted_at": null,
    "roles": [
      {
        "id": 2,
        "role_name": "content_manager",
        "description": "Quản lý nội dung"
      }
    ],
    "permissions": [
      {
        "id": 10,
        "name": "CONTENT_APPROVE",
        "label": "Duyệt nội dung",
        "type": "action",
        "route": "/content/approve"
      }
    ],
    "source_providers": []
  }
}
```

---

### 1.4 Logout

**Method:** `POST`  
**URL:** `http://localhost:8000/api/auth/logout`  
**Auth:** ✅ Bearer Token bắt buộc

**Mô tả:**  
Đăng xuất khỏi hệ thống. Phía server thông báo logout thành công; client cần tự xóa token khỏi bộ nhớ (localStorage/sessionStorage).

**Use case:**  
Người dùng nhấn nút "Đăng xuất" trên giao diện. Do JWT không thể thu hồi server-side (không có blacklist), client phải tự xóa token.

---

**Headers**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Logged out successfully. Please remove token from client storage."
}
```

---

### 1.5 Refresh Token

**Method:** `POST`  
**URL:** `http://localhost:8000/api/auth/refresh`  
**Auth:** ✅ Bearer Token bắt buộc

**Mô tả:**  
Tạo mới access token với thời hạn gia hạn. Dùng khi token sắp hết hạn mà không muốn buộc người dùng đăng nhập lại.

**Use case:**  
Frontend kiểm tra thời gian hết hạn token, nếu còn < 5 phút thì tự động gọi API này để lấy token mới mà không interrupt trải nghiệm người dùng.

---

**Headers**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(new token)...",
    "token_type": "Bearer",
    "expires_at": "2025-01-15T11:00:00"
  }
}
```

---

## 2. Users - Quản lý người dùng

> **Base URL:** `/api/users`  
> **Auth:** ✅ Bearer Token bắt buộc cho tất cả endpoints

### 2.1 List Users

**Method:** `GET`  
**URL:** `http://localhost:8000/api/users`

**Mô tả:**  
Lấy danh sách người dùng trong hệ thống với hỗ trợ phân trang, lọc và tìm kiếm. Chỉ trả về user chưa bị xóa mềm.

**Use case:**  
Admin quản lý danh sách tài khoản: xem tất cả nông dân đã đăng ký, lọc tài khoản chưa kích hoạt, tìm kiếm user theo tên/email.

**Liên kết với API khác:**
- Activate User API
- Assign Roles API
- Delete User API

**Biến thể (Query Parameters):**

| Param | Type | Mô tả |
|-------|------|-------|
| `page` | int | Trang hiện tại (mặc định: 1) |
| `limit` | int | Số kết quả/trang (mặc định: 50, tối đa: 500) |
| `model` | string | Lọc theo loại: `consumer` / `producer` / `admin` |
| `activated` | int | Lọc theo trạng thái: `1` (hoạt động) / `0` (bị khóa) |
| `search` | string | Tìm kiếm theo tên hoặc email |

---

**Headers**

```
Authorization: Bearer <token>
```

---

**Example Request**

```
GET http://localhost:8000/api/users?page=1&limit=10&model=producer&activated=1&search=nguyen
```

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 42,
      "email": "nguyen.van.a@gmail.com",
      "name": "Nguyễn Văn A",
      "gender": "male",
      "activated": 1,
      "type": "producer",
      "created_at": "2025-01-01T00:00:00",
      "updated_at": null,
      "deleted_at": null
    }
  ],
  "meta": {
    "total": 1,
    "limit": 10,
    "current_page": 1,
    "total_pages": 1
  }
}
```

---

### 2.2 Create User

**Method:** `POST`  
**URL:** `http://localhost:8000/api/users`

**Mô tả:**  
Admin tạo tài khoản người dùng mới (không qua luồng tự đăng ký).

**Use case:**  
Admin hệ thống tạo tài khoản cho cán bộ HTX, nhân viên vận hành mà không cần họ tự đăng ký.

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

**Request Body**

```json
{
  "email": "staff@htx-langnghe.vn",
  "password": "securepass123",
  "name": "Trần Thị B",
  "gender": "female",
  "type": "producer",
  "activated": 1
}
```

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `email` | string | ✅ | Email hợp lệ |
| `password` | string | ✅ | Mật khẩu |
| `name` | string | ✅ | Họ tên |
| `gender` | string | ❌ | Giới tính |
| `type` | string | ❌ | Loại tài khoản |
| `activated` | int | ❌ | `1` = kích hoạt (mặc định), `0` = chưa kích hoạt |

---

**Example Response** `200 OK`

```json
{
  "id": 55,
  "email": "staff@htx-langnghe.vn",
  "name": "Trần Thị B",
  "gender": "female",
  "activated": 1,
  "type": "producer",
  "created_at": "2025-01-15T08:00:00",
  "updated_at": null
}
```

---

### 2.3 Get User By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/users/{user_id}`

**Mô tả:**  
Lấy thông tin chi tiết của một người dùng theo ID.

---

**Headers**

```
Authorization: Bearer <token>
```

---

**Example Request**

```
GET http://localhost:8000/api/users/42
```

---

**Example Response** `200 OK`

```json
{
  "id": 42,
  "email": "nguyen.van.a@gmail.com",
  "name": "Nguyễn Văn A",
  "gender": "male",
  "activated": 1,
  "type": "producer",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": null
}
```

---

### 2.4 Update User

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/users/{user_id}`

**Mô tả:**  
Cập nhật thông tin người dùng. Chỉ gửi các field cần thay đổi.

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

**Request Body** (chỉ gửi field cần cập nhật)

```json
{
  "name": "Nguyễn Văn A (Updated)",
  "type": "producer",
  "activated": 1
}
```

---

**Example Response** `200 OK`

```json
{
  "id": 42,
  "email": "nguyen.van.a@gmail.com",
  "name": "Nguyễn Văn A (Updated)",
  "type": "producer",
  "activated": 1,
  "updated_at": "2025-01-15T09:00:00"
}
```

---

### 2.5 Delete User (Soft Delete)

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/users/{user_id}`

**Mô tả:**  
Xóa mềm (soft delete) người dùng - không xóa khỏi database mà chỉ đánh dấu `deleted_at`. User bị xóa sẽ không xuất hiện trong các danh sách.

**Use case:**  
Admin vô hiệu hóa tài khoản vi phạm. Dữ liệu vẫn được giữ lại để kiểm tra lịch sử.

---

**Example Request**

```
DELETE http://localhost:8000/api/users/42
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

**Error** (tự xóa bản thân):

```json
{
  "detail": "Cannot delete yourself"
}
```

---

### 2.6 Activate / Deactivate User

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/users/{user_id}/activate?activated=1`

**Mô tả:**  
Kích hoạt hoặc vô hiệu hóa tài khoản người dùng mà không xóa dữ liệu.

**Use case:**  
Admin tạm khóa tài khoản vi phạm chính sách, sau khi xử lý có thể mở lại.

---

**Headers**

```
Authorization: Bearer <token>
```

---

**Query Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `activated` | int | ✅ | `1` = kích hoạt, `0` = vô hiệu hóa |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "User activated successfully"
}
```

---

### 2.7 Assign Roles to User

**Method:** `POST`  
**URL:** `http://localhost:8000/api/users/{user_id}/roles`

**Mô tả:**  
Gán danh sách roles cho người dùng. Thao tác này sẽ XÓA tất cả roles cũ và gán roles mới.

**Use case:**  
Admin cấp quyền `content_manager` cho nhân viên mới, hoặc thay đổi quyền của người dùng hiện tại.

**Liên kết với API khác:**
- List Roles API (`GET /api/admin/roles`)

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

**Request Body**

```json
[2, 3]
```

*(Mảng các role_id cần gán)*

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Assigned 2 roles to user",
  "role_ids": [2, 3]
}
```

---

### 2.8 Get User Roles

**Method:** `GET`  
**URL:** `http://localhost:8000/api/users/{user_id}/roles`

**Mô tả:**  
Lấy danh sách tất cả roles đang được gán cho người dùng.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 2,
      "role_name": "content_manager",
      "description": "Quản lý và duyệt nội dung"
    }
  ]
}
```

---

## 3. Roles - Quản lý vai trò

> **Base URL:** `/api/admin/roles`  
> **Auth:** ✅ Bearer Token bắt buộc

### 3.1 List Roles

**Method:** `GET`  
**URL:** `http://localhost:8000/api/admin/roles`

**Mô tả:**  
Lấy danh sách tất cả vai trò trong hệ thống.

**Use case:**  
Admin xem danh sách roles để gán cho người dùng, hoặc quản lý phân quyền hệ thống.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số kết quả/trang |
| `search` | Tìm theo tên role |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    { "id": 1, "role_name": "admin", "description": "Quản trị viên hệ thống" },
    { "id": 2, "role_name": "content_manager", "description": "Quản lý nội dung" },
    { "id": 3, "role_name": "operation_coordinator", "description": "Điều phối vận hành" },
    { "id": 4, "role_name": "cooperative_staff", "description": "Cán bộ HTX" }
  ],
  "meta": { "total": 4, "page": 1, "limit": 50 }
}
```

---

### 3.2 Create Role

**Method:** `POST`  
**URL:** `http://localhost:8000/api/admin/roles`

---

**Request Body**

```json
{
  "role_name": "regional_manager",
  "description": "Quản lý khu vực"
}
```

---

**Example Response** `200 OK`

```json
{
  "id": 5,
  "role_name": "regional_manager",
  "description": "Quản lý khu vực"
}
```

---

### 3.3 Update Role

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/admin/roles/{role_id}`

---

**Request Body**

```json
{
  "description": "Quản lý khu vực miền Nam"
}
```

---

### 3.4 Delete Role

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/admin/roles/{role_id}`

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Role deleted successfully"
}
```

---

## 4. Permissions - Quản lý quyền hạn

> **Base URL:** `/api/admin/permissions`  
> **Auth:** ✅ Bearer Token bắt buộc

### 4.1 List Permissions

**Method:** `GET`  
**URL:** `http://localhost:8000/api/admin/permissions`

**Mô tả:**  
Lấy danh sách tất cả quyền hạn. Permissions có thể có phân cấp cha-con (`parent_id`) dùng để render menu và phân quyền UI.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số kết quả/trang |
| `search` | Tìm theo tên permission |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "parent_id": null,
      "name": "PRODUCT_APPROVE",
      "label": "Duyệt sản phẩm",
      "type": "action",
      "route": "/products/approve",
      "status": 1,
      "order": 1,
      "icon": "check-circle"
    }
  ],
  "meta": { "total": 20, "page": 1 }
}
```

---

### 4.2 Create Permission

**Method:** `POST`  
**URL:** `http://localhost:8000/api/admin/permissions`

---

**Request Body**

```json
{
  "name": "REPORT_VIEW",
  "label": "Xem báo cáo",
  "type": "menu",
  "route": "/reports",
  "parent_id": null,
  "status": 1,
  "order": 10,
  "icon": "bar-chart"
}
```

---

### 4.3 Update Permission

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/admin/permissions/{permission_id}`

---

### 4.4 Delete Permission

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/admin/permissions/{permission_id}`

---

## 5. Products - Quản lý sản phẩm

> **Base URL:** `/api/products`

### 5.1 List Products

**Method:** `GET`  
**URL:** `http://localhost:8000/api/products`  
**Auth:** ❌ Tùy chọn (có token sẽ thấy nhiều thông tin hơn)

**Mô tả:**  
Lấy danh sách sản phẩm với phân trang, lọc theo trạng thái, nhà sản xuất, nhãn và tìm kiếm theo tên.

**Use case:**  
Admin xem tất cả sản phẩm cần duyệt. Content manager lọc sản phẩm `PENDING` để xét duyệt. Người dùng tìm sản phẩm theo tên.

**Biến thể (Query Parameters):**

| Param | Type | Mô tả |
|-------|------|-------|
| `page` | int | Trang (mặc định: 1) |
| `limit` | int | Số bản ghi/trang (mặc định: 20, tối đa: 100) |
| `status` | string | `PENDING` / `APPROVED` / `REJECTED` |
| `producer_id` | int | Lọc theo ID nhà sản xuất |
| `label` | string | `CLEAN_AGRICULTURE` / `TRADITIONAL_CRAFT` / `OCOP` |
| `search` | string | Tìm kiếm theo tên sản phẩm |

---

**Example Request**

```
GET http://localhost:8000/api/products?page=1&limit=20&status=PENDING&label=OCOP
```

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 10,
      "name": "Gạo ST25 Sóc Trăng",
      "description": "Gạo ngon nhất thế giới 2019",
      "price": "150000.00",
      "producer_id": 42,
      "producer_name": "Nguyễn Văn A",
      "status": "PENDING",
      "label": "OCOP",
      "images": "https://supabase.co/storage/v1/object/public/file_test00/abc.jpg",
      "created_at": "2025-01-10T08:00:00",
      "updated_at": null
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "limit": 20,
    "total_pages": 1
  }
}
```

---

### 5.2 Get Product By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/products/{product_id}`  
**Auth:** ❌ Tùy chọn

---

**Example Request**

```
GET http://localhost:8000/api/products/10
```

---

**Example Response** `200 OK`

```json
{
  "id": 10,
  "name": "Gạo ST25 Sóc Trăng",
  "description": "Gạo ngon nhất thế giới 2019",
  "price": "150000.00",
  "producer_id": 42,
  "producer_name": "Nguyễn Văn A",
  "status": "APPROVED",
  "label": "OCOP",
  "images": "https://supabase.co/storage/v1/object/public/file_test00/abc.jpg",
  "created_at": "2025-01-10T08:00:00"
}
```

---

### 5.3 Create Product

**Method:** `POST`  
**URL:** `http://localhost:8000/api/products`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Tạo sản phẩm mới. Sản phẩm được tạo ở trạng thái `PENDING`, chờ admin/content_manager duyệt.

**Use case:**  
Nông dân / HTX đăng sản phẩm lên sàn. Sản phẩm sẽ được content manager xét duyệt trước khi hiển thị công khai.

**Liên kết:**
- Approve Product API (`POST /api/products/{id}/approve`)
- Media Upload API (để lấy URL ảnh)

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

**Request Body**

```json
{
  "name": "Mật ong hoa nhãn Hưng Yên",
  "description": "Mật ong nguyên chất từ hoa nhãn, không pha trộn",
  "price": 250000,
  "producer_id": 42,
  "label": "CLEAN_AGRICULTURE",
  "images": "[\"https://example.com/mat-ong.jpg\"]"
}
```

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `name` | string | ✅ | Tên sản phẩm, 2–255 ký tự |
| `description` | string | ❌ | Mô tả sản phẩm |
| `price` | decimal | ✅ | Giá (≥ 0) |
| `producer_id` | int | ✅ | ID nhà sản xuất |
| `label` | string | ❌ | `CLEAN_AGRICULTURE` / `TRADITIONAL_CRAFT` / `OCOP` |
| `images` | string | ❌ | JSON array URL ảnh |

---

**Example Response** `200 OK`

```json
{
  "id": 11,
  "name": "Mật ong hoa nhãn Hưng Yên",
  "price": "250000.00",
  "producer_id": 42,
  "producer_name": "Nguyễn Văn A",
  "status": "PENDING",
  "label": "CLEAN_AGRICULTURE",
  "created_at": "2025-01-15T10:00:00"
}
```

---

### 5.4 Update Product

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/products/{product_id}`  
**Auth:** ✅ Bắt buộc

---

**Request Body** (chỉ gửi field cần cập nhật)

```json
{
  "price": 280000,
  "description": "Mật ong nguyên chất, đã được kiểm định VSATTP"
}
```

---

### 5.5 Delete Product

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/products/{product_id}`  
**Auth:** ✅ Bắt buộc

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

---

### 5.6 Approve / Reject Product

**Method:** `POST`  
**URL:** `http://localhost:8000/api/products/{product_id}/approve`  
**Auth:** ✅ Bắt buộc (role: `admin` hoặc `content_manager`)

**Mô tả:**  
Duyệt hoặc từ chối sản phẩm đang ở trạng thái `PENDING`. Lưu lại lịch sử duyệt.

**Use case:**  
Content manager kiểm tra sản phẩm: xem ảnh, giá cả, mô tả, sau đó phê duyệt hoặc yêu cầu chỉnh sửa.

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

**Request Body**

```json
{
  "product_id": 11,
  "status": "APPROVED",
  "notes": "Sản phẩm đạt tiêu chuẩn, hình ảnh rõ ràng",
  "checked_description": true,
  "checked_price": true,
  "checked_images": true
}
```

| Field | Type | Mô tả |
|-------|------|-------|
| `product_id` | int | ID sản phẩm |
| `status` | string | `APPROVED` hoặc `REJECTED` |
| `notes` | string | Ghi chú của người duyệt |
| `checked_description` | bool | Đã kiểm tra mô tả |
| `checked_price` | bool | Đã kiểm tra giá |
| `checked_images` | bool | Đã kiểm tra ảnh |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Product approved successfully"
}
```

**Error** `403 Forbidden`

```json
{
  "detail": "Không có quyền duyệt sản phẩm. Yêu cầu role: admin hoặc content_manager"
}
```

---

### 5.7 Update Product Label

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/products/{product_id}/label?label=OCOP`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Cập nhật nhãn phân loại cho sản phẩm.

**Các nhãn:**
- `CLEAN_AGRICULTURE` - Nông sản sạch
- `TRADITIONAL_CRAFT` - Làng nghề truyền thống
- `OCOP` - Sản phẩm OCOP (One Commune One Product)

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Product label updated successfully"
}
```

---

## 6. Orders - Quản lý đơn hàng

> **Base URL:** `/api/orders`  
> **Auth:** ✅ Bearer Token bắt buộc

### 6.1 List Orders

**Method:** `GET`  
**URL:** `http://localhost:8000/api/orders`

**Mô tả:**  
Lấy danh sách đơn hàng với phân trang và bộ lọc.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang (tối đa: 100) |
| `status` | `PENDING` / `CONFIRMED` / `PROCESSING` / `SHIPPING` / `DELIVERED` / `CANCELLED` / `REFUNDED` |
| `customer_id` | Lọc theo khách hàng |
| `seller_id` | Lọc theo người bán |
| `payment_status` | `UNPAID` / `PAID` |
| `search` | Tìm theo mã đơn hàng |

---

**Example Request**

```
GET http://localhost:8000/api/orders?status=PENDING&page=1&limit=20
```

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 101,
      "order_number": "ORD-20250115-A1B2C3D4",
      "customer_id": 5,
      "customer_name": "Lê Văn C",
      "customer_phone": "0901234567",
      "customer_email": "levanc@gmail.com",
      "shipping_address": "123 Đường Láng, Hà Nội",
      "seller_id": 42,
      "seller_name": "Nguyễn Văn A",
      "subtotal": "300000.00",
      "shipping_fee": "30000.00",
      "discount_amount": "0.00",
      "total_amount": "330000.00",
      "platform_fee_percentage": "5.00",
      "platform_fee_amount": "16500.00",
      "seller_amount": "313500.00",
      "status": "PENDING",
      "payment_method": "COD",
      "payment_status": "UNPAID",
      "customer_note": "Giao buổi sáng",
      "created_at": "2025-01-15T10:00:00",
      "items": [
        {
          "id": 1,
          "product_id": 10,
          "product_name": "Gạo ST25 Sóc Trăng",
          "unit_price": "150000.00",
          "quantity": 2,
          "total_price": "300000.00"
        }
      ]
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "limit": 20,
    "total_pages": 1
  }
}
```

---

### 6.2 Get Order By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/orders/{order_id}`

---

**Example Response** `200 OK`

*(Tương tự cấu trúc một phần tử trong List Orders)*

---

### 6.3 Update Order Status

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/orders/{order_id}/status`

**Mô tả:**  
Cập nhật trạng thái đơn hàng. Hệ thống tự động cập nhật timestamp tương ứng (`confirmed_at`, `shipped_at`, `delivered_at`...).

**Luồng trạng thái:**
```
PENDING → CONFIRMED → PROCESSING → SHIPPING → DELIVERED
                                             → CANCELLED
                                             → REFUNDED
```

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

**Request Body**

```json
{
  "status": "CONFIRMED",
  "note": "Đã xác nhận đơn hàng với người bán",
  "cancel_reason": null
}
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Order status updated from PENDING to CONFIRMED",
  "order_id": 101
}
```

---

### 6.4 Get Order Statistics

**Method:** `GET`  
**URL:** `http://localhost:8000/api/orders/stats/overview`

**Mô tả:**  
Thống kê tổng quan đơn hàng: tổng số, theo trạng thái và doanh thu.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "total_orders": 500,
    "by_status": {
      "pending": 50,
      "confirmed": 30,
      "processing": 20,
      "shipping": 80,
      "delivered": 300,
      "cancelled": 15,
      "refunded": 5
    },
    "revenue": {
      "total": "45000000.00",
      "platform_fee": "2250000.00",
      "seller_amount": "42750000.00"
    }
  }
}
```

---

## 7. Payments - Quản lý thanh toán

> **Base URL:** `/api/payments`

### 7.1 List Payments

**Method:** `GET`  
**URL:** `http://localhost:8000/api/payments`  
**Auth:** ❌ Tùy chọn

**Mô tả:**  
Lấy danh sách giao dịch thanh toán với phân trang và bộ lọc.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `status` | `PENDING` / `COMPLETED` / `REFUNDED` |
| `customer_id` | Lọc theo khách hàng |
| `seller_id` | Lọc theo người bán |

---

**Example Response** `200 OK`

```json
{
  "total": 200,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "order_id": 101,
      "customer_id": 5,
      "seller_id": 42,
      "amount": "330000.00",
      "platform_fee_percentage": "5.00",
      "platform_fee_amount": "16500.00",
      "seller_amount": "313500.00",
      "status": "COMPLETED",
      "payment_cycle": "MONTHLY",
      "created_at": "2025-01-15T10:00:00"
    }
  ]
}
```

---

### 7.2 Get Payment Status

**Method:** `GET`  
**URL:** `http://localhost:8000/api/payments/{payment_id}/status`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Kiểm tra trạng thái một giao dịch thanh toán cụ thể.

---

### 7.3 Payment Reconciliation

**Method:** `GET`  
**URL:** `http://localhost:8000/api/payments/reconciliation`  
**Auth:** ❌ Tùy chọn (role: `admin` hoặc `operation_coordinator`)

**Mô tả:**  
Đối soát thanh toán - xem tổng tiền đã thu, hoa hồng nền tảng, và tiền chuyển cho người bán.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `start_date` | Từ ngày (ISO 8601) |
| `end_date` | Đến ngày (ISO 8601) |

---

**Example Request**

```
GET http://localhost:8000/api/payments/reconciliation?start_date=2025-01-01&end_date=2025-01-31
```

---

**Example Response** `200 OK`

```json
{
  "total_customer_paid": "10000000.00",
  "total_platform_commission": "500000.00",
  "total_seller_amount": "9500000.00",
  "payments": [...]
}
```

---

### 7.4 Process Refund

**Method:** `POST`  
**URL:** `http://localhost:8000/api/payments/refund`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Xử lý hoàn tiền cho khách hàng. Tạo transaction `REFUND` và cập nhật trạng thái payment.

---

**Request Body**

```json
{
  "payment_id": 1,
  "amount": 330000,
  "reason": "Khách hàng trả hàng, hàng bị hư"
}
```

---

**Example Response** `200 OK`

```json
{
  "message": "Refund processed successfully"
}
```

---

### 7.5 Create Payment Complaint

**Method:** `POST`  
**URL:** `http://localhost:8000/api/payments/complaint`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Tạo khiếu nại liên quan đến thanh toán.

---

**Request Body**

```json
{
  "payment_id": 1,
  "complaint": "Bị trừ tiền nhưng đơn hàng chưa được xác nhận"
}
```

---

### 7.6 Update Platform Fee

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/payments/config/fee?fee_percentage=5.0`  
**Auth:** ✅ Bắt buộc (role: `admin`)

**Mô tả:**  
Cập nhật phần trăm hoa hồng nền tảng (0–100%).

---

**Example Response** `200 OK`

```json
{
  "message": "Platform fee updated to 5.0%"
}
```

---

### 7.7 Update Payment Cycle

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/payments/config/cycle?cycle=MONTHLY`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Cập nhật chu kỳ thanh toán cho người bán: `WEEKLY` (hàng tuần) hoặc `MONTHLY` (hàng tháng).

---

## 8. Content - Quản lý nội dung

> **Base URL:** `/api/content`

### 8.1 List Contents

**Method:** `GET`  
**URL:** `http://localhost:8000/api/content`  
**Auth:** ❌ Tùy chọn

**Mô tả:**  
Lấy danh sách bài viết, tin tức, mô tả sản phẩm với phân trang và bộ lọc.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `status` | `PENDING` / `APPROVED` / `REJECTED` |
| `author_id` | Lọc theo tác giả |
| `content_type` | `POST` / `PRODUCT_DESCRIPTION` / `NEWS` / `ANNOUNCEMENT` |
| `search` | Tìm kiếm theo tiêu đề |

---

**Example Response** `200 OK`

```json
{
  "total": 50,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "title": "Mùa lúa ST25 năm 2025",
      "content": "Năm nay vụ lúa bội thu...",
      "content_type": "POST",
      "author_id": 42,
      "author_name": "Nguyễn Văn A",
      "product_id": 10,
      "status": "APPROVED",
      "images": "https://example.com/lua.jpg",
      "videos": null,
      "approved_by": 1,
      "approved_at": "2025-01-10T10:00:00",
      "created_at": "2025-01-09T08:00:00"
    }
  ]
}
```

---

### 8.2 Get Content By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/content/{content_id}`  
**Auth:** ❌ Tùy chọn

---

### 8.3 Create Content

**Method:** `POST`  
**URL:** `http://localhost:8000/api/content`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Tạo nội dung mới (bài viết, tin tức...). Nội dung được tạo ở trạng thái `PENDING`.

---

**Request Body**

```json
{
  "title": "Thu hoạch mật ong vụ xuân",
  "content": "Đây là mùa thu hoạch mật ong đặc biệt...",
  "content_type": "POST",
  "author_id": 42,
  "product_id": 11,
  "images": "https://example.com/mat-ong-thu-hoach.jpg",
  "videos": null
}
```

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `title` | string | ✅ | Tiêu đề, 2–255 ký tự |
| `content` | string | ❌ | Nội dung bài viết |
| `content_type` | string | ✅ | `POST` / `PRODUCT_DESCRIPTION` / `NEWS` / `ANNOUNCEMENT` |
| `author_id` | int | ✅ | ID tác giả |
| `product_id` | int | ❌ | Liên kết với sản phẩm |
| `images` | string | ❌ | URL ảnh |
| `videos` | string | ❌ | URL video |

---

### 8.4 Update Content

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/content/{content_id}`  
**Auth:** ✅ Bắt buộc

---

### 8.5 Delete Content

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/content/{content_id}`  
**Auth:** ✅ Bắt buộc

---

### 8.6 Approve / Reject Content

**Method:** `POST`  
**URL:** `http://localhost:8000/api/content/{content_id}/approve`  
**Auth:** ✅ Bắt buộc (role: `content_manager`)

**Mô tả:**  
Content manager duyệt hoặc từ chối bài viết.

---

**Request Body**

```json
{
  "content_id": 1,
  "status": "APPROVED",
  "notes": "Bài viết chất lượng tốt, hình ảnh rõ nét"
}
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Content approved successfully"
}
```

---

## 9. Complaints - Khiếu nại & Đánh giá

> **Base URL:** `/api/complaints`

### 9.1 List Product Reviews

**Method:** `GET`  
**URL:** `http://localhost:8000/api/complaints/reviews`  
**Auth:** ❌ Tùy chọn

**Mô tả:**  
Lấy danh sách đánh giá sản phẩm.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `product_id` | Lọc theo sản phẩm |
| `user_id` | Lọc theo người đánh giá |

---

**Example Response** `200 OK`

```json
{
  "total": 30,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "product_id": 10,
      "user_id": 5,
      "rating": 5,
      "comment": "Gạo rất ngon, đóng gói cẩn thận",
      "created_at": "2025-01-12T10:00:00"
    }
  ]
}
```

---

### 9.2 List Complaints

**Method:** `GET`  
**URL:** `http://localhost:8000/api/complaints/complaints`  
**Auth:** ❌ Tùy chọn

**Mô tả:**  
Lấy danh sách khiếu nại liên quan đến sản phẩm hoặc đơn hàng.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `status` | `OPEN` / `IN_PROGRESS` / `RESOLVED` |
| `complaint_type` | Loại khiếu nại |

---

**Example Response** `200 OK`

```json
{
  "total": 10,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "product_id": 10,
      "order_id": 101,
      "user_id": 5,
      "complaint_type": "PRODUCT_QUALITY",
      "title": "Sản phẩm không đúng mô tả",
      "description": "Gạo bị ẩm, không đúng như quảng cáo",
      "status": "OPEN",
      "handled_by": null,
      "resolution": null,
      "created_at": "2025-01-14T10:00:00"
    }
  ]
}
```

---

### 9.3 Handle Complaint

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/complaints/complaints/{complaint_id}/handle`  
**Auth:** ✅ Bắt buộc (role: `operation_coordinator`)

**Mô tả:**  
Xử lý khiếu nại: cập nhật trạng thái và ghi nhận biện pháp giải quyết.

---

**Query Parameters**

| Param | Mô tả |
|-------|-------|
| `status` | `IN_PROGRESS` / `RESOLVED` |
| `resolution` | Mô tả biện pháp xử lý |

---

**Example Request**

```
PUT http://localhost:8000/api/complaints/complaints/1/handle?status=RESOLVED&resolution=Đã hoàn tiền cho khách hàng
```

---

**Example Response** `200 OK`

```json
{
  "message": "Complaint handled successfully"
}
```

---

## 10. Contracts - Hợp đồng đối tác

> **Base URL:** `/api/contracts`

### 10.1 List Contracts

**Method:** `GET`  
**URL:** `http://localhost:8000/api/contracts`  
**Auth:** ❌ Tùy chọn

**Mô tả:**  
Lấy danh sách hợp đồng đối tác với phân trang và bộ lọc.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `status` | `DRAFT` / `ACTIVE` / `COMPLETED` / `CANCELLED` |
| `partner_id` | Lọc theo đối tác |
| `contract_type` | `ADVERTISING` / `PARTNERSHIP` / `DISTRIBUTION` / `OTHER` |
| `search` | Tìm theo số hợp đồng |

---

**Example Response** `200 OK`

```json
{
  "total": 5,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "contract_number": "HD-2025-001",
      "partner_id": 42,
      "partner_name": "Nguyễn Văn A",
      "contract_type": "DISTRIBUTION",
      "start_date": "2025-01-01T00:00:00",
      "end_date": "2025-12-31T00:00:00",
      "amount": "50000000.00",
      "status": "ACTIVE",
      "terms": "Phân phối độc quyền sản phẩm gạo tại khu vực Hà Nội",
      "created_at": "2025-01-01T08:00:00"
    }
  ]
}
```

---

### 10.2 Get Contract By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/contracts/{contract_id}`  
**Auth:** ✅ Bắt buộc

---

### 10.3 Create Contract

**Method:** `POST`  
**URL:** `http://localhost:8000/api/contracts`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Tạo hợp đồng mới với đối tác. Hợp đồng được tạo ở trạng thái `DRAFT`.

---

**Request Body**

```json
{
  "contract_number": "HD-2025-002",
  "partner_id": 42,
  "contract_type": "DISTRIBUTION",
  "start_date": "2025-02-01T00:00:00",
  "end_date": "2026-01-31T00:00:00",
  "amount": 30000000,
  "terms": "Điều khoản hợp đồng phân phối..."
}
```

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `contract_number` | string | ✅ | Mã hợp đồng, duy nhất |
| `partner_id` | int | ✅ | ID đối tác |
| `contract_type` | string | ✅ | `ADVERTISING` / `PARTNERSHIP` / `DISTRIBUTION` / `OTHER` |
| `start_date` | datetime | ✅ | Ngày bắt đầu |
| `end_date` | datetime | ❌ | Ngày kết thúc |
| `amount` | decimal | ❌ | Giá trị hợp đồng |
| `terms` | string | ❌ | Điều khoản hợp đồng |

---

### 10.4 Update Contract

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/contracts/{contract_id}`  
**Auth:** ✅ Bắt buộc

---

**Request Body** (chỉ gửi field cần cập nhật)

```json
{
  "status": "ACTIVE",
  "terms": "Điều khoản đã được cập nhật..."
}
```

---

### 10.5 Delete Contract

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/contracts/{contract_id}`  
**Auth:** ✅ Bắt buộc

---

## 11. Categories - Danh mục sản phẩm

> **Base URL:** `/api/categories`

### 11.1 List Categories

**Method:** `GET`  
**URL:** `http://localhost:8000/api/categories`  
**Auth:** ❌ Không cần

**Mô tả:**  
Lấy danh sách danh mục sản phẩm, có hỗ trợ phân cấp cha-con.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `is_active` | `true` / `false` |
| `parent_id` | Lọc theo danh mục cha |
| `search` | Tìm theo tên |

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "name": "Lương thực",
      "slug": "luong-thuc",
      "parent_id": null,
      "is_active": true,
      "created_at": "2025-01-01T00:00:00"
    },
    {
      "id": 2,
      "name": "Gạo",
      "slug": "gao",
      "parent_id": 1,
      "is_active": true,
      "created_at": "2025-01-01T00:00:00"
    }
  ],
  "meta": { "total": 2, "page": 1, "limit": 20 }
}
```

---

### 11.2 Get Category By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/categories/{category_id}`

---

### 11.3 Create Category

**Method:** `POST`  
**URL:** `http://localhost:8000/api/categories`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Tạo danh mục mới. Slug được tự động tạo từ tên nếu không cung cấp.

---

**Request Body**

```json
{
  "name": "Trái cây",
  "slug": "trai-cay",
  "parent_id": null,
  "is_active": true,
  "description": "Các loại trái cây tươi"
}
```

---

### 11.4 Update Category

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/categories/{category_id}`  
**Auth:** ✅ Bắt buộc

---

### 11.5 Delete Category

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/categories/{category_id}`  
**Auth:** ✅ Bắt buộc

**Lưu ý:** Không thể xóa danh mục có danh mục con.

---

## 12. Regions - Vùng địa lý

> **Base URL:** `/api/regions`

### 12.1 List Regions

**Method:** `GET`  
**URL:** `http://localhost:8000/api/regions`  
**Auth:** ❌ Không cần

**Mô tả:**  
Lấy danh sách vùng địa lý (tỉnh/thành phố, vùng nguyên liệu...).

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `is_active` | `true` / `false` |
| `search` | Tìm theo tên vùng |

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "name": "Đồng bằng sông Cửu Long",
      "slug": "dong-bang-song-cuu-long",
      "latitude": 10.0452,
      "longitude": 105.7469,
      "is_active": true,
      "created_at": "2025-01-01T00:00:00"
    }
  ],
  "meta": { "total": 10, "page": 1 }
}
```

---

### 12.2 Get Region By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/regions/{region_id}`

---

### 12.3 Create Region

**Method:** `POST`  
**URL:** `http://localhost:8000/api/regions`  
**Auth:** ✅ Bắt buộc

---

**Request Body**

```json
{
  "name": "Tây Nguyên",
  "description": "Vùng cao nguyên trung bộ",
  "latitude": 14.0583,
  "longitude": 108.2772,
  "is_active": true
}
```

---

### 12.4 Update Region

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/regions/{region_id}`  
**Auth:** ✅ Bắt buộc

---

### 12.5 Delete Region

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/regions/{region_id}`  
**Auth:** ✅ Bắt buộc

---

## 13. Organizations - Tổ chức / HTX

> **Base URL:** `/api/org`  
> **Auth:** ✅ Bearer Token bắt buộc

### 13.1 List Organizations

**Method:** `GET`  
**URL:** `http://localhost:8000/api/org`

**Mô tả:**  
Lấy danh sách tổ chức (Hợp tác xã, Làng nghề, Tổ sản xuất...).

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "name": "HTX Nông nghiệp Sóc Trăng",
      "description": "Hợp tác xã chuyên sản xuất gạo ST25",
      "created_at": "2025-01-01T00:00:00"
    }
  ],
  "meta": { "total": 5, "page": 1 }
}
```

---

### 13.2 Get Organization By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/org/{org_id}`

---

### 13.3 Create Organization

**Method:** `POST`  
**URL:** `http://localhost:8000/api/org`

---

**Request Body**

```json
{
  "name": "Làng nghề gốm Bát Tràng",
  "description": "Làng nghề truyền thống sản xuất gốm sứ tại Hà Nội"
}
```

---

### 13.4 Update Organization

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/org/{org_id}`

---

### 13.5 Delete Organization

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/org/{org_id}`

**Lưu ý:** Không thể xóa tổ chức còn thành viên.

---

### 13.6 List Organization Members

**Method:** `GET`  
**URL:** `http://localhost:8000/api/org/{org_id}/members`

**Mô tả:**  
Lấy danh sách thành viên của một tổ chức.

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 42,
      "name": "Nguyễn Văn A",
      "email": "nguyen.van.a@gmail.com",
      "type": "producer"
    }
  ]
}
```

---

### 13.7 Add Member to Organization

**Method:** `POST`  
**URL:** `http://localhost:8000/api/org/{org_id}/members`

---

**Request Body**

```json
{
  "user_id": 42
}
```

---

### 13.8 Remove Member from Organization

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/org/{org_id}/members/{user_id}`

---

## 14. Media - Upload file

> **Base URL:** `/api/medias`  
> **Auth:** ✅ Bearer Token bắt buộc

### 14.1 List Media

**Method:** `GET`  
**URL:** `http://localhost:8000/api/medias`

**Mô tả:**  
Lấy danh sách file media đã upload.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `file_type` | `IMAGE` / `VIDEO` |

---

**Example Response** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "filename": "gao-st25.jpg",
      "file_path": "https://xxx.supabase.co/storage/v1/object/public/file_test00/uuid.jpg",
      "file_type": "IMAGE",
      "file_size": 204800,
      "mime_type": "image/jpeg",
      "uploaded_by": 42,
      "created_at": "2025-01-15T09:00:00"
    }
  ],
  "meta": { "total": 20, "page": 1 }
}
```

---

### 14.2 Get Media By ID

**Method:** `GET`  
**URL:** `http://localhost:8000/api/medias/{media_id}`

---

### 14.3 Upload File

**Method:** `POST`  
**URL:** `http://localhost:8000/api/medias/uploads`  
**Content-Type:** `multipart/form-data`

**Mô tả:**  
Upload ảnh hoặc video lên Supabase S3 Storage. Trả về public URL để dùng trong các API khác (products, content...).

**Use case:**  
Người dùng chọn ảnh sản phẩm, frontend upload lên đây trước, lấy URL trả về, rồi dùng URL đó khi tạo sản phẩm.

**Giới hạn:**
- Kích thước tối đa: **10 MB**
- Định dạng được hỗ trợ: `JPEG`, `PNG`, `GIF`, `WebP` (ảnh), `MP4`, `MOV` (video)

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

---

**Request Body** (form-data)

| Field | Type | Mô tả |
|-------|------|-------|
| `file` | File | File cần upload |

---

**Example Response** `200 OK`

```json
{
  "id": 5,
  "filename": "mat-ong.jpg",
  "file_path": "https://xxx.supabase.co/storage/v1/object/public/file_test00/a1b2c3d4.jpg",
  "file_type": "IMAGE",
  "file_size": 102400,
  "mime_type": "image/jpeg",
  "uploaded_by": 42
}
```

---

### 14.4 Delete Media

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/medias/{media_id}`

**Mô tả:**  
Xóa file khỏi Supabase S3 và xóa bản ghi khỏi database.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Media deleted successfully"
}
```

---

## 15. Dashboard - Thống kê tổng quan

> **Base URL:** Các route đăng ký trực tiếp tại `/api/dashboard/`  
> **Auth:** ✅ Bearer Token bắt buộc

### 15.1 Dashboard Overview

**Method:** `GET`  
**URL:** `http://localhost:8000/api/dashboard/overview`

**Mô tả:**  
Tổng quan hệ thống: tổng số người dùng, sản phẩm, đơn hàng và doanh thu. Dùng cho trang chủ admin dashboard.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "total_users": 500,
    "total_producers": 120,
    "total_consumers": 380,
    "total_products": 250,
    "pending_products": 30,
    "total_orders": 1500,
    "total_revenue": "150000000.00"
  }
}
```

---

### 15.2 Revenue Statistics

**Method:** `GET`  
**URL:** `http://localhost:8000/api/dashboard/revenue`

**Mô tả:**  
Thống kê doanh thu theo khoảng thời gian.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `period` | `daily` / `weekly` / `monthly` / `yearly` |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "period": "monthly",
    "total_revenue": "30000000.00",
    "platform_commission": "1500000.00",
    "seller_revenue": "28500000.00",
    "order_count": 300
  }
}
```

---

### 15.3 Product Statistics

**Method:** `GET`  
**URL:** `http://localhost:8000/api/dashboard/products`

**Mô tả:**  
Thống kê sản phẩm theo trạng thái và nhãn.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "total": 250,
    "by_status": {
      "pending": 30,
      "approved": 200,
      "rejected": 20
    },
    "by_label": {
      "CLEAN_AGRICULTURE": 100,
      "TRADITIONAL_CRAFT": 80,
      "OCOP": 70
    }
  }
}
```

---

### 15.4 Order Statistics (Dashboard)

**Method:** `GET`  
**URL:** `http://localhost:8000/api/dashboard/orders`

**Mô tả:**  
Thống kê đơn hàng theo trạng thái và danh sách đơn hàng gần đây.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "total": 1500,
    "by_status": {
      "pending": 50,
      "delivered": 1200,
      "cancelled": 100
    },
    "recent_orders": [
      {
        "id": 101,
        "order_number": "ORD-20250115-A1B2C3D4",
        "total_amount": "330000.00",
        "status": "PENDING"
      }
    ]
  }
}
```

---

### 15.5 User Statistics (Dashboard)

**Method:** `GET`  
**URL:** `http://localhost:8000/api/dashboard/users`

**Mô tả:**  
Thống kê người dùng theo loại tài khoản và trạng thái.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "total": 500,
    "by_type": {
      "producer": 120,
      "consumer": 380
    },
    "by_status": {
      "active": 480,
      "inactive": 20
    },
    "new_this_month": 35
  }
}
```

---

## 16. Statistics - Thống kê chi tiết

> **Base URL:** Các route đăng ký trực tiếp tại `/api/stats/`  
> **Auth:** ✅ Bearer Token bắt buộc

### 16.1 Producer Statistics

**Method:** `GET`  
**URL:** `http://localhost:8000/api/stats/producers`

**Mô tả:**  
Thống kê chi tiết về người sản xuất (nông dân, HTX, làng nghề).

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "total": 120,
    "active": 110,
    "inactive": 10,
    "new_this_month": 15
  }
}
```

---

### 16.2 Consumer Statistics

**Method:** `GET`  
**URL:** `http://localhost:8000/api/stats/consumers`

**Mô tả:**  
Thống kê về người tiêu dùng.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "total": 380,
    "active": 350,
    "new_this_month": 40
  }
}
```

---

### 16.3 Trending Products

**Method:** `GET`  
**URL:** `http://localhost:8000/api/stats/trending`

**Mô tả:**  
Lấy danh sách sản phẩm trending (theo lượng đơn hàng).

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "name": "Gạo ST25 Sóc Trăng",
      "producer_name": "Nguyễn Văn A",
      "order_count": 150,
      "rating": 4.8
    }
  ]
}
```

---

### 16.4 Region Statistics

**Method:** `GET`  
**URL:** `http://localhost:8000/api/stats/regions`

**Mô tả:**  
Thống kê theo vùng địa lý (đang phát triển).

---

### 16.5 Category Statistics

**Method:** `GET`  
**URL:** `http://localhost:8000/api/stats/categories`

**Mô tả:**  
Thống kê theo danh mục sản phẩm (đang phát triển).

---

## 17. Mobile App - API dành cho mobile

> **Base URL:** `/api/mobile`  
> **Đặc điểm:** Tối ưu cho ứng dụng di động, nhiều endpoint public (không cần token)

### 17.1 Get Public Posts

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/posts`  
**Auth:** ❌ Không cần

**Mô tả:**  
Lấy danh sách bài viết đã được duyệt hiển thị công khai trên mobile app. Nội dung được cắt bớt (200 ký tự).

**Use case:**  
Trang feed chính của mobile app: người dùng scroll xem bài viết của các nông dân/HTX.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang (tối đa: 50) |
| `author_id` | Lọc theo tác giả |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Mùa lúa ST25 năm 2025",
      "content": "Năm nay vụ lúa bội thu, chúng tôi rất vui mừng...",
      "author_id": 42,
      "author_name": "Nguyễn Văn A",
      "author_type": "producer",
      "images": "https://example.com/lua.jpg",
      "videos": null,
      "created_at": "2025-01-09T08:00:00"
    }
  ],
  "meta": { "total": 50, "page": 1, "limit": 20, "total_pages": 3 }
}
```

---

### 17.2 Get My Posts

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/posts/my`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Producer xem danh sách bài viết của chính mình (bao gồm cả PENDING và REJECTED).

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `status` | Lọc theo trạng thái |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Mùa lúa ST25 năm 2025",
      "status": "APPROVED",
      "created_at": "2025-01-09T08:00:00"
    }
  ],
  "meta": { "total": 5, "page": 1, "limit": 20 }
}
```

---

### 17.3 Create Post (Producer)

**Method:** `POST`  
**URL:** `http://localhost:8000/api/mobile/posts/my`  
**Auth:** ✅ Bắt buộc  
**Content-Type:** `multipart/form-data`

**Mô tả:**  
Producer tạo bài viết mới kèm ảnh. Hỗ trợ upload ảnh trực tiếp (tự động upload lên Supabase) hoặc cung cấp URL ảnh sẵn. Bài viết sẽ ở trạng thái `PENDING` chờ duyệt.

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

---

**Request Body** (form-data)

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `title` | string | ✅ | Tiêu đề bài viết |
| `content` | string | ❌ | Nội dung |
| `product_id` | int | ❌ | Liên kết với sản phẩm |
| `images` | string | ❌ | URL ảnh (nếu đã có sẵn) |
| `videos` | string | ❌ | URL video |
| `image_file` | File | ❌ | File ảnh upload trực tiếp (JPEG/PNG/GIF/WebP, max 10MB) |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Post created successfully. Waiting for approval.",
  "data": {
    "id": 10,
    "title": "Thu hoạch mùa vụ mới",
    "status": "PENDING",
    "images": "https://xxx.supabase.co/storage/v1/object/public/file_test00/uuid.jpg"
  }
}
```

---

### 17.4 Get Post Detail

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/posts/{post_id}`  
**Auth:** ❌ Không cần

**Mô tả:**  
Xem chi tiết bài viết đã được duyệt.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Mùa lúa ST25 năm 2025",
    "content": "Toàn bộ nội dung bài viết...",
    "author_id": 42,
    "author_name": "Nguyễn Văn A",
    "author_type": "producer",
    "images": "https://example.com/lua.jpg",
    "videos": null,
    "product_id": 10,
    "created_at": "2025-01-09T08:00:00"
  }
}
```

---

### 17.5 Update My Post

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/mobile/posts/my/{post_id}`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Producer cập nhật bài viết của mình. Sau khi cập nhật, bài viết sẽ về trạng thái `PENDING` để duyệt lại.

---

**Request Body**

```json
{
  "title": "Mùa lúa ST25 - Cập nhật",
  "content": "Nội dung đã được cập nhật...",
  "images": "https://example.com/new-image.jpg"
}
```

---

### 17.6 Delete My Post

**Method:** `DELETE`  
**URL:** `http://localhost:8000/api/mobile/posts/my/{post_id}`  
**Auth:** ✅ Bắt buộc

---

### 17.7 Get Public Products (Mobile)

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/products`  
**Auth:** ❌ Không cần

**Mô tả:**  
Lấy danh sách sản phẩm đã được duyệt cho trang mua sắm trên mobile. Hỗ trợ lọc giá, tìm kiếm.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang (tối đa: 50) |
| `producer_id` | Lọc theo nhà sản xuất |
| `label` | `CLEAN_AGRICULTURE` / `TRADITIONAL_CRAFT` / `OCOP` |
| `search` | Tìm kiếm theo tên |
| `min_price` | Giá tối thiểu |
| `max_price` | Giá tối đa |

---

**Example Request**

```
GET http://localhost:8000/api/mobile/products?search=gạo&min_price=100000&max_price=300000&label=OCOP
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "name": "Gạo ST25 Sóc Trăng",
      "description": "Gạo ngon nhất thế giới...",
      "price": "150000.00",
      "producer_id": 42,
      "producer_name": "Nguyễn Văn A",
      "label": "OCOP",
      "images": "https://example.com/gao-st25.jpg"
    }
  ],
  "meta": { "total": 1, "page": 1, "limit": 20, "total_pages": 1 }
}
```

---

### 17.8 Get Product Detail (Mobile)

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/products/{product_id}`  
**Auth:** ❌ Không cần

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "Gạo ST25 Sóc Trăng",
    "description": "Toàn bộ mô tả sản phẩm...",
    "price": "150000.00",
    "producer_id": 42,
    "producer_name": "Nguyễn Văn A",
    "producer_type": "producer",
    "label": "OCOP",
    "images": "https://example.com/gao-st25.jpg",
    "created_at": "2025-01-10T08:00:00"
  }
}
```

---

### 17.9 Checkout (Tạo đơn hàng)

**Method:** `POST`  
**URL:** `http://localhost:8000/api/mobile/checkout`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Người dùng đặt hàng từ giỏ hàng. Tất cả sản phẩm trong một đơn hàng phải từ **cùng một người bán**. Phí ship mặc định 30.000 VND, hoa hồng nền tảng 5%.

**Use case:**  
Khách hàng chọn sản phẩm, điền địa chỉ giao hàng, chọn phương thức thanh toán và nhấn "Đặt hàng".

**Liên kết với API khác:**
- Get My Orders API
- Update Order Status API
- Products API (kiểm tra sản phẩm còn bán không)

---

**Headers**

```
Authorization: Bearer <token>
Content-Type: application/json
```

---

**Request Body**

```json
{
  "customer_name": "Lê Văn C",
  "customer_phone": "0901234567",
  "customer_email": "levanc@gmail.com",
  "shipping_address": "123 Đường Láng, Đống Đa, Hà Nội",
  "shipping_province": "Hà Nội",
  "shipping_district": "Đống Đa",
  "shipping_ward": "Láng Hạ",
  "payment_method": "COD",
  "customer_note": "Giao giờ hành chính",
  "items": [
    {
      "product_id": 10,
      "quantity": 2
    },
    {
      "product_id": 11,
      "quantity": 1
    }
  ]
}
```

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `customer_name` | string | ✅ | Tên người nhận, 2–255 ký tự |
| `customer_phone` | string | ✅ | Số điện thoại, 10–20 ký tự |
| `customer_email` | string | ❌ | Email người nhận |
| `shipping_address` | string | ✅ | Địa chỉ giao hàng (tối thiểu 10 ký tự) |
| `shipping_province` | string | ❌ | Tỉnh/thành phố |
| `shipping_district` | string | ❌ | Quận/huyện |
| `shipping_ward` | string | ❌ | Phường/xã |
| `payment_method` | string | ✅ | `COD` / `BANK_TRANSFER` / `MOMO` / `VNPAY` / `ZALOPAY` |
| `customer_note` | string | ❌ | Ghi chú cho người bán |
| `items` | array | ✅ | Danh sách sản phẩm đặt hàng |
| `items[].product_id` | int | ✅ | ID sản phẩm |
| `items[].quantity` | int | ✅ | Số lượng (≥ 1) |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "order_id": 101,
    "order_number": "ORD-20250115-A1B2C3D4",
    "total_amount": "360000.00",
    "status": "PENDING",
    "payment_method": "COD"
  }
}
```

**Error** `400 Bad Request`

```json
{
  "detail": "All products must be from the same seller. Please create separate orders."
}
```

---

### 17.10 Get My Orders (Mobile)

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/orders/my`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Người dùng xem danh sách đơn hàng của mình trên mobile.

**Biến thể:**

| Param | Mô tả |
|-------|-------|
| `page` | Trang hiện tại |
| `limit` | Số bản ghi/trang |
| `status` | Lọc theo trạng thái đơn hàng |

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "order_number": "ORD-20250115-A1B2C3D4",
      "total_amount": "360000.00",
      "status": "DELIVERED",
      "payment_status": "PAID",
      "item_count": 2,
      "created_at": "2025-01-15T10:00:00"
    }
  ],
  "meta": { "total": 10, "page": 1, "limit": 20 }
}
```

---

### 17.11 Get My Order Detail (Mobile)

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/orders/my/{order_id}`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Xem chi tiết một đơn hàng cụ thể của người dùng đang đăng nhập.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": 101,
    "order_number": "ORD-20250115-A1B2C3D4",
    "seller_name": "Nguyễn Văn A",
    "subtotal": "300000.00",
    "shipping_fee": "30000.00",
    "discount_amount": "0.00",
    "total_amount": "330000.00",
    "status": "DELIVERED",
    "payment_method": "COD",
    "payment_status": "PAID",
    "shipping_address": "123 Đường Láng, Hà Nội",
    "customer_note": "Giao giờ hành chính",
    "created_at": "2025-01-15T10:00:00",
    "items": [
      {
        "product_name": "Gạo ST25 Sóc Trăng",
        "product_image": "https://example.com/gao.jpg",
        "unit_price": "150000.00",
        "quantity": 2,
        "total_price": "300000.00"
      }
    ]
  }
}
```

---

### 17.12 Get My Profile (Mobile)

**Method:** `GET`  
**URL:** `http://localhost:8000/api/mobile/profile`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Lấy thông tin profile của người dùng đang đăng nhập.

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": 42,
    "email": "nguyen.van.a@gmail.com",
    "name": "Nguyễn Văn A",
    "type": "producer",
    "gender": "male",
    "activated": 1,
    "created_at": "2025-01-01T00:00:00"
  }
}
```

---

### 17.13 Update My Profile (Mobile)

**Method:** `PUT`  
**URL:** `http://localhost:8000/api/mobile/profile`  
**Auth:** ✅ Bắt buộc

**Mô tả:**  
Cập nhật thông tin cá nhân (tên, giới tính).

**Biến thể (Query Parameters):**

| Param | Mô tả |
|-------|-------|
| `name` | Tên mới |
| `gender` | Giới tính mới |

---

**Example Request**

```
PUT http://localhost:8000/api/mobile/profile?name=Nguyễn Văn A (Mới)&gender=male
```

---

**Example Response** `200 OK`

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 42,
    "name": "Nguyễn Văn A (Mới)",
    "gender": "male"
  }
}
```

---

## 📋 Tổng Hợp Tất Cả API Endpoints

| # | Module | Method | URL | Auth | Mô tả ngắn |
|---|--------|--------|-----|------|-------------|
| 1 | Auth | POST | `/api/auth/register` | ❌ | Đăng ký tài khoản |
| 2 | Auth | POST | `/api/auth/login` | ❌ | Đăng nhập |
| 3 | Auth | GET | `/api/auth/me` | ✅ | Thông tin user hiện tại |
| 4 | Auth | POST | `/api/auth/logout` | ✅ | Đăng xuất |
| 5 | Auth | POST | `/api/auth/refresh` | ✅ | Làm mới token |
| 6 | Users | GET | `/api/users` | ✅ | Danh sách users |
| 7 | Users | POST | `/api/users` | ✅ | Tạo user mới |
| 8 | Users | GET | `/api/users/{id}` | ✅ | Chi tiết user |
| 9 | Users | PUT | `/api/users/{id}` | ✅ | Cập nhật user |
| 10 | Users | DELETE | `/api/users/{id}` | ✅ | Xóa mềm user |
| 11 | Users | PUT | `/api/users/{id}/activate` | ✅ | Kích hoạt/khóa user |
| 12 | Users | POST | `/api/users/{id}/roles` | ✅ | Gán roles cho user |
| 13 | Users | GET | `/api/users/{id}/roles` | ✅ | Roles của user |
| 14 | Roles | GET | `/api/admin/roles` | ✅ | Danh sách roles |
| 15 | Roles | POST | `/api/admin/roles` | ✅ | Tạo role mới |
| 16 | Roles | PUT | `/api/admin/roles/{id}` | ✅ | Cập nhật role |
| 17 | Roles | DELETE | `/api/admin/roles/{id}` | ✅ | Xóa role |
| 18 | Permissions | GET | `/api/admin/permissions` | ✅ | Danh sách permissions |
| 19 | Permissions | POST | `/api/admin/permissions` | ✅ | Tạo permission |
| 20 | Permissions | PUT | `/api/admin/permissions/{id}` | ✅ | Cập nhật permission |
| 21 | Permissions | DELETE | `/api/admin/permissions/{id}` | ✅ | Xóa permission |
| 22 | Products | GET | `/api/products` | ❌ | Danh sách sản phẩm |
| 23 | Products | GET | `/api/products/{id}` | ❌ | Chi tiết sản phẩm |
| 24 | Products | POST | `/api/products` | ✅ | Tạo sản phẩm |
| 25 | Products | PUT | `/api/products/{id}` | ✅ | Cập nhật sản phẩm |
| 26 | Products | DELETE | `/api/products/{id}` | ✅ | Xóa sản phẩm |
| 27 | Products | POST | `/api/products/{id}/approve` | ✅ Admin/CM | Duyệt sản phẩm |
| 28 | Products | PUT | `/api/products/{id}/label` | ✅ | Cập nhật nhãn sản phẩm |
| 29 | Orders | GET | `/api/orders` | ✅ | Danh sách đơn hàng |
| 30 | Orders | GET | `/api/orders/{id}` | ✅ | Chi tiết đơn hàng |
| 31 | Orders | PUT | `/api/orders/{id}/status` | ✅ | Cập nhật trạng thái đơn |
| 32 | Orders | GET | `/api/orders/stats/overview` | ✅ | Thống kê đơn hàng |
| 33 | Payments | GET | `/api/payments` | ❌ | Danh sách thanh toán |
| 34 | Payments | GET | `/api/payments/{id}/status` | ✅ | Trạng thái thanh toán |
| 35 | Payments | GET | `/api/payments/reconciliation` | ❌ | Đối soát thanh toán |
| 36 | Payments | POST | `/api/payments/refund` | ✅ | Xử lý hoàn tiền |
| 37 | Payments | POST | `/api/payments/complaint` | ✅ | Khiếu nại thanh toán |
| 38 | Payments | PUT | `/api/payments/config/fee` | ✅ Admin | Cấu hình phí nền tảng |
| 39 | Payments | PUT | `/api/payments/config/cycle` | ✅ | Cấu hình chu kỳ TT |
| 40 | Content | GET | `/api/content` | ❌ | Danh sách nội dung |
| 41 | Content | GET | `/api/content/{id}` | ❌ | Chi tiết nội dung |
| 42 | Content | POST | `/api/content` | ✅ | Tạo nội dung |
| 43 | Content | PUT | `/api/content/{id}` | ✅ | Cập nhật nội dung |
| 44 | Content | DELETE | `/api/content/{id}` | ✅ | Xóa nội dung |
| 45 | Content | POST | `/api/content/{id}/approve` | ✅ CM | Duyệt nội dung |
| 46 | Complaints | GET | `/api/complaints/reviews` | ❌ | Danh sách đánh giá |
| 47 | Complaints | GET | `/api/complaints/complaints` | ❌ | Danh sách khiếu nại |
| 48 | Complaints | PUT | `/api/complaints/complaints/{id}/handle` | ✅ | Xử lý khiếu nại |
| 49 | Contracts | GET | `/api/contracts` | ❌ | Danh sách hợp đồng |
| 50 | Contracts | GET | `/api/contracts/{id}` | ✅ | Chi tiết hợp đồng |
| 51 | Contracts | POST | `/api/contracts` | ✅ | Tạo hợp đồng |
| 52 | Contracts | PUT | `/api/contracts/{id}` | ✅ | Cập nhật hợp đồng |
| 53 | Contracts | DELETE | `/api/contracts/{id}` | ✅ | Xóa hợp đồng |
| 54 | Categories | GET | `/api/categories` | ❌ | Danh mục sản phẩm |
| 55 | Categories | GET | `/api/categories/{id}` | ❌ | Chi tiết danh mục |
| 56 | Categories | POST | `/api/categories` | ✅ | Tạo danh mục |
| 57 | Categories | PUT | `/api/categories/{id}` | ✅ | Cập nhật danh mục |
| 58 | Categories | DELETE | `/api/categories/{id}` | ✅ | Xóa danh mục |
| 59 | Regions | GET | `/api/regions` | ❌ | Danh sách vùng |
| 60 | Regions | GET | `/api/regions/{id}` | ❌ | Chi tiết vùng |
| 61 | Regions | POST | `/api/regions` | ✅ | Tạo vùng |
| 62 | Regions | PUT | `/api/regions/{id}` | ✅ | Cập nhật vùng |
| 63 | Regions | DELETE | `/api/regions/{id}` | ✅ | Xóa vùng |
| 64 | Organizations | GET | `/api/org` | ✅ | Danh sách tổ chức |
| 65 | Organizations | GET | `/api/org/{id}` | ✅ | Chi tiết tổ chức |
| 66 | Organizations | POST | `/api/org` | ✅ | Tạo tổ chức |
| 67 | Organizations | PUT | `/api/org/{id}` | ✅ | Cập nhật tổ chức |
| 68 | Organizations | DELETE | `/api/org/{id}` | ✅ | Xóa tổ chức |
| 69 | Organizations | GET | `/api/org/{id}/members` | ✅ | Thành viên tổ chức |
| 70 | Organizations | POST | `/api/org/{id}/members` | ✅ | Thêm thành viên |
| 71 | Organizations | DELETE | `/api/org/{id}/members/{uid}` | ✅ | Xóa thành viên |
| 72 | Media | GET | `/api/medias` | ✅ | Danh sách media |
| 73 | Media | GET | `/api/medias/{id}` | ✅ | Chi tiết media |
| 74 | Media | POST | `/api/medias/uploads` | ✅ | Upload file |
| 75 | Media | DELETE | `/api/medias/{id}` | ✅ | Xóa media |
| 76 | Dashboard | GET | `/api/dashboard/overview` | ✅ | Tổng quan hệ thống |
| 77 | Dashboard | GET | `/api/dashboard/revenue` | ✅ | Thống kê doanh thu |
| 78 | Dashboard | GET | `/api/dashboard/products` | ✅ | Thống kê sản phẩm |
| 79 | Dashboard | GET | `/api/dashboard/orders` | ✅ | Thống kê đơn hàng |
| 80 | Dashboard | GET | `/api/dashboard/users` | ✅ | Thống kê người dùng |
| 81 | Stats | GET | `/api/stats/producers` | ✅ | Thống kê nhà SX |
| 82 | Stats | GET | `/api/stats/consumers` | ✅ | Thống kê NTD |
| 83 | Stats | GET | `/api/stats/trending` | ✅ | Sản phẩm trending |
| 84 | Stats | GET | `/api/stats/regions` | ✅ | Thống kê theo vùng |
| 85 | Stats | GET | `/api/stats/categories` | ✅ | Thống kê theo danh mục |
| 86 | Mobile | GET | `/api/mobile/posts` | ❌ | Bài viết công khai |
| 87 | Mobile | GET | `/api/mobile/posts/my` | ✅ | Bài viết của tôi |
| 88 | Mobile | POST | `/api/mobile/posts/my` | ✅ | Tạo bài viết |
| 89 | Mobile | GET | `/api/mobile/posts/{id}` | ❌ | Chi tiết bài viết |
| 90 | Mobile | PUT | `/api/mobile/posts/my/{id}` | ✅ | Cập nhật bài viết |
| 91 | Mobile | DELETE | `/api/mobile/posts/my/{id}` | ✅ | Xóa bài viết |
| 92 | Mobile | GET | `/api/mobile/products` | ❌ | Sản phẩm (mobile) |
| 93 | Mobile | GET | `/api/mobile/products/{id}` | ❌ | Chi tiết SP (mobile) |
| 94 | Mobile | POST | `/api/mobile/checkout` | ✅ | Đặt hàng |
| 95 | Mobile | GET | `/api/mobile/orders/my` | ✅ | Đơn hàng của tôi |
| 96 | Mobile | GET | `/api/mobile/orders/my/{id}` | ✅ | Chi tiết đơn hàng |
| 97 | Mobile | GET | `/api/mobile/profile` | ✅ | Profile của tôi |
| 98 | Mobile | PUT | `/api/mobile/profile` | ✅ | Cập nhật profile |

---

## 🔐 Phân Quyền Theo Role

| Role | Quyền hạn chính |
|------|-----------------|
| `admin` | Toàn quyền hệ thống, duyệt sản phẩm, cấu hình phí, quản lý tất cả |
| `content_manager` | Duyệt/từ chối sản phẩm và nội dung |
| `operation_coordinator` | Đối soát thanh toán, xử lý khiếu nại, quản lý hợp đồng |
| `cooperative_staff` | Cán bộ HTX, quyền hạn cơ bản |

---

## ⚠️ Mã Lỗi Thường Gặp

| HTTP Code | Ý nghĩa |
|-----------|---------|
| `200` | Thành công |
| `201` | Tạo mới thành công |
| `400` | Dữ liệu đầu vào không hợp lệ |
| `401` | Chưa xác thực / Token không hợp lệ |
| `403` | Không đủ quyền hạn |
| `404` | Không tìm thấy tài nguyên |
| `422` | Validation error (sai kiểu dữ liệu) |
| `500` | Lỗi server |

---

## 📌 Ghi Chú

- **Swagger UI:** `http://localhost:8000/docs` (chỉ khi `DEBUG=True`)
- **ReDoc:** `http://localhost:8000/redoc` (chỉ khi `DEBUG=True`)
- **Health Check:** `GET http://localhost:8000/health`
- Tất cả timestamps ở định dạng **ISO 8601 UTC**
- Giá tiền ở định dạng **decimal string** (VD: `"150000.00"`)
- Ảnh được lưu trên **Supabase S3 Storage**
- Soft delete: User bị xóa chỉ bị đánh dấu `deleted_at`, dữ liệu vẫn còn trong DB
