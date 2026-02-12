# Function List - Hệ thống CMS Nông sản

> **Cập nhật:** 02/02/2026  
> **Phiên bản:** 1.0

---

## 📋 Tổng quan hệ thống

Hệ thống CMS quản lý nông sản bao gồm 3 thành phần chính:
- **Du_an_cms_API**: Backend API (FastAPI + Python)
- **Du_an_cms_UI**: Web Admin Dashboard (React + TypeScript)
- **App_UI**: Mobile Application (React Native)

---

## 🔐 1. AUTHENTICATION (Xác thực)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 1.1 | Đăng ký tài khoản | `/api/v1/auth/register` | POST | Đăng ký user mới với email, password, name | ✅ Có |
| 1.2 | Đăng nhập | `/api/v1/auth/login` | POST | Đăng nhập và nhận JWT token | ✅ Có |
| 1.3 | Lấy thông tin user | `/api/v1/auth/me` | GET | Lấy thông tin user hiện tại với roles và permissions | ✅ Có |
| 1.4 | Đăng xuất | `/api/v1/auth/logout` | POST | Đăng xuất khỏi hệ thống | ✅ Có |
| 1.5 | Làm mới token | `/api/v1/auth/refresh` | POST | Refresh JWT token | ✅ Có |

---

## 👥 2. USER MANAGEMENT (Quản lý người dùng)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 2.1 | Danh sách users | `/api/v1/users` | GET | Lấy danh sách users với phân trang, filter | ✅ Có |
| 2.2 | Tạo user | `/api/v1/users` | POST | Tạo user mới | ✅ Có |
| 2.3 | Chi tiết user | `/api/v1/users/{id}` | GET | Lấy thông tin chi tiết user | ✅ Có |
| 2.4 | Cập nhật user | `/api/v1/users/{id}` | PUT | Cập nhật thông tin user | ✅ Có |
| 2.5 | Xóa user | `/api/v1/users/{id}` | DELETE | Soft delete user | ✅ Có |
| 2.6 | Kích hoạt/Vô hiệu hóa | `/api/v1/users/{id}/activate` | PUT | Thay đổi trạng thái kích hoạt | ✅ Có |
| 2.7 | Gán roles | `/api/v1/users/{id}/roles` | PUT | Gán roles cho user | ✅ Có |
| 2.8 | Lấy roles của user | `/api/v1/users/{id}/roles` | GET | Lấy danh sách roles đã gán | ✅ Có |

---

## 📊 3. DASHBOARD (Bảng điều khiển)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 3.1 | Tổng quan | `/api/v1/dashboard/overview` | GET | Thống kê tổng quan hệ thống | ✅ Có |
| 3.2 | Thống kê doanh thu | `/api/v1/dashboard/revenue` | GET | Doanh thu theo thời gian | ✅ Có |
| 3.3 | Thống kê sản phẩm | `/api/v1/dashboard/products` | GET | Thống kê sản phẩm theo trạng thái | ✅ Có |
| 3.4 | Thống kê đơn hàng | `/api/v1/dashboard/orders` | GET | Thống kê đơn hàng | ✅ Có |
| 3.5 | Thống kê người dùng | `/api/v1/dashboard/users` | GET | Thống kê user theo loại | ✅ Có |

---

## 📦 4. PRODUCTS (Sản phẩm)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 4.1 | Danh sách sản phẩm | `/api/v1/products` | GET | Lấy danh sách với filter, phân trang | ✅ Có |
| 4.2 | Chi tiết sản phẩm | `/api/v1/products/{id}` | GET | Lấy thông tin chi tiết | ✅ Có |
| 4.3 | Tạo sản phẩm | `/api/v1/products` | POST | Tạo sản phẩm mới | ✅ Có |
| 4.4 | Cập nhật sản phẩm | `/api/v1/products/{id}` | PUT | Cập nhật thông tin sản phẩm | ✅ Có |
| 4.5 | Xóa sản phẩm | `/api/v1/products/{id}` | DELETE | Xóa sản phẩm | ✅ Có |
| 4.6 | Duyệt sản phẩm | `/api/v1/products/{id}/approve` | POST | Duyệt hoặc từ chối sản phẩm | ✅ Có |
| 4.7 | Cập nhật nhãn | `/api/v1/products/{id}/label` | PUT | Gắn nhãn (CLEAN_AGRICULTURE, TRADITIONAL_CRAFT, OCOP) | ✅ Có |

---

## 🛒 5. ORDERS (Đơn hàng)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 5.1 | Danh sách đơn hàng | `/api/v1/orders` | GET | Lấy danh sách đơn hàng | ✅ Có |
| 5.2 | Chi tiết đơn hàng | `/api/v1/orders/{id}` | GET | Xem chi tiết đơn hàng | ✅ Có |
| 5.3 | Cập nhật trạng thái | `/api/v1/orders/{id}/status` | PUT | Cập nhật trạng thái đơn hàng | ✅ Có |
| 5.4 | Thống kê đơn hàng | `/api/v1/orders/stats` | GET | Thống kê tổng quan | ✅ Có |

---

## 🏢 6. ORGANIZATIONS (Tổ chức - Hợp tác xã/Làng nghề)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 6.1 | Danh sách tổ chức | `/api/v1/organizations` | GET | Lấy danh sách HTX, làng nghề | ✅ Có |
| 6.2 | Chi tiết tổ chức | `/api/v1/organizations/{id}` | GET | Xem chi tiết tổ chức | ✅ Có |
| 6.3 | Tạo tổ chức | `/api/v1/organizations` | POST | Tạo tổ chức mới | ✅ Có |
| 6.4 | Cập nhật tổ chức | `/api/v1/organizations/{id}` | PUT | Cập nhật thông tin | ✅ Có |
| 6.5 | Xóa tổ chức | `/api/v1/organizations/{id}` | DELETE | Xóa tổ chức | ✅ Có |
| 6.6 | Danh sách thành viên | `/api/v1/organizations/{id}/members` | GET | Lấy danh sách thành viên | ✅ Có |
| 6.7 | Thêm thành viên | `/api/v1/organizations/{id}/members` | POST | Thêm thành viên vào tổ chức | ✅ Có |
| 6.8 | Xóa thành viên | `/api/v1/organizations/{id}/members/{user_id}` | DELETE | Xóa thành viên | ✅ Có |

---

## 📝 7. CONTENT (Nội dung - Bài viết)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 7.1 | Danh sách nội dung | `/api/v1/content` | GET | Lấy danh sách bài viết | ✅ Có |
| 7.2 | Chi tiết nội dung | `/api/v1/content/{id}` | GET | Xem chi tiết nội dung | ✅ Có |
| 7.3 | Tạo nội dung | `/api/v1/content` | POST | Tạo bài viết mới | ✅ Có |
| 7.4 | Cập nhật nội dung | `/api/v1/content/{id}` | PUT | Cập nhật bài viết | ✅ Có |
| 7.5 | Xóa nội dung | `/api/v1/content/{id}` | DELETE | Xóa bài viết | ✅ Có |
| 7.6 | Duyệt nội dung | `/api/v1/content/{id}/approve` | POST | Duyệt hoặc từ chối nội dung | ✅ Có |

---

## 📄 8. CONTRACTS (Hợp đồng đối tác)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 8.1 | Danh sách hợp đồng | `/api/v1/contracts` | GET | Lấy danh sách hợp đồng | ✅ Có |
| 8.2 | Chi tiết hợp đồng | `/api/v1/contracts/{id}` | GET | Xem chi tiết hợp đồng | ✅ Có |
| 8.3 | Tạo hợp đồng | `/api/v1/contracts` | POST | Tạo hợp đồng mới | ✅ Có |
| 8.4 | Cập nhật hợp đồng | `/api/v1/contracts/{id}` | PUT | Cập nhật thông tin hợp đồng | ✅ Có |
| 8.5 | Xóa hợp đồng | `/api/v1/contracts/{id}` | DELETE | Xóa hợp đồng | ✅ Có |

---

## 💰 9. PAYMENTS (Thanh toán)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 9.1 | Danh sách thanh toán | `/api/v1/payments` | GET | Lấy danh sách thanh toán | ✅ Có |
| 9.2 | Trạng thái thanh toán | `/api/v1/payments/{id}/status` | GET | Kiểm tra trạng thái | ✅ Có |
| 9.3 | Đối soát thanh toán | `/api/v1/payments/reconciliation` | GET | Báo cáo đối soát | ✅ Có |
| 9.4 | Hoàn tiền | `/api/v1/payments/refund` | POST | Xử lý hoàn tiền | ✅ Có |
| 9.5 | Khiếu nại thanh toán | `/api/v1/payments/complaint` | POST | Tạo khiếu nại thanh toán | ✅ Có |
| 9.6 | Cấu hình phí nền tảng | `/api/v1/payments/config/fee` | PUT | Cập nhật % phí nền tảng | ✅ Có |
| 9.7 | Cấu hình chu kỳ thanh toán | `/api/v1/payments/config/cycle` | PUT | Cập nhật chu kỳ (WEEKLY/MONTHLY) | ✅ Có |

---

## 📢 10. COMPLAINTS (Khiếu nại & Đánh giá)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 10.1 | Danh sách đánh giá | `/api/v1/complaints/reviews` | GET | Lấy danh sách đánh giá sản phẩm | ✅ Có |
| 10.2 | Danh sách khiếu nại | `/api/v1/complaints/complaints` | GET | Lấy danh sách khiếu nại | ✅ Có |
| 10.3 | Xử lý khiếu nại | `/api/v1/complaints/{id}/handle` | PUT | Xử lý khiếu nại | ✅ Có |

---

## 📁 11. CATEGORIES (Danh mục)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 11.1 | Danh sách danh mục | `/api/v1/categories` | GET | Lấy danh sách danh mục | ✅ Có |
| 11.2 | Chi tiết danh mục | `/api/v1/categories/{id}` | GET | Xem chi tiết danh mục | ✅ Có |
| 11.3 | Tạo danh mục | `/api/v1/categories` | POST | Tạo danh mục mới | ✅ Có |
| 11.4 | Cập nhật danh mục | `/api/v1/categories/{id}` | PUT | Cập nhật danh mục | ✅ Có |
| 11.5 | Xóa danh mục | `/api/v1/categories/{id}` | DELETE | Xóa danh mục | ✅ Có |

---

## 📷 12. MEDIA (Quản lý media)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 12.1 | Danh sách media | `/api/v1/media` | GET | Lấy danh sách files | ✅ Có |
| 12.2 | Chi tiết media | `/api/v1/media/{id}` | GET | Xem thông tin file | ✅ Có |
| 12.3 | Tạo record media | `/api/v1/media` | POST | Tạo record media | ✅ Có |
| 12.4 | Upload file | `/api/v1/media/uploads` | POST | Upload file lên server | ✅ Có |
| 12.5 | Xóa media | `/api/v1/media/{id}` | DELETE | Xóa file | ✅ Có |

---

## 🔑 13. ROLES (Vai trò)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 13.1 | Danh sách roles | `/api/v1/roles` | GET | Lấy danh sách vai trò | ✅ Có |
| 13.2 | Tạo role | `/api/v1/roles` | POST | Tạo vai trò mới | ✅ Có |
| 13.3 | Cập nhật role | `/api/v1/roles/{id}` | PUT | Cập nhật vai trò | ✅ Có |
| 13.4 | Xóa role | `/api/v1/roles/{id}` | DELETE | Xóa vai trò | ✅ Có |

---

## 🔐 14. PERMISSIONS (Quyền hạn)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 14.1 | Danh sách permissions | `/api/v1/permissions` | GET | Lấy danh sách quyền | ✅ Có |
| 14.2 | Tạo permission | `/api/v1/permissions` | POST | Tạo quyền mới | ✅ Có |
| 14.3 | Cập nhật permission | `/api/v1/permissions/{id}` | PUT | Cập nhật quyền | ✅ Có |
| 14.4 | Xóa permission | `/api/v1/permissions/{id}` | DELETE | Xóa quyền | ✅ Có |

---

## 🗺️ 15. REGIONS (Vùng miền)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 15.1 | Danh sách vùng miền | `/api/v1/regions` | GET | Lấy danh sách vùng miền | ✅ Có |
| 15.2 | Chi tiết vùng miền | `/api/v1/regions/{id}` | GET | Xem chi tiết | ✅ Có |
| 15.3 | Tạo vùng miền | `/api/v1/regions` | POST | Tạo vùng miền mới | ✅ Có |
| 15.4 | Cập nhật vùng miền | `/api/v1/regions/{id}` | PUT | Cập nhật thông tin | ✅ Có |
| 15.5 | Xóa vùng miền | `/api/v1/regions/{id}` | DELETE | Xóa vùng miền | ✅ Có |

---

## 📈 16. STATISTICS (Thống kê)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 16.1 | Thống kê producer | `/api/v1/stats/producers` | GET | Thống kê người sản xuất | ✅ Có |
| 16.2 | Thống kê consumer | `/api/v1/stats/consumers` | GET | Thống kê người tiêu dùng | ✅ Có |
| 16.3 | Sản phẩm trending | `/api/v1/stats/trending` | GET | Sản phẩm được đặt nhiều nhất | ✅ Có |
| 16.4 | Thống kê theo vùng | `/api/v1/stats/regions` | GET | Thống kê sản phẩm theo vùng | ✅ Có |
| 16.5 | Thống kê theo danh mục | `/api/v1/stats/categories` | GET | Thống kê theo danh mục | ✅ Có |

---

## 📱 17. MOBILE APP API

### 17.1 Posts API (Bài viết Mobile)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 17.1.1 | Danh sách bài viết public | `/api/v1/mobile/posts` | GET | Bài viết đã duyệt | ✅ Có |
| 17.1.2 | Chi tiết bài viết | `/api/v1/mobile/posts/{id}` | GET | Xem chi tiết | ✅ Có |
| 17.1.3 | Tạo bài viết | `/api/v1/mobile/my/posts` | POST | Producer tạo bài viết | ✅ Có |
| 17.1.4 | Danh sách bài viết của tôi | `/api/v1/mobile/my/posts` | GET | Bài viết của producer | ✅ Có |
| 17.1.5 | Cập nhật bài viết của tôi | `/api/v1/mobile/my/posts/{id}` | PUT | Sửa bài viết | ✅ Có |
| 17.1.6 | Xóa bài viết của tôi | `/api/v1/mobile/my/posts/{id}` | DELETE | Xóa bài viết | ✅ Có |

### 17.2 Products API (Sản phẩm Mobile)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 17.2.1 | Danh sách sản phẩm | `/api/v1/mobile/products` | GET | Sản phẩm đã duyệt | ✅ Có |
| 17.2.2 | Chi tiết sản phẩm | `/api/v1/mobile/products/{id}` | GET | Xem chi tiết | ✅ Có |

### 17.3 Shopping API (Mua sắm)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 17.3.1 | Đặt hàng | `/api/v1/mobile/checkout` | POST | Tạo đơn hàng | ✅ Có |
| 17.3.2 | Danh sách đơn hàng | `/api/v1/mobile/my/orders` | GET | Đơn hàng của tôi | ✅ Có |
| 17.3.3 | Chi tiết đơn hàng | `/api/v1/mobile/my/orders/{id}` | GET | Xem chi tiết | ✅ Có |

### 17.4 Profile API (Thông tin cá nhân)

| STT | Function | Endpoint | Method | Mô tả | Trạng thái |
|-----|----------|----------|--------|-------|------------|
| 17.4.1 | Lấy profile | `/api/v1/mobile/profile` | GET | Thông tin cá nhân | ✅ Có |
| 17.4.2 | Cập nhật profile | `/api/v1/mobile/profile` | PUT | Cập nhật thông tin | ✅ Có |

---

## ❌ CÁC CHỨC NĂNG CẦN BỔ SUNG

### 🔴 Cần thêm mới (High Priority)

| STT | Function | Mô tả | Module | Priority |
|-----|----------|-------|--------|----------|
| N.1 | Quên mật khẩu | Gửi email reset password | Auth | 🔴 High |
| N.2 | Đổi mật khẩu | User đổi mật khẩu | Auth | 🔴 High |
| N.3 | Tạo đánh giá sản phẩm | Consumer đánh giá sản phẩm đã mua | Complaints | 🔴 High |
| N.4 | Đăng ký Producer | Producer đăng ký tài khoản với thông tin kinh doanh | Auth | 🔴 High |
| N.5 | Xác thực email/OTP | Xác thực email khi đăng ký | Auth | 🔴 High |
| N.6 | Wishlist (Yêu thích) | Consumer lưu sản phẩm yêu thích | Mobile | 🔴 High |
| N.7 | Giỏ hàng (Cart) | Quản lý giỏ hàng | Mobile | 🔴 High |
| N.8 | Notification | Thông báo push/email | System | 🔴 High |

### 🟡 Cần thêm (Medium Priority)

| STT | Function | Mô tả | Module | Priority |
|-----|----------|-------|--------|----------|
| N.9 | Export báo cáo | Xuất báo cáo Excel/PDF | Dashboard | 🟡 Medium |
| N.10 | Lịch sử hoạt động | Audit log các thao tác | System | 🟡 Medium |
| N.11 | Tìm kiếm nâng cao | Search với nhiều tiêu chí | Products | 🟡 Medium |
| N.12 | Lọc sản phẩm theo vùng | Filter products by region | Products | 🟡 Medium |
| N.13 | Chat/Message | Nhắn tin giữa buyer và seller | Communication | 🟡 Medium |
| N.14 | Theo dõi vận chuyển | Tracking đơn hàng | Orders | 🟡 Medium |
| N.15 | Mã giảm giá/Voucher | Quản lý và áp dụng mã giảm giá | Promotions | 🟡 Medium |
| N.16 | Flash sale | Chương trình khuyến mãi | Promotions | 🟡 Medium |

### 🟢 Cần thêm (Low Priority)

| STT | Function | Mô tả | Module | Priority |
|-----|----------|-------|--------|----------|
| N.17 | Social login | Đăng nhập qua Google/Facebook | Auth | 🟢 Low |
| N.18 | Live streaming | Producer livestream bán hàng | Content | 🟢 Low |
| N.19 | AI Recommendation | Gợi ý sản phẩm theo AI | Analytics | 🟢 Low |
| N.20 | Multi-language | Hỗ trợ đa ngôn ngữ | System | 🟢 Low |

---

## 📊 Thống kê tổng hợp

| Module | Số chức năng hiện có | Số chức năng cần thêm |
|--------|---------------------|----------------------|
| Authentication | 5 | 5 |
| User Management | 8 | 0 |
| Dashboard | 5 | 1 |
| Products | 7 | 2 |
| Orders | 4 | 1 |
| Organizations | 8 | 0 |
| Content | 6 | 0 |
| Contracts | 5 | 0 |
| Payments | 7 | 0 |
| Complaints | 3 | 1 |
| Categories | 5 | 0 |
| Media | 5 | 0 |
| Roles | 4 | 0 |
| Permissions | 4 | 0 |
| Regions | 5 | 0 |
| Statistics | 5 | 0 |
| Mobile App | 14 | 2 |
| **TỔNG CỘNG** | **90+** | **12+** |

---

*Document generated by Claude AI - Last updated: 02/02/2026*
