# 📚 API Testing Guide - Hướng dẫn Test API

Tài liệu chi tiết về tất cả API endpoints với request/response format và ví dụ test.

## 📋 Mục lục

1. [Authentication](#authentication)
2. [Users](#users)
3. [Roles](#roles)
4. [Permissions](#permissions)
5. [Products](#products)
6. [Payments](#payments)
7. [Content](#content)
8. [Complaints](#complaints)
9. [Contracts](#contracts)
10. [Media](#media)
11. [Organizations](#organizations)
12. [Dashboard & Stats](#dashboard--stats)

---

## 🔐 Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## 🔑 Authentication

Hầu hết các endpoints yêu cầu Bearer token trong header:

```
Authorization: Bearer <api_token>
```

Lấy token từ endpoint `/api/login`

---

## 1. Authentication

### 1.1. Register (Tạo tài khoản)

**Endpoint**: `POST /api/auth/register`

**Public endpoint** - Không cần authentication

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name",
  "gender": "male",
  "type": "consumer"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "type": "consumer"
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Email already registered"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "User Name",
    "gender": "male",
    "type": "consumer"
  }'
```

---

### 1.2. Login

**Endpoint**: `POST /api/auth/login`

**Public endpoint** - Không cần authentication

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "your-password",
  "recaptcha": null
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_at": "2024-01-01T12:30:00",
    "user": {
      "id": 1,
      "email": "admin@example.com",
      "name": "Admin User",
      "type": "admin"
    }
  }
}
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Incorrect email or password"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your-password"
  }'
```

**Lưu token**: Lưu `api_token` từ `data.api_token` trong response để sử dụng cho các request tiếp theo.

---

### 1.3. Get Current User Info

**Endpoint**: `GET /api/auth/me`

**Protected endpoint** - Cần Bearer token trong header

**Headers**:
```
Authorization: Bearer <your_token_here>
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "data": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin User",
    "gender": "male",
    "activated": 1,
    "created_by": null,
    "updated_by": null,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": null,
    "deleted_by": null,
    "deleted_at": null,
    "type": "admin",
    "roles": [
      {
        "id": 1,
        "role_name": "Admin",
        "description": "Administrator role"
      }
    ],
    "permissions": [
      {
        "id": 1,
        "parent_id": null,
        "name": "dashboard",
        "label": "Dashboard",
        "type": "MENU",
        "route": "/dashboard",
        "status": "ENABLE",
        "order": 1,
        "icon": "dashboard",
        "component": "Dashboard",
        "hide": false,
        "hideTab": false,
        "frameSrc": null,
        "newFeature": false
      }
    ],
    "source_providers": []
  }
}
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 1.3. Logout

**Endpoint**: `GET /api/logout`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/api/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 1.4. Refresh Token

**Endpoint**: `POST /api/refresh`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Response** (200 OK):
```json
{
  "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-01-01T13:00:00"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/refresh \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 2. Users

### 2.1. Get Users List

**Endpoint**: `GET /api/users`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `model` (optional): Filter by user type (admin, consumer, producer, etc.)
- `activated` (optional): Filter by activation status (0 or 1)
- `limit` (optional): Number of items per page (default: 50, max: 500)
- `page` (optional): Page number (default: 1)
- `search` (optional): Search by name or email

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "email": "admin@example.com",
      "name": "Admin User",
      "gender": "male",
      "activated": 1,
      "created_by": null,
      "updated_by": null,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": null,
      "deleted_by": null,
      "deleted_at": null,
      "type": "admin"
    }
  ],
  "meta": {
    "total": 100,
    "limit": 50,
    "current_page": 1,
    "total_pages": 2
  }
}
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/users?limit=10&page=1&search=admin" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 2.2. Create User

**Endpoint**: `POST /api/users`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "New User",
  "gender": "male",
  "type": "consumer",
  "activated": 1
}
```

**Response** (200 OK):
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "name": "New User",
  "gender": "male",
  "activated": 1,
  "created_by": "admin@example.com",
  "updated_by": null,
  "created_at": "2024-01-01T11:00:00",
  "updated_at": null,
  "deleted_by": null,
  "deleted_at": null,
  "type": "consumer"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "name": "New User",
    "gender": "male",
    "type": "consumer",
    "activated": 1
  }'
```

---

### 2.3. Update User

**Endpoint**: `PUT /api/users/{user_id}`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "email": "updated@example.com",
  "name": "Updated Name",
  "gender": "female",
  "type": "producer",
  "activated": 1
}
```

**Response** (200 OK):
```json
{
  "id": 2,
  "email": "updated@example.com",
  "name": "Updated Name",
  "gender": "female",
  "activated": 1,
  "created_by": "admin@example.com",
  "updated_by": "admin@example.com",
  "created_at": "2024-01-01T11:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "deleted_by": null,
  "deleted_at": null,
  "type": "producer"
}
```

**cURL Command**:
```bash
curl -X PUT http://localhost:8000/api/users/2 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "activated": 1
  }'
```

---

## 3. Roles

### 3.1. Get Roles List

**Endpoint**: `GET /api/admin/roles`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `limit` (optional): Number of items per page (default: 50, max: 500)
- `page` (optional): Page number (default: 1)
- `search` (optional): Search by role name

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "role_name": "Admin",
      "description": "Administrator role with full access",
      "created_at": "2024-01-01T10:00:00",
      "updated_at": null
    }
  ],
  "meta": {
    "total": 10,
    "limit": 50,
    "current_page": 1,
    "total_pages": 1
  }
}
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/admin/roles?limit=10&page=1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 3.2. Create Role

**Endpoint**: `POST /api/admin/roles`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "role_name": "Manager",
  "description": "Manager role with limited access"
}
```

**Response** (200 OK):
```json
{
  "id": 2,
  "role_name": "Manager",
  "description": "Manager role with limited access",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": null
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/admin/roles \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name": "Manager",
    "description": "Manager role with limited access"
  }'
```

---

### 3.3. Update Role

**Endpoint**: `PUT /api/admin/roles/{role_id}`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "role_name": "Updated Manager",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "id": 2,
  "role_name": "Updated Manager",
  "description": "Updated description",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T13:00:00"
}
```

**cURL Command**:
```bash
curl -X PUT http://localhost:8000/api/admin/roles/2 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

---

### 3.4. Delete Role

**Endpoint**: `DELETE /api/admin/roles/{role_id}`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Response** (200 OK):
```json
{
  "message": "Role deleted successfully"
}
```

**cURL Command**:
```bash
curl -X DELETE http://localhost:8000/api/admin/roles/2 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 4. Permissions

### 4.1. Get Permissions List

**Endpoint**: `GET /api/admin/permissions`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `limit` (optional): Number of items per page (default: 50, max: 500)
- `page` (optional): Page number (default: 1)
- `search` (optional): Search by name or label

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "parent_id": null,
      "name": "dashboard",
      "label": "Dashboard",
      "type": "MENU",
      "route": "/dashboard",
      "status": "ENABLE",
      "order": 1,
      "icon": "dashboard",
      "component": "Dashboard",
      "hide": false,
      "hideTab": false,
      "frameSrc": null,
      "newFeature": false,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": null
    }
  ],
  "meta": {
    "total": 20,
    "limit": 50,
    "current_page": 1,
    "total_pages": 1
  }
}
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/admin/permissions?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 5. Products

### 5.1. Get Products List

**Endpoint**: `GET /api/products`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `status` (optional): Filter by status (PENDING, APPROVED, REJECTED)
- `producer_id` (optional): Filter by producer ID

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Organic Rice",
    "description": "High quality organic rice",
    "price": "50000.00",
    "producer_id": 5,
    "status": "APPROVED",
    "label": "CLEAN_AGRICULTURE",
    "images": "image1.jpg,image2.jpg",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T11:00:00"
  }
]
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/products?status=APPROVED" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 5.2. Approve/Reject Product

**Endpoint**: `POST /api/products/{product_id}/approve`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_id": 1,
  "status": "APPROVED",
  "notes": "Product meets all requirements",
  "checked_description": true,
  "checked_price": true,
  "checked_images": true
}
```

**Response** (200 OK):
```json
{
  "message": "Product approved successfully"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/products/1/approve \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "status": "APPROVED",
    "notes": "Product meets all requirements",
    "checked_description": true,
    "checked_price": true,
    "checked_images": true
  }'
```

---

### 5.3. Update Product Label

**Endpoint**: `PUT /api/products/{product_id}/label?label=CLEAN_AGRICULTURE`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `label`: Label value (CLEAN_AGRICULTURE, TRADITIONAL_CRAFT, OCOP)

**Response** (200 OK):
```json
{
  "message": "Product label updated successfully"
}
```

**cURL Command**:
```bash
curl -X PUT "http://localhost:8000/api/products/1/label?label=CLEAN_AGRICULTURE" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 6. Payments

### 6.1. Get Payments List

**Endpoint**: `GET /api/payments`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `status` (optional): Filter by status
- `customer_id` (optional): Filter by customer ID
- `seller_id` (optional): Filter by seller ID

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "order_id": 100,
    "customer_id": 10,
    "seller_id": 5,
    "amount": "100000.00",
    "platform_fee_percentage": "5.00",
    "platform_fee_amount": "5000.00",
    "seller_amount": "95000.00",
    "status": "COMPLETED",
    "payment_cycle": "WEEKLY",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/payments?status=COMPLETED" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 6.2. Get Payment Status

**Endpoint**: `GET /api/payments/{payment_id}/status`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "order_id": 100,
  "customer_id": 10,
  "seller_id": 5,
  "amount": "100000.00",
  "platform_fee_percentage": "5.00",
  "platform_fee_amount": "5000.00",
  "seller_amount": "95000.00",
  "status": "COMPLETED",
  "payment_cycle": "WEEKLY",
  "created_at": "2024-01-01T10:00:00"
}
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/api/payments/1/status \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 6.3. Get Payment Reconciliation

**Endpoint**: `GET /api/payments/reconciliation`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Response** (200 OK):
```json
{
  "total_customer_paid": "1000000.00",
  "total_platform_commission": "50000.00",
  "total_seller_amount": "950000.00",
  "payments": [
    {
      "id": 1,
      "order_id": 100,
      "customer_id": 10,
      "seller_id": 5,
      "amount": "100000.00",
      "platform_fee_percentage": "5.00",
      "platform_fee_amount": "5000.00",
      "seller_amount": "95000.00",
      "status": "COMPLETED",
      "payment_cycle": "WEEKLY",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/payments/reconciliation?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 6.4. Refund Payment

**Endpoint**: `POST /api/payments/refund`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "payment_id": 1,
  "amount": "50000.00",
  "reason": "Customer requested refund"
}
```

**Response** (200 OK):
```json
{
  "message": "Refund processed successfully"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/payments/refund \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": 1,
    "amount": "50000.00",
    "reason": "Customer requested refund"
  }'
```

---

## 7. Content

### 7.1. Get Content List

**Endpoint**: `GET /api/content`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `status` (optional): Filter by status (PENDING, APPROVED, REJECTED)
- `author_id` (optional): Filter by author ID
- `content_type` (optional): Filter by content type

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Product Review",
    "content": "This is a great product...",
    "content_type": "REVIEW",
    "author_id": 5,
    "product_id": 10,
    "status": "APPROVED",
    "images": "image1.jpg",
    "videos": null,
    "created_at": "2024-01-01T10:00:00"
  }
]
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/content?status=PENDING" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 7.2. Approve Content

**Endpoint**: `POST /api/content/{content_id}/approve`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "content_id": 1,
  "status": "APPROVED"
}
```

**Response** (200 OK):
```json
{
  "message": "Content approved successfully"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/content/1/approve \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 1,
    "status": "APPROVED"
  }'
```

---

## 8. Complaints

### 8.1. Get Reviews List

**Endpoint**: `GET /api/complaints/reviews`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "product_id": 10,
    "user_id": 5,
    "rating": 5,
    "comment": "Great product!",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/api/complaints/reviews \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 8.2. Get Complaints List

**Endpoint**: `GET /api/complaints/complaints`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 5,
    "order_id": 100,
    "complaint_type": "PRODUCT_QUALITY",
    "description": "Product quality is not as described",
    "status": "PENDING",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/api/complaints/complaints \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 8.3. Handle Complaint

**Endpoint**: `PUT /api/complaints/complaints/{complaint_id}/handle`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "status": "RESOLVED",
  "resolution": "Refund processed"
}
```

**Response** (200 OK):
```json
{
  "message": "Complaint handled successfully"
}
```

**cURL Command**:
```bash
curl -X PUT http://localhost:8000/api/complaints/complaints/1/handle \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "RESOLVED",
    "resolution": "Refund processed"
  }'
```

---

## 9. Contracts

### 9.1. Get Contracts List

**Endpoint**: `GET /api/contracts`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `status` (optional): Filter by status
- `partner_id` (optional): Filter by partner ID
- `contract_type` (optional): Filter by contract type

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "contract_number": "CT-2024-001",
    "partner_id": 5,
    "contract_type": "OPERATION",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "amount": "10000000.00",
    "status": "ACTIVE",
    "terms": "Contract terms here...",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/contracts?status=ACTIVE" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 10. Media

### 10.1. Get Media List

**Endpoint**: `GET /api/medias`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Query Parameters**:
- `limit` (optional): Number of items per page
- `page` (optional): Page number
- `media_type` (optional): Filter by media type

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "media_type": "IMAGE",
      "file_path": "/uploads/image1.jpg",
      "file_size": 1024000,
      "mime_type": "image/jpeg",
      "created_at": "2024-01-01T10:00:00"
    }
  ],
  "meta": {
    "total": 100,
    "limit": 50,
    "current_page": 1,
    "total_pages": 2
  }
}
```

**cURL Command**:
```bash
curl -X GET "http://localhost:8000/api/medias?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 10.2. Upload Media

**Endpoint**: `POST /api/medias/uploads`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: multipart/form-data
```

**Request Body** (form-data):
- `file`: File to upload
- `media_type` (optional): Type of media (IMAGE, VIDEO, DOCUMENT)

**Response** (200 OK):
```json
{
  "id": 1,
  "media_type": "IMAGE",
  "file_path": "/uploads/image1.jpg",
  "file_size": 1024000,
  "mime_type": "image/jpeg",
  "created_at": "2024-01-01T10:00:00"
}
```

**cURL Command**:
```bash
curl -X POST http://localhost:8000/api/medias/uploads \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/image.jpg" \
  -F "media_type=IMAGE"
```

---

## 11. Organizations

### 11.1. Get Organizations List

**Endpoint**: `GET /api/org`

**Headers**:
```
Authorization: Bearer <api_token>
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Organization Name",
    "type": "COOPERATIVE",
    "description": "Organization description",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/api/org \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 12. Dashboard & Stats

### 12.1. Health Check

**Endpoint**: `GET /health`

**Headers**: None required

**Response** (200 OK):
```json
{
  "status": "healthy"
}
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/health
```

---

### 12.2. Root Endpoint

**Endpoint**: `GET /`

**Headers**: None required

**Response** (200 OK):
```json
{
  "message": "CMS API",
  "version": "1.0.0"
}
```

**cURL Command**:
```bash
curl -X GET http://localhost:8000/
```

---

## 🔧 Testing với Postman

### Import Collection

1. Tạo new Collection trong Postman
2. Set Base URL: `http://localhost:8000`
3. Tạo Environment variable:
   - `base_url`: `http://localhost:8000`
   - `api_token`: (sẽ được set sau khi login)

### Setup Authentication

1. Tạo request Login
2. Trong Tests tab, thêm script:
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("api_token", jsonData.api_token);
}
```

3. Tạo Authorization template cho Collection:
   - Type: Bearer Token
   - Token: `{{api_token}}`

---

## 📝 Notes

1. **Token Expiration**: Token hết hạn sau 30 phút (mặc định), cần refresh hoặc login lại
2. **Error Responses**: Tất cả errors trả về format:
   ```json
   {
     "detail": "Error message here"
   }
   ```
3. **Pagination**: Các endpoints có pagination trả về `meta` object với thông tin phân trang
4. **Date Format**: Tất cả dates sử dụng ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

---

## 🐛 Common Errors

### 401 Unauthorized
- Token không hợp lệ hoặc đã hết hạn
- Giải pháp: Login lại để lấy token mới

### 403 Forbidden
- User không có quyền truy cập
- Giải pháp: Kiểm tra roles và permissions

### 404 Not Found
- Resource không tồn tại
- Giải pháp: Kiểm tra ID trong URL

### 422 Validation Error
- Request body không đúng format
- Giải pháp: Kiểm tra required fields và data types

---

**Chúc bạn test API thành công! 🚀**

