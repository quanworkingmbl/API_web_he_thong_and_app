# CMS API — FastAPI Backend

REST API backend cho **Agrarian Platform** — nền tảng thương mại điện tử multi-seller chuyên về nông sản sạch và sản phẩm làng nghề truyền thống Việt Nam. Xây dựng bằng **FastAPI** + **SQLAlchemy** + **PostgreSQL** (Google Cloud SQL).

## 🚀 Tính năng

### Core
- **Authentication & Authorization**: JWT (Argon2/Bcrypt) + Refresh Token + reCAPTCHA v3
- **RBAC Permission System**: Phân quyền theo role (`admin`, `producer/seller`, `consumer`, `content_manager`)
- **API Security**: Middleware `X-Quan-Secret` bảo vệ toàn bộ endpoints

### E-Commerce
- **Product Management**: CRUD sản phẩm, biến thể (variant), SKU, tồn kho
- **Product Approval**: Queue duyệt sản phẩm với checklist (mô tả, giá, hình, truy xuất nguồn gốc)
- **Order Management**: Đơn hàng multi-seller, state machine chuyển trạng thái theo role
- **Cart**: Giỏ hàng + checkout
- **Payment**: VNPay gateway integration (sandbox)
- **Shipping**: GHN (Giao Hàng Nhanh) API — tính phí, tracking
- **Promotions**: Mã giảm giá, khuyến mãi

### Seller Ecosystem
- **Seller Onboarding (KYC)**: Đăng ký seller, upload CCCD, giấy phép kinh doanh
- **Seller Wallet**: Ví seller — tỷ lệ 80/20 reserve, rút tiền, min_reserve
- **Settlement**: Kỳ đối soát, chi trả, yêu cầu rút tiền
- **Store**: Quản lý cửa hàng

### Truy Xuất Nguồn Gốc
- **ProductOrigin**: Nguồn gốc sản phẩm (làng nghề, cơ sở SX, lô SX)
- **ProductCertificate**: Chứng nhận (VietGAP, OCOP, ISO 22000)

### AI Services
- **Content Moderation**: Kiểm duyệt nội dung tự động (Google Vertex AI — Gemini 2.5 Flash)
- **Auto-Generate Description**: AI viết mô tả sản phẩm
- **Product Embedding**: Vector embedding cho tìm kiếm ngữ nghĩa
- **Cost Tracking**: Theo dõi chi phí AI, budget guardrail $5/ngày

### Others
- **Content Management**: Blog, bài viết, duyệt nội dung
- **Complaint & Review**: Đánh giá sản phẩm, khiếu nại
- **Return/Refund**: Yêu cầu trả hàng, hoàn tiền
- **Notification**: In-app + Firebase Cloud Messaging push
- **Media Upload**: Google Cloud Storage
- **Dashboard Analytics**: Thống kê doanh thu, đơn hàng, người dùng
- **Partner Contracts**: Quản lý hợp đồng đối tác

## 📋 Yêu cầu

- Python 3.11+
- PostgreSQL 14+ (local hoặc Google Cloud SQL)
- pip

## 🔧 Cài đặt Local

### 1. Clone repository

```bash
git clone <repo-url>
cd Du_an_cms_API
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment variables

Tạo file `.env` (copy từ template bên dưới):

```env
# ─── Database (PostgreSQL) ───
DATABASE_URL=postgresql://user:password@localhost:5432/cms_db
DIRECT_URL=postgresql://user:password@localhost:5432/cms_db

# ─── JWT / Auth ───
SECRET_KEY=your-super-secret-key-at-least-32-chars
REFRESH_TOKEN_SECRET_KEY=your-refresh-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── App ───
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=True
SHOW_DOCS=True

# ─── API Secret Header ───
API_SECRET_KEY=VLU15122004

# ─── CORS ───
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ─── Google Cloud Storage ───
GCS_BUCKET_NAME=your-bucket-name

# ─── VNPay (sandbox) ───
VNPAY_TMN_CODE=
VNPAY_HASH_SECRET=
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:8000/api/payments/vnpay/return
VNPAY_IPN_URL=http://localhost:8000/api/payments/vnpay/ipn

# ─── GHN Shipping ───
GHN_TOKEN=
GHN_SHOP_ID=
GHN_URL=https://dev-online-gateway.ghn.vn/shiip/public-api

# ─── Google Vertex AI (Gemini) ───
VERTEX_PROJECT_ID=
VERTEX_LOCATION=asia-southeast1
VERTEX_MODERATION_MODEL_ID=gemini-2.5-flash
VERTEX_CREATIVE_MODEL_ID=gemini-2.5-flash
VERTEX_EMBEDDING_MODEL_ID=text-embedding-005
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# ─── Google reCAPTCHA v3 ───
RECAPTCHA_ENABLED=False
RECAPTCHA_SECRET_KEY=
RECAPTCHA_BYPASS_ENABLED=True
RECAPTCHA_BYPASS_SECRET_KEY=VLU15122004
RECAPTCHA_BYPASS_CLIENTS=mobile,postman
```

### 5. Chạy database migrations

```bash
alembic upgrade head
```

### 6. Chạy ứng dụng

```bash
# Cách 1: Dùng run.py (recommended)
python run.py

# Cách 2: Dùng uvicorn trực tiếp
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API chạy tại: `http://localhost:8000`

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📁 Cấu trúc dự án

```
Du_an_cms_API/
├── app/
│   ├── main.py                    ★ Entry point — FastAPI app, middleware, router
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py        ★ API router registry (28 modules)
│   │       ├── auth.py              Login, Register, Refresh, Logout
│   │       ├── users.py             User CRUD
│   │       ├── roles.py             Role management (admin)
│   │       ├── organizations.py     Organization management
│   │       ├── dashboard.py         Dashboard analytics
│   │       ├── media.py             Media upload (GCS)
│   │       ├── products.py          Product CRUD, approval
│   │       ├── payments.py          VNPay integration
│   │       ├── content.py           Blog, content management
│   │       ├── complaints.py        Complaint handling
│   │       ├── contracts.py         Partner contracts
│   │       ├── stats.py             System stats
│   │       ├── orders.py            Order management (admin/seller)
│   │       ├── categories.py        Product categories
│   │       ├── regions.py           Regions management
│   │       ├── cart.py              Shopping cart
│   │       ├── seller.py            Seller dashboard, products, orders
│   │       ├── seller_onboarding.py KYC verification
│   │       ├── shipping.py          GHN shipping
│   │       ├── reviews.py           Product reviews
│   │       ├── returns.py           Return/refund requests
│   │       ├── settlement.py        Wallet, settlement, withdrawals
│   │       ├── traceability.py      Origin & certificates
│   │       ├── promotions.py        Promotions, coupons
│   │       ├── mobile_app.py        ★ Mobile App API (all-in-one)
│   │       ├── ai.py                AI moderation & generation
│   │       ├── settings.py          System settings
│   │       └── notifications.py     Push notifications
│   ├── core/
│   │   ├── config.py              ★ Pydantic Settings (.env)
│   │   ├── database.py            ★ SQLAlchemy engine + session
│   │   ├── security.py            ★ JWT + Argon2 password hash
│   │   ├── permissions.py         ★ Centralized RBAC functions
│   │   ├── middleware.py            ApiSecret + Logging middleware
│   │   ├── exceptions.py           Global exception handlers
│   │   ├── logging_config.py       Logging setup
│   │   └── url_utils.py            DB URL builder
│   ├── models/                    34+ SQLAlchemy ORM models
│   │   ├── __init__.py            ★ All models registry
│   │   ├── user.py                  User, UserRole, UserOrganization
│   │   ├── product.py               Product, ProductApproval, PriceLog
│   │   ├── order.py                 Order, OrderItem, OrderStatusLog
│   │   ├── seller_profile.py        SellerProfile (KYC)
│   │   ├── settlement.py            SellerWallet, Settlement, Payout, Withdrawal
│   │   ├── traceability.py          ProductCertificate, ProductOrigin
│   │   ├── product_variant.py       Variant, Option, Inventory
│   │   ├── payment.py               Payment, Transaction, AuditLog
│   │   └── ...                      (34 model files)
│   └── services/
│       ├── order_state.py         ★ Order state machine (role-based transitions)
│       ├── wallet.py              ★ Wallet logic (80/20 reserve)
│       ├── inventory.py             Stock management
│       ├── notification.py          Notification logic
│       ├── fcm_push.py              Firebase Cloud Messaging
│       ├── vnpay.py                 VNPay payment gateway
│       ├── ghn.py                   GHN shipping API
│       └── ai/                      AI moderation & generation
├── alembic/                       Database migrations
├── scripts/                       Utility scripts
├── Dockerfile                     Multi-stage Docker build
├── cloudbuild.yaml                ★ Google Cloud Build CI/CD
├── entrypoint.sh                  Gunicorn + Uvicorn startup
├── requirements.txt               Python dependencies
├── run.py                         Local dev runner
└── .env                           Environment variables
```

## 🔐 API Security

Tất cả API requests (trừ `/`, `/health`, `/docs`, `/redoc`) yêu cầu:

```
X-Quan-Secret: <API_SECRET_KEY>
Authorization: Bearer <jwt_token>    (cho endpoints cần auth)
```

### Middleware Stack (thứ tự xử lý):

```
Request → CORS → Logging → ApiSecret → Router → Handler → Response
```

## 📡 API Endpoints (28 Modules)

### Authentication (`/api/auth`)

| Method | Path | Mô tả |
|---|---|---|
| POST | `/api/auth/register` | Đăng ký tài khoản |
| POST | `/api/auth/login` | Đăng nhập (JWT + reCAPTCHA) |
| POST | `/api/auth/refresh` | Refresh token |
| POST | `/api/auth/logout` | Đăng xuất |
| GET | `/api/auth/me` | Thông tin user hiện tại |
| PUT | `/api/auth/profile` | Cập nhật profile |

### Orders (`/api/orders`)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/orders` | Danh sách đơn hàng |
| GET | `/api/orders/{id}` | Chi tiết đơn hàng |
| PUT | `/api/orders/{id}/status` | Cập nhật trạng thái |

### Seller (`/api/seller`)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/seller/products` | Sản phẩm của seller |
| GET | `/api/seller/orders` | Đơn hàng của seller |
| POST | `/api/seller/onboarding/register` | Đăng ký seller |

### Settlement (`/api/settlement`)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/settlement/wallet/me` | Xem ví seller |
| POST | `/api/settlement/withdrawals` | Yêu cầu rút tiền |

### Mobile App (`/api/mobile`)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/mobile/home` | Trang chủ app |
| GET | `/api/mobile/products` | Danh sách sản phẩm |
| POST | `/api/mobile/orders` | Tạo đơn hàng |
| GET | `/api/mobile/orders/my` | Đơn hàng của tôi |

> 📖 Xem đầy đủ tại `/docs` (Swagger UI)

## ☁️ Deployment (Google Cloud)

### CI/CD Pipeline (Cloud Build)

```
Git push → Cloud Build → Docker Build → Alembic Migrate → Cloud Run Deploy
```

| Bước | Chi tiết |
|---|---|
| Build | Docker multi-stage (python:3.11-slim) |
| Registry | Artifact Registry (asia-southeast1) |
| Migrate | `alembic upgrade head` (trong Cloud Build) |
| Deploy | Cloud Run (512Mi, 1 CPU, 0-3 instances) |
| Database | Cloud SQL via Cloud SQL Proxy |
| Secrets | Google Secret Manager |

### Cloud Run Config

```yaml
Region: asia-southeast1
Memory: 512Mi
CPU: 1
Min instances: 0 (scale-to-zero)
Max instances: 3
Timeout: 300s
```

### Production Domains

| Domain | Service |
|---|---|
| `api.quancmsbe.site` | Backend API |
| `quancmsbe.site` | Backend (root) |

## 📝 Database Migrations

```bash
# Tạo migration mới (auto-detect thay đổi model)
alembic revision --autogenerate -m "add new_table"

# Chạy migration
alembic upgrade head

# Rollback 1 bước
alembic downgrade -1

# Xem migration hiện tại
alembic current
```

## 🔍 Order State Machine

```
PENDING → CONFIRMED → PROCESSING → SHIPPING → DELIVERED
    ↓          ↓
 CANCELLED  CANCELLED                          REFUNDED
```

| Role | Transitions |
|---|---|
| Consumer | PENDING/CONFIRMED → CANCELLED |
| Seller | PENDING → CONFIRMED/CANCELLED → PROCESSING → SHIPPING → DELIVERED |
| Admin | Không hạn chế |

## 💰 Wallet Logic (80/20 Reserve)

```
Order DELIVERED → seller_amount tách:
  80% → available_balance (rút ngay, trừ min_reserve)
  20% → reserve_balance   (giữ 30 ngày)

max_withdrawable = available_balance - (active_products × 50,000 VND)
```

## 🐛 Troubleshooting

| Lỗi | Nguyên nhân | Fix |
|---|---|---|
| 403 Forbidden | Thiếu `X-Quan-Secret` header | Thêm header |
| 401 Unauthorized | JWT hết hạn hoặc sai | Refresh token hoặc login lại |
| 500 DB Error | Schema chưa sync | Chạy `alembic upgrade head` |
| CORS Error | Origin chưa whitelist | Thêm vào `CORS_ORIGINS` trong `.env` |

## 📚 Dependencies Chính

| Package | Version | Mục đích |
|---|---|---|
| fastapi | 0.109.0 | Web framework |
| uvicorn | 0.27.0 | ASGI server |
| gunicorn | 21.2.0 | Production WSGI server |
| sqlalchemy | 2.0.25 | ORM |
| alembic | 1.13.1 | Migration |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| python-jose | 3.3.0 | JWT |
| argon2-cffi | 23.1.0 | Password hashing |
| google-genai | ≥1.66.0 | Vertex AI Gemini |
| google-cloud-storage | ≥2.14.0 | GCS upload |
| httpx | ≥0.28.1 | HTTP client |

---

**Production URL**: `https://api.quancmsbe.site`
