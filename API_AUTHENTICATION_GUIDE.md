# 🔐 API Authentication & Authorization Guide

## 📋 Tổng quan

API sử dụng **Bearer Token Authentication** theo chuẩn OAuth 2.0. Tất cả các protected endpoints yêu cầu token trong header `Authorization: Bearer <token>`.

## 🔑 Authentication Flow

### 1. Register (Tạo tài khoản)

**Endpoint**: `POST /api/auth/register`

**Public endpoint** - Không cần authentication

**Request**:
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

---

### 2. Login (Đăng nhập)

**Endpoint**: `POST /api/auth/login`

**Public endpoint** - Không cần authentication

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
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
      "email": "user@example.com",
      "name": "User Name",
      "type": "consumer"
    }
  }
}
```

**Lưu token**: Lưu `api_token` từ response để sử dụng cho các request tiếp theo.

---

### 3. Get Current User Info

**Endpoint**: `GET /api/auth/me`

**Protected endpoint** - Cần Bearer token

**Headers**:
```
Authorization: Bearer <your_token_here>
```

**Request**:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "gender": "male",
    "activated": 1,
    "created_by": null,
    "updated_by": null,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": null,
    "deleted_by": null,
    "deleted_at": null,
    "type": "consumer",
    "roles": [
      {
        "id": 1,
        "role_name": "consumer",
        "description": "Consumer role"
      }
    ],
    "permissions": [
      {
        "id": 1,
        "name": "product_view",
        "label": "View Products"
      }
    ],
    "source_providers": []
  }
}
```

---

### 4. Refresh Token

**Endpoint**: `POST /api/auth/refresh`

**Protected endpoint** - Cần Bearer token

**Headers**:
```
Authorization: Bearer <your_token_here>
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "api_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_at": "2024-01-01T13:00:00"
  }
}
```

---

### 5. Logout

**Endpoint**: `POST /api/auth/logout`

**Protected endpoint** - Cần Bearer token

**Note**: JWT tokens không thể bị invalidate server-side. Client phải tự xóa token khỏi storage.

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully. Please remove token from client storage."
}
```

---

## 🔒 Standard API Response Format

Tất cả API endpoints trả về format chuẩn:

```json
{
  "success": true|false,
  "message": "Human readable message",
  "data": { ... },
  "errors": [ ... ]  // Optional, only when success = false
}
```

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "errors": [
    {
      "field": "email",
      "message": "Email is required"
    }
  ]
}
```

---

## 🛡️ Using Bearer Token in Requests

### Cách 1: cURL
```bash
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Cách 2: JavaScript/Fetch
```javascript
fetch('http://localhost:8000/api/users', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

### Cách 3: Axios
```javascript
axios.get('http://localhost:8000/api/users', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### Cách 4: Postman
1. Vào **Authorization** tab
2. Chọn **Type**: Bearer Token
3. Paste token vào **Token** field

---

## ⚠️ Error Responses

### 401 Unauthorized
Token không hợp lệ hoặc thiếu:
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
User không có quyền truy cập:
```json
{
  "detail": "User account is not activated"
}
```

### 422 Validation Error
Request body không đúng format:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 📝 Best Practices

1. **Store token securely**: Lưu token trong secure storage (localStorage/sessionStorage với HTTPS, hoặc httpOnly cookies)

2. **Handle token expiration**: Check `expires_at` và tự động refresh token trước khi hết hạn

3. **Remove token on logout**: Luôn xóa token khỏi client storage khi logout

4. **Use HTTPS**: Luôn sử dụng HTTPS trong production để bảo vệ token

5. **Don't expose token**: Không log token trong console, không commit token vào git

---

## 🔄 Complete Flow Example

```bash
# Step 1: Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "User Name"
  }'

# Step 2: Login và lấy token
RESPONSE=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }')

TOKEN=$(echo $RESPONSE | jq -r '.data.api_token')

# Step 3: Sử dụng token để gọi protected endpoint
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Step 4: Sử dụng token cho các API khác
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📚 Related Documentation

- [API Testing Guide](./API_TESTING_GUIDE.md) - Chi tiết tất cả endpoints
- [RBAC Guide](./RBAC_GUIDE.md) - Hướng dẫn phân quyền

---

**Chúc bạn sử dụng API thành công! 🚀**

