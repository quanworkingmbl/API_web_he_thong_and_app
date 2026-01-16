# Deployment Checklist - Railway

## ✅ Pre-Deployment Checklist

### 1. Code Quality
- [x] Cấu trúc dự án theo best practices
- [x] Type hints và docstrings đầy đủ
- [x] Error handling đã được implement
- [x] Logging đã được setup
- [x] CORS đã được cấu hình đúng

### 2. Security
- [x] SECRET_KEY đã được thay đổi (không dùng default)
- [x] Database credentials không được commit vào git
- [x] Environment variables đã được tách ra .env
- [x] CORS_ORIGINS chỉ chứa trusted domains
- [x] DEBUG=False trong production
- [x] API docs được ẩn trong production

### 3. Database
- [x] Database models đã được định nghĩa
- [x] Alembic migrations đã được setup
- [x] Database connection string đã được cấu hình
- [ ] Initial migration đã được tạo và test
- [ ] Database indexes đã được tối ưu (nếu cần)

### 4. API Endpoints
- [x] Authentication endpoints
- [x] User management endpoints
- [x] Role & Permission endpoints
- [x] Product approval endpoints
- [x] Payment management endpoints
- [x] Content management endpoints
- [x] Complaint & Review endpoints
- [x] Partner contract endpoints
- [x] Media upload endpoints
- [x] Dashboard & Stats endpoints

### 5. Railway Configuration
- [x] Procfile đã được tạo
- [x] railway.json đã được cấu hình
- [x] runtime.txt đã được set
- [x] requirements.txt đã được cập nhật

### 6. Frontend Integration
- [x] API client đã được cập nhật với Bearer token
- [x] .env.example đã được tạo
- [x] Environment variables đã được document

## 🚀 Deployment Steps

### Step 1: Push to GitHub
```bash
cd Du_an_cms_API
git add .
git commit -m "feat: Production-ready FastAPI backend"
git push origin main
```

### Step 2: Railway Setup
1. Tạo project trên Railway
2. Connect GitHub repository
3. Railway sẽ auto-detect Python project

### Step 3: Environment Variables
Thêm các biến sau trong Railway dashboard:

```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.bfzxkojszxxjbfisocwt.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres.bfzxkojszxxjbfisocwt:[PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
SECRET_KEY=[GENERATE_STRONG_SECRET_KEY]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend-domain.com
APP_NAME=CMS API
APP_VERSION=1.0.0
DEBUG=False
```

### Step 4: Run Migrations
```bash
railway run alembic upgrade head
```

### Step 5: Verify Deployment
1. Check Railway logs
2. Test health endpoint: `https://your-domain.railway.app/health`
3. Test API docs (should be hidden in production if DEBUG=False)
4. Test authentication endpoint

### Step 6: Update Frontend
1. Update `.env.production` với Railway API URL
2. Build và deploy frontend
3. Test integration

## 🔍 Post-Deployment Verification

### API Health Check
```bash
curl https://your-domain.railway.app/health
# Expected: {"status": "healthy"}
```

### Authentication Test
```bash
curl -X POST https://your-domain.railway.app/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'
```

### CORS Test
- Test từ frontend domain
- Verify CORS headers trong response

## 📊 Monitoring

### Railway Metrics
- CPU usage
- Memory usage
- Network traffic
- Request logs

### Application Logs
- Check Railway logs dashboard
- Monitor error rates
- Check response times

## 🔧 Troubleshooting

### Build Fails
- Check Railway logs
- Verify requirements.txt
- Check Python version in runtime.txt

### Database Connection Errors
- Verify DATABASE_URL format
- Check Supabase database status
- Verify network connectivity

### CORS Errors
- Check CORS_ORIGINS configuration
- Verify frontend domain matches
- Check browser console for details

### Authentication Issues
- Verify SECRET_KEY is set
- Check token expiration
- Verify Bearer token format in requests

## 📝 Notes

- Railway tự động rebuild khi có commit mới
- Database migrations nên chạy sau mỗi deploy nếu có thay đổi schema
- Monitor logs trong 24h đầu để catch issues sớm
- Setup alerts cho error rates và response times

