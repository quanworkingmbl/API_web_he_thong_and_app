# CMS API — FastAPI Backend

REST API backend cho **Agrarian Platform** — nền tảng thương mại điện tử multi-seller (nông sản sạch & làng nghề Việt Nam).

**Stack:** FastAPI + SQLAlchemy + PostgreSQL (Cloud SQL) · Deploy: Cloud Run

| Liên kết | URL |
|---|---|
| Production API | `https://api.quancmsbe.site` |
| Swagger | `https://api.quancmsbe.site/docs` |
| CMS Web (client) | `UI_CMS/UI_web_he_thong_and` |
| Mobile App (client) | `App/agrarian_app` |

> **Bảo mật:** Không commit file `.env`, service account JSON, hay password DB. Xin giá trị thật từ team lead.

---

## Yêu cầu hệ thống

| Công cụ | Phiên bản |
|---|---|
| Python | 3.11+ |
| PostgreSQL | 14+ (local hoặc Cloud SQL) |
| pip + venv | — |
| gcloud CLI | Tuỳ chọn (deploy GCP) |
| Docker | Tuỳ chọn (build image local) |

---

## Bạn cần có gì trước khi setup?

### 1. File & quyền truy cập (xin team lead)

| Hạng mục | Mục đích |
|---|---|
| File `.env` hoặc danh sách biến môi trường | Chạy local |
| PostgreSQL connection string | Database local hoặc Cloud SQL dev |
| `API_SECRET_KEY` | Header `X-Quan-Secret` — **phải khớp CMS Web & Mobile App** |
| `SECRET_KEY`, `REFRESH_TOKEN_SECRET_KEY` | JWT signing |
| VNPay sandbox (`VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET`) | Test thanh toán |
| GHN token (`GHN_TOKEN`, `GHN_SHOP_ID`) | Test vận chuyển |
| GCS bucket name + SA JSON | Upload media (`GOOGLE_APPLICATION_CREDENTIALS`) |
| Vertex AI project + SA | AI moderation / generate (tuỳ chọn local) |
| reCAPTCHA secret key | Login CMS (production) |
| Resend API key + Redis URL | Email OTP (tuỳ chọn) |

### 2. Quyền GCP (nếu deploy / debug production)

- Project backend trên GCP (xem `cloudbuild.yaml` → `_PROJECT`)
- Cloud SQL, Cloud Run, Secret Manager, Artifact Registry, Cloud Build

---

## Cài đặt local

### Bước 1 — Clone & virtualenv

```bash
cd Du_an_cms_API
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Bước 2 — Tạo file `.env`

Tạo `.env` tại root repo. **Không commit file này.**

Danh sách biến đầy đủ nằm trong `app/core/config.py`. Template mẫu:

```env
# ─── Database ───
DATABASE_URL=postgresql://<USER>:<PASSWORD>@localhost:5432/cms_db
DIRECT_URL=postgresql://<USER>:<PASSWORD>@localhost:5432/cms_db

# ─── JWT / Auth ───
SECRET_KEY=<YOUR_JWT_SECRET_MIN_32_CHARS>
REFRESH_TOKEN_SECRET_KEY=<YOUR_REFRESH_SECRET>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── App ───
APP_NAME=CMS API
DEBUG=True
SHOW_DOCS=True

# ─── API Secret (header X-Quan-Secret) ───
API_SECRET_KEY=<YOUR_API_SECRET>

# ─── CORS ───
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ─── Google Cloud Storage ───
GCS_BUCKET_NAME=<YOUR_MEDIA_BUCKET>

# ─── VNPay sandbox ───
VNPAY_TMN_CODE=<VNPAY_TMN>
VNPAY_HASH_SECRET=<VNPAY_HASH>
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:8000/api/payments/vnpay/return
VNPAY_IPN_URL=http://localhost:8000/api/payments/vnpay/ipn

# ─── GHN Shipping ───
GHN_TOKEN=<GHN_TOKEN>
GHN_SHOP_ID=<GHN_SHOP_ID>
GHN_URL=https://dev-online-gateway.ghn.vn/shiip/public-api

# ─── Vertex AI (tuỳ chọn) ───
VERTEX_PROJECT_ID=<GCP_PROJECT_ID>
VERTEX_LOCATION=asia-southeast1
GOOGLE_APPLICATION_CREDENTIALS=<PATH_TO_SA_JSON>

# ─── reCAPTCHA (dev: có thể tắt) ───
RECAPTCHA_ENABLED=False
RECAPTCHA_SECRET_KEY=<RECAPTCHA_SECRET>
RECAPTCHA_BYPASS_ENABLED=True
RECAPTCHA_BYPASS_CLIENTS=mobile,postman

# ─── Email OTP / Redis (tuỳ chọn) ───
RESEND_API_KEY=<RESEND_KEY>
REDIS_URL=redis://localhost:6379/0
```

### Bước 3 — Migration & chạy server

```bash
alembic upgrade head
python run.py
```

| Endpoint | URL |
|---|---|
| API | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

### Bước 4 — Test nhanh

Mọi request (trừ `/`, `/health`, `/docs`, `/redoc`) cần header:

```http
X-Quan-Secret: <API_SECRET_KEY>
Authorization: Bearer <jwt_token>   # endpoints cần auth
```

---

## Kết nối với CMS Web & Mobile App

| Client | Cấu hình cần khớp backend |
|---|---|
| CMS Web | `VITE_APP_API_SECRET` = `API_SECRET_KEY` |
| Mobile App | `--dart-define=API_SECRET=<API_SECRET_KEY>` |
| Mobile (local API) | `--dart-define=API_BASE_URL=http://10.0.2.2:8000/api` |

Backend local: thêm `http://localhost:3000` vào `CORS_ORIGINS`.

---

## Cấu trúc dự án (rút gọn)

```
Du_an_cms_API/
├── app/
│   ├── main.py              Entry point
│   ├── api/v1/              28 router modules
│   ├── core/                config, database, security, middleware
│   ├── models/              34+ SQLAlchemy models
│   └── services/            business logic, VNPay, GHN, FCM, AI
├── alembic/                 migrations
├── cloudbuild.yaml          CI/CD Cloud Build → Cloud Run
├── Dockerfile
├── requirements.txt
├── run.py                   local dev runner
└── .env                     ← không commit
```

Chi tiết từng module: xem `md_du_an/02_CAU_TRUC_FOLDER_VA_ENTRY_POINTS.md`.

---

## API Security

Middleware stack:

```
Request → CORS → Logging → ApiSecret → Router → Handler → Response
```

---

## Database migrations

```bash
alembic revision --autogenerate -m "mo_ta_thay_doi"
alembic upgrade head
alembic downgrade -1
alembic current
```

---

## Deploy production (Google Cloud)

Pipeline trong `cloudbuild.yaml`:

```
Git push → Docker build → Artifact Registry → Alembic migrate → Cloud Run deploy
```

| Resource | Tên (trong repo) |
|---|---|
| Cloud Run service | `api-web-he-thong-and-app` |
| Cloud SQL | `mbl-cms-db` |
| Region | `asia-southeast1` |
| Secrets (Secret Manager) | `DATABASE_URL`, `SECRET_KEY`, `VNPAY_*` |

Deploy thủ công:

```bash
gcloud config set project <BACKEND_GCP_PROJECT>
gcloud builds submit --config=cloudbuild.yaml .
```

---

## Troubleshooting

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| 403 Forbidden | Thiếu `X-Quan-Secret` | Thêm header, kiểm tra `API_SECRET_KEY` |
| 401 Unauthorized | JWT hết hạn | Refresh token hoặc login lại |
| 500 DB Error | Schema chưa sync | `alembic upgrade head` |
| CORS Error | Origin chưa whitelist | Thêm origin vào `CORS_ORIGINS` |
| Upload media fail | Thiếu GCS credentials | Kiểm tra `GCS_BUCKET_NAME` + SA JSON |

---

## Tài liệu thêm

| File | Nội dung |
|---|---|
| `app/core/config.py` | Toàn bộ env vars |
| `md_du_an/03_API_FLOW_VA_REQUEST_LIFECYCLE.md` | Request / auth flow |
| `md_du_an/07_DEPLOYMENT_DEBUG_VA_READING_ORDER.md` | Deploy & debug |
| `md_du_an/11_HUONG_DAN_BAT_LAI_GCP.md` | Bật lại GCP sau shutdown |
