# 🚀 Quick Start - Connect Supabase Database

## ⚡ Các bước nhanh

### 1. Tạo file .env

```bash
cd Du_an_cms_API
cp .env.example .env
```

### 2. Cập nhật DATABASE_URL

Mở file `.env` và thay `[YOUR-PASSWORD]` bằng password Supabase của bạn:

```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:YOUR_ACTUAL_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

### 3. Test Connection

```bash
python test_db_connection.py
```

Nếu thành công, bạn sẽ thấy:
```
✅ Connection successful!
📦 PostgreSQL version: PostgreSQL 15.x
🗄️  Connected to database: postgres
```

### 4. Tạo Tables

```bash
# Option 1: Sử dụng Alembic (Recommended)
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Option 2: Quick setup (tạo tables + admin user)
python setup_database.py
```

### 5. Start API

```bash
uvicorn app.main:app --reload
```

API sẽ chạy tại: `http://localhost:8000`

## ✅ Verify

1. **Test health endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test login** (nếu đã tạo admin):
   ```bash
   curl -X POST http://localhost:8000/api/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "admin123"}'
   ```

3. **Check API docs**:
   - Mở browser: `http://localhost:8000/docs`

## 🔍 Troubleshooting

### Connection Failed?

1. ✅ Kiểm tra DATABASE_URL đã đúng format
2. ✅ Verify password đã được thay thế
3. ✅ Check Supabase project đang active
4. ✅ Test connection từ Supabase dashboard

### Tables Not Created?

1. ✅ Chạy `alembic upgrade head`
2. ✅ Hoặc chạy `python setup_database.py`
3. ✅ Check logs để xem lỗi cụ thể

## 📚 Chi tiết hơn

Xem `DATABASE_SETUP.md` để biết hướng dẫn chi tiết.

