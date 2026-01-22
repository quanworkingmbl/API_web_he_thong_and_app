# 🚀 Hướng dẫn Chạy Local

## 📋 Yêu cầu

- Python 3.11+
- Virtual environment đã được tạo và activate
- Dependencies đã được cài đặt
- File `.env` đã được cấu hình

## 🔧 Cài đặt Dependencies

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## 🚀 Cách 1: Sử dụng run.py (Khuyến nghị)

```bash
python run.py
```

**Ưu điểm:**
- ✅ Đơn giản nhất
- ✅ Tự động reload khi có thay đổi code
- ✅ Đã được cấu hình sẵn

## 🚀 Cách 2: Sử dụng uvicorn trực tiếp

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Các options:**
- `--reload`: Tự động reload khi code thay đổi (development)
- `--host 0.0.0.0`: Cho phép truy cập từ mọi IP
- `--port 8000`: Chạy trên port 8000

## 🌐 Truy cập API

Sau khi chạy, API sẽ available tại:

- **API Base URL**: `http://localhost:8000`
- **API Documentation (Swagger)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **Root Endpoint**: `http://localhost:8000/`

## 🧪 Test API

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

Kết quả mong đợi:
```json
{"status": "healthy"}
```

### Test Root Endpoint
```bash
curl http://localhost:8000/
```

Kết quả mong đợi:
```json
{"message": "CMS API", "version": "1.0.0"}
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}'
```

## ⚙️ Cấu hình Environment Variables

Đảm bảo file `.env` có các biến sau:

```env
DATABASE_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?pgbouncer=true
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=True
```

## 🗄️ Chạy Database Migrations

Trước khi chạy API lần đầu, cần chạy migrations:

```bash
alembic upgrade head
```

## 🔍 Troubleshooting

### Lỗi: Module not found

**Nguyên nhân**: Chưa activate virtual environment hoặc chưa cài dependencies

**Giải pháp**:
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Cài dependencies
pip install -r requirements.txt
```

### Lỗi: Database connection failed

**Nguyên nhân**: `DATABASE_URL` không đúng hoặc database không accessible

**Giải pháp**:
1. Kiểm tra file `.env` có đúng format không
2. Verify Supabase database đang chạy
3. Test connection: `python -c "from app.core.database import engine; print('OK')"`

### Lỗi: Port already in use

**Nguyên nhân**: Port 8000 đã được sử dụng bởi process khác

**Giải pháp**:
```bash
# Windows: Tìm process sử dụng port 8000
netstat -ano | findstr :8000

# Kill process (thay PID bằng process ID)
taskkill /PID <PID> /F

# Hoặc chạy trên port khác
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Lỗi: Import errors

**Nguyên nhân**: PYTHONPATH không đúng

**Giải pháp**:
```bash
# Chạy từ root directory của project
cd Du_an_cms_API
python run.py
```

## 📝 Các lệnh hữu ích khác

### Chạy với workers (Production-like)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Chạy không reload (Production mode)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Chạy với log level debug
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### Chạy migrations
```bash
# Upgrade to latest
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback
alembic downgrade -1
```

## 🎯 Quick Start Checklist

- [ ] Virtual environment đã được activate
- [ ] Dependencies đã được cài: `pip install -r requirements.txt`
- [ ] File `.env` đã được tạo và cấu hình
- [ ] Database migrations đã chạy: `alembic upgrade head`
- [ ] Chạy server: `python run.py`
- [ ] Test health endpoint: `curl http://localhost:8000/health`
- [ ] Mở browser: `http://localhost:8000/docs`

---

**Chúc bạn code vui vẻ! 🚀**

