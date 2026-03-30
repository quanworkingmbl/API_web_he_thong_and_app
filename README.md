# CMS API - FastAPI Backend

API backend cho hệ thống CMS quản lý sản phẩm địa phương, được xây dựng bằng FastAPI và PostgreSQL (AWS RDS).

## 🚀 Tính năng

- **Authentication & Authorization**: JWT-based authentication với role-based access control
- **User Management**: Quản lý người dùng (Consumer, Producer, Admin, etc.)
- **Role & Permission Management**: Quản lý vai trò và quyền truy cập
- **Product Approval**: Duyệt sản phẩm với kiểm tra mô tả, giá cả, hình ảnh
- **Payment Management**: Quản lý thanh toán, đối soát, hoàn tiền
- **Content Management**: Duyệt nội dung từ Producer và Cooperative
- **Complaint & Review Management**: Quản lý đánh giá và khiếu nại
- **Partner Contracts**: Quản lý hợp đồng đối tác vận hành
- **Media Management**: Upload và quản lý media files (AWS S3)
- **Dashboard**: API cho dashboard với thống kê realtime

## 📋 Yêu cầu

- Python 3.11+
- PostgreSQL (AWS RDS)
- pip hoặc poetry

## 🔧 Cài đặt Local

### 1. Clone repository

```bash
git clone https://github.com/quanworkingmbl/API_web_he_thong_and_app.git
cd Du_an_cms_API
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

Tạo file `.env` và điền các giá trị:

```env
# Database (AWS RDS PostgreSQL)
DATABASE_URL=postgresql://user:password@your-rds.amazonaws.com:5432/postgres?sslmode=require
DIRECT_URL=postgresql://user:password@your-rds.amazonaws.com:5432/postgres?sslmode=require
DB_SSL_CERT=/path/to/us-east-1-bundle.pem

# JWT
SECRET_KEY=your-super-secret-key-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# App
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=False

# API Secret Header
API_SECRET_KEY=VLU15122004

# CORS
CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:3000

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
```

### 5. Chạy database migrations

```bash
alembic upgrade head
```

### 6. Chạy ứng dụng local

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại: `http://localhost:8000`

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📁 Cấu trúc dự án

```
Du_an_cms_API/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── users.py          # User management
│   │       ├── roles.py          # Role management
│   │       ├── organizations.py  # Organization management
│   │       ├── dashboard.py      # Dashboard endpoints
│   │       ├── media.py          # Media upload/management (S3)
│   │       ├── products.py       # Product approval
│   │       ├── payments.py       # Payment management
│   │       ├── content.py        # Content management
│   │       ├── complaints.py     # Complaint & review
│   │       └── contracts.py      # Partner contracts
│   ├── core/
│   │   ├── config.py             # Configuration (pydantic settings)
│   │   ├── database.py           # Database setup (SQLAlchemy)
│   │   ├── middleware.py         # Custom middleware (ApiSecretMiddleware, LoggingMiddleware)
│   │   └── security.py           # JWT utilities
│   ├── models/                   # SQLAlchemy models
│   └── main.py                   # FastAPI app entry point
├── alembic/                      # Database migrations
├── global-bundle.pem             # AWS RDS SSL certificate
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Python version
└── README.md                     # This file
```

## 🔐 API Security

Tất cả API request (trừ `/`, `/health`, `/docs`, `/redoc`) đều **yêu cầu header**:

```
X-Quan-Secret: VLU15122004
Authorization: Bearer <jwt_token>
```

## 🔐 API Endpoints

### Authentication

- `POST /api/auth/register` - Đăng ký tài khoản
- `POST /api/auth/login` - Đăng nhập, trả về JWT token
- `GET /api/auth/me` - Lấy thông tin user hiện tại
- `POST /api/auth/logout` - Đăng xuất
- `POST /api/auth/refresh` - Refresh token
- `PUT /api/auth/profile` - Cập nhật profile

### Users

- `GET /api/users` - Danh sách users
- `POST /api/users` - Tạo user mới
- `PUT /api/users/{id}` - Cập nhật user

### Media (AWS S3)

- `GET /api/media` - Danh sách media
- `POST /api/media/upload` - Upload file lên S3

### Dashboard

- `GET /api/dashboard/stats` - Thống kê tổng quan

## ☁️ Deploy lên AWS EC2

### 1. Kết nối SSH vào EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Cập nhật `.env` trên server

```bash
nano /home/ubuntu/Du_an_cms_API/.env
```

### 3. Cài đặt dependencies & chạy

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

### 4. Chạy dưới dạng service (systemd)

```bash
sudo systemctl restart cms-api
sudo systemctl status cms-api
```

## 🔒 Security Notes

1. **SECRET_KEY**: Luôn dùng secret key mạnh (min 32 ký tự) trong production
2. **API_SECRET_KEY**: Header `X-Quan-Secret` bảo vệ toàn bộ API
3. **CORS**: Cấu hình đúng `CORS_ORIGINS` cho production domain
4. **Database**: Không commit credentials vào git
5. **HTTPS**: Cấu hình HTTPS qua AWS ALB/Nginx
6. **Rate Limiting**: Cân nhắc thêm rate limiting cho production

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
- Đảm bảo Security Group của RDS cho phép kết nối từ EC2
- Kiểm tra SSL cert: `DB_SSL_CERT` trỏ đúng đường dẫn

### Lỗi 403 Forbidden
- Request thiếu header `X-Quan-Secret: VLU15122004`

### Lỗi 401 Unauthorized
- Token JWT hết hạn hoặc không đúng format `Bearer <token>`

## 📚 Tài liệu tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

---

**Production URL**: `https://api.quancmsbe.site`
