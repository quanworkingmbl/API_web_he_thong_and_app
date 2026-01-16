# Hướng dẫn Deploy lên Railway

## 📋 Bước 1: Chuẩn bị Repository

1. Đảm bảo code đã được push lên GitHub:
   ```bash
   git add .
   git commit -m "Initial FastAPI setup"
   git push origin main
   ```

## 🚂 Bước 2: Tạo Project trên Railway

1. Đăng nhập vào [Railway](https://railway.app)
2. Click **"New Project"**
3. Chọn **"Deploy from GitHub repo"**
4. Chọn repository: `quanworkingmbl/API_web_he_thong_and_app`
5. Railway sẽ tự động detect Python project

## ⚙️ Bước 3: Cấu hình Environment Variables

Trong Railway dashboard, vào **Settings → Variables**, thêm các biến sau:

### Database Configuration
```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

**Lưu ý**: Thay `[YOUR-PASSWORD]` bằng password thực tế của Supabase database.

### JWT Configuration
```
SECRET_KEY=your-very-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Lưu ý**: Tạo SECRET_KEY mạnh (ít nhất 32 ký tự). Có thể dùng:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### CORS Configuration
```
CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
```

Thay `https://your-frontend-domain.com` bằng domain của frontend khi deploy production.

### Application Configuration
```
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=False
```

## 🗄️ Bước 4: Setup Database

### Option 1: Chạy migrations qua Railway CLI

1. Cài đặt Railway CLI:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. Link project:
   ```bash
   railway link
   ```

3. Chạy migrations:
   ```bash
   railway run alembic upgrade head
   ```

### Option 2: Chạy migrations qua Railway Dashboard

1. Vào **Deployments** tab
2. Click vào deployment mới nhất
3. Mở **Shell**
4. Chạy:
   ```bash
   alembic upgrade head
   ```

## 🔧 Bước 5: Kiểm tra Build

Railway sẽ tự động:
- Detect Python từ `runtime.txt`
- Install dependencies từ `requirements.txt`
- Chạy start command từ `Procfile`

Kiểm tra logs để đảm bảo build thành công.

## 🌐 Bước 6: Cấu hình Domain

### Public Domain (Railway tự động tạo)

1. Vào **Settings → Networking**
2. Railway đã tự động tạo public domain
3. Copy domain này

### Custom Domain (Optional)

1. Vào **Settings → Networking**
2. Click **"Custom Domain"**
3. Thêm domain của bạn
4. Cấu hình DNS records theo hướng dẫn
5. Cập nhật `CORS_ORIGINS` với domain mới

## ✅ Bước 7: Verify Deployment

1. Truy cập: `https://your-railway-domain.railway.app/docs`
2. Kiểm tra API documentation
3. Test endpoint `/health`:
   ```bash
   curl https://your-railway-domain.railway.app/health
   ```

## 🔄 Bước 8: Update Frontend

Cập nhật `VITE_APP_BASE_API` trong frontend `.env`:

```env
VITE_APP_BASE_API=https://your-railway-domain.railway.app/api
```

## 📊 Monitoring

Railway cung cấp:
- **Logs**: Realtime logs trong dashboard
- **Metrics**: CPU, Memory, Network usage
- **Deploy History**: Lịch sử các lần deploy

## 🐛 Troubleshooting

### Build fails

- Kiểm tra logs trong Railway dashboard
- Đảm bảo `requirements.txt` đúng format
- Kiểm tra Python version trong `runtime.txt`

### Database connection errors

- Kiểm tra `DATABASE_URL` đúng format
- Đảm bảo Supabase database đang accessible
- Kiểm tra firewall/network settings

### Application crashes

- Kiểm tra logs trong Railway dashboard
- Đảm bảo tất cả environment variables đã được set
- Kiểm tra database migrations đã chạy

### CORS errors

- Cập nhật `CORS_ORIGINS` với đúng frontend domain
- Đảm bảo không có trailing slash trong CORS_ORIGINS

## 🔒 Security Checklist

- [ ] SECRET_KEY đã được thay đổi (không dùng default)
- [ ] Database password không được commit vào git
- [ ] CORS_ORIGINS chỉ chứa trusted domains
- [ ] DEBUG=False trong production
- [ ] HTTPS được enable (Railway tự động)

## 📝 Notes

- Railway tự động rebuild khi có commit mới
- Railway tự động scale dựa trên traffic
- Railway cung cấp free tier với giới hạn nhất định
- Database migrations nên chạy sau mỗi lần deploy nếu có thay đổi schema

## 🆘 Support

Nếu gặp vấn đề:
1. Kiểm tra Railway logs
2. Kiểm tra Railway documentation: https://docs.railway.app
3. Kiểm tra FastAPI documentation: https://fastapi.tiangolo.com

