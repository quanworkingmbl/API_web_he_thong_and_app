# CMS API - FastAPI Backend

API backend cho hệ thống CMS quản lý sản phẩm địa phương, được xây dựng bằng FastAPI và PostgreSQL (Supabase).

## 🚀 Tính năng

- **Authentication & Authorization**: JWT-based authentication với role-based access control
- **User Management**: Quản lý người dùng (Consumer, Producer, Admin, etc.)
- **Role & Permission Management**: Quản lý vai trò và quyền truy cập
- **Product Approval**: Duyệt sản phẩm với kiểm tra mô tả, giá cả, hình ảnh
- **Payment Management**: Quản lý thanh toán, đối soát, hoàn tiền
- **Content Management**: Duyệt nội dung từ Producer và Cooperative
- **Complaint & Review Management**: Quản lý đánh giá và khiếu nại
- **Partner Contracts**: Quản lý hợp đồng đối tác vận hành
- **Media Management**: Upload và quản lý media files
- **Dashboard**: API cho dashboard với thống kê realtime

## 📋 Yêu cầu

- Python 3.11+
- PostgreSQL (Supabase)
- pip hoặc poetry

## 🔧 Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/quanworkingmbl/API_web_he_thong_and_app.git
cd API_web_he_thong_and_app
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment variables

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Cập nhật các giá trị trong `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=True
```

### 5. Chạy database migrations

```bash
# Tạo migration đầu tiên
alembic revision --autogenerate -m "Initial migration"

# Chạy migrations
alembic upgrade head
```

### 6. Chạy ứng dụng

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại: `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📁 Cấu trúc dự án

```
Du_an_cms_API/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── users.py          # User management
│   │       ├── roles.py          # Role management
│   │       ├── permissions.py    # Permission management
│   │       ├── organizations.py  # Organization management
│   │       ├── dashboard.py      # Dashboard endpoints
│   │       ├── media.py          # Media upload/management
│   │       ├── products.py       # Product approval
│   │       ├── payments.py      # Payment management
│   │       ├── content.py       # Content management
│   │       ├── complaints.py    # Complaint & review
│   │       └── contracts.py     # Partner contracts
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database setup
│   │   └── security.py          # Security utilities
│   ├── models/
│   │   ├── user.py              # User models
│   │   ├── role.py              # Role models
│   │   ├── permission.py        # Permission models
│   │   ├── product.py           # Product models
│   │   ├── payment.py           # Payment models
│   │   ├── content.py           # Content models
│   │   ├── complaint.py        # Complaint models
│   │   └── partner_contract.py  # Contract models
│   └── main.py                  # FastAPI app
├── alembic/                     # Database migrations
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── Procfile                     # Railway deployment
├── railway.json                 # Railway configuration
└── README.md                    # This file
```

## 🛒 Seller: Đăng bài & Đăng sản phẩm — Web hay App?

### ✅ Đăng bài (đăng bài viết / post)

**Seller đăng bài được hỗ trợ trên CẢ HAI nền tảng:**

| Nền tảng | Endpoint | File | Dòng |
|----------|----------|------|------|
| **APP (mobile)** | `POST /api/mobile/posts/my` | `app/api/v1/mobile_app.py` | **218** |
| **WEB** | `POST /api/content` | `app/api/v1/content.py` | **164** |

- **APP**: `app/api/v1/mobile_app.py` — dòng **218** (`@router.post("/posts/my")`)  
  Endpoint chính cho seller/producer đăng bài qua mobile app. Hỗ trợ upload ảnh/video trực tiếp. Bài viết tạo ra ở trạng thái `PENDING` chờ admin duyệt.

- **WEB**: `app/api/v1/content.py` — dòng **164** (`@router.post("")`)  
  Endpoint web cho phép tạo nội dung (bài viết, article, v.v.) qua giao diện web. Bài viết cũng ở trạng thái `PENDING` chờ duyệt.

---

### ✅ Đăng sản phẩm (tạo sản phẩm mới)

**Seller đăng sản phẩm chỉ qua WEB:**

| Nền tảng | Endpoint | File | Dòng |
|----------|----------|------|------|
| **WEB** | `POST /api/products` | `app/api/v1/products.py` | **162** |
| ~~APP (mobile)~~ | *(không có — chỉ đọc)* | — | — |

- **WEB**: `app/api/v1/products.py` — dòng **162** (`@router.post("")`)  
  Đây là endpoint duy nhất để tạo sản phẩm mới. Sản phẩm tạo ra ở trạng thái `PENDING` chờ admin duyệt.

- **Mobile app** chỉ có thể **ĐỌC** (`GET`) danh sách sản phẩm đã được duyệt:  
  `app/api/v1/mobile_app.py` — `GET /api/mobile/products` (không có `POST`).

---

### Tóm tắt phân chia Web / App

| Chức năng | WEB (`/api/...`) | APP (`/api/mobile/...`) |
|-----------|-----------------|------------------------|
| Đăng bài  | ✅ `POST /api/content` (`content.py:164`) | ✅ `POST /api/mobile/posts/my` (`mobile_app.py:218`) |
| Đăng sản phẩm | ✅ `POST /api/products` (`products.py:162`) | ❌ (chỉ đọc) |
| Đăng ký seller | ✅ `POST /api/seller/register` (`seller_onboarding.py:58`) | — |
| Dashboard seller | ✅ `GET /api/seller/dashboard` (`seller.py:58`) | — |

---

## 🔐 API Endpoints

### Authentication

- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/info` - Lấy thông tin user
- `GET /api/auth/logout` - Đăng xuất
- `POST /api/auth/refresh` - Refresh token

### Users

- `GET /api/users` - Danh sách users
- `POST /api/users` - Tạo user mới
- `PUT /api/users/{id}` - Cập nhật user

### Roles & Permissions

- `GET /api/admin/roles` - Danh sách roles
- `POST /api/admin/roles` - Tạo role mới
- `PUT /api/admin/roles/{id}` - Cập nhật role
- `DELETE /api/admin/roles/{id}` - Xóa role

- `GET /api/admin/permissions` - Danh sách permissions
- `POST /api/admin/permissions` - Tạo permission mới
- `PUT /api/admin/permissions/{id}` - Cập nhật permission
- `DELETE /api/admin/permissions/{id}` - Xóa permission

### Products

- `GET /api/products` - Danh sách sản phẩm
- `POST /api/products/{id}/approve` - Duyệt/từ chối sản phẩm
- `PUT /api/products/{id}/label` - Cập nhật nhãn sản phẩm

### Payments

- `GET /api/payments` - Danh sách thanh toán
- `GET /api/payments/{id}/status` - Trạng thái thanh toán
- `GET /api/payments/reconciliation` - Đối soát thanh toán
- `POST /api/payments/refund` - Hoàn tiền
- `POST /api/payments/complaint` - Khiếu nại thanh toán
- `PUT /api/payments/config/fee` - Cấu hình phí nền tảng
- `PUT /api/payments/config/cycle` - Cấu hình chu kỳ thanh toán

### Content

- `GET /api/content` - Danh sách nội dung
- `POST /api/content/{id}/approve` - Duyệt nội dung

### Complaints & Reviews

- `GET /api/complaints/reviews` - Danh sách đánh giá
- `GET /api/complaints/complaints` - Danh sách khiếu nại
- `PUT /api/complaints/complaints/{id}/handle` - Xử lý khiếu nại

### Partner Contracts

- `GET /api/contracts` - Danh sách hợp đồng
- `POST /api/contracts` - Tạo hợp đồng mới

### Media

- `GET /api/medias` - Danh sách media
- `POST /api/medias` - Tạo media record
- `POST /api/medias/uploads` - Upload file

### Dashboard

- `GET /api/accounts` - Danh sách accounts
- `GET /api/advertiser-private` - Advertisers private
- `GET /api/flights` - Flights
- `GET /api/report/flights/realtime` - Flight realtime reports

## 🚂 Deploy lên Railway

### 1. Chuẩn bị

1. Đăng ký tài khoản Railway tại [railway.app](https://railway.app)
2. Tạo project mới trên Railway
3. Kết nối GitHub repository

### 2. Cấu hình Environment Variables trên Railway

Trong Railway dashboard, thêm các biến môi trường:

```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend-domain.com
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=False
```

### 3. Setup Database

Railway sẽ tự động detect Python project và build. Sau khi deploy:

1. SSH vào Railway instance hoặc chạy migrations qua Railway CLI:

```bash
railway run alembic upgrade head
```

### 4. Cấu hình Build & Deploy

Railway sẽ tự động detect:
- `Procfile` cho start command
- `requirements.txt` cho dependencies
- Python version từ `runtime.txt`

### 5. Custom Domain (Optional)

Trong Railway dashboard:
1. Vào Settings → Networking
2. Thêm custom domain
3. Cập nhật `CORS_ORIGINS` với domain mới

### 6. Monitoring

Railway cung cấp:
- Logs realtime
- Metrics (CPU, Memory, Network)
- Deploy history

## 🔒 Security Notes

1. **SECRET_KEY**: Luôn sử dụng secret key mạnh trong production
2. **CORS**: Cấu hình đúng CORS_ORIGINS cho production
3. **Database**: Không commit credentials vào git
4. **HTTPS**: Railway tự động cung cấp HTTPS
5. **Rate Limiting**: Cân nhắc thêm rate limiting cho production

## 🧪 Testing

```bash
# Chạy tests (nếu có)
pytest

# Chạy với coverage
pytest --cov=app
```

## 📝 Database Migrations

```bash
# Tạo migration mới
alembic revision --autogenerate -m "Description"

# Chạy migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🐛 Troubleshooting

### Lỗi kết nối database

- Kiểm tra `DATABASE_URL` trong `.env`
- Đảm bảo Supabase database đang chạy
- Kiểm tra firewall/network settings

### Lỗi import modules

- Đảm bảo đã activate virtual environment
- Kiểm tra `PYTHONPATH`
- Chạy từ root directory của project

### Lỗi migrations

- Kiểm tra database connection
- Đảm bảo models đã được import trong `alembic/env.py`

## 📚 Tài liệu tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Railway Documentation](https://docs.railway.app/)

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

---

**Lưu ý**: Đảm bảo thay đổi tất cả placeholder values (passwords, secrets, etc.) trước khi deploy production!

