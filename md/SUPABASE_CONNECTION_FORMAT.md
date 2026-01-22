# 🔌 Supabase Connection String Format

## ✅ Format Đúng cho Supabase

### DATABASE_URL (Cho Application - Connection Pooling)

```
DATABASE_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

**Đặc điểm:**
- ✅ Port **6543** - Connection pooling port
- ✅ `?pgbouncer=true` - Sử dụng PgBouncer cho connection pooling
- ✅ Tốt cho production app (giảm số lượng connections)
- ✅ Code tự động xử lý `pgbouncer=true` parameter

### DIRECT_URL (Cho Migrations - Direct Connection)

```
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

**Đặc điểm:**
- ✅ Port **5432** - Direct connection port
- ✅ Không có `pgbouncer=true` - Direct connection
- ✅ Tốt cho migrations (Alembic cần direct connection)
- ✅ Không bị giới hạn bởi connection pooling

## 📊 So sánh 2 Format

| Format | Port | PgBouncer | Mục đích | Khi nào dùng |
|--------|------|-----------|----------|--------------|
| **DATABASE_URL** | 6543 | ✅ Có | Connection Pooling | Application runtime |
| **DIRECT_URL** | 5432 | ❌ Không | Direct Connection | Migrations, Admin tasks |

## 🔍 Tại sao cần 2 format?

### 1. DATABASE_URL (Port 6543 với PgBouncer)
- **Ưu điểm**: 
  - Connection pooling giảm số lượng connections đến database
  - Tốt cho production với nhiều requests
  - Tối ưu performance
- **Nhược điểm**: 
  - Một số operations (như migrations) có thể bị giới hạn
  - Transaction mode có thể bị ảnh hưởng

### 2. DIRECT_URL (Port 5432)
- **Ưu điểm**: 
  - Direct connection, không qua pooling
  - Tốt cho migrations và admin tasks
  - Không bị giới hạn bởi pooling
- **Nhược điểm**: 
  - Tốn nhiều connections hơn
  - Không tối ưu cho high-traffic apps

## 💡 Code đã xử lý như thế nào?

### Trong `app/core/database.py`:
```python
def clean_database_url(url: str) -> str:
    """Remove pgbouncer parameter from connection string"""
    # Code tự động remove ?pgbouncer=true nếu có
    # Đảm bảo compatibility với cả 2 format
```

### Trong `alembic/env.py`:
```python
# Sử dụng DIRECT_URL cho migrations nếu có
# Nếu không có DIRECT_URL, dùng DATABASE_URL
db_url = settings.DIRECT_URL if settings.DIRECT_URL else settings.DATABASE_URL
db_url = clean_database_url(db_url)  # Remove pgbouncer parameter
```

## ✅ Format của bạn

Bạn đưa ra:
```
DATABASE_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:quanquadeptrai@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?pgbouncer=true

DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:quanquadeptrai@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
```

### Phân tích:

1. **DATABASE_URL** ✅ **ĐÚNG**
   - Port 6543 với pgbouncer=true
   - Phù hợp cho application runtime

2. **DIRECT_URL** ⚠️ **NÊN SỬA**
   - Hiện tại: Port 6543 (vẫn qua pooling)
   - **Nên**: Port 5432 (direct connection)

### Format khuyến nghị:

```
DATABASE_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:quanquadeptrai@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?pgbouncer=true

DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:quanquadeptrai@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

**Thay đổi**: Chỉ cần đổi port từ `6543` → `5432` trong DIRECT_URL

## 🧪 Test Connection

### Test DATABASE_URL:
```bash
python -c "
from app.core.config import settings
from app.core.database import engine
print('✅ DATABASE_URL connection successful!')
"
```

### Test DIRECT_URL:
```bash
python -c "
from app.core.config import settings
from sqlalchemy import create_engine
engine = create_engine(settings.DIRECT_URL)
with engine.connect() as conn:
    print('✅ DIRECT_URL connection successful!')
"
```

## 📝 Lấy Connection String từ Supabase

1. Đăng nhập [Supabase Dashboard](https://app.supabase.com)
2. Chọn project
3. Vào **Settings** → **Database**
4. Tìm **Connection string** section
5. Copy **Connection pooling** (port 6543) cho DATABASE_URL
6. Copy **Direct connection** (port 5432) cho DIRECT_URL

## ⚠️ Lưu ý

1. **Password**: Thay `[PASSWORD]` hoặc `quanquadeptrai` bằng password thực tế
2. **Security**: Không commit connection strings vào git
3. **Format**: Đảm bảo format đúng, không có spaces thừa
4. **Port**: 
   - 6543 = Connection pooling (cho app)
   - 5432 = Direct connection (cho migrations)

## 🔗 Tài liệu tham khảo

- [Supabase Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [PgBouncer Documentation](https://www.pgbouncer.org/)

