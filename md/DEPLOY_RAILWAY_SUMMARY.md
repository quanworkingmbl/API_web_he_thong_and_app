# 📋 Tóm tắt: Deploy lên Railway

## 🎯 Tổng quan

Dự án của bạn đã được cấu hình sẵn để deploy lên Railway. Bạn chỉ cần làm theo các bước sau:

## 📁 Files đã được cấu hình sẵn

✅ **railway.json** - Cấu hình build và deploy  
✅ **Procfile** - Start command với gunicorn (2 workers)  
✅ **runtime.txt** - Python 3.11.0  
✅ **requirements.txt** - Tất cả dependencies  
✅ **.railwayignore** - Loại trừ files không cần thiết  

## 🚀 5 Bước Deploy

### Bước 1: Đăng ký và Login Railway
1. Truy cập https://railway.app
2. Đăng nhập bằng GitHub (khuyến nghị)

### Bước 2: Tạo Project mới
1. Click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Chọn repository của bạn
4. Railway tự động detect Python và bắt đầu build

### Bước 3: Cấu hình Environment Variables

Vào tab **"Variables"** và thêm các biến sau:

#### Bắt buộc:
```
DATABASE_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?pgbouncer=true
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
SECRET_KEY=[TẠO_KEY_32_KÝ_TỰ]
```

**Lưu ý**: 
- `DATABASE_URL` dùng port **6543** với pgbouncer (connection pooling)
- `DIRECT_URL` dùng port **5432** (direct connection cho migrations)

#### Khuyến nghị:
```
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend-domain.com
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=False
```

**Tạo SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Bước 4: Chạy Database Migrations

Sau khi deploy thành công, chạy migrations:

**Option 1: Railway CLI (Khuyến nghị)**
```bash
# Cài Railway CLI (nếu chưa có)
npm i -g @railway/cli

# Login và link project
railway login
railway link

# Chạy migrations
railway run alembic upgrade head
```

**Option 2: Railway Dashboard**
- Vào tab "Deployments" → Click deployment mới nhất
- Mở "Shell" → Chạy: `alembic upgrade head`

### Bước 5: Kiểm tra

Test các endpoints:
```bash
# Health check
curl https://your-project.railway.app/health
# Kết quả: {"status": "healthy"}

# Root endpoint
curl https://your-project.railway.app/
# Kết quả: {"message": "CMS API", "version": "1.0.0"}
```

## 📝 Checklist

- [ ] Code đã push lên GitHub
- [ ] Đã tạo project trên Railway
- [ ] Đã kết nối GitHub repository
- [ ] Đã thêm tất cả environment variables
- [ ] Build thành công (xanh trong dashboard)
- [ ] Đã chạy migrations: `alembic upgrade head`
- [ ] Health endpoint trả về `{"status": "healthy"}`
- [ ] Test authentication endpoint hoạt động

## 🔍 Xem Logs

1. Vào Railway dashboard
2. Chọn project
3. Tab **"Deployments"** → Click deployment
4. Tab **"Logs"** để xem logs real-time

## 🌐 Custom Domain (Tùy chọn)

1. Vào **Settings** → **Networking**
2. Click **"Custom Domain"**
3. Nhập domain của bạn
4. Thêm CNAME record trong DNS provider
5. Cập nhật `CORS_ORIGINS` với domain mới

## ⚠️ Lưu ý quan trọng

1. **SECRET_KEY**: Phải là key mạnh, tối thiểu 32 ký tự
2. **DEBUG**: Đặt `False` trong production để ẩn API docs
3. **CORS_ORIGINS**: Phải chứa domain frontend thực tế
4. **Database**: Đảm bảo Supabase cho phép connection từ external IPs
5. **Migrations**: Luôn chạy migrations sau khi deploy

## 📚 Tài liệu chi tiết

- **Hướng dẫn đầy đủ**: Xem `RAILWAY_DEPLOYMENT_GUIDE.md`
- **Quick Start**: Xem `RAILWAY_QUICK_START.md`
- **Troubleshooting**: Xem phần Troubleshooting trong `RAILWAY_DEPLOYMENT_GUIDE.md`

## 🆘 Hỗ trợ

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check logs trong Railway dashboard để debug

---

**Thời gian deploy: ~5-10 phút** ⏱️

**Chúc bạn deploy thành công! 🚀**

