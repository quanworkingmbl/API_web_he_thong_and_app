# 🚂 Hướng dẫn Deploy lên Railway

Hướng dẫn chi tiết từng bước để deploy dự án CMS API lên Railway.

## 📋 Mục lục

1. [Chuẩn bị](#chuẩn-bị)
2. [Tạo tài khoản Railway](#tạo-tài-khoản-railway)
3. [Kết nối GitHub Repository](#kết-nối-github-repository)
4. [Cấu hình Environment Variables](#cấu-hình-environment-variables)
5. [Chạy Database Migrations](#chạy-database-migrations)
6. [Kiểm tra Deployment](#kiểm-tra-deployment)
7. [Cấu hình Custom Domain (Tùy chọn)](#cấu-hình-custom-domain-tùy-chọn)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Chuẩn bị

### Yêu cầu trước khi deploy:

- [x] Dự án đã được push lên GitHub
- [x] Database (Supabase) đã được setup và có credentials
- [x] Đã có file `.env` với các biến môi trường cần thiết
- [x] Đã test ứng dụng chạy được ở local

### Files đã được cấu hình sẵn:

- ✅ `railway.json` - Cấu hình build và deploy
- ✅ `Procfile` - Start command cho Railway
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Dependencies
- ✅ `.railwayignore` - Files không cần deploy

---

## 1️⃣ Tạo tài khoản Railway

1. Truy cập [railway.app](https://railway.app)
2. Click **"Login"** hoặc **"Get Started"**
3. Đăng nhập bằng GitHub account (khuyến nghị) hoặc email
4. Xác thực tài khoản nếu cần

---

## 2️⃣ Kết nối GitHub Repository

### Cách 1: Tạo Project mới từ GitHub

1. Trong Railway dashboard, click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Authorize Railway truy cập GitHub repositories (nếu chưa)
4. Chọn repository `Du_an_cms_API` hoặc repository của bạn
5. Railway sẽ tự động detect Python project và bắt đầu build

### Cách 2: Sử dụng Railway CLI

```bash
# Cài đặt Railway CLI (nếu chưa có)
npm i -g @railway/cli

# Login vào Railway
railway login

# Link project với repository
railway link

# Deploy
railway up
```

---

## 3️⃣ Cấu hình Environment Variables

Sau khi Railway đã detect project, bạn cần cấu hình các biến môi trường:

### Bước 1: Mở Variables tab

1. Trong Railway dashboard, chọn project vừa tạo
2. Click vào tab **"Variables"** hoặc **"Settings" → "Variables"**

### Bước 2: Thêm các biến môi trường

Thêm các biến sau (click **"New Variable"** cho mỗi biến):

#### Database Configuration
```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres
```

```
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

**Lưu ý**: Thay `[YOUR-PASSWORD]` bằng password thực tế của Supabase database

#### JWT Configuration
```
SECRET_KEY=your-very-secure-secret-key-minimum-32-characters-long
```

**Tạo SECRET_KEY mạnh:**
```bash
# Trên Linux/Mac
openssl rand -hex 32

# Hoặc sử dụng Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

```
ALGORITHM=HS256
```

```
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### CORS Configuration
```
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

**Lưu ý**: 
- Thay bằng domain frontend thực tế của bạn
- Nếu chưa có domain, có thể dùng Railway domain tạm thời
- Có thể thêm nhiều origins, cách nhau bằng dấu phẩy

#### Application Configuration
```
APP_NAME=CMS API
```

```
APP_VERSION=1.0.0
```

```
DEBUG=False
```

**Quan trọng**: Đặt `DEBUG=False` trong production để ẩn API docs và tăng bảo mật

### Bước 3: Lưu và Redeploy

Sau khi thêm tất cả biến môi trường:
1. Railway sẽ tự động redeploy khi có thay đổi variables
2. Hoặc click **"Redeploy"** trong tab **"Deployments"**

---

## 4️⃣ Chạy Database Migrations

Sau khi deploy thành công, cần chạy database migrations:

### Cách 1: Sử dụng Railway CLI

```bash
# Login vào Railway
railway login

# Link với project
railway link

# Chạy migrations
railway run alembic upgrade head
```

### Cách 2: Sử dụng Railway Dashboard

1. Vào tab **"Deployments"**
2. Click vào deployment mới nhất
3. Mở **"View Logs"**
4. Trong tab **"Shell"**, chạy:
```bash
alembic upgrade head
```

### Cách 3: Sử dụng Railway Service

1. Trong Railway dashboard, vào **"Settings"**
2. Tìm **"Service Commands"** hoặc **"Run Command"**
3. Chạy: `alembic upgrade head`

---

## 5️⃣ Kiểm tra Deployment

### Bước 1: Kiểm tra Logs

1. Vào tab **"Deployments"** trong Railway dashboard
2. Click vào deployment mới nhất
3. Xem logs để đảm bảo không có lỗi
4. Tìm dòng: `Application startup complete` hoặc `Uvicorn running on...`

### Bước 2: Test Health Endpoint

Railway sẽ cung cấp một domain tự động (ví dụ: `your-project.railway.app`)

Test health endpoint:
```bash
curl https://your-project.railway.app/health
```

Kết quả mong đợi:
```json
{"status": "healthy"}
```

### Bước 3: Test Root Endpoint

```bash
curl https://your-project.railway.app/
```

Kết quả mong đợi:
```json
{"message": "CMS API", "version": "1.0.0"}
```

### Bước 4: Test API Documentation

**Lưu ý**: Nếu `DEBUG=False`, API docs sẽ bị ẩn. Để test, tạm thời đặt `DEBUG=True`

```bash
# Nếu DEBUG=True
curl https://your-project.railway.app/docs
```

### Bước 5: Test Authentication

```bash
curl -X POST https://your-project.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}'
```

---

## 6️⃣ Cấu hình Custom Domain (Tùy chọn)

### Bước 1: Thêm Domain trong Railway

1. Vào **"Settings" → "Networking"**
2. Click **"Custom Domain"**
3. Nhập domain của bạn (ví dụ: `api.yourdomain.com`)
4. Railway sẽ cung cấp DNS records cần thêm

### Bước 2: Cấu hình DNS

Thêm CNAME record trong DNS provider của bạn:
- **Type**: CNAME
- **Name**: `api` (hoặc subdomain bạn muốn)
- **Value**: Domain mà Railway cung cấp (ví dụ: `your-project.railway.app`)

### Bước 3: Cập nhật CORS_ORIGINS

Sau khi domain đã active, cập nhật biến môi trường:
```
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Bước 4: Chờ SSL Certificate

Railway tự động cung cấp SSL certificate (Let's Encrypt). Chờ vài phút để certificate được cấp.

---

## 7️⃣ Monitoring và Logs

### Xem Logs Real-time

1. Vào tab **"Deployments"**
2. Click vào deployment
3. Tab **"Logs"** sẽ hiển thị logs real-time

### Metrics

Railway cung cấp metrics trong dashboard:
- CPU Usage
- Memory Usage
- Network Traffic
- Request Count

### Alerts

Có thể setup alerts cho:
- High error rates
- High memory usage
- Deployment failures

---

## 🔧 Troubleshooting

### ❌ Build Fails

**Nguyên nhân có thể:**
- Thiếu dependencies trong `requirements.txt`
- Python version không đúng
- Lỗi syntax trong code

**Giải pháp:**
1. Kiểm tra logs trong Railway dashboard
2. Test build local: `pip install -r requirements.txt`
3. Kiểm tra `runtime.txt` có đúng Python version
4. Kiểm tra code không có lỗi syntax

### ❌ Application không start

**Nguyên nhân có thể:**
- Thiếu environment variables
- Database connection failed
- Port không đúng

**Giải pháp:**
1. Kiểm tra tất cả environment variables đã được set
2. Kiểm tra `DATABASE_URL` đúng format
3. Kiểm tra logs để xem lỗi cụ thể
4. Đảm bảo `Procfile` đúng format

### ❌ Database Connection Error

**Nguyên nhân có thể:**
- `DATABASE_URL` sai format
- Database không accessible từ Railway
- Firewall blocking connection

**Giải pháp:**
1. Kiểm tra `DATABASE_URL` format:
   ```
   postgresql://user:password@host:port/database
   ```
2. Kiểm tra Supabase database đang chạy
3. Kiểm tra Supabase có cho phép connection từ external IPs
4. Test connection từ local trước

### ❌ CORS Errors

**Nguyên nhân có thể:**
- `CORS_ORIGINS` không chứa frontend domain
- Domain không match chính xác

**Giải pháp:**
1. Kiểm tra `CORS_ORIGINS` có chứa frontend domain
2. Đảm bảo format đúng: `https://domain.com` (không có trailing slash)
3. Thêm `http://localhost:3000` nếu test local
4. Kiểm tra browser console để xem lỗi CORS chi tiết

### ❌ Migrations không chạy

**Nguyên nhân có thể:**
- Database chưa được tạo
- Connection string sai
- Models chưa được import trong `alembic/env.py`

**Giải pháp:**
1. Kiểm tra database connection
2. Kiểm tra `alembic/env.py` có import tất cả models
3. Chạy migrations local trước để test
4. Kiểm tra logs khi chạy migrations

### ❌ 502 Bad Gateway

**Nguyên nhân có thể:**
- Application crash
- Port không đúng
- Timeout

**Giải pháp:**
1. Kiểm tra logs để xem application có đang chạy
2. Đảm bảo application listen trên `0.0.0.0` và port `$PORT`
3. Kiểm tra `Procfile` đúng format
4. Restart service trong Railway

---

## 📝 Checklist sau khi Deploy

- [ ] Application đã start thành công (check logs)
- [ ] Health endpoint trả về `{"status": "healthy"}`
- [ ] Database migrations đã chạy thành công
- [ ] Test authentication endpoint hoạt động
- [ ] CORS đã được cấu hình đúng
- [ ] Custom domain đã được setup (nếu có)
- [ ] SSL certificate đã được cấp (nếu có custom domain)
- [ ] Environment variables đã được set đầy đủ
- [ ] `DEBUG=False` trong production
- [ ] API docs đã bị ẩn (nếu `DEBUG=False`)
- [ ] Monitoring và alerts đã được setup

---

## 🔄 Auto-deploy từ GitHub

Railway tự động deploy khi có push mới vào branch được kết nối:

1. Push code lên GitHub
2. Railway tự động detect changes
3. Tự động build và deploy
4. Có thể xem progress trong Railway dashboard

### Disable Auto-deploy (nếu cần)

1. Vào **"Settings" → "Source"**
2. Tắt **"Auto Deploy"**

---

## 💡 Tips và Best Practices

1. **Environment Variables**: Luôn sử dụng Railway Variables thay vì hardcode
2. **Secrets**: Không commit secrets vào git, luôn dùng Railway Variables
3. **Database**: Sử dụng connection pooling cho production
4. **Logging**: Sử dụng structured logging để dễ debug
5. **Monitoring**: Setup alerts sớm để catch issues
6. **Backup**: Đảm bảo database có backup strategy
7. **Testing**: Test kỹ ở staging environment trước khi deploy production
8. **Rollback**: Railway cho phép rollback về deployment cũ nếu có vấn đề

---

## 📞 Hỗ trợ

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

---

**Chúc bạn deploy thành công! 🚀**

