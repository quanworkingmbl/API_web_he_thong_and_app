# Tổng thể dự án (đối chiếu mã nguồn backend `Du_an_cms_API`)

Tài liệu này mô tả **phần backend API** (FastAPI) trong hệ marketplace. **Web dashboard** và **ứng dụng mobile** là các client riêng; chúng gọi API theo các endpoint dưới đây.

---

## 1. Tên và bản chất đề tài

Có thể phát biểu như sau:

**Xây dựng hệ thống thương mại điện tử cho sản phẩm làng nghề và đặc sản vùng miền theo mô hình marketplace đa người bán.**

Đây không phải website một cửa hàng đơn lẻ mà là **nền tảng trung gian** kết nối:

- người sản xuất / người bán  
- người tiêu dùng  
- quản trị viên nền tảng  

Ngoài mua bán, backend hỗ trợ các bài toán thường gặp với hàng địa phương:

- kiểm duyệt người bán (KYC / hồ sơ)  
- kiểm duyệt sản phẩm  
- chứng nhận sản phẩm  
- truy xuất nguồn gốc  
- thanh toán (COD, VNPay, …)  
- vận chuyển (tích hợp GHN trong code hiện tại)  
- phí nền tảng, ví seller, đối soát, chi trả  
- khiếu nại, đổi trả, đánh giá  

---

## 2. Ý tưởng cốt lõi

Sản phẩm làng nghề / đặc sản thường khó tiếp cận thị trường, thiếu minh bạch nguồn gốc và niềm tin khi mua online. Hệ thống hướng tới:

- một sàn chuyên phân khúc này  
- quy trình đăng bán có kiểm soát  
- thông tin truy xuất và chứng nhận để tăng tin cậy  

---

## 3. Mô hình hệ thống (3 phần chính)

| Thành phần | Vai trò |
|------------|---------|
| **Backend API** (repo này) | Xác thực, dữ liệu, đơn hàng, thanh toán, vận chuyển, hoa hồng, truy xuất nguồn gốc, khiếu nại, … |
| **Web quản trị / vận hành** | Admin + seller/producer: duyệt, vận hành sàn, theo dõi KD (client gọi API) |
| **Ứng dụng mobile** | **Người mua** (consumer): xem SP, giỏ, đặt hàng, TT, theo dõi đơn, đánh giá, khiếu nại (client gọi API; có nhóm route `/mobile/...`) |

Tóm lại: **mobile = kênh mua hàng**, **web = kênh vận hành (seller/admin)**, **API = lõi nghiệp vụ**.

---

## 4. Các tác nhân chính

1. **Người tiêu dùng** — tìm kiếm, xem SP & truy xuất, giỏ, đặt hàng, thanh toán, theo dõi đơn, đánh giá, khiếu nại / đổi trả.  
2. **Người bán / nhà sản xuất** — onboarding, hồ sơ xác minh, sản phẩm, tồn kho, đơn hàng, doanh thu / phí / ví (trong API có `SellerProfile`, `Store`, settlement, …).  
3. **Quản trị viên** — user, duyệt SP, chứng nhận, khiếu nại, cấu hình liên quan, dashboard, đối soát / chi trả (theo từng endpoint và `user.type` / quyền trong code).  
4. **Hệ thống ngoài** — cổng thanh toán (VNPay trong `app/services/vnpay.py`), đơn vị vận chuyển (**GHN** trong `app/services/ghn.py` và `shipping.py`).

---

## 5. Mục tiêu dự án (tóm tắt)

- Marketplace đa seller cho đặc sản / làng nghề  
- Minh bạch và kiểm soát đầu vào (seller + sản phẩm + traceability)  
- Vận hành thực tế: đặt hàng, thanh toán, giao hàng, sau bán, phí nền tảng  

---

## 6. Phạm vi nghiệp vụ trong backend (theo module API)

- **Nền tảng:** users, roles (CRUD danh sách role), organizations, dashboard, stats, content  
- **Hàng hóa:** categories, regions, products (+ duyệt), promotions, traceability (chứng nhận + nguồn gốc)  
- **Giao dịch:** cart, orders, payments, shipping  
- **Sau bán:** reviews, complaints, returns  
- **Tài chính seller:** settlement, ví `SellerWallet`  
- **Khác:** contracts (đối tác), seller onboarding, media  

*(Danh sách router gốc trong `app/api/v1/__init__.py`.)*

---

## 7. Kiến trúc kỹ thuật (đúng với repo hiện tại)

- **Framework:** FastAPI  
- **Ngôn ngữ:** Python  
- **CSDL:** PostgreSQL (cấu hình qua `DATABASE_URL` trong `.env`, thường dùng AWS RDS — xem README)  
- **ORM:** SQLAlchemy  
- **Migration:** Alembic  
- **Lưu trữ file:**  
  - **AWS S3** — module `app/api/v1/media.py` (biến môi trường `AWS_*`)  
  - **Supabase Storage (S3-compatible)** — một số luồng upload trong `app/api/v1/mobile_app.py` (biến `SUPABASE_*`)  
- **Thanh toán:** enum trong `Order` gồm COD, chuyển khoản, MoMo, VNPay, ZaloPay; tích hợp cổng **VNPay** trong service  
- **Vận chuyển:** trong code có **tích hợp GHN** (tạo vận đơn, webhook, …). Model có thể mô tả thêm **GHTK / VNPOST** nhưng **chưa có service tương ứng** trong `app/services/` — không nên ghi “đã tích hợp đầy đủ GHTK/VNPost” nếu chỉ bàn mã hiện tại.  
- **Tiền tố API:** toàn bộ route gắn dưới **`/api`** (ví dụ `POST /api/auth/login`), **không** phải `/api/v1/...` — thư mục `app/api/v1` chỉ là tổ chức package.

---

## 8. Chức năng lớn (đối chiếu code)

**A. Tài khoản & phân quyền**

- Đăng ký / đăng nhập, JWT (`Authorization: Bearer`)  
- Endpoint **`POST /api/auth/refresh`**: cấp lại access token khi gửi **Bearer token còn hiệu lực** (gia hạn), **không** phải refresh token kiểu OAuth2 riêng (không có refresh token rotation trong DB)  
- Trong DB có bảng `roles`, `permissions`, `user_roles`; **`/api/auth/me`** trả thêm danh sách role. **Phần lớn kiểm tra quyền endpoint** dùng **`user.type`** (chuỗi: `consumer`, `producer`, `seller`, `admin`, `content_manager`, …) trong `app/core/permissions.py` — cần ghi rõ trong báo cáo nếu hội đồng hỏi “RBAC chi tiết theo permission code”.  

**B. Người bán**

- `SellerProfile`, onboarding, KYC (`check_seller_kyc_verified` trước khi tạo/sửa sản phẩm theo luồng đã cấu hình)  

**C. Sản phẩm**

- Trạng thái duyệt (`PENDING` / `APPROVED` / `REJECTED`), nhãn gợi ý địa phương (OCOP, nông sản sạch, làng nghề truyền thống — trong model `ProductLabel`)  
- **Đặt hàng đa seller:** luồng checkout trong `mobile_app` **tách nhiều đơn theo từng seller** nếu giỏ có nhiều người bán  

**D. Truy xuất & chứng nhận**

- `ProductCertificate`, `ProductOrigin` (làng nghề, vùng, lô, …)  

**E–G. Đặt hàng, thanh toán, vận chuyển**

- Đơn hàng, snapshot dòng hàng, log trạng thái  
- Thanh toán VNPay + IPN/return  
- GHN: phí, tạo đơn vận chuyển, tracking, webhook  

**H. Phí nền tảng & ví**

- Trên `Order` có `platform_fee_*`, `seller_amount`  
- `SellerWallet`, `Settlement`, `Payout` trong `settlement`  

**I. Sau bán**

- Reviews, complaints, returns  

---

## 9. Gợi ý quy trình nghiệp vụ (cho báo cáo / sơ đồ)

Có thể mô tả hoặc vẽ các quy trình sau (không gắn với file sơ đồ cụ thể trong repo):

1. Tổng quan hệ thống  
2. Quản lý / xác minh người bán  
3. Quản lý & duyệt sản phẩm  
4. Đặt hàng & thanh toán  
5. Vận chuyển & hoàn tất đơn  
6. Khiếu nại / đổi trả  
7. Đối soát & chi trả  
8. Truy xuất nguồn gốc & chứng nhận  

---

## 10. Điểm khác biệt so với shop đơn lẻ

- Đa seller, phí nền tảng, ví & settlement  
- Kiểm duyệt seller và sản phẩm  
- Traceability + chứng nhận  
- Sau bán: đánh giá, khiếu nại, đổi trả  

---

## 11. Gợi ý đoạn mô tả tổng quan (đưa vào báo cáo)

Đề tài xây dựng hệ thống thương mại điện tử cho sản phẩm làng nghề và đặc sản vùng miền theo mô hình **marketplace đa người bán**. **Phần backend** (FastAPI) đóng vai trò xử lý nghiệp vụ: tài khoản, sản phẩm, đơn hàng, thanh toán, vận chuyển, phí nền tảng, truy xuất nguồn gốc và xử lý sau bán. **Web quản trị** phục vụ quản trị viên và người bán; **ứng dụng mobile** phục vụ người mua. Ngoài các chức năng thương mại điện tử cơ bản, hệ thống nhấn mạnh **minh bạch và kiểm soát chất lượng** thông qua xác minh người bán, duyệt sản phẩm, chứng nhận và truy xuất nguồn gốc.

---

## 12. Tóm tắt một dòng

Marketplace đặc sản / làng nghề: **web cho admin & seller**, **mobile cho người mua**, **API** xử lý đầy đủ luồng TMĐT + traceability + phí nền tảng.

---

## 13. Ghi chú khi viết báo cáo

- Làm rõ **hai kênh giao diện** (web vận hành vs mobile mua hàng).  
- Làm rõ **marketplace** (trung gian, không phải một chủ shop).  
- Nêu **phạm vi tích hợp thực tế trong code** (VNPay, GHN, S3/Supabase như trên) để tránh “mô tả quá tay” so với implementation.  
- Nếu cần chi tiết endpoint: dùng OpenAPI tại `/docs` khi bật `SHOW_DOCS` và server đang chạy.  

---

*Tài liệu được chỉnh sửa để khớp mã nguồn backend tại thời điểm cập nhật; các client (web/mobile) có thể có repo riêng.*
