# 🚀 Railway Quick Start - Checklist Nhanh

Checklist ngắn gọn để deploy lên Railway trong 5 phút.

## ✅ Checklist Deploy

### 1. Chuẩn bị (2 phút)
- [ ] Đã push code lên GitHub
- [ ] Đã có tài khoản Railway (đăng ký tại railway.app)
- [ ] Đã có Supabase database credentials

### 2. Tạo Project trên Railway (1 phút)
- [ ] Login vào Railway
- [ ] Click "New Project"
- [ ] Chọn "Deploy from GitHub repo"
- [ ] Chọn repository của bạn
- [ ] Railway tự động bắt đầu build

### 3. Cấu hình Environment Variables (2 phút)

Vào **Variables** tab và thêm:

```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
SECRET_KEY=[TẠO_KEY_32_KÝ_TỰ]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend.com
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=False
```

**Tạo SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Chạy Migrations (1 phút)

Sau khi deploy xong, chạy migrations:

**Cách 1: Railway CLI**
```bash
railway login
railway link
railway run alembic upgrade head
```

**Cách 2: Railway Dashboard**
- Vào tab "Deployments" → Click deployment mới nhất
- Mở "Shell" và chạy: `alembic upgrade head`

### 5. Kiểm tra (1 phút)

Test các endpoints:
```bash
# Health check
curl https://your-project.railway.app/health

# Root endpoint
curl https://your-project.railway.app/
```

## 🎯 Kết quả mong đợi

- ✅ Build thành công (xanh trong Railway dashboard)
- ✅ Health endpoint trả về: `{"status": "healthy"}`
- ✅ Root endpoint trả về: `{"message": "CMS API", "version": "1.0.0"}`
- ✅ Logs không có lỗi

## ❌ Troubleshooting Nhanh

**Build fails?**
- Check logs trong Railway dashboard
- Kiểm tra `requirements.txt` đầy đủ

**App không start?**
- Kiểm tra tất cả environment variables đã set
- Check logs để xem lỗi cụ thể

**Database error?**
- Kiểm tra `DATABASE_URL` đúng format
- Test connection từ local trước

**CORS error?**
- Kiểm tra `CORS_ORIGINS` có chứa frontend domain
- Format: `https://domain.com` (không có trailing slash)

## 📚 Tài liệu chi tiết

Xem file `RAILWAY_DEPLOYMENT_GUIDE.md` để có hướng dẫn đầy đủ.

---

**Thời gian ước tính: 5-10 phút** ⏱️

