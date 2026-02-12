# Product Backlog - Hệ thống CMS Nông sản

> **Ngày tạo:** 02/02/2026  
> **Product Owner:** [Tên Product Owner]  
> **Scrum Master:** [Tên Scrum Master]

---

## 📋 Quy ước

- **Priority**: Must Have (🔴) > Should Have (🟡) > Could Have (🟢)
- **Status**: ✅ Hoàn thành | 🔄 Đang làm | ⏳ Chưa làm
- **Story Points**: Fibonacci scale (1, 2, 3, 5, 8, 13, 21)

---

# 🏃 SPRINT 1 - Authentication & User Management (ĐÃ HOÀN THÀNH)

**Sprint Goal**: Xây dựng hệ thống xác thực và quản lý người dùng cơ bản

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Auth | US-AUTH-001 | Đăng ký tài khoản | Người dùng mới | Đăng ký tài khoản với email | Tôi có thể sử dụng hệ thống | 🔴 Must | Đăng ký với email, password, name | 1. Nhập email, password, name 2. Password ≥ 8 ký tự 3. Email duy nhất | 5 | ✅ |
| Auth | US-AUTH-002 | Đăng nhập | Người dùng | Đăng nhập vào hệ thống | Tôi có thể truy cập tài khoản | 🔴 Must | Đăng nhập và nhận JWT token | 1. Nhập email, password 2. Nhận JWT token 3. Token hết hạn sau 24h | 3 | ✅ |
| Auth | US-AUTH-003 | Lấy thông tin user | Người dùng đã đăng nhập | Xem thông tin tài khoản | Tôi biết thông tin cá nhân | 🔴 Must | API lấy user info với roles và permissions | 1. Trả về user info 2. Bao gồm roles, permissions | 2 | ✅ |
| Auth | US-AUTH-004 | Đăng xuất | Người dùng | Đăng xuất khỏi hệ thống | Bảo mật tài khoản | 🔴 Must | Logout và xóa token | 1. Xóa token 2. Redirect về login | 1 | ✅ |
| Auth | US-AUTH-005 | Làm mới token | Người dùng | Refresh token khi hết hạn | Không cần đăng nhập lại | 🟡 Should | Refresh JWT token | 1. Gửi token cũ 2. Nhận token mới | 2 | ✅ |
| User | US-USER-001 | Danh sách users | Admin | Xem danh sách người dùng | Quản lý users | 🔴 Must | Lấy danh sách với filter, phân trang | 1. Phân trang 2. Filter theo type, activated 3. Tìm kiếm | 3 | ✅ |
| User | US-USER-002 | Tạo user | Admin | Tạo tài khoản cho người dùng | Thêm user mới | 🔴 Must | Admin tạo user | 1. Nhập thông tin 2. Set password 3. Gán role | 3 | ✅ |
| User | US-USER-003 | Cập nhật user | Admin | Sửa thông tin user | Cập nhật thông tin | 🔴 Must | Sửa user | 1. Sửa name, gender, type 2. Không sửa được password | 2 | ✅ |
| User | US-USER-004 | Xóa user | Admin | Vô hiệu hóa user | Loại bỏ user vi phạm | 🔴 Must | Soft delete | 1. Đánh dấu deleted_at 2. User không thể đăng nhập | 2 | ✅ |
| User | US-USER-005 | Kích hoạt/Vô hiệu hóa | Admin | Bật/tắt tài khoản | Kiểm soát truy cập | 🔴 Must | Toggle activated | 1. Set activated = 0/1 2. Thông báo | 1 | ✅ |
| User | US-USER-006 | Gán roles | Admin | Gán vai trò cho user | Phân quyền | 🔴 Must | Assign roles to user | 1. Chọn roles 2. Xóa roles cũ 3. Gán roles mới | 3 | ✅ |

**Tổng Sprint 1:** 27 SP | **Status:** ✅ HOÀN THÀNH

---

# 🏃 SPRINT 2 - Products & Categories (ĐÃ HOÀN THÀNH)

**Sprint Goal**: Quản lý sản phẩm và danh mục

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Product | US-PROD-001 | Danh sách sản phẩm | Người dùng | Xem danh sách sản phẩm | Tìm sản phẩm cần mua | 🔴 Must | Lấy danh sách với filter | 1. Phân trang 2. Filter status, label 3. Tìm kiếm | 5 | ✅ |
| Product | US-PROD-002 | Chi tiết sản phẩm | Người dùng | Xem chi tiết sản phẩm | Biết thông tin đầy đủ | 🔴 Must | API get product by ID | 1. Thông tin đầy đủ 2. Bao gồm producer info | 2 | ✅ |
| Product | US-PROD-003 | Tạo sản phẩm | Producer | Đăng sản phẩm mới | Bán hàng trên nền tảng | 🔴 Must | Tạo sản phẩm chờ duyệt | 1. Nhập thông tin 2. Upload ảnh 3. Trạng thái PENDING | 5 | ✅ |
| Product | US-PROD-004 | Cập nhật sản phẩm | Producer | Sửa thông tin sản phẩm | Cập nhật thông tin | 🔴 Must | Update product | 1. Sửa name, price, description 2. Chuyển về PENDING | 3 | ✅ |
| Product | US-PROD-005 | Xóa sản phẩm | Producer/Admin | Xóa sản phẩm | Loại bỏ sản phẩm | 🔴 Must | Delete product | 1. Xóa khỏi danh sách 2. Xóa ảnh liên quan | 2 | ✅ |
| Product | US-PROD-006 | Duyệt sản phẩm | Admin | Duyệt sản phẩm của producer | Kiểm soát chất lượng | 🔴 Must | Approve/reject product | 1. Duyệt/Từ chối 2. Ghi chú lý do 3. Thông báo producer | 5 | ✅ |
| Product | US-PROD-007 | Gắn nhãn sản phẩm | Admin | Gắn nhãn OCOP/Nông sản sạch | Phân loại sản phẩm | 🟡 Should | Update label | 1. Chọn label 2. Cập nhật thành công | 2 | ✅ |
| Category | US-CAT-001 | Danh sách danh mục | Người dùng | Xem danh mục sản phẩm | Tìm kiếm theo nhóm | 🔴 Must | Get categories | 1. Danh sách phân cấp 2. Filter is_active | 3 | ✅ |
| Category | US-CAT-002 | Tạo danh mục | Admin | Thêm danh mục mới | Tổ chức sản phẩm | 🔴 Must | Create category | 1. Nhập name 2. Chọn parent 3. Tự động tạo slug | 3 | ✅ |
| Category | US-CAT-003 | Cập nhật danh mục | Admin | Sửa danh mục | Cập nhật thông tin | 🔴 Must | Update category | 1. Sửa name, description 2. Cập nhật slug | 2 | ✅ |
| Category | US-CAT-004 | Xóa danh mục | Admin | Xóa danh mục | Loại bỏ không cần thiết | 🔴 Must | Delete category | 1. Kiểm tra subcategories 2. Xóa nếu không có con | 2 | ✅ |

**Tổng Sprint 2:** 34 SP | **Status:** ✅ HOÀN THÀNH

---

# 🏃 SPRINT 3 - Orders & Payments (ĐÃ HOÀN THÀNH)

**Sprint Goal**: Hệ thống đặt hàng và thanh toán

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Order | US-ORD-001 | Danh sách đơn hàng | Admin/Seller | Xem danh sách đơn hàng | Quản lý đơn hàng | 🔴 Must | Get orders với filter | 1. Phân trang 2. Filter theo status 3. Tìm theo order number | 5 | ✅ |
| Order | US-ORD-002 | Chi tiết đơn hàng | User | Xem chi tiết đơn hàng | Biết thông tin đơn | 🔴 Must | Get order by ID | 1. Thông tin đơn 2. Danh sách items 3. Thông tin thanh toán | 3 | ✅ |
| Order | US-ORD-003 | Cập nhật trạng thái | Admin/Seller | Thay đổi trạng thái đơn | Xử lý đơn hàng | 🔴 Must | Update order status | 1. Chọn status mới 2. Ghi chú 3. Thông báo customer | 5 | ✅ |
| Order | US-ORD-004 | Thống kê đơn hàng | Admin | Xem thống kê đơn | Theo dõi kinh doanh | 🟡 Should | Order statistics | 1. Tổng đơn 2. Theo status 3. Doanh thu | 3 | ✅ |
| Payment | US-PAY-001 | Danh sách thanh toán | Admin | Xem thanh toán | Quản lý tài chính | 🔴 Must | Get payments | 1. Phân trang 2. Filter status | 3 | ✅ |
| Payment | US-PAY-002 | Trạng thái thanh toán | User | Kiểm tra thanh toán | Biết trạng thái | 🔴 Must | Get payment status | 1. Trạng thái hiện tại | 2 | ✅ |
| Payment | US-PAY-003 | Đối soát thanh toán | Admin | Xem báo cáo đối soát | Kiểm tra tài chính | 🟡 Should | Payment reconciliation | 1. Tổng hợp theo ngày 2. Platform fee 3. Seller amount | 5 | ✅ |
| Payment | US-PAY-004 | Hoàn tiền | Admin | Xử lý hoàn tiền | Giải quyết khiếu nại | 🔴 Must | Process refund | 1. Chọn đơn 2. Nhập số tiền 3. Ghi lý do | 5 | ✅ |
| Payment | US-PAY-005 | Cấu hình phí nền tảng | Admin | Đặt % phí platform | Quản lý doanh thu | 🟡 Should | Update platform fee | 1. Nhập % 2. Áp dụng cho đơn mới | 2 | ✅ |

**Tổng Sprint 3:** 33 SP | **Status:** ✅ HOÀN THÀNH

---

# 🏃 SPRINT 4 - Content & Organizations (ĐÃ HOÀN THÀNH)

**Sprint Goal**: Quản lý nội dung và tổ chức

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Content | US-CNT-001 | Danh sách nội dung | User | Xem bài viết | Tìm thông tin | 🔴 Must | Get contents | 1. Phân trang 2. Filter type, status | 3 | ✅ |
| Content | US-CNT-002 | Chi tiết nội dung | User | Đọc bài viết | Xem thông tin đầy đủ | 🔴 Must | Get content by ID | 1. Nội dung đầy đủ 2. Thông tin author | 2 | ✅ |
| Content | US-CNT-003 | Tạo nội dung | Producer | Đăng bài viết | Quảng bá sản phẩm | 🔴 Must | Create content | 1. Nhập title, content 2. Upload media 3. Chờ duyệt | 5 | ✅ |
| Content | US-CNT-004 | Cập nhật nội dung | Producer | Sửa bài viết | Cập nhật thông tin | 🔴 Must | Update content | 1. Sửa title, content 2. Cập nhật media | 3 | ✅ |
| Content | US-CNT-005 | Xóa nội dung | Producer/Admin | Xóa bài viết | Loại bỏ nội dung | 🔴 Must | Delete content | 1. Xóa bài 2. Xóa media liên quan | 2 | ✅ |
| Content | US-CNT-006 | Duyệt nội dung | Admin | Kiểm duyệt bài | Kiểm soát nội dung | 🔴 Must | Approve content | 1. Duyệt/Từ chối 2. Ghi chú | 3 | ✅ |
| Org | US-ORG-001 | Danh sách tổ chức | Admin | Xem HTX, làng nghề | Quản lý tổ chức | 🔴 Must | Get organizations | 1. Phân trang 2. Tìm kiếm | 3 | ✅ |
| Org | US-ORG-002 | Chi tiết tổ chức | User | Xem thông tin tổ chức | Biết về HTX | 🔴 Must | Get org by ID | 1. Thông tin đầy đủ 2. Số thành viên | 2 | ✅ |
| Org | US-ORG-003 | Tạo tổ chức | Admin | Thêm HTX mới | Mở rộng mạng lưới | 🔴 Must | Create organization | 1. Nhập thông tin 2. Tạo thành công | 3 | ✅ |
| Org | US-ORG-004 | Quản lý thành viên | Admin | Thêm/xóa thành viên | Quản lý HTX | 🔴 Must | Manage members | 1. Thêm user vào 2. Xóa user khỏi | 5 | ✅ |

**Tổng Sprint 4:** 31 SP | **Status:** ✅ HOÀN THÀNH

---

# 🏃 SPRINT 5 - System Management & Dashboard (ĐÃ HOÀN THÀNH)

**Sprint Goal**: Quản lý hệ thống và dashboard

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Dashboard | US-DASH-001 | Tổng quan hệ thống | Admin | Xem thống kê tổng quan | Nắm bắt tình hình | 🔴 Must | Dashboard overview | 1. Tổng users, products, orders 2. Doanh thu | 5 | ✅ |
| Dashboard | US-DASH-002 | Thống kê doanh thu | Admin | Xem doanh thu theo kỳ | Theo dõi kinh doanh | 🔴 Must | Revenue stats | 1. Theo ngày/tuần/tháng 2. Platform fee 3. Seller amount | 5 | ✅ |
| Dashboard | US-DASH-003 | Thống kê sản phẩm | Admin | Xem phân bố sản phẩm | Phân tích dữ liệu | 🟡 Should | Product stats | 1. Theo status 2. Theo label | 3 | ✅ |
| Dashboard | US-DASH-004 | Thống kê đơn hàng | Admin | Xem tình trạng đơn | Quản lý vận hành | 🟡 Should | Order stats | 1. Theo status 2. Đơn gần đây | 3 | ✅ |
| Dashboard | US-DASH-005 | Thống kê users | Admin | Xem phân bố user | Hiểu khách hàng | 🟡 Should | User stats | 1. Producer/Consumer 2. Active/Inactive | 3 | ✅ |
| Role | US-ROLE-001 | Quản lý roles | Admin | CRUD roles | Phân quyền | 🔴 Must | Manage roles | 1. Tạo role 2. Sửa 3. Xóa | 5 | ✅ |
| Permission | US-PERM-001 | Quản lý permissions | Admin | CRUD permissions | Phân quyền chi tiết | 🔴 Must | Manage permissions | 1. Tạo permission 2. Gán cho role | 5 | ✅ |
| Region | US-REG-001 | Quản lý vùng miền | Admin | CRUD regions | Phân loại địa lý | 🟡 Should | Manage regions | 1. Tạo 2. Sửa 3. Xóa | 5 | ✅ |
| Media | US-MED-001 | Quản lý media | User | Upload/quản lý file | Quản lý tài nguyên | 🔴 Must | Media management | 1. Upload 2. List 3. Delete | 5 | ✅ |
| Contract | US-CON-001 | Quản lý hợp đồng | Admin | CRUD hợp đồng đối tác | Quản lý đối tác | 🟡 Should | Manage contracts | 1. Tạo 2. Sửa 3. Xóa 4. Theo dõi status | 5 | ✅ |

**Tổng Sprint 5:** 44 SP | **Status:** ✅ HOÀN THÀNH

---

# 🏃 SPRINT 6 - Mobile App API (ĐÃ HOÀN THÀNH)

**Sprint Goal**: API cho ứng dụng di động

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Mobile | US-MOB-001 | Danh sách posts public | Người dùng mobile | Xem bài viết đã duyệt | Tìm hiểu sản phẩm | 🔴 Must | Get public posts | 1. Chỉ hiện APPROVED 2. Phân trang | 3 | ✅ |
| Mobile | US-MOB-002 | Chi tiết post | Người dùng mobile | Xem chi tiết bài | Đọc đầy đủ | 🔴 Must | Get post detail | 1. Nội dung đầy đủ 2. Author info | 2 | ✅ |
| Mobile | US-MOB-003 | Producer tạo post | Producer | Đăng bài trên mobile | Quảng bá sản phẩm | 🔴 Must | Create post | 1. Nhập nội dung 2. Upload ảnh | 5 | ✅ |
| Mobile | US-MOB-004 | Quản lý posts của tôi | Producer | Xem/sửa/xóa bài của tôi | Quản lý nội dung | 🔴 Must | My posts CRUD | 1. List 2. Update 3. Delete | 5 | ✅ |
| Mobile | US-MOB-005 | Danh sách sản phẩm | Người dùng mobile | Xem sản phẩm | Tìm mua | 🔴 Must | Get products | 1. Sản phẩm APPROVED 2. Filter giá, nhãn | 5 | ✅ |
| Mobile | US-MOB-006 | Chi tiết sản phẩm | Người dùng mobile | Xem chi tiết sản phẩm | Quyết định mua | 🔴 Must | Product detail | 1. Thông tin đầy đủ 2. Producer info | 2 | ✅ |
| Mobile | US-MOB-007 | Đặt hàng | Consumer | Mua sản phẩm | Sở hữu sản phẩm | 🔴 Must | Create order | 1. Thêm vào giỏ 2. Nhập địa chỉ 3. Thanh toán | 8 | ✅ |
| Mobile | US-MOB-008 | Đơn hàng của tôi | Consumer | Xem đơn đã đặt | Theo dõi đơn | 🔴 Must | My orders | 1. Danh sách 2. Chi tiết 3. Trạng thái | 5 | ✅ |
| Mobile | US-MOB-009 | Profile | Người dùng | Xem/sửa profile | Quản lý thông tin | 🔴 Must | Profile CRUD | 1. Xem 2. Cập nhật | 3 | ✅ |

**Tổng Sprint 6:** 38 SP | **Status:** ✅ HOÀN THÀNH

---

# 🏃 SPRINT 7 - Complaints & Reviews (ĐÃ HOÀN THÀNH)

**Sprint Goal**: Hệ thống khiếu nại và đánh giá

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Review | US-REV-001 | Danh sách đánh giá | Admin | Xem đánh giá sản phẩm | Theo dõi phản hồi | 🔴 Must | Get reviews | 1. Phân trang 2. Filter product_id | 3 | ✅ |
| Complaint | US-CMP-001 | Danh sách khiếu nại | Admin | Xem khiếu nại | Xử lý vấn đề | 🔴 Must | Get complaints | 1. Phân trang 2. Filter status, type | 3 | ✅ |
| Complaint | US-CMP-002 | Xử lý khiếu nại | Admin | Giải quyết khiếu nại | Hỗ trợ khách hàng | 🔴 Must | Handle complaint | 1. Cập nhật status 2. Ghi resolution 3. Thông báo user | 5 | ✅ |
| Stats | US-STAT-001 | Thống kê producer | Admin | Xem stats producer | Phân tích đối tác | 🟡 Should | Producer stats | 1. Tổng 2. Active/Inactive 3. Mới trong tháng | 3 | ✅ |
| Stats | US-STAT-002 | Thống kê consumer | Admin | Xem stats consumer | Phân tích KH | 🟡 Should | Consumer stats | 1. Tổng 2. Active 3. Mới trong tháng | 3 | ✅ |
| Stats | US-STAT-003 | Sản phẩm trending | Admin | Xem top sản phẩm | Phân tích bán hàng | 🟡 Should | Trending products | 1. Top N products 2. Order count | 3 | ✅ |

**Tổng Sprint 7:** 20 SP | **Status:** ✅ HOÀN THÀNH

---

# 🏃 SPRINT 8 - Authentication Enhancement (CHƯA LÀM)

**Sprint Goal**: Hoàn thiện tính năng xác thực còn thiếu

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Auth | US-AUTH-006 | Quên mật khẩu | Người dùng | Khôi phục mật khẩu | Truy cập lại tài khoản | 🔴 Must | Gửi link reset qua email | 1. Nhập email 2. Nhận link 3. Reset password | 5 | ⏳ |
| Auth | US-AUTH-007 | Đổi mật khẩu | Người dùng | Thay đổi mật khẩu | Bảo mật tài khoản | 🔴 Must | Đổi password | 1. Nhập cũ 2. Nhập mới 3. Xác nhận | 3 | ⏳ |
| Auth | US-AUTH-008 | Xác thực OTP | Người dùng mới | Xác thực email | Xác minh email | 🔴 Must | Gửi và verify OTP | 1. Gửi OTP 2. Nhập OTP 3. Verify | 5 | ⏳ |
| Auth | US-AUTH-009 | Đăng ký Producer | Người bán | Đăng ký bán hàng | Bán trên nền tảng | 🔴 Must | Đăng ký với thông tin KD | 1. Thông tin chi tiết 2. Upload giấy phép 3. Chờ duyệt | 8 | ⏳ |
| User | US-USER-007 | Upload avatar | Người dùng | Thay ảnh đại diện | Cá nhân hóa | 🟡 Should | Upload và crop avatar | 1. Upload 2. Crop 3. Save | 3 | ⏳ |

**Tổng Sprint 8:** 24 SP | **Status:** ⏳ CHƯA LÀM

---

# 🏃 SPRINT 9 - Mobile Shopping Enhancement (CHƯA LÀM)

**Sprint Goal**: Nâng cao trải nghiệm mua sắm mobile

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Cart | US-CART-001 | Giỏ hàng | Consumer | Quản lý giỏ hàng | Mua nhiều sản phẩm | 🔴 Must | Cart CRUD | 1. Thêm/xóa 2. Thay đổi SL 3. Lưu local | 8 | ⏳ |
| Wishlist | US-WISH-001 | Yêu thích | Consumer | Lưu sản phẩm yêu thích | Xem lại sau | 🔴 Must | Wishlist CRUD | 1. Thêm/bỏ 2. Danh sách | 5 | ⏳ |
| Review | US-REV-002 | Đánh giá sản phẩm | Consumer | Đánh giá sản phẩm đã mua | Chia sẻ trải nghiệm | 🔴 Must | Create review | 1. 1-5 sao 2. Comment 3. Upload ảnh | 5 | ⏳ |
| Noti | US-NOTI-001 | Push notification | Người dùng | Nhận thông báo | Cập nhật đơn hàng | 🔴 Must | Push notifications | 1. Order updates 2. Promotions | 13 | ⏳ |
| Noti | US-NOTI-002 | Lịch sử thông báo | Người dùng | Xem thông báo cũ | Xem lại thông tin | 🟡 Should | Notification list | 1. Danh sách 2. Mark as read | 3 | ⏳ |

**Tổng Sprint 9:** 34 SP | **Status:** ⏳ CHƯA LÀM

---

# 🏃 SPRINT 10 - Order & Delivery Tracking (CHƯA LÀM)

**Sprint Goal**: Theo dõi đơn hàng và vận chuyển

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Order | US-ORD-005 | Tracking vận chuyển | Consumer | Theo dõi đơn đang giao | Biết đơn ở đâu | 🟡 Should | Order tracking | 1. Timeline 2. Vị trí (nếu có) | 8 | ⏳ |
| Order | US-ORD-006 | Hủy đơn hàng | Consumer | Hủy đơn PENDING | Thay đổi quyết định | 🔴 Must | Cancel order | 1. Chỉ PENDING 2. Chọn lý do | 3 | ⏳ |
| Order | US-ORD-007 | Xác nhận nhận hàng | Consumer | Xác nhận đã nhận | Hoàn tất đơn | 🔴 Must | Confirm received | 1. Bấm xác nhận 2. Chuyển DELIVERED | 2 | ⏳ |
| Seller | US-SELL-001 | Dashboard seller | Producer | Xem doanh thu | Theo dõi hiệu quả | 🟡 Should | Seller dashboard | 1. Doanh thu 2. Đơn hàng 3. Biểu đồ | 8 | ⏳ |
| Seller | US-SELL-002 | Quản lý SP mobile | Producer | CRUD sản phẩm mobile | Quản lý dễ dàng | 🔴 Must | Mobile product mgmt | 1. Thêm 2. Sửa 3. Xem status | 8 | ⏳ |

**Tổng Sprint 10:** 29 SP | **Status:** ⏳ CHƯA LÀM

---

# 🏃 SPRINT 11 - Promotions System (CHƯA LÀM)

**Sprint Goal**: Hệ thống khuyến mãi

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Voucher | US-PROMO-001 | Tạo voucher | Admin | Tạo mã giảm giá | Khuyến khích mua | 🟡 Should | CRUD voucher | 1. Code 2. % hoặc VNĐ 3. Điều kiện | 8 | ⏳ |
| Voucher | US-PROMO-002 | Áp dụng voucher | Consumer | Dùng mã giảm giá | Được giảm giá | 🟡 Should | Apply voucher | 1. Nhập code 2. Validate 3. Áp dụng | 5 | ⏳ |
| Flash | US-PROMO-003 | Flash sale | Admin | Tạo flash sale | Thu hút KH | 🟢 Could | Flash sale mgmt | 1. Chọn SP 2. Giá sale 3. Thời gian | 8 | ⏳ |
| Banner | US-MKT-001 | Banner quảng cáo | Admin | Quản lý banner | Quảng bá | 🟡 Should | Banner CRUD | 1. Upload 2. Link 3. Order | 5 | ⏳ |
| Feature | US-MKT-002 | SP nổi bật | Admin | Đánh dấu featured | Ưu tiên hiển thị | 🟡 Should | Featured products | 1. Mark 2. Hiển thị trang chủ | 3 | ⏳ |

**Tổng Sprint 11:** 29 SP | **Status:** ⏳ CHƯA LÀM

---

# 🏃 SPRINT 12 - Communication & Support (CHƯA LÀM)

**Sprint Goal**: Giao tiếp và hỗ trợ

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Chat | US-CHAT-001 | Chat với seller | Consumer | Nhắn tin với seller | Hỏi sản phẩm | 🟡 Should | Real-time chat | 1. Text 2. Ảnh 3. Notification | 13 | ⏳ |
| Chat | US-CHAT-002 | Danh sách chat | User | Xem conversations | Quản lý chat | 🟡 Should | Chat list | 1. Danh sách 2. Sort by time 3. Unread badge | 5 | ⏳ |
| Support | US-SUP-001 | Tạo ticket | User | Gửi yêu cầu hỗ trợ | Được giải đáp | 🟡 Should | Create ticket | 1. Chọn loại 2. Mô tả 3. Attach | 5 | ⏳ |
| Support | US-SUP-002 | Quản lý ticket | Admin | Xử lý ticket | Hỗ trợ KH | 🟡 Should | Ticket mgmt | 1. List 2. Assign 3. Reply 4. Close | 5 | ⏳ |
| FAQ | US-FAQ-001 | Xem FAQ | User | Xem câu hỏi thường gặp | Tự tìm câu trả lời | 🟢 Could | FAQ list | 1. Danh sách 2. Search 3. Categories | 3 | ⏳ |

**Tổng Sprint 12:** 31 SP | **Status:** ⏳ CHƯA LÀM

---

# 🏃 SPRINT 13 - Analytics & Reporting (CHƯA LÀM)

**Sprint Goal**: Báo cáo và phân tích

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Export | US-REP-001 | Xuất Excel | Admin | Xuất báo cáo Excel | Phân tích offline | 🟡 Should | Export to Excel | 1. Chọn loại 2. Chọn ngày 3. Download | 5 | ⏳ |
| Export | US-REP-002 | Xuất PDF | Admin | Xuất báo cáo PDF | In ấn lưu trữ | 🟢 Could | Export to PDF | 1. Định dạng đẹp 2. Logo 3. Date | 5 | ⏳ |
| Chart | US-ANA-001 | Biểu đồ doanh thu | Admin | Xem chart doanh thu | Theo dõi xu hướng | 🟡 Should | Revenue chart | 1. Line chart 2. So sánh kỳ | 5 | ⏳ |
| Chart | US-ANA-002 | Phân tích SP | Admin | Xem top sản phẩm | Quyết định KD | 🟡 Should | Product analytics | 1. Top bán chạy 2. Theo danh mục | 5 | ⏳ |
| Audit | US-AUD-001 | Activity log | Admin | Xem log hoạt động | Kiểm tra | 🟡 Should | Audit log | 1. Ghi log 2. Filter 3. Export | 8 | ⏳ |

**Tổng Sprint 13:** 28 SP | **Status:** ⏳ CHƯA LÀM

---

# 🏃 SPRINT 14 - Advanced Features (CHƯA LÀM)

**Sprint Goal**: Tính năng nâng cao

| FEATURE | User Story ID | User Story Title | AS A/AN (Là) | I NEED TO (Tôi cần…) | SO THAT I CAN (Để…) | PRIORITY | USER STORY DESCRIPTION | ACCEPTANCE CRITERIA | STORY POINT | STATUS |
|---------|---------------|------------------|--------------|----------------------|---------------------|----------|------------------------|---------------------|-------------|--------|
| Search | US-SRCH-001 | Tìm kiếm nâng cao | Consumer | Tìm với nhiều filter | Tìm SP phù hợp | 🟡 Should | Advanced search | 1. Giá 2. Vùng 3. Nhãn 4. Rating | 8 | ⏳ |
| OAuth | US-SOC-001 | Google login | User | Đăng nhập Google | Đăng nhập nhanh | 🟢 Could | Google OAuth | 1. Bấm login 2. Chọn TK 3. Auto create | 5 | ⏳ |
| OAuth | US-SOC-002 | Facebook login | User | Đăng nhập Facebook | Tiện lợi | 🟢 Could | Facebook OAuth | 1. Bấm login 2. Cấp quyền 3. Login | 5 | ⏳ |
| Share | US-SHR-001 | Chia sẻ sản phẩm | User | Share lên mạng XH | Giới thiệu SP | 🟢 Could | Share product | 1. Bấm share 2. Chọn platform 3. Generate link | 3 | ⏳ |
| i18n | US-LANG-001 | Đa ngôn ngữ | User | Chuyển ngôn ngữ | Dùng ngôn ngữ quen | 🟢 Could | Multi-language | 1. Chọn ngôn ngữ 2. Switch toàn app | 13 | ⏳ |

**Tổng Sprint 14:** 34 SP | **Status:** ⏳ CHƯA LÀM

---

## 📊 TỔNG HỢP PRODUCT BACKLOG

| Sprint | Mục tiêu | Story Points | Status |
|--------|----------|--------------|--------|
| Sprint 1 | Authentication & User Management | 27 | ✅ Hoàn thành |
| Sprint 2 | Products & Categories | 34 | ✅ Hoàn thành |
| Sprint 3 | Orders & Payments | 33 | ✅ Hoàn thành |
| Sprint 4 | Content & Organizations | 31 | ✅ Hoàn thành |
| Sprint 5 | System Management & Dashboard | 44 | ✅ Hoàn thành |
| Sprint 6 | Mobile App API | 38 | ✅ Hoàn thành |
| Sprint 7 | Complaints & Reviews | 20 | ✅ Hoàn thành |
| Sprint 8 | Authentication Enhancement | 24 | ⏳ Chưa làm |
| Sprint 9 | Mobile Shopping Enhancement | 34 | ⏳ Chưa làm |
| Sprint 10 | Order & Delivery Tracking | 29 | ⏳ Chưa làm |
| Sprint 11 | Promotions System | 29 | ⏳ Chưa làm |
| Sprint 12 | Communication & Support | 31 | ⏳ Chưa làm |
| Sprint 13 | Analytics & Reporting | 28 | ⏳ Chưa làm |
| Sprint 14 | Advanced Features | 34 | ⏳ Chưa làm |
| **TỔNG CỘNG** | | **436 SP** | **7/14 Sprints** |

---

## 📈 Tiến độ dự án

```
Đã hoàn thành: ████████████████████░░░░░░░░░░░░░ 50%
                     7/14 Sprints
                     227/436 Story Points
```

### Release Plan

| Release | Sprints | Status | Description |
|---------|---------|--------|-------------|
| **v1.0 (MVP)** | 1-7 | ✅ Done | Core CMS, Products, Orders, Mobile API |
| **v1.1** | 8-10 | ⏳ Planned | Enhanced Auth, Shopping, Order Tracking |
| **v2.0** | 11-12 | ⏳ Planned | Promotions, Communication |
| **v2.1** | 13-14 | ⏳ Planned | Analytics, Advanced Features |

---

*Document generated - Last updated: 02/02/2026*
