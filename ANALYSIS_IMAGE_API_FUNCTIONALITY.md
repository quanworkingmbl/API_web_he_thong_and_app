# PHÂN TÍCH CHỨC NĂNG API XỬ LÝ HÌNH ẢNH (IMAGE API ANALYSIS)

**Ngày phân tích:** 29/03/2026
**Dự án:** API Web Hệ Thống và App
**Mục đích:** Kiểm tra và phân tích luồng hoạt động của các API có xử lý hình ảnh

---

## 📋 TÓM TẮT TỔNG QUAN

Dự án sử dụng kiến trúc **tập trung hóa** cho việc quản lý hình ảnh với:
- **Backend Storage:** Supabase S3-compatible Storage
- **API chính:** `/api/medias` - endpoint trung tâm cho upload/quản lý media
- **Số lượng API sử dụng image:** 7 module chính
- **Kiểu lưu trữ:** JSON array hoặc single URL dạng Text trong database

---

## 🏗️ KIẾN TRÚC XỬ LÝ HÌNH ẢNH

### 1. Luồng Hoạt Động Tổng Thể

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER/CLIENT                                │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ 1. Upload file (multipart/form-data)
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│              API ENDPOINT: POST /api/medias/uploads               │
│                                                                    │
│  ✓ Validate MIME type (image/jpeg, png, gif, webp, video)        │
│  ✓ Validate size (max 10MB)                                      │
│  ✓ Generate unique filename (UUID + extension)                   │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ 2. Upload file với boto3 S3 client
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                   SUPABASE S3 STORAGE                             │
│                                                                    │
│  Bucket: file_test00 (default)                                   │
│  Endpoint: https://{project}.supabase.co/storage/v1               │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ 3. Return public URL
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│              DATABASE: medias table                               │
│                                                                    │
│  - id (PK)                                                        │
│  - filename                                                       │
│  - file_path (public URL)   ← GIÁ TRỊ QUAN TRỌNG                │
│  - file_type (image/video/document)                              │
│  - file_size                                                      │
│  - mime_type                                                      │
│  - uploaded_by (FK -> users.id)                                  │
│  - created_at, updated_at                                         │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ 4. Return JSON response
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  Response:                                                        │
│  {                                                                │
│    "success": true,                                               │
│    "id": 123,                                                     │
│    "filename": "image.jpg",                                       │
│    "url": "https://xxx.supabase.co/.../uuid.jpg"  ← SỬ DỤNG     │
│    "file_type": "image",                                          │
│    "file_size": 1024000                                           │
│  }                                                                │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ 5. Sử dụng URL trong các API khác
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│         CÁC MODEL/API SỬ DỤNG IMAGE URL                          │
│                                                                    │
│  • Products (images: JSON array)                                  │
│  • Contents (images, videos: JSON arrays)                         │
│  • ReturnRequests (images: JSON array)                           │
│  • SellerProfile (id_card_front_url, id_card_back_url, etc)     │
│  • Categories (image: single URL)                                │
│  • Regions (image: single URL)                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 CHI TIẾT CÁC API SỬ DỤNG HÌNH ẢNH

### 1. **MEDIA API** (`/api/medias`) - HỆ THỐNG TRUNG TÂM

**File:** `app/api/v1/media.py`
**Model:** `app/models/media.py`

#### 🔹 Endpoints:

| Method | Endpoint | Chức năng | Authentication |
|--------|----------|-----------|----------------|
| POST | `/api/medias/uploads` | Upload file lên Supabase Storage | ✅ Required |
| GET | `/api/medias` | List media với phân trang | ✅ Required |
| GET | `/api/medias/{media_id}` | Lấy chi tiết 1 media | ✅ Required |
| DELETE | `/api/medias/{media_id}` | Xóa media (cả storage & DB) | ✅ Required |

#### 🔹 Cấu hình Storage (từ `.env`):

```python
SUPABASE_PROJECT_ID = ""
SUPABASE_S3_ENDPOINT = ""
SUPABASE_S3_ACCESS_KEY = ""
SUPABASE_S3_SECRET_KEY = ""
SUPABASE_S3_REGION = "ap-south-1"  # default
SUPABASE_STORAGE_BUCKET = "file_test00"  # default
```

#### 🔹 Validation Rules:

```python
ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/quicktime"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
```

#### 🔹 Upload Process (POST /api/medias/uploads):

```python
# 1. Validate MIME type
if file.content_type not in ALLOWED_TYPES:
    raise HTTPException(400, "Loại file không được hỗ trợ")

# 2. Read và validate size
content = await file.read()
if len(content) > MAX_FILE_SIZE:
    raise HTTPException(400, "File quá lớn. Tối đa 10 MB")

# 3. Generate unique filename
ext = os.path.splitext(file.filename)[1].lower()
unique_key = f"{uuid.uuid4()}{ext}"

# 4. Upload to Supabase via boto3
s3 = boto3.client("s3", endpoint_url=SUPABASE_S3_ENDPOINT, ...)
s3.put_object(
    Bucket=SUPABASE_BUCKET,
    Key=unique_key,
    Body=content,
    ContentType=file.content_type
)

# 5. Generate public URL
public_url = f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/{SUPABASE_BUCKET}/{unique_key}"

# 6. Save to database
new_media = Media(
    filename=file.filename,
    file_path=public_url,  # ← QUAN TRỌNG
    file_type="image" / "video",
    file_size=len(content),
    mime_type=file.content_type,
    uploaded_by=current_user.id
)
```

#### 🔹 Response Format:

```json
{
    "success": true,
    "id": 123,
    "filename": "sample.jpg",
    "url": "https://xxx.supabase.co/storage/v1/object/public/file_test00/uuid.jpg",
    "file_type": "image",
    "file_size": 1024000
}
```

#### ✅ ĐÁNH GIÁ:
- **Hoạt động:** ✅ ĐÚNG - Validation đầy đủ, upload an toàn
- **Security:** ✅ TỐT - UUID ngăn collision, authentication required
- **Storage:** ✅ TỐT - Sử dụng Supabase S3-compatible storage
- **Tracking:** ✅ TỐT - Lưu metadata đầy đủ trong DB

---

### 2. **PRODUCTS API** (`/api/products`)

**File:** `app/api/v1/products.py`
**Model:** `app/models/product.py`

#### 🔹 Image Field:
```python
images = Column(Text, nullable=True)  # JSON array of image URLs
```

#### 🔹 Endpoints sử dụng images:

| Method | Endpoint | Image Field | Mô tả |
|--------|----------|-------------|-------|
| POST | `/api/products` | `images` (optional) | Tạo sản phẩm với hình ảnh |
| PUT | `/api/products/{id}` | `images` (optional) | Cập nhật hình ảnh sản phẩm |
| GET | `/api/products` | `images` | Trả về danh sách với images |
| GET | `/api/products/{id}` | `images` | Chi tiết sản phẩm với images |

#### 🔹 Request Schema:
```python
class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str]
    price: Decimal
    producer_id: int
    category_id: Optional[int]
    label: Optional[str]
    images: Optional[str] = None  # JSON array string
    # Example: '["https://...url1.jpg", "https://...url2.jpg"]'
```

#### 🔹 Approval với checked_images:
```python
class ProductApproval(Base):
    # ...
    checked_images = Column(Boolean, default=False)  # ← Kiểm tra hình ảnh
    checked_description = Column(Boolean, default=False)
    checked_price = Column(Boolean, default=False)
```

**Endpoint:** `POST /api/products/{product_id}/approve`
```python
# Admin/content_manager duyệt sản phẩm
approval_data = ProductApprovalRequest(
    product_id=...,
    status="APPROVED" / "REJECTED",
    checked_images=True,  # ← Admin đã kiểm tra hình ảnh
    checked_description=True,
    checked_price=True,
    notes="..."
)
```

#### ✅ ĐÁNH GIÁ:
- **Hoạt động:** ✅ ĐÚNG - Lưu trữ dạng JSON array
- **Approval Flow:** ✅ TỐT - Có workflow kiểm duyệt hình ảnh (`checked_images`)
- **Validation:** ⚠️ CHÚ Ý - Không validate format JSON tại API level
- **Gợi ý:** Nên thêm validation để đảm bảo `images` là valid JSON array

---

### 3. **CONTENT API** (`/api/content`)

**File:** `app/api/v1/content.py`
**Model:** `app/models/content.py`

#### 🔹 Image/Video Fields:
```python
images = Column(Text, nullable=True)  # JSON array
videos = Column(Text, nullable=True)  # JSON array
```

#### 🔹 Endpoints:

| Method | Endpoint | Image Fields | Mô tả |
|--------|----------|--------------|-------|
| POST | `/api/content` | `images`, `videos` | Tạo nội dung với media |
| PUT | `/api/content/{id}` | `images`, `videos` | Cập nhật media |
| GET | `/api/content` | `images`, `videos` | List content với media |
| GET | `/api/content/{id}` | `images`, `videos` | Chi tiết content |
| POST | `/api/content/{id}/approve` | - | Duyệt content |

#### 🔹 Content Types:
```python
content_type: str = Field(..., pattern="^(POST|PRODUCT_DESCRIPTION|NEWS|ANNOUNCEMENT)$")
```

#### 🔹 Request Schema:
```python
class CreateContentRequest(BaseModel):
    title: str
    content: Optional[str]
    content_type: str  # POST, PRODUCT_DESCRIPTION, NEWS, ANNOUNCEMENT
    author_id: int
    product_id: Optional[int]
    images: Optional[str] = None  # JSON array
    videos: Optional[str] = None  # JSON array
```

#### 🔹 Approval Flow:
```python
# POST /api/content/{content_id}/approve
# Chỉ admin hoặc content_manager có quyền
if current_user.type not in ("admin", "content_manager"):
    raise HTTPException(403, "Không có quyền duyệt content")
```

#### ✅ ĐÁNH GIÁ:
- **Hoạt động:** ✅ ĐÚNG - Hỗ trợ cả images và videos
- **Flexibility:** ✅ TỐT - Có nhiều content_type khác nhau
- **Approval:** ✅ TỐT - Có workflow phê duyệt
- **Validation:** ⚠️ CHÚ Ý - Giống Products, cần validate JSON format

---

### 4. **SELLER ONBOARDING API** (`/api/seller`)

**File:** `app/api/v1/seller_onboarding.py`
**Model:** `app/models/seller_profile.py`

#### 🔹 Image Fields (KYC Documents):
```python
id_card_front_url = Column(Text, nullable=True)     # Ảnh CCCD mặt trước
id_card_back_url = Column(Text, nullable=True)      # Ảnh CCCD mặt sau
business_license_url = Column(Text, nullable=True)  # Giấy phép kinh doanh
```

#### 🔹 Endpoints:

| Method | Endpoint | Document Fields | Mô tả |
|--------|----------|-----------------|-------|
| POST | `/api/seller/register` | `id_card_front_url`, `id_card_back_url`, `business_license_url` | Seller nộp hồ sơ |
| GET | `/api/seller/verification-status` | - | Xem trạng thái duyệt |
| PUT | `/api/seller/verify/{user_id}` | - | Admin duyệt/từ chối |
| GET | `/api/seller/applications` | - | Admin xem danh sách hồ sơ |

#### 🔹 Use Case: KYC (Know Your Customer)
```python
# Seller upload documents
{
    "business_name": "Cửa hàng ABC",
    "business_type": "INDIVIDUAL",
    "id_card_number": "001234567890",
    "id_card_front_url": "https://...supabase.../front.jpg",
    "id_card_back_url": "https://...supabase.../back.jpg",
    "business_license_url": "https://...supabase.../license.pdf",
    "bank_name": "Vietcombank",
    "bank_account_number": "0123456789"
}
```

#### 🔹 Verification Flow:
```python
# Seller nộp hồ sơ → status = PENDING
# Admin duyệt → PUT /api/seller/verify/{user_id}
{
    "status": "VERIFIED" / "REJECTED",
    "rejection_reason": "..." (nếu REJECTED)
}

# Nếu VERIFIED → seller_user.activated = 1 (cho phép bán hàng)
# Nếu REJECTED → giữ activated = 0
```

#### ✅ ĐÁNH GIÁ:
- **Hoạt động:** ✅ ĐÚNG - Lưu trữ document URLs
- **Security:** ✅ QUAN TRỌNG - Dùng cho xác minh danh tính (KYC)
- **Workflow:** ✅ TỐT - Có quy trình duyệt rõ ràng (PENDING → VERIFIED/REJECTED)
- **Privacy:** ⚠️ CHÚ Ý - Documents chứa thông tin nhạy cảm, cần kiểm tra access control

---

### 5. **RETURN REQUESTS API** (`/api/returns`)

**File:** `app/api/v1/returns.py`
**Model:** `app/models/return_request.py`

#### 🔹 Image Field:
```python
images = Column(Text, nullable=True)  # JSON array - ảnh chứng cứ
```

#### 🔹 Endpoints:

| Method | Endpoint | Image Field | Mô tả |
|--------|----------|-------------|-------|
| POST | `/api/returns` | `images` | Tạo yêu cầu đổi/trả với ảnh chứng cứ |
| GET | `/api/returns/my` | `images` | Khách hàng xem yêu cầu |
| GET | `/api/returns` | `images` | Admin xem tất cả yêu cầu |
| PUT | `/api/returns/{id}/approve` | - | Admin duyệt |
| PUT | `/api/returns/{id}/reject` | - | Admin từ chối |

#### 🔹 Use Case: Evidence Images
```python
# Khách hàng tạo yêu cầu đổi/trả với ảnh chứng cứ
{
    "order_id": 123,
    "return_type": "RETURN" / "EXCHANGE",
    "reason": "Sản phẩm bị lỗi, không đúng mô tả...",
    "images": '["https://.../evidence1.jpg", "https://.../evidence2.jpg"]'
}
```

#### 🔹 Return Flow:
```
Customer: Tạo yêu cầu (PENDING) với ảnh chứng cứ
    ↓
Admin: Xem ảnh → Approve (APPROVED) / Reject (REJECTED)
    ↓
Customer: Gửi hàng về
    ↓
Admin: Nhận hàng (RECEIVED) → Hoàn tiền (REFUNDED) hoặc Gửi hàng đổi (EXCHANGED)
```

#### ✅ ĐÁNH GIÁ:
- **Hoạt động:** ✅ ĐÚNG - Images dùng làm chứng cứ
- **Workflow:** ✅ TỐT - Quy trình đầy đủ với nhiều trạng thái
- **Use Case:** ✅ QUAN TRỌNG - Giúp admin quyết định approve/reject
- **Validation:** ⚠️ CHÚ Ý - Cần validate JSON format

---

### 6. **CATEGORIES API** (`/api/categories`)

**File:** `app/api/v1/categories.py`
**Model:** `app/models/category.py`

#### 🔹 Image Fields:
```python
icon = Column(String(100), nullable=True)  # Icon class hoặc URL
image = Column(Text, nullable=True)        # Category thumbnail URL
```

#### 🔹 Endpoints:

| Method | Endpoint | Image Field | Mô tả |
|--------|----------|-------------|-------|
| POST | `/api/categories` | `icon`, `image` | Tạo category với hình đại diện |
| PUT | `/api/categories/{id}` | `icon`, `image` | Cập nhật hình đại diện |
| GET | `/api/categories` | `icon`, `image` | List categories |
| GET | `/api/categories/{id}` | `icon`, `image` | Chi tiết category |

#### 🔹 Use Case:
```python
# Tạo danh mục với hình ảnh đại diện
{
    "name": "Rau củ quả",
    "description": "Các loại rau củ quả tươi sạch",
    "icon": "fa-leaf",  # Font Awesome icon hoặc URL
    "image": "https://.../vegetables-category.jpg",
    "parent_id": null,
    "order": 1,
    "is_active": true
}
```

#### ✅ ĐÁNH GIÁ:
- **Hoạt động:** ✅ ĐÚNG - Single image URL
- **Flexibility:** ✅ TỐT - Hỗ trợ cả icon class và image URL
- **Structure:** ✅ TỐT - Hỗ trợ subcategories (parent_id)

---

### 7. **REGIONS API** (`/api/regions`)

**File:** `app/api/v1/regions.py` (nếu có)
**Model:** `app/models/region.py`

#### 🔹 Image Field:
```python
image = Column(Text, nullable=True)  # Region representative image
```

#### 🔹 Use Case:
```python
# Phân loại sản phẩm theo vùng miền
{
    "name": "Miền Bắc",
    "slug": "mien-bac",
    "description": "Sản phẩm đặc trưng vùng Miền Bắc",
    "image": "https://.../northern-region.jpg",
    "latitude": "21.0285",
    "longitude": "105.8542",
    "order": 1,
    "is_active": true
}
```

#### ✅ ĐÁNH GIÁ:
- **Hoạt động:** ✅ ĐÚNG - Single image URL
- **Use Case:** ✅ TỐT - Phân loại sản phẩm theo địa lý

---

## 🔍 PHÂN TÍCH KIẾN TRÚC

### ✅ ĐIỂM MẠNH (Strengths)

1. **Tập trung hóa (Centralized)**
   - Có 1 endpoint duy nhất cho upload (`POST /api/medias/uploads`)
   - Dễ quản lý, bảo trì và mở rộng
   - Consistent validation và error handling

2. **Storage Architecture**
   - Sử dụng Supabase S3-compatible storage (hiện đại, scalable)
   - Public URLs dễ sử dụng và share
   - Không cần serve files qua backend (giảm tải server)

3. **Security**
   - UUID filename ngăn chặn collision và directory traversal
   - Authentication required cho tất cả endpoints
   - File type validation (MIME type checking)
   - File size limit (10MB)
   - Track uploader qua `uploaded_by` field

4. **Metadata Tracking**
   - Lưu đầy đủ thông tin: filename, file_path, file_type, file_size, mime_type
   - Có timestamp (created_at, updated_at)
   - Link với user qua foreign key

5. **Approval Workflows**
   - Products có `checked_images` flag trong approval
   - Content và Products có workflow PENDING → APPROVED/REJECTED
   - Seller profile có verification workflow cho KYC documents

6. **Flexibility**
   - Hỗ trợ cả images và videos
   - Có thể lưu single URL hoặc JSON array tùy use case
   - Multiple use cases: products, content, KYC documents, evidence photos

### ⚠️ ĐIỂM CẦN CHÚ Ý (Areas of Concern)

1. **JSON Validation**
   - ❌ THIẾU: Không validate JSON format khi nhận `images` field
   - **Vấn đề:** Có thể lưu invalid JSON → lỗi khi parse
   - **Gợi ý:** Thêm validation:
     ```python
     import json

     def validate_json_array(value: Optional[str]) -> Optional[str]:
         if value is None:
             return None
         try:
             parsed = json.loads(value)
             if not isinstance(parsed, list):
                 raise ValueError("Must be a JSON array")
             return value
         except json.JSONDecodeError:
             raise HTTPException(400, "Invalid JSON format for images")
     ```

2. **URL Validation**
   - ❌ THIẾU: Không validate URLs trong JSON array có đúng format
   - **Vấn đề:** Có thể lưu URLs không hợp lệ hoặc không phải từ Supabase
   - **Gợi ý:** Validate URLs thuộc Supabase domain:
     ```python
     def validate_supabase_urls(urls: List[str]) -> bool:
         for url in urls:
             if not url.startswith(SUPABASE_PUBLIC_URL_BASE):
                 raise HTTPException(400, f"Invalid URL: {url}")
         return True
     ```

3. **Orphaned Files**
   - ⚠️ TIỀM ẨN: Khi xóa Product/Content, URLs vẫn còn trong medias table
   - **Vấn đề:** File trên storage không bị xóa, tốn dung lượng
   - **Gợi ý:**
     - Option 1: Cascade delete (xóa luôn medias records)
     - Option 2: Cleanup job định kỳ (xóa media không được reference)
     - Option 3: Soft delete với flag `is_deleted`

4. **Access Control cho Documents**
   - ⚠️ BẢO MẬT: ID card images có thể truy cập qua public URL
   - **Vấn đề:** Thông tin nhạy cảm (CCCD) có thể bị leak nếu biết URL
   - **Gợi ý:**
     - Sử dụng Supabase Storage Policies để restrict access
     - Hoặc dùng signed URLs có thời gian expire
     - Hoặc serve qua backend với authentication check

5. **Image Processing**
   - ❌ THIẾU: Không có resize, compression, thumbnail generation
   - **Vấn đề:** File gốc có thể rất lớn, ảnh hưởng performance frontend
   - **Gợi ý:** Thêm image processing:
     - Resize to multiple sizes (thumbnail, medium, large)
     - Compression để giảm dung lượng
     - WebP conversion cho browser support

6. **Virus Scanning**
   - ❌ THIẾU: Không có malware/virus scanning
   - **Vấn đề:** User có thể upload file độc hại
   - **Gợi ý:** Tích hợp antivirus scanner (ClamAV, VirusTotal API)

7. **Rate Limiting**
   - ❌ THIẾU: Không có rate limiting cho upload endpoint
   - **Vấn đề:** Có thể bị abuse (upload spam)
   - **Gợi ý:** Thêm rate limiting middleware

8. **File Type Validation**
   - ⚠️ KHÔNG ĐẦY ĐỦ: Chỉ check MIME type, không check magic bytes
   - **Vấn đề:** Có thể fake MIME type
   - **Gợi ý:** Validate magic bytes (file signature) bằng python-magic

---

## 🔄 LUỒNG HOẠT ĐỘNG CHI TIẾT

### Scenario 1: Tạo sản phẩm mới với hình ảnh

```
[Frontend]
   │
   │ 1. User chọn 3 ảnh sản phẩm
   │
   ▼
[Upload ảnh 1] ──→ POST /api/medias/uploads ──→ Response: {"url": "url1.jpg"}
[Upload ảnh 2] ──→ POST /api/medias/uploads ──→ Response: {"url": "url2.jpg"}
[Upload ảnh 3] ──→ POST /api/medias/uploads ──→ Response: {"url": "url3.jpg"}
   │
   │ 2. Frontend nhận 3 URLs, tạo JSON array
   │
   ▼
[Tạo sản phẩm] ──→ POST /api/products
   Body: {
       "name": "Dưa hấu",
       "price": 50000,
       "producer_id": 5,
       "images": "[\"url1.jpg\", \"url2.jpg\", \"url3.jpg\"]"
   }
   │
   ▼
[Database]
   products table:
   - images: '[\"url1.jpg\", \"url2.jpg\", \"url3.jpg\"]'
   - status: PENDING
   │
   ▼
[Admin duyệt] ──→ POST /api/products/{id}/approve
   Body: {
       "status": "APPROVED",
       "checked_images": true,
       "checked_description": true,
       "checked_price": true
   }
   │
   ▼
[Product status] = APPROVED
[Frontend hiển thị sản phẩm với 3 ảnh]
```

### Scenario 2: Seller nộp hồ sơ KYC

```
[Seller]
   │
   │ 1. Upload CCCD mặt trước
   │
   ▼
POST /api/medias/uploads (file: front.jpg)
   → Response: {"url": "https://...front.jpg"}
   │
   │ 2. Upload CCCD mặt sau
   │
   ▼
POST /api/medias/uploads (file: back.jpg)
   → Response: {"url": "https://...back.jpg"}
   │
   │ 3. Upload giấy phép kinh doanh
   │
   ▼
POST /api/medias/uploads (file: license.pdf)
   → Response: {"url": "https://...license.pdf"}
   │
   │ 4. Nộp hồ sơ
   │
   ▼
POST /api/seller/register
   Body: {
       "business_name": "ABC Shop",
       "business_type": "INDIVIDUAL",
       "id_card_number": "001234567890",
       "id_card_front_url": "https://...front.jpg",
       "id_card_back_url": "https://...back.jpg",
       "business_license_url": "https://...license.pdf"
   }
   │
   ▼
[Database]
   seller_profiles table:
   - verification_status: PENDING
   │
   ▼
[Admin xem hồ sơ] ──→ GET /api/seller/applications
   → Xem ảnh CCCD và giấy phép
   │
   ▼
[Admin duyệt] ──→ PUT /api/seller/verify/{user_id}
   Body: {"status": "VERIFIED"}
   │
   ▼
[User.activated] = 1 (cho phép bán hàng)
[SellerProfile.verification_status] = VERIFIED
```

### Scenario 3: Khách hàng đổi/trả hàng với ảnh chứng cứ

```
[Customer]
   │
   │ 1. Upload ảnh sản phẩm lỗi (3 ảnh)
   │
   ▼
POST /api/medias/uploads × 3
   → urls: ["evidence1.jpg", "evidence2.jpg", "evidence3.jpg"]
   │
   │ 2. Tạo yêu cầu đổi/trả
   │
   ▼
POST /api/returns
   Body: {
       "order_id": 123,
       "return_type": "RETURN",
       "reason": "Sản phẩm bị hư hỏng khi nhận hàng",
       "images": "[\"evidence1.jpg\", \"evidence2.jpg\", \"evidence3.jpg\"]"
   }
   │
   ▼
[Database]
   return_requests table:
   - status: PENDING
   - images: JSON array
   │
   ▼
[Admin xem] ──→ GET /api/returns
   → Xem ảnh chứng cứ
   │
   │ Admin kiểm tra ảnh, xác nhận sản phẩm thật sự bị lỗi
   │
   ▼
[Admin duyệt] ──→ PUT /api/returns/{id}/approve
   │
   ▼
[Status] = APPROVED
[Customer gửi hàng về]
   │
   ▼
[Admin nhận hàng] ──→ PUT /api/returns/{id}/received
   │
   ▼
[Status] = RECEIVED
[Hoàn tiền cho khách hàng]
```

---

## 📊 THỐNG KÊ HỆ THỐNG

### Image Storage Pattern

| Model | Field Name | Type | Format | Use Case |
|-------|-----------|------|--------|----------|
| Media | file_path | Text | Single URL | Central storage tracking |
| Product | images | Text | JSON Array | Product photos (multiple) |
| Content | images | Text | JSON Array | Content images (multiple) |
| Content | videos | Text | JSON Array | Content videos (multiple) |
| ReturnRequest | images | Text | JSON Array | Evidence photos |
| SellerProfile | id_card_front_url | Text | Single URL | KYC document |
| SellerProfile | id_card_back_url | Text | Single URL | KYC document |
| SellerProfile | business_license_url | Text | Single URL | KYC document |
| Category | image | Text | Single URL | Category thumbnail |
| Region | image | Text | Single URL | Region representative |

### API Endpoints Summary

| Module | Endpoints Count | Authentication | Image Upload | Image Display |
|--------|----------------|----------------|--------------|---------------|
| Media | 4 | ✅ | ✅ Primary | ✅ |
| Products | 5 | ✅ | ❌ (via Media) | ✅ |
| Content | 5 | ✅ | ❌ (via Media) | ✅ |
| Seller | 4 | ✅ | ❌ (via Media) | ✅ |
| Returns | 6 | ✅ | ❌ (via Media) | ✅ |
| Categories | 4 | ✅ | ❌ (via Media) | ✅ |
| Regions | ~4 | ✅ | ❌ (via Media) | ✅ |

**Total:** 32 endpoints liên quan đến image handling

---

## 🎯 KẾT LUẬN

### ✅ Tổng Quan Đánh Giá

**Hệ thống xử lý hình ảnh của dự án HOẠT ĐỘNG ĐÚNG và có kiến trúc tốt:**

1. ✅ **Architecture:** Tập trung hóa tốt với Media API là trung tâm
2. ✅ **Storage:** Sử dụng Supabase S3 hiện đại và scalable
3. ✅ **Security:** Có authentication, validation cơ bản
4. ✅ **Tracking:** Metadata đầy đủ trong database
5. ✅ **Workflows:** Có quy trình phê duyệt cho các module quan trọng
6. ✅ **Flexibility:** Hỗ trợ nhiều use cases khác nhau

### ⚠️ Các Điểm Cần Cải Thiện

**Ưu tiên cao:**
1. 🔴 Thêm JSON validation cho `images` fields
2. 🔴 Thêm URL validation (check Supabase domain)
3. 🔴 Implement access control cho KYC documents (CCCD)

**Ưu tiên trung bình:**
4. 🟡 Thêm orphaned files cleanup mechanism
5. 🟡 Thêm image processing (resize, compression)
6. 🟡 Thêm rate limiting cho upload endpoint

**Ưu tiên thấp:**
7. 🟢 Thêm virus scanning
8. 🟢 Validate magic bytes (file signature)
9. 🟢 Generate thumbnails tự động

### 📈 Recommendations

1. **Short-term (1-2 tuần):**
   - Thêm JSON validation helpers
   - Document URLs validation
   - Kiểm tra và fix access control cho sensitive documents

2. **Mid-term (1-2 tháng):**
   - Implement image processing pipeline
   - Thêm rate limiting
   - Orphaned files cleanup job

3. **Long-term (3-6 tháng):**
   - Migration sang CDN cho static files
   - Advanced image optimization (WebP, AVIF)
   - Comprehensive audit logging cho file access

---

## 📝 PHỤ LỤC

### A. Environment Variables Checklist

```bash
# Supabase Storage Configuration
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_S3_ENDPOINT=https://your-project.supabase.co
SUPABASE_S3_ACCESS_KEY=your_access_key
SUPABASE_S3_SECRET_KEY=your_secret_key
SUPABASE_S3_REGION=ap-south-1
SUPABASE_STORAGE_BUCKET=file_test00
```

### B. Database Schema (Image-related)

```sql
-- medias table
CREATE TABLE medias (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,  -- Public URL
    file_type VARCHAR(100),            -- image/video/document
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- products table (excerpt)
CREATE TABLE products (
    -- ...
    images TEXT,  -- JSON array of URLs
    -- ...
);

-- contents table (excerpt)
CREATE TABLE contents (
    -- ...
    images TEXT,  -- JSON array
    videos TEXT,  -- JSON array
    -- ...
);

-- return_requests table (excerpt)
CREATE TABLE return_requests (
    -- ...
    images TEXT,  -- JSON array
    -- ...
);

-- seller_profiles table (excerpt)
CREATE TABLE seller_profiles (
    -- ...
    id_card_front_url TEXT,
    id_card_back_url TEXT,
    business_license_url TEXT,
    -- ...
);

-- categories table (excerpt)
CREATE TABLE categories (
    -- ...
    icon VARCHAR(100),
    image TEXT,
    -- ...
);

-- regions table (excerpt)
CREATE TABLE regions (
    -- ...
    image TEXT,
    -- ...
);
```

### C. Sample API Calls

#### Upload Image
```bash
curl -X POST "http://localhost:8000/api/medias/uploads" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

#### Create Product with Images
```bash
curl -X POST "http://localhost:8000/api/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dưa hấu",
    "description": "Dưa hấu ngọt",
    "price": 50000,
    "producer_id": 5,
    "images": "[\"https://xxx.supabase.co/.../img1.jpg\", \"https://xxx.supabase.co/.../img2.jpg\"]"
  }'
```

#### Approve Product with Image Check
```bash
curl -X POST "http://localhost:8000/api/products/1/approve" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "status": "APPROVED",
    "checked_description": true,
    "checked_price": true,
    "checked_images": true,
    "notes": "Sản phẩm đạt tiêu chuẩn, hình ảnh rõ ràng"
  }'
```

---

**Tài liệu này được tạo vào:** 29/03/2026
**Phiên bản:** 1.0
**Tác giả:** Claude Code Analysis Agent
**Mục đích:** Kiểm tra chức năng và phân tích luồng hoạt động API xử lý hình ảnh
