# API Request/Response Documentation

- **Generated at:** 2026-03-26 03:25:00
- **Base URL (local):** `http://localhost:8000`
- **Tổng số API endpoints:** `177` (bao gồm `/` và `/health`)

## 1) Tổng hợp toàn bộ endpoint

| STT | Module | Method | Endpoint | Auth |
|---:|---|---|---|---|
| 1 | auth | POST | `/api/auth/login` | Required |
| 2 | auth | POST | `/api/auth/logout` | Required |
| 3 | auth | GET | `/api/auth/me` | Required |
| 4 | auth | PUT | `/api/auth/profile` | Required |
| 5 | auth | POST | `/api/auth/refresh` | Required |
| 6 | auth | POST | `/api/auth/register` | Required |
| 7 | cart | DELETE | `/api/cart` | Required |
| 8 | cart | GET | `/api/cart` | Required |
| 9 | cart | POST | `/api/cart/items` | Required |
| 10 | cart | DELETE | `/api/cart/items/{item_id}` | Required |
| 11 | cart | PUT | `/api/cart/items/{item_id}` | Required |
| 12 | categories | GET | `/api/categories` | Required |
| 13 | categories | POST | `/api/categories` | Required |
| 14 | categories | DELETE | `/api/categories/{category_id}` | Required |
| 15 | categories | GET | `/api/categories/{category_id}` | Required |
| 16 | categories | PUT | `/api/categories/{category_id}` | Required |
| 17 | complaints | GET | `/api/complaints/complaints` | Optional |
| 18 | complaints | POST | `/api/complaints/complaints` | Required |
| 19 | complaints | DELETE | `/api/complaints/complaints/{complaint_id}` | Required |
| 20 | complaints | PUT | `/api/complaints/complaints/{complaint_id}/handle` | Required |
| 21 | complaints | GET | `/api/complaints/reviews` | Optional |
| 22 | content | GET | `/api/content` | Optional |
| 23 | content | POST | `/api/content` | Required |
| 24 | content | DELETE | `/api/content/{content_id}` | Required |
| 25 | content | GET | `/api/content/{content_id}` | Optional |
| 26 | content | PUT | `/api/content/{content_id}` | Required |
| 27 | content | POST | `/api/content/{content_id}/approve` | Required |
| 28 | contracts | GET | `/api/contracts` | Optional |
| 29 | contracts | POST | `/api/contracts` | Required |
| 30 | contracts | DELETE | `/api/contracts/{contract_id}` | Required |
| 31 | contracts | GET | `/api/contracts/{contract_id}` | Required |
| 32 | contracts | PUT | `/api/contracts/{contract_id}` | Required |
| 33 | dashboard | GET | `/api/dashboard/orders` | Required |
| 34 | dashboard | GET | `/api/dashboard/overview` | Required |
| 35 | dashboard | GET | `/api/dashboard/products` | Required |
| 36 | dashboard | GET | `/api/dashboard/revenue` | Required |
| 37 | dashboard | GET | `/api/dashboard/users` | Required |
| 38 | media | GET | `/api/medias` | Required |
| 39 | media | POST | `/api/medias/uploads` | Required |
| 40 | media | DELETE | `/api/medias/{media_id}` | Required |
| 41 | media | GET | `/api/medias/{media_id}` | Required |
| 42 | mobile_app | POST | `/api/mobile/checkout` | Required |
| 43 | mobile_app | GET | `/api/mobile/orders/my` | Required |
| 44 | mobile_app | GET | `/api/mobile/orders/my/{order_id}` | Required |
| 45 | mobile_app | GET | `/api/mobile/posts` | Required |
| 46 | mobile_app | GET | `/api/mobile/posts/my` | Required |
| 47 | mobile_app | POST | `/api/mobile/posts/my` | Required |
| 48 | mobile_app | DELETE | `/api/mobile/posts/my/{post_id}` | Required |
| 49 | mobile_app | PUT | `/api/mobile/posts/my/{post_id}` | Required |
| 50 | mobile_app | GET | `/api/mobile/posts/{post_id}` | Required |
| 51 | mobile_app | GET | `/api/mobile/products` | Required |
| 52 | mobile_app | GET | `/api/mobile/products/{product_id}` | Required |
| 53 | mobile_app | GET | `/api/mobile/profile` | Required |
| 54 | mobile_app | PUT | `/api/mobile/profile` | Required |
| 55 | orders | GET | `/api/orders` | Required |
| 56 | orders | POST | `/api/orders` | Required |
| 57 | orders | GET | `/api/orders/stats/overview` | Required |
| 58 | orders | DELETE | `/api/orders/{order_id}` | Required |
| 59 | orders | GET | `/api/orders/{order_id}` | Required |
| 60 | orders | PUT | `/api/orders/{order_id}/status` | Required |
| 61 | organizations | GET | `/api/org` | Required |
| 62 | organizations | POST | `/api/org` | Required |
| 63 | organizations | DELETE | `/api/org/{org_id}` | Required |
| 64 | organizations | GET | `/api/org/{org_id}` | Required |
| 65 | organizations | PUT | `/api/org/{org_id}` | Required |
| 66 | organizations | GET | `/api/org/{org_id}/members` | Required |
| 67 | organizations | POST | `/api/org/{org_id}/members` | Required |
| 68 | organizations | DELETE | `/api/org/{org_id}/members/{user_id}` | Required |
| 69 | payments | GET | `/api/payments` | Optional |
| 70 | payments | POST | `/api/payments/complaint` | Required |
| 71 | payments | PUT | `/api/payments/config/cycle` | Required |
| 72 | payments | PUT | `/api/payments/config/fee` | Required |
| 73 | payments | GET | `/api/payments/reconciliation` | Optional |
| 74 | payments | POST | `/api/payments/refund` | Required |
| 75 | payments | POST | `/api/payments/vnpay/create` | Required |
| 76 | payments | POST | `/api/payments/vnpay/ipn` | Required |
| 77 | payments | GET | `/api/payments/vnpay/return` | Required |
| 78 | payments | GET | `/api/payments/{payment_id}/status` | Required |
| 79 | products | GET | `/api/products` | Optional |
| 80 | products | POST | `/api/products` | Required |
| 81 | products | DELETE | `/api/products/{product_id}` | Required |
| 82 | products | GET | `/api/products/{product_id}` | Optional |
| 83 | products | PUT | `/api/products/{product_id}` | Required |
| 84 | products | POST | `/api/products/{product_id}/approve` | Required |
| 85 | products | PUT | `/api/products/{product_id}/label` | Required |
| 86 | promotions | GET | `/api/promotions` | Required |
| 87 | promotions | POST | `/api/promotions` | Required |
| 88 | promotions | GET | `/api/promotions/public` | Optional |
| 89 | promotions | DELETE | `/api/promotions/{promotion_id}` | Required |
| 90 | promotions | GET | `/api/promotions/{promotion_id}` | Required |
| 91 | promotions | PUT | `/api/promotions/{promotion_id}` | Required |
| 92 | regions | GET | `/api/regions` | Required |
| 93 | regions | POST | `/api/regions` | Required |
| 94 | regions | DELETE | `/api/regions/{region_id}` | Required |
| 95 | regions | GET | `/api/regions/{region_id}` | Required |
| 96 | regions | PUT | `/api/regions/{region_id}` | Required |
| 97 | returns | GET | `/api/returns` | Required |
| 98 | returns | POST | `/api/returns` | Required |
| 99 | returns | GET | `/api/returns/my` | Required |
| 100 | returns | PUT | `/api/returns/{return_id}/approve` | Required |
| 101 | returns | PUT | `/api/returns/{return_id}/cancel` | Required |
| 102 | returns | PUT | `/api/returns/{return_id}/received` | Required |
| 103 | returns | PUT | `/api/returns/{return_id}/reject` | Required |
| 104 | reviews | POST | `/api/reviews` | Required |
| 105 | reviews | GET | `/api/reviews/product/{product_id}` | Required |
| 106 | reviews | DELETE | `/api/reviews/{review_id}` | Required |
| 107 | reviews | PUT | `/api/reviews/{review_id}` | Required |
| 108 | roles | GET | `/api/admin/roles` | Required |
| 109 | roles | POST | `/api/admin/roles` | Required |
| 110 | roles | DELETE | `/api/admin/roles/{role_id}` | Required |
| 111 | roles | PUT | `/api/admin/roles/{role_id}` | Required |
| 112 | seller | GET | `/api/seller/contracts` | Required |
| 113 | seller | POST | `/api/seller/contracts` | Required |
| 114 | seller | DELETE | `/api/seller/contracts/{contract_id}` | Required |
| 115 | seller | PUT | `/api/seller/contracts/{contract_id}` | Required |
| 116 | seller | GET | `/api/seller/dashboard` | Required |
| 117 | seller | GET | `/api/seller/orders` | Required |
| 118 | seller | PUT | `/api/seller/orders/{order_id}/confirm` | Required |
| 119 | seller | PUT | `/api/seller/orders/{order_id}/reject` | Required |
| 120 | seller | PUT | `/api/seller/orders/{order_id}/ship` | Required |
| 121 | seller | GET | `/api/seller/posts` | Required |
| 122 | seller | POST | `/api/seller/posts` | Required |
| 123 | seller | DELETE | `/api/seller/posts/{post_id}` | Required |
| 124 | seller | PUT | `/api/seller/posts/{post_id}` | Required |
| 125 | seller | GET | `/api/seller/products` | Required |
| 126 | seller | POST | `/api/seller/products` | Required |
| 127 | seller | DELETE | `/api/seller/products/{product_id}` | Required |
| 128 | seller | PUT | `/api/seller/products/{product_id}` | Required |
| 129 | seller | PUT | `/api/seller/products/{product_id}/stock` | Required |
| 130 | seller | GET | `/api/seller/profile` | Required |
| 131 | seller | PUT | `/api/seller/profile` | Required |
| 132 | seller | GET | `/api/seller/returns` | Required |
| 133 | seller | PUT | `/api/seller/returns/{return_id}` | Required |
| 134 | seller_onboarding | GET | `/api/seller/applications` | Required |
| 135 | seller_onboarding | POST | `/api/seller/register` | Required |
| 136 | seller_onboarding | GET | `/api/seller/verification-status` | Required |
| 137 | seller_onboarding | PUT | `/api/seller/verify/{user_id}` | Required |
| 138 | settlement | POST | `/api/settlement/create` | Required |
| 139 | settlement | GET | `/api/settlement/history` | Required |
| 140 | settlement | GET | `/api/settlement/payouts` | Required |
| 141 | settlement | GET | `/api/settlement/wallet` | Required |
| 142 | settlement | POST | `/api/settlement/{settlement_id}/approve` | Required |
| 143 | settlement | POST | `/api/settlement/{settlement_id}/payout` | Required |
| 144 | shipping | POST | `/api/shipping/create` | Required |
| 145 | shipping | POST | `/api/shipping/fee` | Required |
| 146 | shipping | GET | `/api/shipping/order/{order_id}` | Required |
| 147 | shipping | POST | `/api/shipping/webhook` | Required |
| 148 | shipping | GET | `/api/shipping/{shipment_id}/track` | Required |
| 149 | stats | GET | `/api/stats/categories` | Required |
| 150 | stats | GET | `/api/stats/consumers` | Required |
| 151 | stats | GET | `/api/stats/producers` | Required |
| 152 | stats | GET | `/api/stats/regions` | Required |
| 153 | stats | GET | `/api/stats/trending` | Required |
| 154 | system | GET | `/` | Public |
| 155 | system | GET | `/health` | Public |
| 156 | traceability | POST | `/api/traceability/certificates` | Required |
| 157 | traceability | GET | `/api/traceability/certificates/product/{product_id}` | Required |
| 158 | traceability | PUT | `/api/traceability/certificates/{cert_id}/verify` | Required |
| 159 | traceability | POST | `/api/traceability/origins` | Required |
| 160 | traceability | GET | `/api/traceability/origins/product/{product_id}` | Required |
| 161 | traceability | GET | `/api/traceability/product/{product_id}` | Required |
| 162 | users | GET | `/api/users` | Required |
| 163 | users | POST | `/api/users` | Required |
| 164 | users | DELETE | `/api/users/{user_id}` | Required |
| 165 | users | GET | `/api/users/{user_id}` | Required |
| 166 | users | PUT | `/api/users/{user_id}` | Required |
| 167 | users | PUT | `/api/users/{user_id}/activate` | Required |
| 168 | users | GET | `/api/users/{user_id}/roles` | Required |
| 169 | users | POST | `/api/users/{user_id}/roles` | Required |

## 2) Chi tiết từng API (đúng format yêu cầu)

---

### 1. Login

**Method:** POST  
**URL:** http://localhost:8000/api/auth/login

**Description:**  
Endpoint thực thi nghiệp vụ `login` để: Login.

**Use case trong hệ thống:**  
Người dùng đăng nhập từ web/mobile để lấy token Bearer trước khi gọi các API bảo vệ.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý xác thực, phiên đăng nhập và danh tính người dùng trong toàn hệ thống.

**Liên kết với API khác:**
- GET /api/auth/me
- POST /api/auth/logout
- POST /api/auth/refresh
- POST /api/auth/register

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/auth/login

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "string",
  "recaptcha": "string"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "string",
  "data": {},
  "errors": [
    "string"
  ]
}
```

---

**Real use case trong project:**  
Người dùng đăng nhập từ web/mobile để lấy token Bearer trước khi gọi các API bảo vệ.

---

### 2. Logout

**Method:** POST  
**URL:** http://localhost:8000/api/auth/logout

**Description:**  
Endpoint thực thi nghiệp vụ `logout` để: Logout.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý xác thực, phiên đăng nhập và danh tính người dùng trong toàn hệ thống.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/refresh
- POST /api/auth/register

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/auth/logout

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "string",
  "data": {},
  "errors": [
    "string"
  ]
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 3. Get Current User Info

**Method:** GET  
**URL:** http://localhost:8000/api/auth/me

**Description:**  
Endpoint thực thi nghiệp vụ `get_current_user_info` để: Get Current User Info.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý xác thực, phiên đăng nhập và danh tính người dùng trong toàn hệ thống.

**Liên kết với API khác:**
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/refresh
- POST /api/auth/register

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/auth/me

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "string",
  "data": {},
  "errors": [
    "string"
  ]
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 4. Refresh Token

**Method:** POST  
**URL:** http://localhost:8000/api/auth/refresh

**Description:**  
Endpoint thực thi nghiệp vụ `refresh_token` để: Refresh Token.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý xác thực, phiên đăng nhập và danh tính người dùng trong toàn hệ thống.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout
- POST /api/auth/register

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/auth/refresh

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "string",
  "data": {},
  "errors": [
    "string"
  ]
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 5. Register

**Method:** POST  
**URL:** http://localhost:8000/api/auth/register

**Description:**  
Endpoint thực thi nghiệp vụ `register` để: Register.

**Use case trong hệ thống:**  
Người dùng mới tạo tài khoản trước khi thực hiện các luồng mua hàng hoặc bán hàng.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý xác thực, phiên đăng nhập và danh tính người dùng trong toàn hệ thống.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/logout
- POST /api/auth/refresh

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/auth/register

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "string",
  "name": "string",
  "gender": "string",
  "type": "string"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "string",
  "data": {},
  "errors": [
    "string"
  ]
}
```

---

**Real use case trong project:**  
Người dùng mới tạo tài khoản trước khi thực hiện các luồng mua hàng hoặc bán hàng.

---

### 6. Xóa toàn bộ giỏ hàng

**Method:** DELETE  
**URL:** http://localhost:8000/api/cart

**Description:**  
Endpoint thực thi nghiệp vụ `clear_cart` để: Xóa toàn bộ giỏ hàng.

**Use case trong hệ thống:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý giỏ hàng mua sắm.

**Liên kết với API khác:**
- GET /api/products
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/cart
- POST /api/cart/items

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/cart

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

---

### 7. Xem giỏ hàng hiện tại

**Method:** GET  
**URL:** http://localhost:8000/api/cart

**Description:**  
Endpoint thực thi nghiệp vụ `get_cart` để: Xem giỏ hàng hiện tại.

**Use case trong hệ thống:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý giỏ hàng mua sắm.

**Liên kết với API khác:**
- GET /api/products
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- DELETE /api/cart
- POST /api/cart/items

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/cart

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

---

### 8. Thêm sản phẩm vào giỏ hàng

**Method:** POST  
**URL:** http://localhost:8000/api/cart/items

**Description:**  
Endpoint thực thi nghiệp vụ `add_cart_item` để: Thêm sản phẩm vào giỏ hàng.

**Use case trong hệ thống:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý giỏ hàng mua sắm.

**Liên kết với API khác:**
- GET /api/products
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- DELETE /api/cart
- GET /api/cart

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/cart/items

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "product_id": 1,
  "quantity": 1
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

---

### 9. Xóa sản phẩm khỏi giỏ hàng

**Method:** DELETE  
**URL:** http://localhost:8000/api/cart/items/{item_id}

**Description:**  
Endpoint thực thi nghiệp vụ `remove_cart_item` để: Xóa sản phẩm khỏi giỏ hàng.

**Use case trong hệ thống:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý giỏ hàng mua sắm.

**Liên kết với API khác:**
- GET /api/products
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- DELETE /api/cart
- GET /api/cart

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/cart/items/{item_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

---

### 10. Cập nhật số lượng sản phẩm

**Method:** PUT  
**URL:** http://localhost:8000/api/cart/items/{item_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_cart_item` để: Cập nhật số lượng sản phẩm.

**Use case trong hệ thống:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý giỏ hàng mua sắm.

**Liên kết với API khác:**
- GET /api/products
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- DELETE /api/cart
- GET /api/cart

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/cart/items/{item_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "quantity": 1
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

---

### 11. Get Categories

**Method:** GET  
**URL:** http://localhost:8000/api/categories

**Description:**  
Endpoint thực thi nghiệp vụ `get_categories` để: Get Categories.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị danh mục sản phẩm.

**Liên kết với API khác:**
- POST /api/categories
- DELETE /api/categories/{category_id}
- GET /api/categories/{category_id}
- PUT /api/categories/{category_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `is_active`, `parent_id`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `is_active`, `parent_id`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/categories

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "name": "string",
      "slug": "string",
      "description": "string",
      "icon": "string",
      "image": "string",
      "parent_id": 1,
      "order": 1,
      "is_active": true,
      "created_at": "2026-03-14T10:00:00Z",
      "updated_at": "2026-03-14T10:00:00Z"
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 12. Create Category

**Method:** POST  
**URL:** http://localhost:8000/api/categories

**Description:**  
Endpoint thực thi nghiệp vụ `create_category` để: Create Category.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị danh mục sản phẩm.

**Liên kết với API khác:**
- GET /api/categories
- DELETE /api/categories/{category_id}
- GET /api/categories/{category_id}
- PUT /api/categories/{category_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/categories

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string",
  "icon": "string",
  "image": "string",
  "parent_id": 1,
  "order": 1,
  "is_active": true
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "slug": "string",
  "description": "string",
  "icon": "string",
  "image": "string",
  "parent_id": 1,
  "order": 1,
  "is_active": true,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 13. Delete Category

**Method:** DELETE  
**URL:** http://localhost:8000/api/categories/{category_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_category` để: Delete Category.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị danh mục sản phẩm.

**Liên kết với API khác:**
- GET /api/categories
- POST /api/categories
- GET /api/categories/{category_id}
- PUT /api/categories/{category_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/categories/{category_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 14. Get Category By Id

**Method:** GET  
**URL:** http://localhost:8000/api/categories/{category_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_category_by_id` để: Get Category By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị danh mục sản phẩm.

**Liên kết với API khác:**
- GET /api/categories
- POST /api/categories
- DELETE /api/categories/{category_id}
- PUT /api/categories/{category_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/categories/{category_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "slug": "string",
  "description": "string",
  "icon": "string",
  "image": "string",
  "parent_id": 1,
  "order": 1,
  "is_active": true,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 15. Update Category

**Method:** PUT  
**URL:** http://localhost:8000/api/categories/{category_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_category` để: Update Category.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị danh mục sản phẩm.

**Liên kết với API khác:**
- GET /api/categories
- POST /api/categories
- DELETE /api/categories/{category_id}
- GET /api/categories/{category_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/categories/{category_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string",
  "icon": "string",
  "image": "string",
  "parent_id": 1,
  "order": 1,
  "is_active": true
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "slug": "string",
  "description": "string",
  "icon": "string",
  "image": "string",
  "parent_id": 1,
  "order": 1,
  "is_active": true,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 16. Get Complaints

**Method:** GET  
**URL:** http://localhost:8000/api/complaints/complaints

**Description:**  
Endpoint thực thi nghiệp vụ `get_complaints` để: Get Complaints.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Theo dõi review/khiếu nại và xử lý khiếu nại.

**Liên kết với API khác:**
- PUT /api/complaints/complaints/{complaint_id}/handle
- GET /api/complaints/reviews

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`, `complaint_type`.
- Danh sách query params: `page`, `limit`, `status`, `complaint_type`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/complaints/complaints

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "total": 1,
  "page": 1,
  "limit": 1,
  "data": [
    {
      "id": 1,
      "product_id": 1,
      "order_id": 1,
      "user_id": 1,
      "complaint_type": "string",
      "title": "string",
      "description": "string",
      "status": "string",
      "handled_by": 1,
      "resolution": "string",
      "created_at": "2026-03-14T10:00:00Z"
    }
  ]
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 17. Handle Complaint

**Method:** PUT  
**URL:** http://localhost:8000/api/complaints/complaints/{complaint_id}/handle

**Description:**  
Endpoint thực thi nghiệp vụ `handle_complaint` để: Handle Complaint.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Theo dõi review/khiếu nại và xử lý khiếu nại.

**Liên kết với API khác:**
- GET /api/complaints/complaints
- GET /api/complaints/reviews

**Biến thể API:**
- Có filter theo: `status`, `resolution`.
- Danh sách query params: `status`, `resolution`.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/complaints/complaints/{complaint_id}/handle

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 18. Get Reviews

**Method:** GET  
**URL:** http://localhost:8000/api/complaints/reviews

**Description:**  
Endpoint thực thi nghiệp vụ `get_reviews` để: Get Reviews.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Theo dõi review/khiếu nại và xử lý khiếu nại.

**Liên kết với API khác:**
- GET /api/complaints/complaints
- PUT /api/complaints/complaints/{complaint_id}/handle

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `product_id`, `user_id`.
- Danh sách query params: `page`, `limit`, `product_id`, `user_id`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/complaints/reviews

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "total": 1,
  "page": 1,
  "limit": 1,
  "data": [
    {
      "id": 1,
      "product_id": 1,
      "user_id": 1,
      "rating": 1,
      "comment": "string",
      "created_at": "2026-03-14T10:00:00Z"
    }
  ]
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 19. Get Contents

**Method:** GET  
**URL:** http://localhost:8000/api/content

**Description:**  
Endpoint thực thi nghiệp vụ `get_contents` để: Get Contents.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý nội dung truyền thông/bài viết mô tả sản phẩm.

**Liên kết với API khác:**
- POST /api/content/{content_id}/approve
- GET /api/mobile/posts
- GET /api/dashboard/overview
- POST /api/content
- DELETE /api/content/{content_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`, `author_id`, `content_type`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `status`, `author_id`, `content_type`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/content

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "total": 1,
  "page": 1,
  "limit": 1,
  "data": [
    {
      "id": 1,
      "title": "string",
      "content": "string",
      "content_type": "string",
      "author_id": 1,
      "author_name": "string",
      "product_id": 1,
      "status": "string",
      "images": "string",
      "videos": "string",
      "approved_by": 1,
      "approved_at": "2026-03-14T10:00:00Z",
      "created_at": "2026-03-14T10:00:00Z",
      "updated_at": "2026-03-14T10:00:00Z"
    }
  ]
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 20. Create Content

**Method:** POST  
**URL:** http://localhost:8000/api/content

**Description:**  
Endpoint thực thi nghiệp vụ `create_content` để: Create Content.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý nội dung truyền thông/bài viết mô tả sản phẩm.

**Liên kết với API khác:**
- POST /api/content/{content_id}/approve
- GET /api/mobile/posts
- GET /api/dashboard/overview
- GET /api/content
- DELETE /api/content/{content_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/content

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "title": "string",
  "content": "string",
  "content_type": "string",
  "author_id": 1,
  "product_id": 1,
  "images": "string",
  "videos": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "content_type": "string",
  "author_id": 1,
  "author_name": "string",
  "product_id": 1,
  "status": "string",
  "images": "string",
  "videos": "string",
  "approved_by": 1,
  "approved_at": "2026-03-14T10:00:00Z",
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 21. Delete Content

**Method:** DELETE  
**URL:** http://localhost:8000/api/content/{content_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_content` để: Delete Content.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý nội dung truyền thông/bài viết mô tả sản phẩm.

**Liên kết với API khác:**
- POST /api/content/{content_id}/approve
- GET /api/mobile/posts
- GET /api/dashboard/overview
- GET /api/content
- POST /api/content

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/content/{content_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 22. Get Content By Id

**Method:** GET  
**URL:** http://localhost:8000/api/content/{content_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_content_by_id` để: Get Content By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý nội dung truyền thông/bài viết mô tả sản phẩm.

**Liên kết với API khác:**
- POST /api/content/{content_id}/approve
- GET /api/mobile/posts
- GET /api/dashboard/overview
- GET /api/content
- POST /api/content

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/content/{content_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "content_type": "string",
  "author_id": 1,
  "author_name": "string",
  "product_id": 1,
  "status": "string",
  "images": "string",
  "videos": "string",
  "approved_by": 1,
  "approved_at": "2026-03-14T10:00:00Z",
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 23. Update Content

**Method:** PUT  
**URL:** http://localhost:8000/api/content/{content_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_content` để: Update Content.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý nội dung truyền thông/bài viết mô tả sản phẩm.

**Liên kết với API khác:**
- POST /api/content/{content_id}/approve
- GET /api/mobile/posts
- GET /api/dashboard/overview
- GET /api/content
- POST /api/content

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/content/{content_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "title": "string",
  "content": "string",
  "content_type": "string",
  "images": "string",
  "videos": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "content_type": "string",
  "author_id": 1,
  "author_name": "string",
  "product_id": 1,
  "status": "string",
  "images": "string",
  "videos": "string",
  "approved_by": 1,
  "approved_at": "2026-03-14T10:00:00Z",
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 24. Approve Content

**Method:** POST  
**URL:** http://localhost:8000/api/content/{content_id}/approve

**Description:**  
Endpoint thực thi nghiệp vụ `approve_content` để: Approve Content.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý nội dung truyền thông/bài viết mô tả sản phẩm.

**Liên kết với API khác:**
- GET /api/mobile/posts
- GET /api/dashboard/overview
- GET /api/content
- POST /api/content
- DELETE /api/content/{content_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/content/{content_id}/approve

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "content_id": 1,
  "status": "string",
  "notes": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 25. Get Contracts

**Method:** GET  
**URL:** http://localhost:8000/api/contracts

**Description:**  
Endpoint thực thi nghiệp vụ `get_contracts` để: Get Contracts.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý hợp đồng hợp tác với đối tác.

**Liên kết với API khác:**
- POST /api/contracts
- DELETE /api/contracts/{contract_id}
- GET /api/contracts/{contract_id}
- PUT /api/contracts/{contract_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`, `partner_id`, `contract_type`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `status`, `partner_id`, `contract_type`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/contracts

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "total": 1,
  "page": 1,
  "limit": 1,
  "data": [
    {
      "id": 1,
      "contract_number": "string",
      "partner_id": 1,
      "partner_name": "string",
      "contract_type": "string",
      "start_date": "2026-03-14T10:00:00Z",
      "end_date": "2026-03-14T10:00:00Z",
      "amount": "string",
      "status": "string",
      "terms": "string",
      "created_by": 1,
      "created_at": "2026-03-14T10:00:00Z",
      "updated_at": "2026-03-14T10:00:00Z"
    }
  ]
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 26. Create Contract

**Method:** POST  
**URL:** http://localhost:8000/api/contracts

**Description:**  
Endpoint thực thi nghiệp vụ `create_contract` để: Create Contract.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý hợp đồng hợp tác với đối tác.

**Liên kết với API khác:**
- GET /api/contracts
- DELETE /api/contracts/{contract_id}
- GET /api/contracts/{contract_id}
- PUT /api/contracts/{contract_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/contracts

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "contract_number": "string",
  "partner_id": 1,
  "contract_type": "string",
  "start_date": "2026-03-14T10:00:00Z",
  "end_date": "2026-03-14T10:00:00Z",
  "amount": 1000.0,
  "terms": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "contract_number": "string",
  "partner_id": 1,
  "partner_name": "string",
  "contract_type": "string",
  "start_date": "2026-03-14T10:00:00Z",
  "end_date": "2026-03-14T10:00:00Z",
  "amount": "string",
  "status": "string",
  "terms": "string",
  "created_by": 1,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 27. Delete Contract

**Method:** DELETE  
**URL:** http://localhost:8000/api/contracts/{contract_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_contract` để: Delete Contract.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý hợp đồng hợp tác với đối tác.

**Liên kết với API khác:**
- GET /api/contracts
- POST /api/contracts
- GET /api/contracts/{contract_id}
- PUT /api/contracts/{contract_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/contracts/{contract_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 28. Get Contract By Id

**Method:** GET  
**URL:** http://localhost:8000/api/contracts/{contract_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_contract_by_id` để: Get Contract By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý hợp đồng hợp tác với đối tác.

**Liên kết với API khác:**
- GET /api/contracts
- POST /api/contracts
- DELETE /api/contracts/{contract_id}
- PUT /api/contracts/{contract_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/contracts/{contract_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "contract_number": "string",
  "partner_id": 1,
  "partner_name": "string",
  "contract_type": "string",
  "start_date": "2026-03-14T10:00:00Z",
  "end_date": "2026-03-14T10:00:00Z",
  "amount": "string",
  "status": "string",
  "terms": "string",
  "created_by": 1,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 29. Update Contract

**Method:** PUT  
**URL:** http://localhost:8000/api/contracts/{contract_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_contract` để: Update Contract.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý hợp đồng hợp tác với đối tác.

**Liên kết với API khác:**
- GET /api/contracts
- POST /api/contracts
- DELETE /api/contracts/{contract_id}
- GET /api/contracts/{contract_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/contracts/{contract_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "contract_number": "string",
  "contract_type": "string",
  "start_date": "2026-03-14T10:00:00Z",
  "end_date": "2026-03-14T10:00:00Z",
  "amount": 1000.0,
  "status": "string",
  "terms": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "contract_number": "string",
  "partner_id": 1,
  "partner_name": "string",
  "contract_type": "string",
  "start_date": "2026-03-14T10:00:00Z",
  "end_date": "2026-03-14T10:00:00Z",
  "amount": "string",
  "status": "string",
  "terms": "string",
  "created_by": 1,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 30. Get Order Stats

**Method:** GET  
**URL:** http://localhost:8000/api/dashboard/orders

**Description:**  
Endpoint thực thi nghiệp vụ `get_order_stats` để: Get Order Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Cung cấp số liệu tổng quan vận hành cho trang dashboard quản trị.

**Liên kết với API khác:**
- GET /api/stats/producers
- GET /api/stats/consumers
- GET /api/orders/stats/overview
- GET /api/dashboard/overview
- GET /api/dashboard/products

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/dashboard/orders

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 31. Get Dashboard Overview

**Method:** GET  
**URL:** http://localhost:8000/api/dashboard/overview

**Description:**  
Endpoint thực thi nghiệp vụ `get_dashboard_overview` để: Get Dashboard Overview.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Cung cấp số liệu tổng quan vận hành cho trang dashboard quản trị.

**Liên kết với API khác:**
- GET /api/stats/producers
- GET /api/stats/consumers
- GET /api/orders/stats/overview
- GET /api/dashboard/orders
- GET /api/dashboard/products

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/dashboard/overview

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 32. Get Product Stats

**Method:** GET  
**URL:** http://localhost:8000/api/dashboard/products

**Description:**  
Endpoint thực thi nghiệp vụ `get_product_stats` để: Get Product Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Cung cấp số liệu tổng quan vận hành cho trang dashboard quản trị.

**Liên kết với API khác:**
- GET /api/stats/producers
- GET /api/stats/consumers
- GET /api/orders/stats/overview
- GET /api/dashboard/orders
- GET /api/dashboard/overview

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/dashboard/products

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 33. Get Revenue Stats

**Method:** GET  
**URL:** http://localhost:8000/api/dashboard/revenue

**Description:**  
Endpoint thực thi nghiệp vụ `get_revenue_stats` để: Get Revenue Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Cung cấp số liệu tổng quan vận hành cho trang dashboard quản trị.

**Liên kết với API khác:**
- GET /api/stats/producers
- GET /api/stats/consumers
- GET /api/orders/stats/overview
- GET /api/dashboard/orders
- GET /api/dashboard/overview

**Biến thể API:**
- Có filter theo: `period`.
- Danh sách query params: `period`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/dashboard/revenue

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 34. Get User Stats

**Method:** GET  
**URL:** http://localhost:8000/api/dashboard/users

**Description:**  
Endpoint thực thi nghiệp vụ `get_user_stats` để: Get User Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Cung cấp số liệu tổng quan vận hành cho trang dashboard quản trị.

**Liên kết với API khác:**
- GET /api/stats/producers
- GET /api/stats/consumers
- GET /api/orders/stats/overview
- GET /api/dashboard/orders
- GET /api/dashboard/overview

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/dashboard/users

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 35. Get Media List

**Method:** GET  
**URL:** http://localhost:8000/api/medias

**Description:**  
Endpoint thực thi nghiệp vụ `get_media_list` để: Get Media List.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý upload/lưu trữ/tìm kiếm/xóa tài nguyên media.

**Liên kết với API khác:**
- POST /api/medias/uploads
- DELETE /api/medias/{media_id}
- GET /api/medias/{media_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `file_type`.
- Danh sách query params: `page`, `limit`, `file_type`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/medias

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "filename": "string",
      "file_path": "string",
      "file_type": "string",
      "file_size": 1,
      "mime_type": "string",
      "uploaded_by": 1,
      "created_at": "string"
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 36. Upload File

**Method:** POST  
**URL:** http://localhost:8000/api/medias/uploads

**Description:**  
Endpoint thực thi nghiệp vụ `upload_file` để: Upload File.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý upload/lưu trữ/tìm kiếm/xóa tài nguyên media.

**Liên kết với API khác:**
- GET /api/medias
- DELETE /api/medias/{media_id}
- GET /api/medias/{media_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/medias/uploads

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body**

```json
{
  "file": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 37. Delete Media

**Method:** DELETE  
**URL:** http://localhost:8000/api/medias/{media_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_media` để: Delete Media.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý upload/lưu trữ/tìm kiếm/xóa tài nguyên media.

**Liên kết với API khác:**
- GET /api/medias
- POST /api/medias/uploads
- GET /api/medias/{media_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/medias/{media_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 38. Get Media By Id

**Method:** GET  
**URL:** http://localhost:8000/api/medias/{media_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_media_by_id` để: Get Media By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý upload/lưu trữ/tìm kiếm/xóa tài nguyên media.

**Liên kết với API khác:**
- GET /api/medias
- POST /api/medias/uploads
- DELETE /api/medias/{media_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/medias/{media_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "filename": "string",
  "file_path": "string",
  "file_type": "string",
  "file_size": 1,
  "mime_type": "string",
  "uploaded_by": 1,
  "created_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 39. Create Order

**Method:** POST  
**URL:** http://localhost:8000/api/mobile/checkout

**Description:**  
Endpoint thực thi nghiệp vụ `create_order` để: Create Order.

**Use case trong hệ thống:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}
- GET /api/mobile/posts

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/mobile/checkout

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "customer_name": "string",
  "customer_phone": "string",
  "customer_email": "string",
  "shipping_address": "string",
  "shipping_province": "string",
  "shipping_district": "string",
  "shipping_ward": "string",
  "payment_method": "string",
  "customer_note": "string",
  "items": [
    {
      "product_id": 1,
      "quantity": 1
    }
  ]
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dùng trong luồng mua hàng: chọn sản phẩm -> giỏ hàng -> checkout -> tạo đơn.

---

### 40. Get My Orders

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/orders/my

**Description:**  
Endpoint thực thi nghiệp vụ `get_my_orders` để: Get My Orders.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my/{order_id}
- GET /api/mobile/posts

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`.
- Danh sách query params: `page`, `limit`, `status`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/orders/my

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 41. Get My Order Detail

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/orders/my/{order_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_my_order_detail` để: Get My Order Detail.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/posts

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/orders/my/{order_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 42. Get Public Posts

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/posts

**Description:**  
Endpoint thực thi nghiệp vụ `get_public_posts` để: Get Public Posts.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `author_id`.
- Danh sách query params: `page`, `limit`, `author_id`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/posts

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 43. Get My Posts

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/posts/my

**Description:**  
Endpoint thực thi nghiệp vụ `get_my_posts` để: Get My Posts.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`.
- Danh sách query params: `page`, `limit`, `status`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/posts/my

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 44. Create My Post

**Method:** POST  
**URL:** http://localhost:8000/api/mobile/posts/my

**Description:**  
Endpoint thực thi nghiệp vụ `create_my_post` để: Create My Post.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/mobile/posts/my

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body**

```json
{
  "title": "string",
  "content": "string",
  "product_id": 1,
  "images": "string",
  "videos": "string",
  "media_file": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 45. Delete My Post

**Method:** DELETE  
**URL:** http://localhost:8000/api/mobile/posts/my/{post_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_my_post` để: Delete My Post.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/mobile/posts/my/{post_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 46. Update My Post

**Method:** PUT  
**URL:** http://localhost:8000/api/mobile/posts/my/{post_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_my_post` để: Update My Post.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/mobile/posts/my/{post_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "title": "string",
  "content": "string",
  "images": "string",
  "videos": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 47. Get Post Detail

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/posts/{post_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_post_detail` để: Get Post Detail.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/posts/{post_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 48. Get Public Products

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/products

**Description:**  
Endpoint thực thi nghiệp vụ `get_public_products` để: Get Public Products.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}
- GET /api/mobile/posts

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `producer_id`, `label`, `min_price`, `max_price`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `producer_id`, `label`, `search`, `min_price`, `max_price`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/products

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 49. Get Product Detail

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/products/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_product_detail` để: Get Product Detail.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/products/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 50. Get My Profile

**Method:** GET  
**URL:** http://localhost:8000/api/mobile/profile

**Description:**  
Endpoint thực thi nghiệp vụ `get_my_profile` để: Get My Profile.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/mobile/profile

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 51. Update My Profile

**Method:** PUT  
**URL:** http://localhost:8000/api/mobile/profile

**Description:**  
Endpoint thực thi nghiệp vụ `update_my_profile` để: Update My Profile.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
API dành cho ứng dụng mobile: bài viết, sản phẩm, checkout, profile.

**Liên kết với API khác:**
- POST /api/auth/login
- GET /api/mobile/products
- POST /api/mobile/checkout
- GET /api/mobile/orders/my
- GET /api/mobile/orders/my/{order_id}

**Biến thể API:**
- Có filter theo: `name`, `gender`.
- Danh sách query params: `name`, `gender`.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/mobile/profile

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 52. Get Orders

**Method:** GET  
**URL:** http://localhost:8000/api/orders

**Description:**  
Endpoint thực thi nghiệp vụ `get_orders` để: Get Orders.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị đơn hàng và trạng thái đơn.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- POST /api/payments/vnpay/create
- POST /api/shipping/create
- GET /api/orders/stats/overview
- GET /api/orders/{order_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`, `customer_id`, `seller_id`, `payment_status`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `status`, `customer_id`, `seller_id`, `payment_status`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/orders

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "order_number": "string",
      "customer_id": 1,
      "customer_name": "string",
      "customer_phone": "string",
      "customer_email": "string",
      "shipping_address": "string",
      "seller_id": 1,
      "seller_name": "string",
      "subtotal": "string",
      "shipping_fee": "string",
      "discount_amount": "string",
      "total_amount": "string",
      "platform_fee_percentage": "string",
      "platform_fee_amount": "string",
      "seller_amount": "string",
      "status": "string",
      "payment_method": "string",
      "payment_status": "string",
      "customer_note": "string",
      "created_at": "2026-03-14T10:00:00Z",
      "items": [
        {
          "id": "...",
          "product_id": "...",
          "product_name": "...",
          "product_image": "...",
          "unit_price": "...",
          "quantity": "...",
          "total_price": "..."
        }
      ]
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 53. Get Order Stats

**Method:** GET  
**URL:** http://localhost:8000/api/orders/stats/overview

**Description:**  
Endpoint thực thi nghiệp vụ `get_order_stats` để: Get Order Stats.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị đơn hàng và trạng thái đơn.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- POST /api/payments/vnpay/create
- POST /api/shipping/create
- GET /api/orders
- GET /api/orders/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/orders/stats/overview

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 54. Get Order By Id

**Method:** GET  
**URL:** http://localhost:8000/api/orders/{order_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_order_by_id` để: Get Order By Id.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị đơn hàng và trạng thái đơn.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- POST /api/payments/vnpay/create
- POST /api/shipping/create
- GET /api/orders
- GET /api/orders/stats/overview

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/orders/{order_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "order_number": "string",
  "customer_id": 1,
  "customer_name": "string",
  "customer_phone": "string",
  "customer_email": "string",
  "shipping_address": "string",
  "seller_id": 1,
  "seller_name": "string",
  "subtotal": "string",
  "shipping_fee": "string",
  "discount_amount": "string",
  "total_amount": "string",
  "platform_fee_percentage": "string",
  "platform_fee_amount": "string",
  "seller_amount": "string",
  "status": "string",
  "payment_method": "string",
  "payment_status": "string",
  "customer_note": "string",
  "created_at": "2026-03-14T10:00:00Z",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "string",
      "product_image": "string",
      "unit_price": "string",
      "quantity": 1,
      "total_price": "string"
    }
  ]
}
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 55. Update Order Status

**Method:** PUT  
**URL:** http://localhost:8000/api/orders/{order_id}/status

**Description:**  
Endpoint thực thi nghiệp vụ `update_order_status` để: Update Order Status.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị đơn hàng và trạng thái đơn.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- POST /api/payments/vnpay/create
- POST /api/shipping/create
- GET /api/orders
- GET /api/orders/stats/overview

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/orders/{order_id}/status

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "status": "string",
  "note": "string",
  "cancel_reason": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 56. Get Organizations

**Method:** GET  
**URL:** http://localhost:8000/api/org

**Description:**  
Endpoint thực thi nghiệp vụ `get_organizations` để: Get Organizations.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- POST /api/org
- DELETE /api/org/{org_id}
- GET /api/org/{org_id}
- PUT /api/org/{org_id}
- GET /api/org/{org_id}/members

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/org

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "created_at": "string",
      "updated_at": "string",
      "member_count": 1
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 57. Create Organization

**Method:** POST  
**URL:** http://localhost:8000/api/org

**Description:**  
Endpoint thực thi nghiệp vụ `create_organization` để: Create Organization.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- GET /api/org
- DELETE /api/org/{org_id}
- GET /api/org/{org_id}
- PUT /api/org/{org_id}
- GET /api/org/{org_id}/members

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/org

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "created_at": "string",
  "updated_at": "string",
  "member_count": 1
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 58. Delete Organization

**Method:** DELETE  
**URL:** http://localhost:8000/api/org/{org_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_organization` để: Delete Organization.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- GET /api/org
- POST /api/org
- GET /api/org/{org_id}
- PUT /api/org/{org_id}
- GET /api/org/{org_id}/members

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/org/{org_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 59. Get Organization By Id

**Method:** GET  
**URL:** http://localhost:8000/api/org/{org_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_organization_by_id` để: Get Organization By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- GET /api/org
- POST /api/org
- DELETE /api/org/{org_id}
- PUT /api/org/{org_id}
- GET /api/org/{org_id}/members

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/org/{org_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "created_at": "string",
  "updated_at": "string",
  "member_count": 1
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 60. Update Organization

**Method:** PUT  
**URL:** http://localhost:8000/api/org/{org_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_organization` để: Update Organization.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- GET /api/org
- POST /api/org
- DELETE /api/org/{org_id}
- GET /api/org/{org_id}
- GET /api/org/{org_id}/members

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/org/{org_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "created_at": "string",
  "updated_at": "string",
  "member_count": 1
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 61. Get Organization Members

**Method:** GET  
**URL:** http://localhost:8000/api/org/{org_id}/members

**Description:**  
Endpoint thực thi nghiệp vụ `get_organization_members` để: Get Organization Members.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- GET /api/org
- POST /api/org
- DELETE /api/org/{org_id}
- GET /api/org/{org_id}
- PUT /api/org/{org_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Danh sách query params: `page`, `limit`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/org/{org_id}/members

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 62. Add Member To Organization

**Method:** POST  
**URL:** http://localhost:8000/api/org/{org_id}/members

**Description:**  
Endpoint thực thi nghiệp vụ `add_member_to_organization` để: Add Member To Organization.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- GET /api/org
- POST /api/org
- DELETE /api/org/{org_id}
- GET /api/org/{org_id}
- PUT /api/org/{org_id}

**Biến thể API:**
- Có filter theo: `user_id`.
- Danh sách query params: `user_id`.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/org/{org_id}/members

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 63. Remove Member From Organization

**Method:** DELETE  
**URL:** http://localhost:8000/api/org/{org_id}/members/{user_id}

**Description:**  
Endpoint thực thi nghiệp vụ `remove_member_from_organization` để: Remove Member From Organization.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý tổ chức (hợp tác xã/đơn vị) và thành viên trực thuộc.

**Liên kết với API khác:**
- GET /api/org
- POST /api/org
- DELETE /api/org/{org_id}
- GET /api/org/{org_id}
- PUT /api/org/{org_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/org/{org_id}/members/{user_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 64. Get Payments

**Method:** GET  
**URL:** http://localhost:8000/api/payments

**Description:**  
Endpoint thực thi nghiệp vụ `get_payments` để: Get Payments.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- POST /api/payments/complaint
- PUT /api/payments/config/cycle

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`, `customer_id`, `seller_id`.
- Danh sách query params: `page`, `limit`, `status`, `customer_id`, `seller_id`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/payments

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "total": 1,
  "page": 1,
  "limit": 1,
  "data": [
    {
      "id": 1,
      "order_id": 1,
      "customer_id": 1,
      "seller_id": 1,
      "amount": "string",
      "platform_fee_percentage": "string",
      "platform_fee_amount": "string",
      "seller_amount": "string",
      "status": "string",
      "payment_cycle": "string",
      "created_at": "2026-03-14T10:00:00Z"
    }
  ]
}
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 65. Create Payment Complaint

**Method:** POST  
**URL:** http://localhost:8000/api/payments/complaint

**Description:**  
Endpoint thực thi nghiệp vụ `create_payment_complaint` để: Create Payment Complaint.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- PUT /api/payments/config/cycle

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/payments/complaint

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "payment_id": 1,
  "complaint": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 66. Update Payment Cycle

**Method:** PUT  
**URL:** http://localhost:8000/api/payments/config/cycle

**Description:**  
Endpoint thực thi nghiệp vụ `update_payment_cycle` để: Update Payment Cycle.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Có filter theo: `cycle`.
- Danh sách query params: `cycle`.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/payments/config/cycle

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 67. Update Platform Fee

**Method:** PUT  
**URL:** http://localhost:8000/api/payments/config/fee

**Description:**  
Endpoint thực thi nghiệp vụ `update_platform_fee` để: Update Platform Fee.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Có filter theo: `fee_percentage`.
- Danh sách query params: `fee_percentage`.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/payments/config/fee

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 68. Get Payment Reconciliation

**Method:** GET  
**URL:** http://localhost:8000/api/payments/reconciliation

**Description:**  
Endpoint thực thi nghiệp vụ `get_payment_reconciliation` để: Get Payment Reconciliation.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Có filter theo: `start_date`, `end_date`.
- Danh sách query params: `start_date`, `end_date`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/payments/reconciliation

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 69. Process Refund

**Method:** POST  
**URL:** http://localhost:8000/api/payments/refund

**Description:**  
Endpoint thực thi nghiệp vụ `process_refund` để: Process Refund.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/payments/refund

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "payment_id": 1,
  "amount": 1000.0,
  "reason": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 70. Tạo URL thanh toán VNPAY

**Method:** POST  
**URL:** http://localhost:8000/api/payments/vnpay/create

**Description:**  
Endpoint thực thi nghiệp vụ `create_vnpay_payment` để: Tạo URL thanh toán VNPAY.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/payments/vnpay/create

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "order_id": 1
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 71. VNPAY IPN Webhook (server-to-server)

**Method:** POST  
**URL:** http://localhost:8000/api/payments/vnpay/ipn

**Description:**  
Endpoint thực thi nghiệp vụ `vnpay_ipn` để: VNPAY IPN Webhook (server-to-server).

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/payments/vnpay/ipn

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 72. VNPAY return URL (sau khi thanh toán)

**Method:** GET  
**URL:** http://localhost:8000/api/payments/vnpay/return

**Description:**  
Endpoint thực thi nghiệp vụ `vnpay_return` để: VNPAY return URL (sau khi thanh toán).

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/payments/vnpay/return

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 73. Get Payment Status

**Method:** GET  
**URL:** http://localhost:8000/api/payments/{payment_id}/status

**Description:**  
Endpoint thực thi nghiệp vụ `get_payment_status` để: Get Payment Status.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Thanh toán, đối soát, hoàn tiền và cấu hình phí/cycle.

**Liên kết với API khác:**
- POST /api/mobile/checkout
- GET /api/orders/{order_id}
- GET /api/settlement/history
- GET /api/payments
- POST /api/payments/complaint

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/payments/{payment_id}/status

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 74. Get Permissions

**Method:** GET  
**URL:** http://localhost:8000/api/admin/permissions

**Description:**  
Endpoint thực thi nghiệp vụ `get_permissions` để: Get Permissions.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý permission/menu/action để điều khiển quyền truy cập chi tiết.

**Liên kết với API khác:**
- GET /api/admin/roles
- POST /api/admin/roles
- POST /api/users/{user_id}/roles
- POST /api/admin/permissions
- DELETE /api/admin/permissions/{permission_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `limit`, `page`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/admin/permissions

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "parent_id": 1,
      "name": "string",
      "label": "string",
      "type": "string",
      "route": "string",
      "status": "string",
      "order": 1,
      "icon": "string",
      "component": "string",
      "hide": true,
      "hideTab": true,
      "frameSrc": "string",
      "newFeature": true,
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 75. Create Permission

**Method:** POST  
**URL:** http://localhost:8000/api/admin/permissions

**Description:**  
Endpoint thực thi nghiệp vụ `create_permission` để: Create Permission.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý permission/menu/action để điều khiển quyền truy cập chi tiết.

**Liên kết với API khác:**
- GET /api/admin/roles
- POST /api/admin/roles
- POST /api/users/{user_id}/roles
- GET /api/admin/permissions
- DELETE /api/admin/permissions/{permission_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/admin/permissions

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "parent_id": 1,
  "name": "string",
  "label": "string",
  "type": "string",
  "route": "string",
  "status": "string",
  "order": 1,
  "icon": "string",
  "component": "string",
  "hide": true,
  "hide_tab": true,
  "frame_src": "string",
  "new_feature": true
}
```

**Example Response**

```json
{
  "id": 1,
  "parent_id": 1,
  "name": "string",
  "label": "string",
  "type": "string",
  "route": "string",
  "status": "string",
  "order": 1,
  "icon": "string",
  "component": "string",
  "hide": true,
  "hideTab": true,
  "frameSrc": "string",
  "newFeature": true,
  "created_at": "string",
  "updated_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 76. Delete Permission

**Method:** DELETE  
**URL:** http://localhost:8000/api/admin/permissions/{permission_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_permission` để: Delete Permission.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý permission/menu/action để điều khiển quyền truy cập chi tiết.

**Liên kết với API khác:**
- GET /api/admin/roles
- POST /api/admin/roles
- POST /api/users/{user_id}/roles
- GET /api/admin/permissions
- POST /api/admin/permissions

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/admin/permissions/{permission_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 77. Update Permission

**Method:** PUT  
**URL:** http://localhost:8000/api/admin/permissions/{permission_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_permission` để: Update Permission.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý permission/menu/action để điều khiển quyền truy cập chi tiết.

**Liên kết với API khác:**
- GET /api/admin/roles
- POST /api/admin/roles
- POST /api/users/{user_id}/roles
- GET /api/admin/permissions
- POST /api/admin/permissions

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/admin/permissions/{permission_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "parent_id": 1,
  "name": "string",
  "label": "string",
  "type": "string",
  "route": "string",
  "status": "string",
  "order": 1,
  "icon": "string",
  "component": "string",
  "hide": true,
  "hide_tab": true,
  "frame_src": "string",
  "new_feature": true
}
```

**Example Response**

```json
{
  "id": 1,
  "parent_id": 1,
  "name": "string",
  "label": "string",
  "type": "string",
  "route": "string",
  "status": "string",
  "order": 1,
  "icon": "string",
  "component": "string",
  "hide": true,
  "hideTab": true,
  "frameSrc": "string",
  "newFeature": true,
  "created_at": "string",
  "updated_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 78. Get Products

**Method:** GET  
**URL:** http://localhost:8000/api/products

**Description:**  
Endpoint thực thi nghiệp vụ `get_products` để: Get Products.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Vòng đời sản phẩm: niêm yết, duyệt, cập nhật, gán nhãn.

**Liên kết với API khác:**
- POST /api/products/{product_id}/approve
- POST /api/reviews
- POST /api/cart/items
- POST /api/products
- DELETE /api/products/{product_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`, `producer_id`, `label`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `status`, `producer_id`, `label`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/products

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "price": "string",
      "producer_id": 1,
      "producer_name": "string",
      "status": "string",
      "label": "string",
      "images": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 79. Create Product

**Method:** POST  
**URL:** http://localhost:8000/api/products

**Description:**  
Endpoint thực thi nghiệp vụ `create_product` để: Create Product.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Vòng đời sản phẩm: niêm yết, duyệt, cập nhật, gán nhãn.

**Liên kết với API khác:**
- POST /api/products/{product_id}/approve
- POST /api/reviews
- POST /api/cart/items
- GET /api/products
- DELETE /api/products/{product_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/products

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string",
  "price": 1000.0,
  "producer_id": 1,
  "label": "string",
  "images": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "price": "string",
  "producer_id": 1,
  "producer_name": "string",
  "status": "string",
  "label": "string",
  "images": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 80. Delete Product

**Method:** DELETE  
**URL:** http://localhost:8000/api/products/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_product` để: Delete Product.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Vòng đời sản phẩm: niêm yết, duyệt, cập nhật, gán nhãn.

**Liên kết với API khác:**
- POST /api/products/{product_id}/approve
- POST /api/reviews
- POST /api/cart/items
- GET /api/products
- POST /api/products

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/products/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 81. Get Product By Id

**Method:** GET  
**URL:** http://localhost:8000/api/products/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_product_by_id` để: Get Product By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Vòng đời sản phẩm: niêm yết, duyệt, cập nhật, gán nhãn.

**Liên kết với API khác:**
- POST /api/products/{product_id}/approve
- POST /api/reviews
- POST /api/cart/items
- GET /api/products
- POST /api/products

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/products/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "price": "string",
  "producer_id": 1,
  "producer_name": "string",
  "status": "string",
  "label": "string",
  "images": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 82. Update Product

**Method:** PUT  
**URL:** http://localhost:8000/api/products/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_product` để: Update Product.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Vòng đời sản phẩm: niêm yết, duyệt, cập nhật, gán nhãn.

**Liên kết với API khác:**
- POST /api/products/{product_id}/approve
- POST /api/reviews
- POST /api/cart/items
- GET /api/products
- POST /api/products

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/products/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string",
  "price": 1000.0,
  "label": "string",
  "images": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "price": "string",
  "producer_id": 1,
  "producer_name": "string",
  "status": "string",
  "label": "string",
  "images": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 83. Approve Product

**Method:** POST  
**URL:** http://localhost:8000/api/products/{product_id}/approve

**Description:**  
Endpoint thực thi nghiệp vụ `approve_product` để: Approve Product.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Vòng đời sản phẩm: niêm yết, duyệt, cập nhật, gán nhãn.

**Liên kết với API khác:**
- POST /api/reviews
- POST /api/cart/items
- POST /api/mobile/checkout
- GET /api/products
- POST /api/products

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/products/{product_id}/approve

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "product_id": 1,
  "status": "string",
  "notes": "string",
  "checked_description": true,
  "checked_price": true,
  "checked_images": true
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 84. Update Product Label

**Method:** PUT  
**URL:** http://localhost:8000/api/products/{product_id}/label

**Description:**  
Endpoint thực thi nghiệp vụ `update_product_label` để: Update Product Label.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Vòng đời sản phẩm: niêm yết, duyệt, cập nhật, gán nhãn.

**Liên kết với API khác:**
- POST /api/products/{product_id}/approve
- POST /api/reviews
- POST /api/cart/items
- GET /api/products
- POST /api/products

**Biến thể API:**
- Có filter theo: `label`.
- Danh sách query params: `label`.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/products/{product_id}/label

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 85. Get Regions

**Method:** GET  
**URL:** http://localhost:8000/api/regions

**Description:**  
Endpoint thực thi nghiệp vụ `get_regions` để: Get Regions.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vùng/địa phương phục vụ truy xuất và phân loại.

**Liên kết với API khác:**
- POST /api/regions
- DELETE /api/regions/{region_id}
- GET /api/regions/{region_id}
- PUT /api/regions/{region_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `is_active`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `is_active`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/regions

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "name": "string",
      "slug": "string",
      "description": "string",
      "image": "string",
      "latitude": "string",
      "longitude": "string",
      "order": 1,
      "is_active": true,
      "created_at": "2026-03-14T10:00:00Z",
      "updated_at": "2026-03-14T10:00:00Z"
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 86. Create Region

**Method:** POST  
**URL:** http://localhost:8000/api/regions

**Description:**  
Endpoint thực thi nghiệp vụ `create_region` để: Create Region.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vùng/địa phương phục vụ truy xuất và phân loại.

**Liên kết với API khác:**
- GET /api/regions
- DELETE /api/regions/{region_id}
- GET /api/regions/{region_id}
- PUT /api/regions/{region_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/regions

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string",
  "image": "string",
  "latitude": "string",
  "longitude": "string",
  "order": 1,
  "is_active": true
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "slug": "string",
  "description": "string",
  "image": "string",
  "latitude": "string",
  "longitude": "string",
  "order": 1,
  "is_active": true,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 87. Delete Region

**Method:** DELETE  
**URL:** http://localhost:8000/api/regions/{region_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_region` để: Delete Region.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vùng/địa phương phục vụ truy xuất và phân loại.

**Liên kết với API khác:**
- GET /api/regions
- POST /api/regions
- GET /api/regions/{region_id}
- PUT /api/regions/{region_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/regions/{region_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 88. Get Region By Id

**Method:** GET  
**URL:** http://localhost:8000/api/regions/{region_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_region_by_id` để: Get Region By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vùng/địa phương phục vụ truy xuất và phân loại.

**Liên kết với API khác:**
- GET /api/regions
- POST /api/regions
- DELETE /api/regions/{region_id}
- PUT /api/regions/{region_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/regions/{region_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "slug": "string",
  "description": "string",
  "image": "string",
  "latitude": "string",
  "longitude": "string",
  "order": 1,
  "is_active": true,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 89. Update Region

**Method:** PUT  
**URL:** http://localhost:8000/api/regions/{region_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_region` để: Update Region.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vùng/địa phương phục vụ truy xuất và phân loại.

**Liên kết với API khác:**
- GET /api/regions
- POST /api/regions
- DELETE /api/regions/{region_id}
- GET /api/regions/{region_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/regions/{region_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "string",
  "description": "string",
  "image": "string",
  "latitude": "string",
  "longitude": "string",
  "order": 1,
  "is_active": true
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "string",
  "slug": "string",
  "description": "string",
  "image": "string",
  "latitude": "string",
  "longitude": "string",
  "order": 1,
  "is_active": true,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 90. [Admin] Xem tất cả yêu cầu đổi/trả

**Method:** GET  
**URL:** http://localhost:8000/api/returns

**Description:**  
Endpoint thực thi nghiệp vụ `get_all_return_requests` để: [Admin] Xem tất cả yêu cầu đổi/trả.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đổi trả sau bán.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- POST /api/payments/refund
- GET /api/complaints/complaints
- POST /api/returns
- GET /api/returns/my

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`, `return_type`.
- Danh sách query params: `page`, `limit`, `status`, `return_type`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/returns

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 91. Tạo yêu cầu đổi/trả hàng

**Method:** POST  
**URL:** http://localhost:8000/api/returns

**Description:**  
Endpoint thực thi nghiệp vụ `create_return_request` để: Tạo yêu cầu đổi/trả hàng.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đổi trả sau bán.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- POST /api/payments/refund
- GET /api/complaints/complaints
- GET /api/returns
- GET /api/returns/my

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/returns

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "order_id": 1,
  "return_type": "string",
  "reason": "string",
  "images": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 92. Xem yêu cầu đổi/trả của tôi

**Method:** GET  
**URL:** http://localhost:8000/api/returns/my

**Description:**  
Endpoint thực thi nghiệp vụ `get_my_return_requests` để: Xem yêu cầu đổi/trả của tôi.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đổi trả sau bán.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- POST /api/payments/refund
- GET /api/complaints/complaints
- GET /api/returns
- POST /api/returns

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`.
- Danh sách query params: `page`, `limit`, `status`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/returns/my

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 93. [Admin] Duyệt yêu cầu đổi/trả

**Method:** PUT  
**URL:** http://localhost:8000/api/returns/{return_id}/approve

**Description:**  
Endpoint thực thi nghiệp vụ `approve_return_request` để: [Admin] Duyệt yêu cầu đổi/trả.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đổi trả sau bán.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- POST /api/payments/refund
- GET /api/complaints/complaints
- GET /api/returns
- POST /api/returns

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/returns/{return_id}/approve

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "note": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 94. [Admin] Đã nhận hàng trả về

**Method:** PUT  
**URL:** http://localhost:8000/api/returns/{return_id}/received

**Description:**  
Endpoint thực thi nghiệp vụ `mark_return_received` để: [Admin] Đã nhận hàng trả về.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đổi trả sau bán.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- POST /api/payments/refund
- GET /api/complaints/complaints
- GET /api/returns
- POST /api/returns

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/returns/{return_id}/received

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 95. [Admin] Từ chối yêu cầu đổi/trả

**Method:** PUT  
**URL:** http://localhost:8000/api/returns/{return_id}/reject

**Description:**  
Endpoint thực thi nghiệp vụ `reject_return_request` để: [Admin] Từ chối yêu cầu đổi/trả.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đổi trả sau bán.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- POST /api/payments/refund
- GET /api/complaints/complaints
- GET /api/returns
- POST /api/returns

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/returns/{return_id}/reject

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "note": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 96. Tạo đánh giá sản phẩm

**Method:** POST  
**URL:** http://localhost:8000/api/reviews

**Description:**  
Endpoint thực thi nghiệp vụ `create_review` để: Tạo đánh giá sản phẩm.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đánh giá sản phẩm sau mua.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/orders/{order_id}
- POST /api/returns
- GET /api/reviews/product/{product_id}
- DELETE /api/reviews/{review_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/reviews

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "product_id": 1,
  "order_id": 1,
  "rating": 1,
  "comment": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 97. Lấy đánh giá của sản phẩm (public)

**Method:** GET  
**URL:** http://localhost:8000/api/reviews/product/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_product_reviews` để: Lấy đánh giá của sản phẩm (public).

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đánh giá sản phẩm sau mua.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/orders/{order_id}
- POST /api/returns
- POST /api/reviews
- DELETE /api/reviews/{review_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Danh sách query params: `page`, `limit`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/reviews/product/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 98. Xóa đánh giá của mình

**Method:** DELETE  
**URL:** http://localhost:8000/api/reviews/{review_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_review` để: Xóa đánh giá của mình.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đánh giá sản phẩm sau mua.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/orders/{order_id}
- POST /api/returns
- POST /api/reviews
- GET /api/reviews/product/{product_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/reviews/{review_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 99. Cập nhật đánh giá của mình

**Method:** PUT  
**URL:** http://localhost:8000/api/reviews/{review_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_review` để: Cập nhật đánh giá của mình.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ đánh giá sản phẩm sau mua.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/orders/{order_id}
- POST /api/returns
- POST /api/reviews
- GET /api/reviews/product/{product_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/reviews/{review_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "rating": 1,
  "comment": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 100. Get Roles

**Method:** GET  
**URL:** http://localhost:8000/api/admin/roles

**Description:**  
Endpoint thực thi nghiệp vụ `get_roles` để: Get Roles.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vai trò để áp dụng RBAC cho backend và giao diện quản trị.

**Liên kết với API khác:**
- GET /api/admin/permissions
- POST /api/admin/permissions
- POST /api/users/{user_id}/roles
- POST /api/admin/roles
- DELETE /api/admin/roles/{role_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `limit`, `page`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/admin/roles

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "role_name": "string",
      "description": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 101. Create Role

**Method:** POST  
**URL:** http://localhost:8000/api/admin/roles

**Description:**  
Endpoint thực thi nghiệp vụ `create_role` để: Create Role.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vai trò để áp dụng RBAC cho backend và giao diện quản trị.

**Liên kết với API khác:**
- GET /api/admin/permissions
- POST /api/admin/permissions
- POST /api/users/{user_id}/roles
- GET /api/admin/roles
- DELETE /api/admin/roles/{role_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/admin/roles

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "role_name": "string",
  "description": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "role_name": "string",
  "description": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 102. Delete Role

**Method:** DELETE  
**URL:** http://localhost:8000/api/admin/roles/{role_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_role` để: Delete Role.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vai trò để áp dụng RBAC cho backend và giao diện quản trị.

**Liên kết với API khác:**
- GET /api/admin/permissions
- POST /api/admin/permissions
- POST /api/users/{user_id}/roles
- GET /api/admin/roles
- POST /api/admin/roles

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/admin/roles/{role_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 103. Update Role

**Method:** PUT  
**URL:** http://localhost:8000/api/admin/roles/{role_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_role` để: Update Role.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị vai trò để áp dụng RBAC cho backend và giao diện quản trị.

**Liên kết với API khác:**
- GET /api/admin/permissions
- POST /api/admin/permissions
- POST /api/users/{user_id}/roles
- GET /api/admin/roles
- POST /api/admin/roles

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/admin/roles/{role_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "role_name": "string",
  "description": "string"
}
```

**Example Response**

```json
{
  "id": 1,
  "role_name": "string",
  "description": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 104. Thống kê tổng quan của seller

**Method:** GET  
**URL:** http://localhost:8000/api/seller/dashboard

**Description:**  
Endpoint thực thi nghiệp vụ `get_seller_dashboard` để: Thống kê tổng quan của seller.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/orders
- PUT /api/seller/orders/{order_id}/confirm

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/dashboard

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 105. Danh sách đơn hàng của seller

**Method:** GET  
**URL:** http://localhost:8000/api/seller/orders

**Description:**  
Endpoint thực thi nghiệp vụ `get_seller_orders` để: Danh sách đơn hàng của seller.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/dashboard
- PUT /api/seller/orders/{order_id}/confirm

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `page`, `limit`, `status`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/orders

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 106. Xác nhận đơn hàng

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/orders/{order_id}/confirm

**Description:**  
Endpoint thực thi nghiệp vụ `confirm_order` để: Xác nhận đơn hàng.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/dashboard
- GET /api/seller/orders

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/orders/{order_id}/confirm

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 107. Từ chối / hủy đơn hàng

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/orders/{order_id}/reject

**Description:**  
Endpoint thực thi nghiệp vụ `reject_order` để: Từ chối / hủy đơn hàng.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/dashboard
- GET /api/seller/orders

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/orders/{order_id}/reject

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "reason": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 108. Chuyển đơn sang Đang giao hàng

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/orders/{order_id}/ship

**Description:**  
Endpoint thực thi nghiệp vụ `mark_order_shipping` để: Chuyển đơn sang Đang giao hàng.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/dashboard
- GET /api/seller/orders

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/orders/{order_id}/ship

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 109. Sản phẩm của seller

**Method:** GET  
**URL:** http://localhost:8000/api/seller/products

**Description:**  
Endpoint thực thi nghiệp vụ `get_seller_products` để: Sản phẩm của seller.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/dashboard
- GET /api/seller/orders

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`.
- Danh sách query params: `page`, `limit`, `status`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/products

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 110. Cập nhật tồn kho sản phẩm

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/products/{product_id}/stock

**Description:**  
Endpoint thực thi nghiệp vụ `update_product_stock` để: Cập nhật tồn kho sản phẩm.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/dashboard
- GET /api/seller/orders

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/products/{product_id}/stock

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "stock_quantity": 1
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 111. Thông tin shop/profile của seller

**Method:** GET  
**URL:** http://localhost:8000/api/seller/profile

**Description:**  
Endpoint thực thi nghiệp vụ `get_seller_profile` để: Thông tin shop/profile của seller.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Nghiệp vụ người bán: dashboard, đơn hàng, sản phẩm, tồn kho.

**Liên kết với API khác:**
- POST /api/seller/register
- GET /api/seller/verification-status
- POST /api/products
- GET /api/seller/dashboard
- GET /api/seller/orders

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/profile

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 112. Admin xem danh sách hồ sơ chờ duyệt

**Method:** GET  
**URL:** http://localhost:8000/api/seller/applications

**Description:**  
Endpoint thực thi nghiệp vụ `get_seller_applications` để: Admin xem danh sách hồ sơ chờ duyệt.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Onboarding/xác minh hồ sơ seller.

**Liên kết với API khác:**
- POST /api/auth/register
- GET /api/seller/verification-status
- PUT /api/seller/verify/{user_id}
- POST /api/seller/register

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `status`.
- Danh sách query params: `page`, `limit`, `status`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/applications

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 113. Seller nộp hồ sơ kinh doanh

**Method:** POST  
**URL:** http://localhost:8000/api/seller/register

**Description:**  
Endpoint thực thi nghiệp vụ `register_seller_profile` để: Seller nộp hồ sơ kinh doanh.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Onboarding/xác minh hồ sơ seller.

**Liên kết với API khác:**
- POST /api/auth/register
- GET /api/seller/verification-status
- PUT /api/seller/verify/{user_id}
- GET /api/seller/applications

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/seller/register

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "business_name": "string",
  "business_type": "string",
  "description": "string",
  "address": "string",
  "id_card_number": "string",
  "id_card_front_url": "string",
  "id_card_back_url": "string",
  "business_license_url": "string",
  "bank_name": "string",
  "bank_account_number": "string",
  "bank_account_name": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 114. Xem trạng thái xác minh

**Method:** GET  
**URL:** http://localhost:8000/api/seller/verification-status

**Description:**  
Endpoint thực thi nghiệp vụ `get_verification_status` để: Xem trạng thái xác minh.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Onboarding/xác minh hồ sơ seller.

**Liên kết với API khác:**
- POST /api/auth/register
- PUT /api/seller/verify/{user_id}
- GET /api/seller/applications
- POST /api/seller/register

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/verification-status

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 115. Admin duyệt / từ chối hồ sơ seller

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/verify/{user_id}

**Description:**  
Endpoint thực thi nghiệp vụ `verify_seller` để: Admin duyệt / từ chối hồ sơ seller.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Onboarding/xác minh hồ sơ seller.

**Liên kết với API khác:**
- POST /api/auth/register
- GET /api/seller/verification-status
- GET /api/seller/applications
- POST /api/seller/register

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/verify/{user_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "status": "string",
  "rejection_reason": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 116. Admin tạo kỳ đối soát cho seller

**Method:** POST  
**URL:** http://localhost:8000/api/settlement/create

**Description:**  
Endpoint thực thi nghiệp vụ `create_settlement` để: Admin tạo kỳ đối soát cho seller.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Đối soát và chi trả cho seller.

**Liên kết với API khác:**
- GET /api/payments/reconciliation
- GET /api/seller/orders
- POST /api/settlement/{settlement_id}/payout
- GET /api/settlement/history
- GET /api/settlement/payouts

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/settlement/create

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "seller_id": 1,
  "period_start": "2026-03-14T10:00:00Z",
  "period_end": "2026-03-14T10:00:00Z",
  "note": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 117. Lịch sử kỳ đối soát

**Method:** GET  
**URL:** http://localhost:8000/api/settlement/history

**Description:**  
Endpoint thực thi nghiệp vụ `get_settlement_history` để: Lịch sử kỳ đối soát.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Đối soát và chi trả cho seller.

**Liên kết với API khác:**
- GET /api/payments/reconciliation
- GET /api/seller/orders
- POST /api/settlement/{settlement_id}/payout
- POST /api/settlement/create
- GET /api/settlement/payouts

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `seller_id`.
- Danh sách query params: `page`, `limit`, `seller_id`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/settlement/history

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 118. Lịch sử chi trả

**Method:** GET  
**URL:** http://localhost:8000/api/settlement/payouts

**Description:**  
Endpoint thực thi nghiệp vụ `get_payout_history` để: Lịch sử chi trả.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Đối soát và chi trả cho seller.

**Liên kết với API khác:**
- GET /api/payments/reconciliation
- GET /api/seller/orders
- POST /api/settlement/{settlement_id}/payout
- POST /api/settlement/create
- GET /api/settlement/history

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Danh sách query params: `page`, `limit`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/settlement/payouts

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 119. Seller xem ví của mình

**Method:** GET  
**URL:** http://localhost:8000/api/settlement/wallet

**Description:**  
Endpoint thực thi nghiệp vụ `get_seller_wallet` để: Seller xem ví của mình.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Đối soát và chi trả cho seller.

**Liên kết với API khác:**
- GET /api/payments/reconciliation
- GET /api/seller/orders
- POST /api/settlement/{settlement_id}/payout
- POST /api/settlement/create
- GET /api/settlement/history

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/settlement/wallet

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 120. Admin duyệt kỳ đối soát

**Method:** POST  
**URL:** http://localhost:8000/api/settlement/{settlement_id}/approve

**Description:**  
Endpoint thực thi nghiệp vụ `approve_settlement` để: Admin duyệt kỳ đối soát.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Đối soát và chi trả cho seller.

**Liên kết với API khác:**
- GET /api/payments/reconciliation
- GET /api/seller/orders
- POST /api/settlement/{settlement_id}/payout
- POST /api/settlement/create
- GET /api/settlement/history

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/settlement/{settlement_id}/approve

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 121. Admin chi trả cho seller

**Method:** POST  
**URL:** http://localhost:8000/api/settlement/{settlement_id}/payout

**Description:**  
Endpoint thực thi nghiệp vụ `create_payout` để: Admin chi trả cho seller.

**Use case trong hệ thống:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

**API này phục vụ mục đích gì trong dự án:**  
Đối soát và chi trả cho seller.

**Liên kết với API khác:**
- GET /api/payments/reconciliation
- GET /api/seller/orders
- POST /api/settlement/create
- GET /api/settlement/history
- GET /api/settlement/payouts

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/settlement/{settlement_id}/payout

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "note": "string",
  "transaction_ref": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Phục vụ vận hành seller: xác minh hồ sơ, quản trị đơn/sản phẩm và đối soát chi trả.

---

### 122. Tạo vận đơn GHN

**Method:** POST  
**URL:** http://localhost:8000/api/shipping/create

**Description:**  
Endpoint thực thi nghiệp vụ `create_shipment` để: Tạo vận đơn GHN.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Tính phí/tạo vận đơn/đồng bộ trạng thái vận chuyển.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- PUT /api/seller/orders/{order_id}/ship
- POST /api/shipping/webhook
- POST /api/shipping/fee
- GET /api/shipping/order/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/shipping/create

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "order_id": 1,
  "weight": 1,
  "to_district_id": 1,
  "to_ward_code": "string",
  "from_district_id": 1,
  "note": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 123. Tính phí vận chuyển GHN

**Method:** POST  
**URL:** http://localhost:8000/api/shipping/fee

**Description:**  
Endpoint thực thi nghiệp vụ `calculate_shipping_fee` để: Tính phí vận chuyển GHN.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Tính phí/tạo vận đơn/đồng bộ trạng thái vận chuyển.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- PUT /api/seller/orders/{order_id}/ship
- POST /api/shipping/webhook
- POST /api/shipping/create
- GET /api/shipping/order/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/shipping/fee

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "to_district_id": 1,
  "to_ward_code": "string",
  "weight": 1,
  "from_district_id": 1
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 124. Xem vận đơn theo order_id

**Method:** GET  
**URL:** http://localhost:8000/api/shipping/order/{order_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_shipment_by_order` để: Xem vận đơn theo order_id.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Tính phí/tạo vận đơn/đồng bộ trạng thái vận chuyển.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- PUT /api/seller/orders/{order_id}/ship
- POST /api/shipping/webhook
- POST /api/shipping/create
- POST /api/shipping/fee

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/shipping/order/{order_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 125. GHN Webhook – cập nhật trạng thái vận đơn

**Method:** POST  
**URL:** http://localhost:8000/api/shipping/webhook

**Description:**  
Endpoint thực thi nghiệp vụ `ghn_webhook` để: GHN Webhook – cập nhật trạng thái vận đơn.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Tính phí/tạo vận đơn/đồng bộ trạng thái vận chuyển.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- PUT /api/seller/orders/{order_id}/ship
- POST /api/shipping/create
- POST /api/shipping/fee
- GET /api/shipping/order/{order_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/shipping/webhook

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 126. Tra cứu trạng thái vận đơn

**Method:** GET  
**URL:** http://localhost:8000/api/shipping/{shipment_id}/track

**Description:**  
Endpoint thực thi nghiệp vụ `track_shipment` để: Tra cứu trạng thái vận đơn.

**Use case trong hệ thống:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

**API này phục vụ mục đích gì trong dự án:**  
Tính phí/tạo vận đơn/đồng bộ trạng thái vận chuyển.

**Liên kết với API khác:**
- GET /api/orders/{order_id}
- PUT /api/seller/orders/{order_id}/ship
- POST /api/shipping/webhook
- POST /api/shipping/create
- POST /api/shipping/fee

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/shipping/{shipment_id}/track

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Nằm trong luồng xử lý đơn thực tế sau checkout: thanh toán, giao vận và cập nhật trạng thái đơn.

---

### 127. Get Category Stats

**Method:** GET  
**URL:** http://localhost:8000/api/stats/categories

**Description:**  
Endpoint thực thi nghiệp vụ `get_category_stats` để: Get Category Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Tổng hợp thống kê theo nhóm nghiệp vụ.

**Liên kết với API khác:**
- GET /api/dashboard/overview
- GET /api/dashboard/products
- GET /api/orders/stats/overview
- GET /api/stats/consumers
- GET /api/stats/producers

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/stats/categories

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 128. Get Consumer Stats

**Method:** GET  
**URL:** http://localhost:8000/api/stats/consumers

**Description:**  
Endpoint thực thi nghiệp vụ `get_consumer_stats` để: Get Consumer Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Tổng hợp thống kê theo nhóm nghiệp vụ.

**Liên kết với API khác:**
- GET /api/dashboard/overview
- GET /api/dashboard/products
- GET /api/orders/stats/overview
- GET /api/stats/categories
- GET /api/stats/producers

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/stats/consumers

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 129. Get Producer Stats

**Method:** GET  
**URL:** http://localhost:8000/api/stats/producers

**Description:**  
Endpoint thực thi nghiệp vụ `get_producer_stats` để: Get Producer Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Tổng hợp thống kê theo nhóm nghiệp vụ.

**Liên kết với API khác:**
- GET /api/dashboard/overview
- GET /api/dashboard/products
- GET /api/orders/stats/overview
- GET /api/stats/categories
- GET /api/stats/consumers

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/stats/producers

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 130. Get Region Stats

**Method:** GET  
**URL:** http://localhost:8000/api/stats/regions

**Description:**  
Endpoint thực thi nghiệp vụ `get_region_stats` để: Get Region Stats.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Tổng hợp thống kê theo nhóm nghiệp vụ.

**Liên kết với API khác:**
- GET /api/dashboard/overview
- GET /api/dashboard/products
- GET /api/orders/stats/overview
- GET /api/stats/categories
- GET /api/stats/consumers

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/stats/regions

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 131. Get Trending Products

**Method:** GET  
**URL:** http://localhost:8000/api/stats/trending

**Description:**  
Endpoint thực thi nghiệp vụ `get_trending_products` để: Get Trending Products.

**Use case trong hệ thống:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

**API này phục vụ mục đích gì trong dự án:**  
Tổng hợp thống kê theo nhóm nghiệp vụ.

**Liên kết với API khác:**
- GET /api/dashboard/overview
- GET /api/dashboard/products
- GET /api/orders/stats/overview
- GET /api/stats/categories
- GET /api/stats/consumers

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Danh sách query params: `limit`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/stats/trending

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được dashboard quản trị gọi định kỳ để hiển thị số liệu vận hành theo thời gian thực hoặc gần thời gian thực.

---

### 132. Root

**Method:** GET  
**URL:** http://localhost:8000/

**Description:**  
Endpoint thực thi nghiệp vụ `root` để: Root.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Điểm vào kiểm tra tình trạng hệ thống và heartbeat service.

**Liên kết với API khác:**
- GET /health

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/

**Headers**

```http
accept: application/json
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 133. Health

**Method:** GET  
**URL:** http://localhost:8000/health

**Description:**  
Endpoint thực thi nghiệp vụ `health` để: Health.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Điểm vào kiểm tra tình trạng hệ thống và heartbeat service.

**Liên kết với API khác:**
- GET /

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/health

**Headers**

```http
accept: application/json
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 134. Seller thêm chứng nhận cho sản phẩm

**Method:** POST  
**URL:** http://localhost:8000/api/traceability/certificates

**Description:**  
Endpoint thực thi nghiệp vụ `create_certificate` để: Seller thêm chứng nhận cho sản phẩm.

**Use case trong hệ thống:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

**API này phục vụ mục đích gì trong dự án:**  
Truy xuất nguồn gốc/chứng nhận sản phẩm.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/mobile/products/{product_id}
- GET /api/traceability/product/{product_id}
- GET /api/traceability/certificates/product/{product_id}
- PUT /api/traceability/certificates/{cert_id}/verify

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/traceability/certificates

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "product_id": 1,
  "certificate_name": "string",
  "certificate_number": "string",
  "issued_by": "string",
  "issue_date": "2026-03-14",
  "expiry_date": "2026-03-14",
  "document_url": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

---

### 135. Xem chứng nhận sản phẩm (public)

**Method:** GET  
**URL:** http://localhost:8000/api/traceability/certificates/product/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_product_certificates` để: Xem chứng nhận sản phẩm (public).

**Use case trong hệ thống:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

**API này phục vụ mục đích gì trong dự án:**  
Truy xuất nguồn gốc/chứng nhận sản phẩm.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/mobile/products/{product_id}
- GET /api/traceability/product/{product_id}
- POST /api/traceability/certificates
- PUT /api/traceability/certificates/{cert_id}/verify

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/traceability/certificates/product/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

---

### 136. Admin xác minh chứng nhận

**Method:** PUT  
**URL:** http://localhost:8000/api/traceability/certificates/{cert_id}/verify

**Description:**  
Endpoint thực thi nghiệp vụ `verify_certificate` để: Admin xác minh chứng nhận.

**Use case trong hệ thống:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

**API này phục vụ mục đích gì trong dự án:**  
Truy xuất nguồn gốc/chứng nhận sản phẩm.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/mobile/products/{product_id}
- GET /api/traceability/product/{product_id}
- POST /api/traceability/certificates
- GET /api/traceability/certificates/product/{product_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/traceability/certificates/{cert_id}/verify

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "status": "string",
  "rejection_reason": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

---

### 137. Seller khai báo nguồn gốc sản phẩm

**Method:** POST  
**URL:** http://localhost:8000/api/traceability/origins

**Description:**  
Endpoint thực thi nghiệp vụ `create_origin` để: Seller khai báo nguồn gốc sản phẩm.

**Use case trong hệ thống:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

**API này phục vụ mục đích gì trong dự án:**  
Truy xuất nguồn gốc/chứng nhận sản phẩm.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/mobile/products/{product_id}
- GET /api/traceability/product/{product_id}
- POST /api/traceability/certificates
- GET /api/traceability/certificates/product/{product_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/traceability/origins

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "product_id": 1,
  "village_name": "string",
  "region_id": 1,
  "producer_name": "string",
  "batch_number": "string",
  "production_date": "2026-03-14",
  "expiry_date": "2026-03-14",
  "ingredients": "string",
  "process_summary": "string"
}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

---

### 138. Xem nguồn gốc sản phẩm (public)

**Method:** GET  
**URL:** http://localhost:8000/api/traceability/origins/product/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_product_origin` để: Xem nguồn gốc sản phẩm (public).

**Use case trong hệ thống:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

**API này phục vụ mục đích gì trong dự án:**  
Truy xuất nguồn gốc/chứng nhận sản phẩm.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/mobile/products/{product_id}
- GET /api/traceability/product/{product_id}
- POST /api/traceability/certificates
- GET /api/traceability/certificates/product/{product_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/traceability/origins/product/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

---

### 139. Xem toàn bộ truy xuất nguồn gốc (public)

**Method:** GET  
**URL:** http://localhost:8000/api/traceability/product/{product_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_product_traceability` để: Xem toàn bộ truy xuất nguồn gốc (public).

**Use case trong hệ thống:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

**API này phục vụ mục đích gì trong dự án:**  
Truy xuất nguồn gốc/chứng nhận sản phẩm.

**Liên kết với API khác:**
- GET /api/products/{product_id}
- GET /api/mobile/products/{product_id}
- POST /api/traceability/certificates
- GET /api/traceability/certificates/product/{product_id}
- PUT /api/traceability/certificates/{cert_id}/verify

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/traceability/product/{product_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Hỗ trợ minh bạch nguồn gốc/chứng nhận để tăng niềm tin của khách hàng khi xem sản phẩm.

---

### 140. Get Users

**Method:** GET  
**URL:** http://localhost:8000/api/users

**Description:**  
Endpoint thực thi nghiệp vụ `get_users` để: Get Users.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- POST /api/users/{user_id}/roles
- GET /api/users/{user_id}/roles
- GET /api/admin/roles
- POST /api/users
- DELETE /api/users/{user_id}

**Biến thể API:**
- Có pagination qua `page` và/hoặc `limit`.
- Có filter theo: `model`, `activated`.
- Có hỗ trợ tìm kiếm qua `search`.
- Danh sách query params: `model`, `activated`, `limit`, `page`, `search`.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/users

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "data": [
    {
      "id": 1,
      "email": "string",
      "name": "string",
      "gender": "string",
      "activated": 1,
      "created_by": "string",
      "updated_by": "string",
      "created_at": "2026-03-14T10:00:00Z",
      "updated_at": "2026-03-14T10:00:00Z",
      "deleted_by": "string",
      "deleted_at": "2026-03-14T10:00:00Z",
      "type": "string"
    }
  ],
  "meta": {}
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 141. Create User

**Method:** POST  
**URL:** http://localhost:8000/api/users

**Description:**  
Endpoint thực thi nghiệp vụ `create_user` để: Create User.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- POST /api/users/{user_id}/roles
- GET /api/users/{user_id}/roles
- GET /api/admin/roles
- GET /api/users
- DELETE /api/users/{user_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/users

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "string",
  "name": "string",
  "gender": "string",
  "type": "string",
  "activated": 1
}
```

**Example Response**

```json
{
  "id": 1,
  "email": "string",
  "name": "string",
  "gender": "string",
  "activated": 1,
  "created_by": "string",
  "updated_by": "string",
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z",
  "deleted_by": "string",
  "deleted_at": "2026-03-14T10:00:00Z",
  "type": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 142. Delete User

**Method:** DELETE  
**URL:** http://localhost:8000/api/users/{user_id}

**Description:**  
Endpoint thực thi nghiệp vụ `delete_user` để: Delete User.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- POST /api/users/{user_id}/roles
- GET /api/users/{user_id}/roles
- GET /api/admin/roles
- GET /api/users
- POST /api/users

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/users/{user_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 143. Get User By Id

**Method:** GET  
**URL:** http://localhost:8000/api/users/{user_id}

**Description:**  
Endpoint thực thi nghiệp vụ `get_user_by_id` để: Get User By Id.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- POST /api/users/{user_id}/roles
- GET /api/users/{user_id}/roles
- GET /api/admin/roles
- GET /api/users
- POST /api/users

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/users/{user_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "id": 1,
  "email": "string",
  "name": "string",
  "gender": "string",
  "activated": 1,
  "created_by": "string",
  "updated_by": "string",
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z",
  "deleted_by": "string",
  "deleted_at": "2026-03-14T10:00:00Z",
  "type": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 144. Update User

**Method:** PUT  
**URL:** http://localhost:8000/api/users/{user_id}

**Description:**  
Endpoint thực thi nghiệp vụ `update_user` để: Update User.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- POST /api/users/{user_id}/roles
- GET /api/users/{user_id}/roles
- GET /api/admin/roles
- GET /api/users
- POST /api/users

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/users/{user_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "email": "user@example.com",
  "name": "string",
  "gender": "string",
  "type": "string",
  "activated": 1
}
```

**Example Response**

```json
{
  "id": 1,
  "email": "string",
  "name": "string",
  "gender": "string",
  "activated": 1,
  "created_by": "string",
  "updated_by": "string",
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-14T10:00:00Z",
  "deleted_by": "string",
  "deleted_at": "2026-03-14T10:00:00Z",
  "type": "string"
}
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 145. Activate User

**Method:** PUT  
**URL:** http://localhost:8000/api/users/{user_id}/activate

**Description:**  
Endpoint thực thi nghiệp vụ `activate_user` để: Activate User.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- POST /api/users/{user_id}/roles
- GET /api/users/{user_id}/roles
- GET /api/admin/roles
- GET /api/users
- POST /api/users

**Biến thể API:**
- Có filter theo: `activated`.
- Danh sách query params: `activated`.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/users/{user_id}/activate

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 146. Get User Roles

**Method:** GET  
**URL:** http://localhost:8000/api/users/{user_id}/roles

**Description:**  
Endpoint thực thi nghiệp vụ `get_user_roles` để: Get User Roles.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- POST /api/users/{user_id}/roles
- GET /api/admin/roles
- GET /api/users
- POST /api/users
- DELETE /api/users/{user_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/users/{user_id}/roles

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

### 147. Assign Roles To User

**Method:** POST  
**URL:** http://localhost:8000/api/users/{user_id}/roles

**Description:**  
Endpoint thực thi nghiệp vụ `assign_roles_to_user` để: Assign Roles To User.

**Use case trong hệ thống:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

**API này phục vụ mục đích gì trong dự án:**  
Quản trị người dùng nội bộ CMS: tạo, cập nhật, phân quyền, kích hoạt.

**Liên kết với API khác:**
- GET /api/users/{user_id}/roles
- GET /api/admin/roles
- GET /api/users
- POST /api/users
- DELETE /api/users/{user_id}

**Biến thể API:**
- Không có biến thể query đáng kể; chủ yếu dùng path/body chuẩn.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/users/{user_id}/roles

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
[
  1
]
```

**Example Response**

```json
"string"
```

---

**Real use case trong project:**  
Được frontend/backoffice gọi trực tiếp để thao tác nghiệp vụ tương ứng trong CMS và app mobile.

---

## 3) API mới bổ sung (Sprint 2-3)

> Các API bên dưới được bổ sung sau khi loại bỏ module Permissions và tái cấu trúc phân quyền theo `user.type`.

---

### 148. Update Profile

**Method:** PUT  
**URL:** http://localhost:8000/api/auth/profile

**Description:**  
Cập nhật thông tin cá nhân của user đang đăng nhập (dùng chung cho Admin, Seller, Consumer).

**Use case trong hệ thống:**  
User cập nhật tên, giới tính trên trang cá nhân. Không cần phân biệt role.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý thông tin profile người dùng.

**Liên kết với API khác:**
- GET /api/auth/me
- POST /api/auth/login

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/auth/profile

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "Nguyễn Văn A",
  "gender": "male"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Cập nhật thông tin cá nhân thành công",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "Nguyễn Văn A",
    "gender": "male",
    "type": "consumer"
  }
}
```

---

### 149. [Admin] Create Order

**Method:** POST  
**URL:** http://localhost:8000/api/orders

**Description:**  
Admin tạo đơn hàng thủ công (ví dụ đơn offline).

**Use case trong hệ thống:**  
Admin tạo đơn hàng cho khách offline hoặc đơn đặc biệt.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý đơn hàng – tạo mới.

**Liên kết với API khác:**
- GET /api/orders
- GET /api/orders/{order_id}
- PUT /api/orders/{order_id}/status

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/orders

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "customer_name": "Nguyễn Văn B",
  "customer_phone": "0901234567",
  "customer_email": "customer@example.com",
  "shipping_address": "123 Đường ABC, Quận 1, TP.HCM",
  "seller_id": 2,
  "payment_method": "COD",
  "customer_note": "Giao giờ hành chính",
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 3, "quantity": 1}
  ]
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã tạo đơn hàng",
  "data": {
    "id": 15,
    "order_number": "ORD-A1B2C3D4",
    "total_amount": "450000.00",
    "status": "PENDING"
  }
}
```

---

### 150. [Admin] Delete Order

**Method:** DELETE  
**URL:** http://localhost:8000/api/orders/{order_id}

**Description:**  
Admin xóa đơn hàng. Chỉ xóa được đơn ở trạng thái PENDING hoặc CANCELLED.

**Use case trong hệ thống:**  
Admin dọn dẹp đơn hàng rác hoặc đơn bị hủy.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý đơn hàng – xóa.

**Liên kết với API khác:**
- GET /api/orders
- POST /api/orders
- PUT /api/orders/{order_id}/status

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/orders/{order_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã xóa đơn hàng"
}
```

---

### 151. Customer Cancel Return Request

**Method:** PUT  
**URL:** http://localhost:8000/api/returns/{return_id}/cancel

**Description:**  
Khách hàng hủy yêu cầu đổi/trả. Chỉ hủy được khi yêu cầu đang ở trạng thái PENDING.

**Use case trong hệ thống:**  
Khách hàng đổi ý không muốn đổi/trả nữa.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý đổi trả hàng.

**Liên kết với API khác:**
- POST /api/returns
- GET /api/returns/my
- PUT /api/returns/{return_id}/approve

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/returns/{return_id}/cancel

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã hủy yêu cầu đổi/trả",
  "return_id": 5,
  "status": "CANCELLED"
}
```

---

### 152. Create Complaint

**Method:** POST  
**URL:** http://localhost:8000/api/complaints/complaints

**Description:**  
Tạo khiếu nại mới (có thể về sản phẩm hoặc đơn hàng).

**Use case trong hệ thống:**  
Người dùng gửi khiếu nại khi gặp vấn đề với sản phẩm hoặc dịch vụ.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý khiếu nại.

**Liên kết với API khác:**
- GET /api/complaints/complaints
- PUT /api/complaints/complaints/{complaint_id}/handle
- DELETE /api/complaints/complaints/{complaint_id}

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/complaints/complaints

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "product_id": 5,
  "order_id": 12,
  "complaint_type": "PRODUCT",
  "title": "Sản phẩm không đúng mô tả",
  "description": "Sản phẩm nhận được khác hoàn toàn với hình ảnh trên web."
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Khiếu nại đã được gửi",
  "data": {
    "id": 10,
    "product_id": 5,
    "order_id": 12,
    "user_id": 3,
    "complaint_type": "PRODUCT",
    "title": "Sản phẩm không đúng mô tả",
    "description": "Sản phẩm nhận được khác hoàn toàn với hình ảnh trên web.",
    "status": "PENDING",
    "handled_by": null,
    "resolution": null,
    "created_at": "2026-03-26T03:00:00"
  }
}
```

---

### 153. [Admin] Delete Complaint

**Method:** DELETE  
**URL:** http://localhost:8000/api/complaints/complaints/{complaint_id}

**Description:**  
Admin xóa khiếu nại.

**Use case trong hệ thống:**  
Admin dọn dẹp khiếu nại trùng lặp hoặc không hợp lệ.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý khiếu nại.

**Liên kết với API khác:**
- GET /api/complaints/complaints
- POST /api/complaints/complaints
- PUT /api/complaints/complaints/{complaint_id}/handle

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/complaints/complaints/{complaint_id}

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã xóa khiếu nại"
}
```

---

### 154. [Admin] Get All Promotions

**Method:** GET  
**URL:** http://localhost:8000/api/promotions

**Description:**  
Admin xem danh sách tất cả mã khuyến mãi (có phân trang, tìm kiếm).

**Use case trong hệ thống:**  
Admin quản lý chương trình khuyến mãi trên CMS.

**API này phục vụ mục đích gì trong dự án:**  
Quản lý khuyến mãi / mã giảm giá.

**Liên kết với API khác:**
- POST /api/promotions
- PUT /api/promotions/{promotion_id}
- DELETE /api/promotions/{promotion_id}
- GET /api/promotions/public

**Biến thể API:**
- `?page=1&limit=20` – phân trang
- `?search=SUMMER` – tìm theo code hoặc tên

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/promotions?page=1&limit=20&search=SUMMER

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "SUMMER2026",
      "name": "Giảm giá mùa hè",
      "promotion_type": "PERCENTAGE",
      "discount_value": "15.00",
      "max_discount_amount": "100000.00",
      "min_order_amount": "200000.00",
      "usage_limit": 500,
      "used_count": 123,
      "status": "ACTIVE",
      "start_date": "2026-06-01T00:00:00",
      "end_date": "2026-08-31T23:59:59",
      "created_at": "2026-03-20T10:00:00"
    }
  ],
  "meta": {"total": 5, "page": 1, "limit": 20}
}
```

---

### 155. [Admin] Create Promotion

**Method:** POST  
**URL:** http://localhost:8000/api/promotions

**Description:**  
Admin tạo mã khuyến mãi mới.

**Use case trong hệ thống:**  
Admin tạo chương trình giảm giá (theo % hoặc số tiền cố định).

**API này phục vụ mục đích gì trong dự án:**  
Quản lý khuyến mãi.

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/promotions

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "code": "NEWYEAR2026",
  "name": "Giảm giá Tết 2026",
  "description": "Áp dụng cho tất cả đơn hàng từ 300k",
  "promotion_type": "PERCENTAGE",
  "discount_value": 20,
  "max_discount_amount": 150000,
  "min_order_amount": 300000,
  "usage_limit": 1000,
  "start_date": "2026-01-20T00:00:00",
  "end_date": "2026-02-10T23:59:59"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Tạo mã khuyến mãi thành công",
  "data": {
    "id": 6,
    "code": "NEWYEAR2026",
    "status": "ACTIVE"
  }
}
```

---

### 156. Get Promotion Detail

**Method:** GET  
**URL:** http://localhost:8000/api/promotions/{promotion_id}

**Description:**  
Xem chi tiết một mã khuyến mãi theo ID.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/promotions/1

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "SUMMER2026",
    "name": "Giảm giá mùa hè",
    "promotion_type": "PERCENTAGE",
    "discount_value": "15.00",
    "max_discount_amount": "100000.00",
    "min_order_amount": "200000.00",
    "usage_limit": 500,
    "used_count": 123,
    "status": "ACTIVE",
    "start_date": "2026-06-01T00:00:00",
    "end_date": "2026-08-31T23:59:59"
  }
}
```

---

### 157. [Admin] Update Promotion

**Method:** PUT  
**URL:** http://localhost:8000/api/promotions/{promotion_id}

**Description:**  
Admin cập nhật thông tin mã khuyến mãi.

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/promotions/1

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "Giảm giá mùa hè - Gia hạn",
  "end_date": "2026-09-30T23:59:59",
  "usage_limit": 800
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Cập nhật mã khuyến mãi thành công"
}
```

---

### 158. [Admin] Delete Promotion

**Method:** DELETE  
**URL:** http://localhost:8000/api/promotions/{promotion_id}

**Description:**  
Admin xóa mã khuyến mãi.

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/promotions/1

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã xóa mã khuyến mãi"
}
```

---

### 159. Get Public Promotions

**Method:** GET  
**URL:** http://localhost:8000/api/promotions/public

**Description:**  
Consumer xem danh sách mã khuyến mãi đang hoạt động và còn hạn.

**Use case trong hệ thống:**  
Hiển thị trên trang checkout hoặc trang khuyến mãi cho khách hàng.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/promotions/public

**Headers**

```http
accept: application/json
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "SUMMER2026",
      "name": "Giảm giá mùa hè",
      "promotion_type": "PERCENTAGE",
      "discount_value": "15.00",
      "max_discount_amount": "100000.00",
      "min_order_amount": "200000.00",
      "end_date": "2026-08-31T23:59:59"
    }
  ]
}
```

---

### 160. [Seller] Get My Posts

**Method:** GET  
**URL:** http://localhost:8000/api/seller/posts

**Description:**  
Seller xem danh sách bài đăng của mình (có phân trang, tìm kiếm).

**Use case trong hệ thống:**  
Seller quản lý các bài đăng giới thiệu sản phẩm trên Seller Portal.

**Liên kết với API khác:**
- POST /api/seller/posts
- PUT /api/seller/posts/{post_id}
- DELETE /api/seller/posts/{post_id}

**Biến thể API:**
- `?page=1&limit=20` – phân trang
- `?search=...` – tìm theo tiêu đề

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/posts?page=1&limit=20

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "title": "Giới thiệu cà phê đặc biệt",
      "content_type": "POST",
      "status": "APPROVED",
      "created_at": "2026-03-20T10:00:00"
    }
  ],
  "meta": {"total": 5, "page": 1, "limit": 20}
}
```

---

### 161. [Seller] Create Post

**Method:** POST  
**URL:** http://localhost:8000/api/seller/posts

**Description:**  
Seller tạo bài đăng mới (mặc định trạng thái PENDING chờ Admin duyệt).

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/seller/posts

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "title": "Bài giới thiệu sản phẩm mới",
  "content": "Nội dung chi tiết bài đăng...",
  "content_type": "POST",
  "product_id": 10,
  "images": "[\"https://example.com/img1.jpg\"]"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã tạo bài đăng, chờ admin duyệt",
  "data": {
    "id": 15,
    "title": "Bài giới thiệu sản phẩm mới",
    "status": "PENDING"
  }
}
```

---

### 162. [Seller] Update Post

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/posts/{post_id}

**Description:**  
Seller cập nhật bài đăng (chỉ bài của mình).

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/posts/15

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "title": "Bài giới thiệu sản phẩm mới (cập nhật)",
  "content": "Nội dung cập nhật..."
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã cập nhật bài đăng"
}
```

---

### 163. [Seller] Delete Post

**Method:** DELETE  
**URL:** http://localhost:8000/api/seller/posts/{post_id}

**Description:**  
Seller xóa bài đăng (chỉ bài của mình).

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/seller/posts/15

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã xóa bài đăng"
}
```

---

### 164. [Seller] Get My Contracts

**Method:** GET  
**URL:** http://localhost:8000/api/seller/contracts

**Description:**  
Seller xem danh sách hợp đồng quảng cáo của mình.

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/contracts?page=1&limit=20

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "data": [
    {
      "id": 2,
      "contract_number": "CTR-001",
      "contract_type": "ADVERTISING",
      "status": "ACTIVE",
      "start_date": "2026-01-01T00:00:00",
      "end_date": "2026-12-31T23:59:59",
      "amount": "5000000.00"
    }
  ],
  "meta": {"total": 1, "page": 1, "limit": 20}
}
```

---

### 165. [Seller] Create Contract

**Method:** POST  
**URL:** http://localhost:8000/api/seller/contracts

**Description:**  
Seller tạo hợp đồng quảng cáo mới (mặc định DRAFT).

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/seller/contracts

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "contract_type": "ADVERTISING",
  "start_date": "2026-04-01T00:00:00",
  "end_date": "2026-06-30T23:59:59",
  "amount": 3000000,
  "terms": "Điều khoản hợp đồng quảng cáo..."
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã tạo hợp đồng quảng cáo",
  "data": {
    "id": 5,
    "contract_number": "CTR-A1B2C3D4",
    "status": "DRAFT"
  }
}
```

---

### 166. [Seller] Update Contract

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/contracts/{contract_id}

**Description:**  
Seller cập nhật hợp đồng (chỉ hợp đồng DRAFT).

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/contracts/5

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "amount": 4000000,
  "terms": "Điều khoản cập nhật..."
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã cập nhật hợp đồng"
}
```

---

### 167. [Seller] Delete Contract

**Method:** DELETE  
**URL:** http://localhost:8000/api/seller/contracts/{contract_id}

**Description:**  
Seller xóa hợp đồng (chỉ hợp đồng DRAFT).

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/seller/contracts/5

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã xóa hợp đồng"
}
```

---

### 168. [Seller] Delete Product

**Method:** DELETE  
**URL:** http://localhost:8000/api/seller/products/{product_id}

**Description:**  
Seller xóa sản phẩm (chỉ sản phẩm do mình sở hữu).

---

**Postman - Method**

DELETE

**Postman - URL**

http://localhost:8000/api/seller/products/10

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã xóa sản phẩm"
}
```

---

### 169. [Seller] Update Profile

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/profile

**Description:**  
Seller cập nhật thông tin cá nhân (tên, giới tính).

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/profile

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "Trần Văn C",
  "gender": "male"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Cập nhật thông tin thành công",
  "data": {
    "id": 5,
    "email": "seller@example.com",
    "name": "Trần Văn C",
    "gender": "male"
  }
}
```

---

### 170. [Seller] Get Returns

**Method:** GET  
**URL:** http://localhost:8000/api/seller/returns

**Description:**  
Seller xem danh sách yêu cầu đổi/trả liên quan đến đơn hàng của mình.

**Biến thể API:**
- `?page=1&limit=20` – phân trang
- `?status=PENDING` – lọc theo trạng thái

---

**Postman - Method**

GET

**Postman - URL**

http://localhost:8000/api/seller/returns?page=1&limit=20

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
```

**Request Body**

```json
{}
```

**Example Response**

```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "order_id": 12,
      "return_type": "RETURN",
      "reason": "Sản phẩm bị lỗi",
      "status": "PENDING",
      "created_at": "2026-03-25T14:00:00"
    }
  ],
  "meta": {"total": 2, "page": 1, "limit": 20}
}
```

---

### 171. [Seller] Handle Return Request

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/returns/{return_id}

**Description:**  
Seller xử lý yêu cầu đổi/trả (ACCEPT hoặc REJECT).

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/returns/3

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "action": "ACCEPT",
  "note": "Đồng ý đổi hàng cho khách"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã xử lý yêu cầu đổi/trả"
}
```

---

### 172. [Seller] Create Product

**Method:** POST  
**URL:** http://localhost:8000/api/seller/products

**Description:**  
Seller tạo sản phẩm mới (mặc định PENDING chờ Admin duyệt).

---

**Postman - Method**

POST

**Postman - URL**

http://localhost:8000/api/seller/products

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "Cà phê đặc sản Đắk Lắk",
  "description": "Cà phê Arabica 100% từ Đắk Lắk",
  "price": 250000,
  "stock_quantity": 100,
  "category_id": 3,
  "images": "[\"https://example.com/coffee.jpg\"]",
  "unit": "gói 500g"
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã tạo sản phẩm, chờ admin duyệt",
  "data": {
    "id": 25,
    "name": "Cà phê đặc sản Đắk Lắk",
    "status": "PENDING"
  }
}
```

---

### 173. [Seller] Update Product

**Method:** PUT  
**URL:** http://localhost:8000/api/seller/products/{product_id}

**Description:**  
Seller cập nhật sản phẩm (chỉ sản phẩm do mình sở hữu).

---

**Postman - Method**

PUT

**Postman - URL**

http://localhost:8000/api/seller/products/25

**Headers**

```http
accept: application/json
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**

```json
{
  "name": "Cà phê đặc sản Đắk Lắk (Cập nhật)",
  "price": 230000,
  "stock_quantity": 150
}
```

**Example Response**

```json
{
  "success": true,
  "message": "Đã cập nhật sản phẩm"
}
```
