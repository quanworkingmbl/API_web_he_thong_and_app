# Hướng dẫn Setup Database với Supabase

## 📋 Bước 1: Tạo file .env

Tạo file `.env` trong thư mục `Du_an_cms_API`:

```bash
cd Du_an_cms_API
cp .env.example .env
```

## 🔧 Bước 2: Cấu hình Database URL

Mở file `.env` và cập nhật với thông tin Supabase của bạn:

```env
# Supabase Database Connection
# Thay [YOUR-PASSWORD] bằng password thực tế của bạn

# Connection pooling (recommended for production)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres

# Direct connection (for migrations)
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=True
```

### 🔑 Lấy thông tin từ Supabase:

1. Đăng nhập vào [Supabase Dashboard](https://app.supabase.com)
2. Chọn project của bạn
3. Vào **Settings** → **Database**
4. Copy **Connection string** (URI format)
5. Thay `[YOUR-PASSWORD]` bằng password của bạn

## 🧪 Bước 3: Test Connection

Chạy script test connection:

```bash
python test_db_connection.py
```

Kết quả mong đợi:
```
🔍 Testing database connection...
📊 Database URL: postgresql://postgres:***@db.bfzxkojszxxjbfisocwt...
✅ Connection successful!
📦 PostgreSQL version: PostgreSQL 15.x
🗄️  Connected to database: postgres
📋 Found X tables:
   - users
   - roles
   ...
```

Nếu có lỗi, kiểm tra:
- ✅ DATABASE_URL đã đúng format
- ✅ Password đã được thay thế
- ✅ Supabase database đang accessible
- ✅ Network/firewall không block connection

## 🗄️ Bước 4: Tạo Database Tables

### Option 1: Sử dụng Alembic (Recommended)

```bash
# Tạo migration đầu tiên
alembic revision --autogenerate -m "Initial migration"

# Chạy migration
alembic upgrade head
```

### Option 2: Sử dụng SQLAlchemy (Quick setup)

```bash
python setup_database.py
```

Script này sẽ:
- ✅ Test connection
- ✅ Tạo tất cả tables
- ✅ Tạo admin user mặc định (admin@example.com / admin123)

## ✅ Bước 5: Verify Setup

### Kiểm tra tables đã được tạo:

```bash
python test_db_connection.py
```

Bạn sẽ thấy danh sách tables đã được tạo.

### Test API:

```bash
# Start API server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test login (nếu đã tạo admin user)
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

## 🔍 Troubleshooting

### Lỗi: "Connection refused"

**Nguyên nhân**: Database URL không đúng hoặc Supabase không accessible

**Giải pháp**:
1. Kiểm tra DATABASE_URL trong .env
2. Verify Supabase project đang active
3. Check network connectivity

### Lỗi: "Authentication failed"

**Nguyên nhân**: Password không đúng

**Giải pháp**:
1. Reset password trong Supabase Dashboard
2. Cập nhật DATABASE_URL với password mới

### Lỗi: "Table already exists"

**Nguyên nhân**: Tables đã được tạo trước đó

**Giải pháp**:
- Nếu muốn reset: Drop tables và tạo lại
- Nếu muốn update: Sử dụng Alembic migrations

### Lỗi: "Module not found"

**Nguyên nhân**: Chưa cài đặt dependencies

**Giải pháp**:
```bash
pip install -r requirements.txt
```

## 📝 Notes

1. **DATABASE_URL vs DIRECT_URL**:
   - `DATABASE_URL`: Dùng cho connection pooling (production)
   - `DIRECT_URL`: Dùng cho migrations và direct connections

2. **Security**:
   - ⚠️ Không commit file `.env` vào git
   - ⚠️ Thay đổi SECRET_KEY trong production
   - ⚠️ Thay đổi admin password sau khi setup

3. **Migrations**:
   - Luôn sử dụng Alembic cho production
   - Không edit migrations đã được chạy
   - Backup database trước khi chạy migrations

## 🚀 Next Steps

Sau khi setup database thành công:

1. ✅ Test tất cả API endpoints
2. ✅ Tạo users, roles, permissions
3. ✅ Setup initial data
4. ✅ Deploy lên Railway

## 📚 Tài liệu tham khảo

- [Supabase Documentation](https://supabase.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

