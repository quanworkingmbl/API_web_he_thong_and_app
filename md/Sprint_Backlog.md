# Detailed Sprint Backlog – Hệ thống Marketplace Nông sản & Làng nghề

> Tài liệu được phân tích từ source code thực tế. Cập nhật: 2026-03-12
>
> **Ghi chú về Story Point:** Story Point là ước lượng của User Story cha; task con trong Sprint Backlog được ước lượng bằng **Est. (h)** (số giờ), không cộng task để ra Story Point.
>
> **Ghi chú về team:**
> - **Backend / Backend/API**: Xử lý nghiệp vụ, database, API endpoint
> - **FE/CMS**: Web quản trị dành cho Admin và Seller
> - **FE/Mobile**: Ứng dụng mobile dành cho Customer

| Sprint | User Story ID | User Story Description | Story Points | Task ID | Task Description | Team | Est. (h) | Status | Priority |
|--------|---------------|----------------------|--------------|---------|-----------------|------|----------|--------|----------|
| Sprint 1 | US-01 | Đăng ký tài khoản (consumer/producer) | 5 | TASK-01 | Thiết kế bảng `users` với các trường: id, email, password_hash, name, gender, type, activated, created_at, deleted_at | Backend | 2 | Done | High |
| Sprint 1 | US-01 | Đăng ký tài khoản (consumer/producer) | 5 | TASK-02 | Tạo model User (SQLAlchemy ORM) với quan hệ UserRole | Backend | 2 | Done | High |
| Sprint 1 | US-01 | Đăng ký tài khoản (consumer/producer) | 5 | TASK-03 | Tạo schema RegisterRequest (Pydantic) với validate email, password min 8 ký tự | Backend/API | 1 | Done | High |
| Sprint 1 | US-01 | Đăng ký tài khoản (consumer/producer) | 5 | TASK-04 | Viết router POST /api/auth/register – kiểm tra email trùng, hash password, phân biệt activated theo type (producer=0, consumer=1) | Backend/API | 3 | Done | High |
| Sprint 1 | US-02 | Đăng nhập hệ thống | 3 | TASK-05 | Viết module security: hàm hash password (bcrypt), verify password, create JWT token, decode JWT token | Backend | 3 | Done | High |
| Sprint 1 | US-02 | Đăng nhập hệ thống | 3 | TASK-06 | Tạo schema LoginRequest (email, password, recaptcha optional) | Backend/API | 0.5 | Done | High |
| Sprint 1 | US-02 | Đăng nhập hệ thống | 3 | TASK-07 | Viết router POST /api/auth/login – xác thực email/password, kiểm tra activated, trả JWT token với expires_at | Backend/API | 2 | Done | High |
| Sprint 1 | US-02 | Đăng nhập hệ thống | 3 | TASK-08 | Cấu hình settings: SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, DATABASE_URL | Backend | 1 | Done | High |
| Sprint 1 | US-03 | Xem thông tin cá nhân (GET /me) | 2 | TASK-09 | Viết dependency get_current_user – decode token, validate user_id, kiểm tra deleted_at và activated | Backend | 2 | Done | High |
| Sprint 1 | US-03 | Xem thông tin cá nhân (GET /me) | 2 | TASK-10 | Viết router GET /api/auth/me – trả user info kèm roles và permissions (join UserRole → Role → RolePermission → Permission) | Backend/API | 2 | Done | High |
| Sprint 1 | US-04 | Đăng xuất | 1 | TASK-11 | Viết router POST /api/auth/logout – trả message thành công (client-side token removal) | Backend/API | 0.5 | Done | Medium |
| Sprint 1 | US-05 | Làm mới token (refresh) | 3 | TASK-12 | Viết router POST /api/auth/refresh – yêu cầu token hợp lệ, tạo token mới với thời hạn mới | Backend/API | 1.5 | Done | Medium |
| Sprint 1 | US-05 | Làm mới token (refresh) | 3 | TASK-13 | Viết dependency get_current_user_optional – xác thực tùy chọn, hỗ trợ DEBUG mode mock user | Backend | 1.5 | Done | Medium |
| Sprint 1 | US-06 | Xem danh sách người dùng | 3 | TASK-14 | Viết router GET /api/users – phân trang (page, limit), lọc type, activated, search name/email, loại trừ soft deleted | Backend/API | 3 | Done | High |
| Sprint 1 | US-07 | Tạo người dùng mới (Admin) | 3 | TASK-15 | Tạo schema CreateUserRequest (email, password, name, type, activated) | Backend/API | 0.5 | Done | High |
| Sprint 1 | US-07 | Tạo người dùng mới (Admin) | 3 | TASK-16 | Viết router POST /api/users – kiểm tra email trùng, hash password, tạo user | Backend/API | 2 | Done | High |
| Sprint 1 | US-08 | Xem chi tiết người dùng | 2 | TASK-17 | Viết router GET /api/users/{user_id} – trả thông tin user theo ID, xử lý 404 | Backend/API | 1 | Done | Medium |
| Sprint 1 | US-09 | Cập nhật thông tin người dùng | 3 | TASK-18 | Tạo schema UpdateUserRequest và viết router PUT /api/users/{user_id} – cập nhật name, type, email, kiểm tra email trùng | Backend/API | 2 | Done | High |
| Sprint 1 | US-10 | Xoá người dùng (soft delete) | 2 | TASK-19 | Viết router DELETE /api/users/{user_id} – đánh dấu deleted_at = datetime.now(), không xoá vĩnh viễn | Backend/API | 1 | Done | Medium |
| Sprint 1 | US-11 | Kích hoạt/vô hiệu hoá tài khoản | 2 | TASK-20 | Viết router PUT /api/users/{user_id}/activate – toggle activated (0↔1) | Backend/API | 1 | Done | Medium |
| Sprint 1 | US-12 | Gán role cho người dùng | 3 | TASK-21 | Viết router POST /api/users/{user_id}/roles – xoá UserRole cũ, insert danh sách role_ids mới | Backend/API | 2 | Done | Medium |
| Sprint 1 | US-13 | Xem role của người dùng | 2 | TASK-22 | Viết router GET /api/users/{user_id}/roles – join UserRole → Role, trả danh sách roles | Backend/API | 1 | Done | Medium |
| Sprint 1 | US-14 | Quản lý Role (CRUD) | 5 | TASK-23 | Thiết kế bảng `roles` (id, role_name, description) và bảng `role_permissions` (role_id, permission_id) | Backend | 1 | Done | Medium |
| Sprint 1 | US-14 | Quản lý Role (CRUD) | 5 | TASK-24 | Tạo model Role, RolePermission (SQLAlchemy ORM) | Backend | 1 | Done | Medium |
| Sprint 1 | US-14 | Quản lý Role (CRUD) | 5 | TASK-25 | Viết 4 router CRUD: GET /api/admin/roles (phân trang, search), POST, PUT /{role_id}, DELETE /{role_id} | Backend/API | 3 | Done | Medium |
| Sprint 1 | US-15 | Quản lý Permission (CRUD) | 5 | TASK-26 | Thiết kế bảng `permissions` (id, parent_id, name, label, type, route, status, order, icon, component, hide, hide_tab, frame_src, new_feature) | Backend | 1 | Done | Medium |
| Sprint 1 | US-15 | Quản lý Permission (CRUD) | 5 | TASK-27 | Tạo model Permission (SQLAlchemy ORM) | Backend | 1 | Done | Medium |
| Sprint 1 | US-15 | Quản lý Permission (CRUD) | 5 | TASK-28 | Viết 4 router CRUD: GET /api/admin/permissions (phân trang, search), POST, PUT /{permission_id}, DELETE /{permission_id} | Backend/API | 3 | Done | Medium |
| Sprint 1 | US-01 | Đăng ký tài khoản | 5 | TASK-206 | Thiết kế UI trang đăng ký: form email, password, name, chọn loại tài khoản (consumer/producer) | FE/CMS | 3 | To Do | High |
| Sprint 1 | US-01 | Đăng ký tài khoản | 5 | TASK-207 | Tích hợp API POST /api/auth/register, xử lý validate form, hiển thị thông báo lỗi/thành công | FE/CMS | 2 | To Do | High |
| Sprint 1 | US-02 | Đăng nhập hệ thống | 3 | TASK-208 | Thiết kế UI trang đăng nhập: form email/password, nút Quên mật khẩu, nút Đăng ký | FE/CMS | 2 | To Do | High |
| Sprint 1 | US-02 | Đăng nhập hệ thống | 3 | TASK-209 | Tích hợp API POST /api/auth/login, lưu token vào localStorage/cookie, redirect sau đăng nhập | FE/CMS | 2 | To Do | High |
| Sprint 1 | US-02 | Đăng nhập hệ thống | 3 | TASK-210 | Viết service AuthGuard / middleware xác thực: kiểm tra token, tự động refresh token, redirect nếu hết hạn | FE/CMS | 3 | To Do | High |
| Sprint 1 | US-03 | Xem thông tin cá nhân | 2 | TASK-211 | Thiết kế UI trang Profile cá nhân: hiển thị thông tin user, roles, permissions | FE/CMS | 2 | To Do | Medium |
| Sprint 1 | US-03 | Xem thông tin cá nhân | 2 | TASK-212 | Tích hợp API GET /api/auth/me, lưu user context (React Context / Vuex / Redux) | FE/CMS | 2 | To Do | Medium |
| Sprint 1 | US-04 | Đăng xuất | 1 | TASK-213 | Viết logic đăng xuất: gọi API logout, xoá token, redirect về trang đăng nhập | FE/CMS | 1 | To Do | Medium |
| Sprint 1 | US-06 | Xem danh sách người dùng | 3 | TASK-214 | Thiết kế UI trang Quản lý người dùng: bảng danh sách có phân trang, bộ lọc (type, activated), ô tìm kiếm | FE/CMS | 4 | To Do | High |
| Sprint 1 | US-06 | Xem danh sách người dùng | 3 | TASK-215 | Tích hợp API GET /api/users với query params (page, limit, type, activated, search) | FE/CMS | 2 | To Do | High |
| Sprint 1 | US-07 | Tạo người dùng mới | 3 | TASK-216 | Thiết kế modal/trang Tạo người dùng: form email, password, name, type, activated | FE/CMS | 2 | To Do | High |
| Sprint 1 | US-07 | Tạo người dùng mới | 3 | TASK-217 | Tích hợp API POST /api/users, validate form, hiển thị thông báo kết quả | FE/CMS | 1.5 | To Do | High |
| Sprint 1 | US-08 | Xem chi tiết người dùng | 2 | TASK-218 | Thiết kế UI trang Chi tiết người dùng: thông tin cá nhân, trạng thái, danh sách roles | FE/CMS | 2 | To Do | Medium |
| Sprint 1 | US-09 | Cập nhật thông tin người dùng | 3 | TASK-219 | Thiết kế modal/form Chỉnh sửa người dùng, tích hợp API PUT /api/users/{id} | FE/CMS | 2 | To Do | High |
| Sprint 1 | US-10 | Xoá người dùng (soft delete) | 2 | TASK-220 | Viết dialog xác nhận xoá, tích hợp API DELETE /api/users/{id}, refresh danh sách | FE/CMS | 1 | To Do | Medium |
| Sprint 1 | US-11 | Kích hoạt/vô hiệu hoá tài khoản | 2 | TASK-221 | Viết nút toggle activate trên danh sách/chi tiết user, tích hợp API PUT /api/users/{id}/activate | FE/CMS | 1.5 | To Do | Medium |
| Sprint 1 | US-12 | Gán role cho người dùng | 3 | TASK-222 | Thiết kế UI gán roles: multi-select dropdown roles, tích hợp API POST /api/users/{id}/roles | FE/CMS | 2 | To Do | Medium |
| Sprint 1 | US-14 | Quản lý Role (CRUD) | 5 | TASK-223 | Thiết kế UI trang Quản lý Role: danh sách roles, form tạo/sửa, nút xoá, gán permissions cho role | FE/CMS | 4 | To Do | Medium |
| Sprint 1 | US-14 | Quản lý Role (CRUD) | 5 | TASK-224 | Tích hợp 4 API CRUD roles + API gán permissions | FE/CMS | 2.5 | To Do | Medium |
| Sprint 1 | US-15 | Quản lý Permission (CRUD) | 5 | TASK-225 | Thiết kế UI quản lý Permission: cây permission (tree view parent-child), form tạo/sửa | FE/CMS | 4 | To Do | Medium |
| Sprint 1 | US-15 | Quản lý Permission (CRUD) | 5 | TASK-226 | Tích hợp 4 API CRUD permissions | FE/CMS | 2 | To Do | Medium |
| Sprint 1 | – | Thiết kế hệ thống giao diện | – | TASK-227 | Xây dựng Layout chính CMS: sidebar menu, header (user info, logout), breadcrumb, responsive | FE/CMS | 6 | To Do | High |
| Sprint 1 | – | Thiết kế hệ thống giao diện | – | TASK-228 | Xây dựng bộ component dùng chung: DataTable, Pagination, SearchBar, Modal, Toast notification, Loading spinner | FE/CMS | 8 | To Do | High |
| Sprint 2 | US-16 | Quản lý tổ chức (HTX, Làng nghề) | 5 | TASK-29 | Thiết kế bảng `organizations` (id, name, type, address, phone, description, created_at) và bảng `organization_members` (org_id, user_id) | Backend | 2 | Done | Medium |
| Sprint 2 | US-16 | Quản lý tổ chức (HTX, Làng nghề) | 5 | TASK-30 | Tạo model Organization, OrganizationMember (SQLAlchemy ORM) | Backend | 1 | Done | Medium |
| Sprint 2 | US-16 | Quản lý tổ chức (HTX, Làng nghề) | 5 | TASK-31 | Viết 5 router: GET /api/org (phân trang, search), GET /{org_id}, POST, PUT /{org_id}, DELETE /{org_id} (kiểm tra thành viên trước khi xoá) | Backend/API | 4 | Done | Medium |
| Sprint 2 | US-17 | Quản lý thành viên tổ chức | 3 | TASK-32 | Viết router GET /api/org/{org_id}/members – danh sách thành viên | Backend/API | 1 | Done | Medium |
| Sprint 2 | US-17 | Quản lý thành viên tổ chức | 3 | TASK-33 | Viết router POST /api/org/{org_id}/members – thêm user vào org, kiểm tra user tồn tại | Backend/API | 1.5 | Done | Medium |
| Sprint 2 | US-17 | Quản lý thành viên tổ chức | 3 | TASK-34 | Viết router DELETE /api/org/{org_id}/members/{user_id} – xoá thành viên | Backend/API | 1 | Done | Medium |
| Sprint 2 | US-18 | Quản lý danh mục sản phẩm | 5 | TASK-35 | Thiết kế bảng `categories` (id, parent_id, name, slug, description, is_active, created_at) | Backend | 1 | Done | High |
| Sprint 2 | US-18 | Quản lý danh mục sản phẩm | 5 | TASK-36 | Tạo model Category (SQLAlchemy ORM) với self-referencing parent_id FK | Backend | 1 | Done | High |
| Sprint 2 | US-18 | Quản lý danh mục sản phẩm | 5 | TASK-37 | Viết hàm tự sinh slug từ tên danh mục (unidecode Vietnamese) | Backend | 1 | Done | Medium |
| Sprint 2 | US-18 | Quản lý danh mục sản phẩm | 5 | TASK-38 | Viết 5 router CRUD categories: GET (phân trang, lọc parent_id, is_active, search), GET /{id}, POST, PUT /{id}, DELETE /{id} (chặn xoá nếu có con) | Backend/API | 4 | Done | High |
| Sprint 2 | US-19 | Xem danh sách sản phẩm | 3 | TASK-39 | Viết router GET /api/products – phân trang, lọc status (PENDING/APPROVED/REJECTED), producer_id, label, search theo tên | Backend/API | 3 | Done | High |
| Sprint 2 | US-20 | Xem chi tiết sản phẩm | 2 | TASK-40 | Viết router GET /api/products/{product_id} – trả đầy đủ thông tin sản phẩm, xử lý 404 | Backend/API | 1 | Done | High |
| Sprint 2 | US-21 | Tạo sản phẩm mới | 5 | TASK-41 | Thiết kế bảng `products` (id, name, description, price, stock_quantity, category_id, producer_id, status, label, created_at) | Backend | 2 | Done | High |
| Sprint 2 | US-21 | Tạo sản phẩm mới | 5 | TASK-42 | Tạo model Product với enum ProductStatus (PENDING/APPROVED/REJECTED) và enum ProductLabel (CLEAN_AGRICULTURE/TRADITIONAL_CRAFT/OCOP) | Backend | 1.5 | Done | High |
| Sprint 2 | US-21 | Tạo sản phẩm mới | 5 | TASK-43 | Tạo schema CreateProductRequest (name, description, price, category_id, stock_quantity) | Backend/API | 1 | Done | High |
| Sprint 2 | US-21 | Tạo sản phẩm mới | 5 | TASK-44 | Viết router POST /api/products – gán producer_id = current_user.id, status = PENDING, validate required fields | Backend/API | 2 | Done | High |
| Sprint 2 | US-22 | Cập nhật sản phẩm | 3 | TASK-45 | Viết router PUT /api/products/{product_id} – kiểm tra quyền sở hữu (producer_id == current_user.id), cập nhật partial fields | Backend/API | 2 | Done | High |
| Sprint 2 | US-23 | Xoá sản phẩm | 2 | TASK-46 | Viết router DELETE /api/products/{product_id} – kiểm tra quyền chủ sản phẩm hoặc admin | Backend/API | 1 | Done | Medium |
| Sprint 2 | US-24 | Duyệt/từ chối sản phẩm | 5 | TASK-47 | Thiết kế bảng `product_approvals` (id, product_id, admin_id, action, reason, created_at) | Backend | 1 | Done | High |
| Sprint 2 | US-24 | Duyệt/từ chối sản phẩm | 5 | TASK-48 | Tạo model ProductApproval (SQLAlchemy ORM) | Backend | 0.5 | Done | High |
| Sprint 2 | US-24 | Duyệt/từ chối sản phẩm | 5 | TASK-49 | Viết router POST /api/products/{product_id}/approve – nhận action (APPROVED/REJECTED) + reason, cập nhật product.status, tạo approval record | Backend/API | 3 | Done | High |
| Sprint 2 | US-25 | Gán nhãn sản phẩm | 2 | TASK-50 | Viết router PUT /api/products/{product_id}/label – nhận label enum, validate 3 giá trị hợp lệ, yêu cầu quyền admin | Backend/API | 1.5 | Done | Medium |
| Sprint 2 | US-16 | Quản lý tổ chức (HTX, Làng nghề) | 5 | TASK-229 | Thiết kế UI trang Quản lý tổ chức: danh sách, form tạo/sửa, quản lý thành viên | FE/CMS | 4 | To Do | Medium |
| Sprint 2 | US-16 | Quản lý tổ chức (HTX, Làng nghề) | 5 | TASK-230 | Tích hợp API CRUD tổ chức + API thành viên (GET/POST/DELETE members) | FE/CMS | 3 | To Do | Medium |
| Sprint 2 | US-18 | Quản lý danh mục sản phẩm | 5 | TASK-231 | Thiết kế UI trang Danh mục: hiển thị dạng cây (parent-child), form tạo/sửa, toggle active | FE/CMS | 4 | To Do | High |
| Sprint 2 | US-18 | Quản lý danh mục sản phẩm | 5 | TASK-232 | Tích hợp API CRUD categories, xử lý cây danh mục, auto-slug | FE/CMS | 2.5 | To Do | High |
| Sprint 2 | US-19 | Xem danh sách sản phẩm | 3 | TASK-233 | Thiết kế UI trang Sản phẩm: bảng danh sách có phân trang, bộ lọc (status, label, seller), ô tìm kiếm, badge trạng thái | FE/CMS | 5 | To Do | High |
| Sprint 2 | US-19 | Xem danh sách sản phẩm | 3 | TASK-234 | Tích hợp API GET /api/products với filter và phân trang | FE/CMS | 2 | To Do | High |
| Sprint 2 | US-21 | Tạo sản phẩm mới | 5 | TASK-235 | Thiết kế UI form Tạo sản phẩm: name, description (rich editor), price, stock, category (dropdown), upload ảnh | FE/CMS | 5 | To Do | High |
| Sprint 2 | US-21 | Tạo sản phẩm mới | 5 | TASK-236 | Tích hợp API POST /api/products, upload media, validate form | FE/CMS | 3 | To Do | High |
| Sprint 2 | US-22 | Cập nhật sản phẩm | 3 | TASK-237 | Thiết kế UI form Chỉnh sửa sản phẩm (pre-fill data), tích hợp API PUT /api/products/{id} | FE/CMS | 3 | To Do | High |
| Sprint 2 | US-24 | Duyệt/từ chối sản phẩm | 5 | TASK-238 | Thiết kế UI trang Duyệt sản phẩm: danh sách PENDING, nút Duyệt/Từ chối + form ghi lý do | FE/CMS | 4 | To Do | High |
| Sprint 2 | US-24 | Duyệt/từ chối sản phẩm | 5 | TASK-239 | Tích hợp API POST /api/products/{id}/approve, hiển thị lịch sử duyệt | FE/CMS | 2 | To Do | High |
| Sprint 2 | US-25 | Gán nhãn sản phẩm | 2 | TASK-240 | Viết UI gán nhãn (CLEAN_AGRICULTURE / TRADITIONAL_CRAFT / OCOP) trên trang chi tiết sản phẩm | FE/CMS | 1.5 | To Do | Medium |
| Sprint 3 | US-26 | Xem giỏ hàng | 3 | TASK-51 | Thiết kế bảng `carts` (id, user_id, created_at) và bảng `cart_items` (id, cart_id, product_id, quantity) | Backend | 1.5 | Done | High |
| Sprint 3 | US-26 | Xem giỏ hàng | 3 | TASK-52 | Tạo model Cart, CartItem (SQLAlchemy ORM) với quan hệ FK đến Product | Backend | 1 | Done | High |
| Sprint 3 | US-26 | Xem giỏ hàng | 3 | TASK-53 | Viết router GET /api/cart – lấy cart theo current_user.id, join CartItem → Product, trả danh sách items kèm thông tin SP và tổng tiền | Backend/API | 2 | Done | High |
| Sprint 3 | US-27 | Thêm sản phẩm vào giỏ hàng | 3 | TASK-54 | Tạo schema AddToCartRequest (product_id, quantity) | Backend/API | 0.5 | Done | High |
| Sprint 3 | US-27 | Thêm sản phẩm vào giỏ hàng | 3 | TASK-55 | Viết router POST /api/cart/items – tạo cart nếu chưa có, thêm item mới hoặc cộng dồn quantity nếu product đã tồn tại | Backend/API | 2 | Done | High |
| Sprint 3 | US-28 | Cập nhật số lượng trong giỏ | 2 | TASK-56 | Viết router PUT /api/cart/items/{item_id} – cập nhật quantity, validate > 0, kiểm tra item thuộc cart của user | Backend/API | 1.5 | Done | High |
| Sprint 3 | US-29 | Xoá sản phẩm khỏi giỏ | 1 | TASK-57 | Viết router DELETE /api/cart/items/{item_id} – xoá item, kiểm tra ownership | Backend/API | 1 | Done | Medium |
| Sprint 3 | US-30 | Xoá toàn bộ giỏ hàng | 1 | TASK-58 | Viết router DELETE /api/cart – xoá tất cả cart_items theo cart_id của user | Backend/API | 1 | Done | Medium |
| Sprint 3 | US-31 | Đặt hàng (Checkout) | 8 | TASK-59 | Thiết kế bảng `orders` (id, order_number, customer_id, seller_id, total_amount, platform_fee_percentage, platform_fee_amount, seller_amount, status, payment_status, shipping_address, created_at) | Backend | 2 | Done | High |
| Sprint 3 | US-31 | Đặt hàng (Checkout) | 8 | TASK-60 | Thiết kế bảng `order_items` (id, order_id, product_id, product_name, quantity, unit_price, subtotal) | Backend | 1 | Done | High |
| Sprint 3 | US-31 | Đặt hàng (Checkout) | 8 | TASK-61 | Tạo model Order, OrderItem, OrderStatus enum (PENDING/CONFIRMED/SHIPPING/DELIVERED/CANCELLED) | Backend | 2 | Done | High |
| Sprint 3 | US-31 | Đặt hàng (Checkout) | 8 | TASK-62 | Viết logic tách đơn theo seller – nhóm cart items theo producer_id, tạo 1 order riêng cho mỗi seller | Backend | 3 | Done | High |
| Sprint 3 | US-31 | Đặt hàng (Checkout) | 8 | TASK-63 | Viết logic tính phí sàn (platform_fee_percentage, platform_fee_amount, seller_amount) cho từng đơn | Backend | 2 | Done | High |
| Sprint 3 | US-31 | Đặt hàng (Checkout) | 8 | TASK-64 | Viết logic tạm giữ (reserve) stock_quantity sản phẩm và xoá giỏ hàng sau checkout | Backend | 1.5 | Done | High |
| Sprint 3 | US-31 | Đặt hàng (Checkout) | 8 | TASK-65 | Viết router POST /api/checkout – gọi logic checkout, trả danh sách orders đã tạo | Backend/API | 2 | Done | High |
| Sprint 3 | US-32 | Xem danh sách đơn hàng | 5 | TASK-66 | Viết router GET /api/orders – phân quyền: consumer (customer_id), producer (seller_id), admin (all), phân trang, lọc status | Backend/API | 4 | Done | High |
| Sprint 3 | US-33 | Xem chi tiết đơn hàng | 3 | TASK-67 | Viết router GET /api/orders/{order_id} – join OrderItem, kiểm tra phân quyền xem | Backend/API | 2 | Done | High |
| Sprint 3 | US-34 | Cập nhật trạng thái đơn hàng | 3 | TASK-68 | Viết router PUT /api/orders/{order_id}/status – validate flow trạng thái hợp lệ, phân quyền theo vai trò | Backend/API | 2.5 | Done | High |
| Sprint 3 | US-35 | Thống kê đơn hàng | 3 | TASK-69 | Viết router GET /api/orders/stats/overview – đếm theo status, tính tổng revenue từ orders DELIVERED | Backend/API | 2 | Done | Medium |
| Sprint 3 | US-32 | Xem danh sách đơn hàng | 5 | TASK-241 | Thiết kế UI trang Quản lý đơn hàng: bảng danh sách, phân trang, lọc status, badge trạng thái màu | FE/CMS | 5 | To Do | High |
| Sprint 3 | US-32 | Xem danh sách đơn hàng | 5 | TASK-242 | Tích hợp API GET /api/orders, xử lý phân quyền hiển thị (admin thấy all, seller thấy shop mình) | FE/CMS | 2.5 | To Do | High |
| Sprint 3 | US-33 | Xem chi tiết đơn hàng | 3 | TASK-243 | Thiết kế UI trang Chi tiết đơn hàng: thông tin đơn, danh sách items (sản phẩm, số lượng, giá), timeline trạng thái | FE/CMS | 4 | To Do | High |
| Sprint 3 | US-33 | Xem chi tiết đơn hàng | 3 | TASK-244 | Tích hợp API GET /api/orders/{id}, hiển thị order items, thông tin shipping | FE/CMS | 2 | To Do | High |
| Sprint 3 | US-34 | Cập nhật trạng thái đơn hàng | 3 | TASK-245 | Viết UI cập nhật trạng thái đơn: dropdown/button chuyển status, dialog xác nhận | FE/CMS | 2 | To Do | High |
| Sprint 4 | US-36 | Tạo thanh toán VNPAY | 8 | TASK-70 | Viết service VNPay: cấu hình vnp_TmnCode, vnp_HashSecret, vnp_Url, vnp_ReturnUrl từ environment | Backend | 1.5 | Done | High |
| Sprint 4 | US-36 | Tạo thanh toán VNPAY | 8 | TASK-71 | Viết hàm create_payment_url – tạo URL thanh toán VNPAY với HMAC-SHA512 signature, encode params đúng chuẩn | Backend | 4 | Done | High |
| Sprint 4 | US-36 | Tạo thanh toán VNPAY | 8 | TASK-72 | Viết router POST /api/payments/vnpay/create – kiểm tra order ownership, payment_status chưa PAID, lấy client IP, gọi VNPay service | Backend/API | 2 | Done | High |
| Sprint 4 | US-37 | Xử lý VNPAY Return | 5 | TASK-73 | Viết hàm verify_return_url – parse query params, verify HMAC-SHA512 signature, extract order_id, response_code | Backend | 2 | Done | High |
| Sprint 4 | US-37 | Xử lý VNPAY Return | 5 | TASK-74 | Viết router GET /api/payments/vnpay/return – verify chữ ký, cập nhật order (payment_status=PAID, status=CONFIRMED), tạo Payment record với platform_fee | Backend/API | 3 | Done | High |
| Sprint 4 | US-38 | VNPAY IPN Webhook | 5 | TASK-75 | Viết router POST /api/payments/vnpay/ipn – server-to-server verify, trả RspCode chuẩn VNPAY, chống duplicate Payment record | Backend/API | 3 | Done | High |
| Sprint 4 | US-39 | Xem danh sách thanh toán | 3 | TASK-76 | Thiết kế bảng `payments` (id, order_id, customer_id, seller_id, amount, platform_fee_percentage, platform_fee_amount, seller_amount, status, payment_cycle, created_at) | Backend | 1.5 | Done | Medium |
| Sprint 4 | US-39 | Xem danh sách thanh toán | 3 | TASK-77 | Tạo model Payment với enum PaymentStatus (PENDING/COMPLETED/REFUNDED) và PaymentCycle (WEEKLY/MONTHLY) | Backend | 1 | Done | Medium |
| Sprint 4 | US-39 | Xem danh sách thanh toán | 3 | TASK-78 | Viết router GET /api/payments – phân trang, lọc status, customer_id, seller_id | Backend/API | 2 | Done | Medium |
| Sprint 4 | US-40 | Xem trạng thái thanh toán | 2 | TASK-79 | Viết router GET /api/payments/{payment_id}/status – trả PaymentResponse, xử lý 404 | Backend/API | 1 | Done | Medium |
| Sprint 4 | US-41 | Đối soát thanh toán | 5 | TASK-80 | Viết router GET /api/payments/reconciliation – query payments COMPLETED, tính SUM(amount), SUM(platform_fee_amount), SUM(seller_amount), hỗ trợ lọc ngày | Backend/API | 3 | Done | Medium |
| Sprint 4 | US-42 | Hoàn tiền | 5 | TASK-81 | Thiết kế bảng `payment_transactions` (id, payment_id, transaction_type, amount, status, notes, created_at) | Backend | 1 | Done | Medium |
| Sprint 4 | US-42 | Hoàn tiền | 5 | TASK-82 | Tạo model PaymentTransaction (SQLAlchemy ORM) | Backend | 0.5 | Done | Medium |
| Sprint 4 | US-42 | Hoàn tiền | 5 | TASK-83 | Viết router POST /api/payments/refund – tạo refund transaction (type=REFUND), cập nhật payment status=REFUNDED | Backend/API | 2 | Done | Medium |
| Sprint 4 | US-43 | Khiếu nại thanh toán | 3 | TASK-84 | Viết router POST /api/payments/complaint – nhận payment_id và complaint text (chưa tạo complaint record riêng, cần bổ sung) | Backend/API | 1 | In Progress | Low |
| Sprint 4 | US-43 | Khiếu nại thanh toán | 3 | TASK-85 | Thiết kế bảng `payment_complaints` và tạo model để lưu khiếu nại vào DB | Backend | 2 | To Do | Low |
| Sprint 4 | US-44 | Cấu hình phí sàn | 3 | TASK-86 | Viết router PUT /api/payments/config/fee – nhận fee_percentage (0-100), validate | Backend/API | 1 | In Progress | Medium |
| Sprint 4 | US-44 | Cấu hình phí sàn | 3 | TASK-87 | Thiết kế bảng `platform_config` và viết logic persist fee_percentage vào DB thay vì chỉ return message | Backend | 2 | To Do | Medium |
| Sprint 4 | US-45 | Cấu hình chu kỳ thanh toán | 2 | TASK-88 | Viết router PUT /api/payments/config/cycle – nhận cycle (WEEKLY/MONTHLY), validate regex | Backend/API | 1 | In Progress | Medium |
| Sprint 4 | US-45 | Cấu hình chu kỳ thanh toán | 2 | TASK-89 | Viết logic persist payment cycle vào bảng platform_config | Backend | 1.5 | To Do | Medium |
| Sprint 4 | US-46 | Tính phí vận chuyển | 5 | TASK-90 | Viết service GHN: cấu hình GHN_TOKEN, GHN_SHOP_ID, GHN_API_URL từ environment | Backend | 1 | Done | High |
| Sprint 4 | US-46 | Tính phí vận chuyển | 5 | TASK-91 | Viết hàm calculate_shipping_fee – gọi GHN API /v2/shipping-order/fee, truyền from/to district, weight | Backend | 3 | Done | High |
| Sprint 4 | US-46 | Tính phí vận chuyển | 5 | TASK-92 | Viết router POST /api/shipping/fee – nhận địa chỉ gửi/nhận, trọng lượng, gọi GHN service | Backend/API | 2 | Done | High |
| Sprint 4 | US-47 | Tạo vận đơn GHN | 8 | TASK-93 | Thiết kế bảng `shipments` (id, order_id, tracking_code, shipping_provider, status, estimated_delivery, created_at) | Backend | 1.5 | Done | High |
| Sprint 4 | US-47 | Tạo vận đơn GHN | 8 | TASK-94 | Tạo model Shipment (SQLAlchemy ORM) | Backend | 1 | Done | High |
| Sprint 4 | US-47 | Tạo vận đơn GHN | 8 | TASK-95 | Viết hàm create_shipping_order – gọi GHN API /v2/shipping-order/create, truyền thông tin đơn hàng, địa chỉ | Backend | 3 | Done | High |
| Sprint 4 | US-47 | Tạo vận đơn GHN | 8 | TASK-96 | Viết router POST /api/shipping/create – tạo vận đơn, lưu Shipment, cập nhật order status = SHIPPING | Backend/API | 2.5 | Done | High |
| Sprint 4 | US-48 | Tra cứu vận đơn | 3 | TASK-97 | Viết hàm track_shipping_order – gọi GHN API /v2/shipping-order/detail | Backend | 2 | Done | High |
| Sprint 4 | US-48 | Tra cứu vận đơn | 3 | TASK-98 | Viết router GET /api/shipping/{shipment_id}/track – gọi GHN service, trả trạng thái chi tiết | Backend/API | 1.5 | Done | High |
| Sprint 4 | US-49 | Xem vận đơn theo đơn hàng | 2 | TASK-99 | Viết router GET /api/shipping/order/{order_id} – query Shipment theo order_id, trả thông tin vận đơn | Backend/API | 1 | Done | Medium |
| Sprint 4 | US-50 | GHN Webhook cập nhật trạng thái | 5 | TASK-100 | Viết router POST /api/shipping/webhook – nhận payload từ GHN, cập nhật shipment.status | Backend/API | 2 | Done | High |
| Sprint 4 | US-50 | GHN Webhook cập nhật trạng thái | 5 | TASK-101 | Viết logic cập nhật order.status = DELIVERED khi shipment status là đã giao | Backend | 2 | Done | High |
| Sprint 4 | US-39 | Xem danh sách thanh toán | 3 | TASK-246 | Thiết kế UI trang Quản lý thanh toán: danh sách payments, phân trang, lọc status/customer/seller | FE/CMS | 4 | To Do | Medium |
| Sprint 4 | US-39 | Xem danh sách thanh toán | 3 | TASK-247 | Tích hợp API GET /api/payments, hiển thị chi tiết từng payment | FE/CMS | 2 | To Do | Medium |
| Sprint 4 | US-41 | Đối soát thanh toán | 5 | TASK-248 | Thiết kế UI trang Đối soát: báo cáo tổng thu, hoa hồng sàn, tiền seller, bộ lọc ngày | FE/CMS | 4 | To Do | Medium |
| Sprint 4 | US-41 | Đối soát thanh toán | 5 | TASK-249 | Tích hợp API GET /api/payments/reconciliation, hiển thị biểu đồ tổng hợp | FE/CMS | 3 | To Do | Medium |
| Sprint 4 | US-42 | Hoàn tiền | 5 | TASK-250 | Thiết kế UI hoàn tiền: form ghi lý do, xác nhận, tích hợp API POST /api/payments/refund | FE/CMS | 2.5 | To Do | Medium |
| Sprint 4 | US-46 | Tính phí vận chuyển | 5 | TASK-251 | Thiết kế UI widget tính phí ship: chọn địa chỉ, nhập trọng lượng, hiển thị phí | FE/CMS | 3 | To Do | High |
| Sprint 4 | US-47 | Tạo vận đơn GHN | 8 | TASK-252 | Thiết kế UI tạo vận đơn: form thông tin gửi/nhận, nút Tạo vận đơn, hiển thị tracking code | FE/CMS | 4 | To Do | High |
| Sprint 4 | US-47 | Tạo vận đơn GHN | 8 | TASK-253 | Tích hợp API POST /api/shipping/create, hiển thị kết quả tạo vận đơn | FE/CMS | 2 | To Do | High |
| Sprint 4 | US-48 | Tra cứu vận đơn | 3 | TASK-254 | Thiết kế UI tra cứu vận đơn: timeline trạng thái shipping chi tiết | FE/CMS | 2.5 | To Do | High |
| Sprint 5 | US-51 | Dashboard seller | 5 | TASK-102 | Viết router GET /api/seller/dashboard – đếm orders theo seller_id, tính SUM revenue, đếm products, đơn pending | Backend/API | 3 | Done | High |
| Sprint 5 | US-52 | Xem đơn hàng của shop | 3 | TASK-103 | Viết router GET /api/seller/orders – query Order.seller_id == current_user.id, phân trang | Backend/API | 2 | Done | High |
| Sprint 5 | US-53 | Xác nhận đơn hàng | 5 | TASK-104 | Viết router PUT /api/seller/orders/{order_id}/confirm – validate status PENDING, chuyển CONFIRMED, xác nhận chính thức trừ kho (tồn kho đã được tạm giữ từ checkout) | Backend/API | 3 | Done | High |
| Sprint 5 | US-53 | Xác nhận đơn hàng | 5 | TASK-105 | Viết logic xác nhận trừ tồn kho chính thức – lặp order_items, giảm product.stock_quantity tương ứng | Backend | 2 | Done | High |
| Sprint 5 | US-54 | Từ chối/huỷ đơn hàng | 5 | TASK-106 | Viết router PUT /api/seller/orders/{order_id}/reject – chuyển status CANCELLED, ghi reason | Backend/API | 2 | Done | High |
| Sprint 5 | US-54 | Từ chối/huỷ đơn hàng | 5 | TASK-107 | Viết logic hoàn tồn kho – lặp order_items, cộng lại stock_quantity sản phẩm | Backend | 2 | Done | High |
| Sprint 5 | US-55 | Chuyển trạng thái giao hàng | 3 | TASK-108 | Viết router PUT /api/seller/orders/{order_id}/ship – validate CONFIRMED → SHIPPING, kiểm tra seller ownership | Backend/API | 1.5 | Done | High |
| Sprint 5 | US-56 | Xem sản phẩm của seller | 3 | TASK-109 | Viết router GET /api/seller/products – query Product.producer_id == current_user.id, trả tất cả status | Backend/API | 2 | Done | High |
| Sprint 5 | US-57 | Cập nhật tồn kho | 3 | TASK-110 | Viết router PUT /api/seller/products/{product_id}/stock – nhận stock_quantity >= 0, kiểm tra ownership | Backend/API | 1.5 | Done | High |
| Sprint 5 | US-58 | Xem profile seller | 3 | TASK-111 | Viết router GET /api/seller/profile – trả thông tin user kèm thống kê tổng sản phẩm, tổng đơn hàng | Backend/API | 2 | Done | Medium |
| Sprint 5 | US-59 | Đăng ký hồ sơ kinh doanh | 8 | TASK-112 | Thiết kế bảng `seller_profiles` (id, user_id, business_name, id_card_number, business_license, bank_name, bank_account, verification_status, rejection_reason, created_at) | Backend | 2 | Done | High |
| Sprint 5 | US-59 | Đăng ký hồ sơ kinh doanh | 8 | TASK-113 | Tạo model SellerProfile với enum VerificationStatus (PENDING/APPROVED/REJECTED) | Backend | 1 | Done | High |
| Sprint 5 | US-59 | Đăng ký hồ sơ kinh doanh | 8 | TASK-114 | Tạo schema SellerRegistrationRequest (business_name, id_card_number, business_license, bank_name, bank_account) | Backend/API | 1 | Done | High |
| Sprint 5 | US-59 | Đăng ký hồ sơ kinh doanh | 8 | TASK-115 | Viết router POST /api/seller/register – tạo seller_profile với status PENDING, validate CCCD và giấy phép | Backend/API | 3 | Done | High |
| Sprint 5 | US-60 | Xem trạng thái xác minh | 2 | TASK-116 | Viết router GET /api/seller/verification-status – query seller_profile theo current_user.id, trả verification_status và rejection_reason | Backend/API | 1.5 | Done | High |
| Sprint 5 | US-61 | Admin duyệt hồ sơ seller | 5 | TASK-117 | Viết router PUT /api/seller/verify/{user_id} – nhận action (APPROVED/REJECTED), reason, cập nhật verification_status | Backend/API | 2 | Done | High |
| Sprint 5 | US-61 | Admin duyệt hồ sơ seller | 5 | TASK-118 | Viết logic cập nhật user.activated = 1 khi duyệt APPROVED, giữ activated = 0 khi REJECTED | Backend | 1.5 | Done | High |
| Sprint 5 | US-62 | Danh sách hồ sơ chờ duyệt | 3 | TASK-119 | Viết router GET /api/seller/applications – query seller_profiles status PENDING, phân trang, join user info | Backend/API | 2 | Done | High |
| Sprint 5 | US-51 | Dashboard seller | 5 | TASK-255 | Thiết kế UI trang Dashboard Seller: card tổng đơn, doanh thu, sản phẩm, đơn pending; biểu đồ doanh thu | FE/CMS | 6 | To Do | High |
| Sprint 5 | US-51 | Dashboard seller | 5 | TASK-256 | Tích hợp API GET /api/seller/dashboard, render biểu đồ (Chart.js / ECharts) | FE/CMS | 3 | To Do | High |
| Sprint 5 | US-52 | Xem đơn hàng của shop | 3 | TASK-257 | Thiết kế UI trang Đơn hàng Seller: danh sách đơn cần xử lý, tab theo trạng thái | FE/CMS | 4 | To Do | High |
| Sprint 5 | US-53 | Xác nhận đơn hàng | 5 | TASK-258 | Viết UI xác nhận đơn: nút Xác nhận trên chi tiết đơn, dialog xác nhận, tích hợp API confirm | FE/CMS | 2 | To Do | High |
| Sprint 5 | US-54 | Từ chối/huỷ đơn hàng | 5 | TASK-259 | Viết UI từ chối đơn: nút Từ chối, form ghi lý do, tích hợp API reject | FE/CMS | 2 | To Do | High |
| Sprint 5 | US-55 | Chuyển trạng thái giao hàng | 3 | TASK-260 | Viết nút Gửi hàng trên chi tiết đơn CONFIRMED, tích hợp API ship | FE/CMS | 1.5 | To Do | High |
| Sprint 5 | US-56 | Xem sản phẩm của seller | 3 | TASK-261 | Thiết kế UI trang Sản phẩm Seller: danh sách SP của mình, badge status, nút Sửa/Xoá | FE/CMS | 3 | To Do | High |
| Sprint 5 | US-57 | Cập nhật tồn kho | 3 | TASK-262 | Viết UI cập nhật tồn kho: input số lượng trên danh sách SP, tích hợp API stock | FE/CMS | 1.5 | To Do | High |
| Sprint 5 | US-58 | Xem profile seller | 3 | TASK-263 | Thiết kế UI trang Profile Shop: thông tin shop, thống kê tổng sản phẩm/đơn hàng | FE/CMS | 2.5 | To Do | Medium |
| Sprint 5 | US-59 | Đăng ký hồ sơ kinh doanh | 8 | TASK-264 | Thiết kế UI form Đăng ký Seller: CCCD, giấy phép kinh doanh, thông tin ngân hàng, upload file | FE/CMS | 5 | To Do | High |
| Sprint 5 | US-59 | Đăng ký hồ sơ kinh doanh | 8 | TASK-265 | Tích hợp API POST /api/seller/register, upload files, validate form | FE/CMS | 3 | To Do | High |
| Sprint 5 | US-60 | Xem trạng thái xác minh | 2 | TASK-266 | Thiết kế UI hiển thị trạng thái xác minh: PENDING/APPROVED/REJECTED + lý do từ chối | FE/CMS | 2 | To Do | High |
| Sprint 5 | US-61 | Admin duyệt hồ sơ seller | 5 | TASK-267 | Thiết kế UI trang Duyệt Seller: danh sách hồ sơ, xem chi tiết, nút Duyệt/Từ chối + lý do | FE/CMS | 4 | To Do | High |
| Sprint 5 | US-61 | Admin duyệt hồ sơ seller | 5 | TASK-268 | Tích hợp API PUT /api/seller/verify/{id}, hiển thị kết quả duyệt | FE/CMS | 2 | To Do | High |
| Sprint 6 | US-63 | Tạo đánh giá sản phẩm | 5 | TASK-120 | Thiết kế bảng `reviews` (id, product_id, user_id, order_id, rating, comment, created_at, updated_at) | Backend | 1.5 | Done | High |
| Sprint 6 | US-63 | Tạo đánh giá sản phẩm | 5 | TASK-121 | Tạo model Review (SQLAlchemy ORM) | Backend | 0.5 | Done | High |
| Sprint 6 | US-63 | Tạo đánh giá sản phẩm | 5 | TASK-122 | Viết router POST /api/reviews – validate order DELIVERED, kiểm tra chưa review đơn này, lưu rating 1-5 + comment | Backend/API | 3 | Done | High |
| Sprint 6 | US-64 | Xem đánh giá sản phẩm (public) | 3 | TASK-123 | Viết router GET /api/reviews/product/{product_id} – public endpoint, trả danh sách reviews + tính avg_rating + phân bố sao (1-5) | Backend/API | 2.5 | Done | High |
| Sprint 6 | US-65 | Cập nhật đánh giá | 2 | TASK-124 | Viết router PUT /api/reviews/{review_id} – kiểm tra ownership, cập nhật rating và comment | Backend/API | 1.5 | Done | Medium |
| Sprint 6 | US-66 | Xoá đánh giá | 1 | TASK-125 | Viết router DELETE /api/reviews/{review_id} – kiểm tra ownership, xoá review | Backend/API | 1 | Done | Low |
| Sprint 6 | US-67 | Tạo yêu cầu đổi/trả hàng | 5 | TASK-126 | Thiết kế bảng `return_requests` (id, order_id, user_id, reason, return_type, status, admin_id, admin_notes, created_at) | Backend | 1.5 | Done | High |
| Sprint 6 | US-67 | Tạo yêu cầu đổi/trả hàng | 5 | TASK-127 | Tạo model ReturnRequest với enum ReturnStatus (PENDING/APPROVED/REJECTED/RECEIVED) | Backend | 1 | Done | High |
| Sprint 6 | US-67 | Tạo yêu cầu đổi/trả hàng | 5 | TASK-128 | Viết router POST /api/returns – validate order DELIVERED, tạo return request với status PENDING | Backend/API | 2.5 | Done | High |
| Sprint 6 | US-68 | Xem yêu cầu đổi/trả của tôi | 2 | TASK-129 | Viết router GET /api/returns/my – query ReturnRequest theo current_user.id, trả danh sách kèm status | Backend/API | 1.5 | Done | Medium |
| Sprint 6 | US-69 | Admin xem tất cả đổi/trả | 3 | TASK-130 | Viết router GET /api/returns – admin xem tất cả return requests, phân trang | Backend/API | 2 | Done | Medium |
| Sprint 6 | US-70 | Duyệt yêu cầu đổi/trả | 3 | TASK-131 | Viết router PUT /api/returns/{return_id}/approve – cập nhật status APPROVED, ghi admin_id | Backend/API | 1.5 | Done | High |
| Sprint 6 | US-71 | Từ chối yêu cầu đổi/trả | 2 | TASK-132 | Viết router PUT /api/returns/{return_id}/reject – cập nhật status REJECTED, ghi admin_notes | Backend/API | 1.5 | Done | Medium |
| Sprint 6 | US-72 | Xác nhận đã nhận hàng trả về | 2 | TASK-133 | Viết router PUT /api/returns/{return_id}/received – cập nhật status RECEIVED, ghi thời gian | Backend/API | 1 | Done | Medium |
| Sprint 6 | US-73 | Xem ví seller | 5 | TASK-134 | Thiết kế bảng `seller_wallets` (id, seller_id, pending_amount, available_amount, withdrawn_amount, updated_at) | Backend | 1.5 | Done | High |
| Sprint 6 | US-73 | Xem ví seller | 5 | TASK-135 | Tạo model SellerWallet (SQLAlchemy ORM) | Backend | 0.5 | Done | High |
| Sprint 6 | US-73 | Xem ví seller | 5 | TASK-136 | Viết router GET /api/settlement/wallet – query wallet theo current_user.id, trả pending/available/withdrawn | Backend/API | 2 | Done | High |
| Sprint 6 | US-74 | Lịch sử đối soát | 3 | TASK-137 | Viết router GET /api/settlement/history – seller xem của mình (seller_id filter), admin xem tất cả, phân trang | Backend/API | 2 | Done | High |
| Sprint 6 | US-75 | Tạo kỳ đối soát | 8 | TASK-138 | Thiết kế bảng `settlements` (id, seller_id, period_start, period_end, total_orders, total_amount, platform_fee, seller_amount, status, created_at) | Backend | 2 | Done | High |
| Sprint 6 | US-75 | Tạo kỳ đối soát | 8 | TASK-139 | Tạo model Settlement với enum SettlementStatus (PENDING/APPROVED/PAID) | Backend | 1 | Done | High |
| Sprint 6 | US-75 | Tạo kỳ đối soát | 8 | TASK-140 | Viết router POST /api/settlement/create – query orders DELIVERED trong khoảng thời gian, group by seller, tính SUM, tạo settlement record | Backend/API | 4 | Done | High |
| Sprint 6 | US-76 | Duyệt kỳ đối soát | 5 | TASK-141 | Viết router POST /api/settlement/{settlement_id}/approve – cập nhật status APPROVED, chuyển tiền pending → available trong SellerWallet | Backend/API | 3 | Done | High |
| Sprint 6 | US-77 | Chi trả cho seller (Payout) | 5 | TASK-142 | Thiết kế bảng `payouts` (id, settlement_id, seller_id, amount, status, created_at) | Backend | 1 | Done | High |
| Sprint 6 | US-77 | Chi trả cho seller (Payout) | 5 | TASK-143 | Tạo model Payout (SQLAlchemy ORM) | Backend | 0.5 | Done | High |
| Sprint 6 | US-77 | Chi trả cho seller (Payout) | 5 | TASK-144 | Viết router POST /api/settlement/{settlement_id}/payout – trừ available, cộng withdrawn, tạo payout record | Backend/API | 3 | Done | High |
| Sprint 6 | US-78 | Lịch sử chi trả | 3 | TASK-145 | Viết router GET /api/settlement/payouts – seller xem của mình, admin xem tất cả, phân trang | Backend/API | 2 | Done | Medium |
| Sprint 6 | US-63 | Tạo đánh giá sản phẩm | 5 | TASK-269 | Thiết kế component Đánh giá: chọn sao (1-5), textarea comment, nút Gửi | FE/Mobile | 3 | To Do | High |
| Sprint 6 | US-64 | Xem đánh giá sản phẩm (public) | 3 | TASK-270 | Thiết kế UI hiển thị đánh giá: danh sách reviews, biểu đồ phân bố sao, điểm trung bình | FE/Mobile | 3 | To Do | High |
| Sprint 6 | US-63 | Quản lý đánh giá (Admin) | 5 | TASK-271 | Thiết kế UI trang Quản lý đánh giá CMS: danh sách reviews, lọc theo sản phẩm/rating | FE/CMS | 3 | To Do | Medium |
| Sprint 6 | US-67 | Tạo yêu cầu đổi/trả hàng | 5 | TASK-272 | Thiết kế UI form Yêu cầu đổi/trả: chọn đơn hàng, ghi lý do, chọn loại (đổi/trả) | FE/Mobile | 3 | To Do | High |
| Sprint 6 | US-69 | Admin xem tất cả đổi/trả | 3 | TASK-273 | Thiết kế UI trang Quản lý Đổi/Trả CMS: danh sách, lọc status, xem chi tiết, nút Duyệt/Từ chối/Đã nhận | FE/CMS | 4 | To Do | Medium |
| Sprint 6 | US-69 | Admin xem tất cả đổi/trả | 3 | TASK-274 | Tích hợp các API returns: GET list, PUT approve/reject/received | FE/CMS | 2.5 | To Do | Medium |
| Sprint 6 | US-73 | Xem ví seller | 5 | TASK-275 | Thiết kế UI trang Ví Seller: card hiển thị 3 số dư (pending, available, withdrawn), lịch sử giao dịch | FE/CMS | 4 | To Do | High |
| Sprint 6 | US-73 | Xem ví seller | 5 | TASK-276 | Tích hợp API GET /api/settlement/wallet, hiển thị số dư realtime | FE/CMS | 2 | To Do | High |
| Sprint 6 | US-75 | Tạo kỳ đối soát | 8 | TASK-277 | Thiết kế UI trang Đối soát Admin: form chọn khoảng thời gian, danh sách settlement, nút Tạo/Duyệt/Chi trả | FE/CMS | 5 | To Do | High |
| Sprint 6 | US-75 | Tạo kỳ đối soát | 8 | TASK-278 | Tích hợp API settlement: create, approve, payout + hiển thị danh sách history | FE/CMS | 3 | To Do | High |
| Sprint 6 | US-78 | Lịch sử chi trả | 3 | TASK-279 | Thiết kế UI trang Lịch sử Payout: bảng danh sách, phân trang, lọc theo seller/kỳ | FE/CMS | 3 | To Do | Medium |
| Sprint 7 | US-79 | Thêm chứng nhận sản phẩm | 5 | TASK-146 | Thiết kế bảng `product_certificates` (id, product_id, seller_id, certificate_name, certificate_type, file_url, verification_status, verified_by, verified_at, rejection_reason, created_at) | Backend | 2 | Done | High |
| Sprint 7 | US-79 | Thêm chứng nhận sản phẩm | 5 | TASK-147 | Tạo model ProductCertificate với enum CertificateStatus (PENDING/VERIFIED/REJECTED) | Backend | 1 | Done | High |
| Sprint 7 | US-79 | Thêm chứng nhận sản phẩm | 5 | TASK-148 | Viết router POST /api/traceability/certificates – seller tạo certificate, gán status PENDING, liên kết product_id | Backend/API | 2.5 | Done | High |
| Sprint 7 | US-80 | Xem chứng nhận sản phẩm (public) | 2 | TASK-149 | Viết router GET /api/traceability/certificates/product/{product_id} – public endpoint, chỉ trả certificates VERIFIED | Backend/API | 1.5 | Done | High |
| Sprint 7 | US-81 | Admin xác minh chứng nhận | 3 | TASK-150 | Viết router PUT /api/traceability/certificates/{cert_id}/verify – admin cập nhật status VERIFIED/REJECTED, ghi verified_by, verified_at, rejection_reason | Backend/API | 2 | Done | High |
| Sprint 7 | US-82 | Khai báo nguồn gốc sản phẩm | 5 | TASK-151 | Thiết kế bảng `product_origins` (id, product_id, seller_id, production_location, production_method, raw_materials, harvest_date, created_at, updated_at) | Backend | 1.5 | Done | High |
| Sprint 7 | US-82 | Khai báo nguồn gốc sản phẩm | 5 | TASK-152 | Tạo model ProductOrigin (SQLAlchemy ORM) | Backend | 0.5 | Done | High |
| Sprint 7 | US-82 | Khai báo nguồn gốc sản phẩm | 5 | TASK-153 | Viết router POST /api/traceability/origins – seller tạo hoặc cập nhật origin (upsert theo product_id) | Backend/API | 2.5 | Done | High |
| Sprint 7 | US-83 | Xem nguồn gốc sản phẩm (public) | 2 | TASK-154 | Viết router GET /api/traceability/origins/product/{product_id} – public endpoint, trả thông tin nguồn gốc | Backend/API | 1 | Done | High |
| Sprint 7 | US-84 | Xem toàn bộ truy xuất nguồn gốc | 3 | TASK-155 | Viết router GET /api/traceability/product/{product_id} – join Product + ProductOrigin + ProductCertificates (VERIFIED), trả tổng hợp 1 response | Backend/API | 2.5 | Done | High |
| Sprint 7 | US-85 | Quản lý nội dung (CRUD) | 5 | TASK-156 | Thiết kế bảng `contents` (id, title, body, content_type, author_id, status, created_at, updated_at) | Backend | 1.5 | Done | Medium |
| Sprint 7 | US-85 | Quản lý nội dung (CRUD) | 5 | TASK-157 | Tạo model Content với enum ContentType (POST/PRODUCT_DESCRIPTION/NEWS/ANNOUNCEMENT) và ContentStatus | Backend | 1 | Done | Medium |
| Sprint 7 | US-85 | Quản lý nội dung (CRUD) | 5 | TASK-158 | Viết 5 router CRUD: GET /api/content (phân trang, lọc status/author/type, search), GET /{id}, POST, PUT /{id}, DELETE /{id} | Backend/API | 4 | Done | Medium |
| Sprint 7 | US-86 | Duyệt nội dung | 3 | TASK-159 | Viết router POST /api/content/{content_id}/approve – admin duyệt/từ chối, cập nhật status APPROVED/REJECTED, ghi lý do | Backend/API | 2 | Done | Medium |
| Sprint 7 | US-87 | Xem danh sách đánh giá & khiếu nại | 3 | TASK-160 | Thiết kế bảng `complaints` (id, user_id, type, subject, description, status, handled_by, handled_at, notes, created_at) | Backend | 1.5 | Done | Medium |
| Sprint 7 | US-87 | Xem danh sách đánh giá & khiếu nại | 3 | TASK-161 | Tạo model Complaint (SQLAlchemy ORM) | Backend | 0.5 | Done | Medium |
| Sprint 7 | US-87 | Xem danh sách đánh giá & khiếu nại | 3 | TASK-162 | Viết router GET /api/complaints/reviews – danh sách reviews, phân trang; GET /api/complaints/complaints – danh sách complaints, phân trang, lọc status/type | Backend/API | 2.5 | Done | Medium |
| Sprint 7 | US-88 | Xử lý khiếu nại | 3 | TASK-163 | Viết router PUT /api/complaints/complaints/{complaint_id}/handle – admin cập nhật status, ghi notes kết quả xử lý | Backend/API | 2 | Done | Medium |
| Sprint 7 | US-89 | Quản lý hợp đồng đối tác (CRUD) | 5 | TASK-164 | Thiết kế bảng `partner_contracts` (id, partner_name, contract_type, start_date, end_date, value, status, description, created_at) | Backend | 1.5 | Done | Medium |
| Sprint 7 | US-89 | Quản lý hợp đồng đối tác (CRUD) | 5 | TASK-165 | Tạo model PartnerContract với enum ContractType (ADVERTISING/PARTNERSHIP/DISTRIBUTION/OTHER) | Backend | 1 | Done | Medium |
| Sprint 7 | US-89 | Quản lý hợp đồng đối tác (CRUD) | 5 | TASK-166 | Viết 5 router CRUD: GET /api/contracts (phân trang, lọc status/type, search), GET /{id}, POST, PUT /{id}, DELETE /{id} | Backend/API | 4 | Done | Medium |
| Sprint 7 | US-79 | Thêm chứng nhận sản phẩm | 5 | TASK-280 | Thiết kế UI form Thêm chứng nhận: loại chứng nhận, upload file, liên kết sản phẩm | FE/CMS | 3 | To Do | High |
| Sprint 7 | US-79 | Thêm chứng nhận sản phẩm | 5 | TASK-281 | Tích hợp API POST /api/traceability/certificates, upload file | FE/CMS | 2 | To Do | High |
| Sprint 7 | US-80 | Xem chứng nhận sản phẩm (public) | 2 | TASK-282 | Thiết kế UI hiển thị chứng nhận trên trang chi tiết sản phẩm: badge VERIFIED, danh sách chứng nhận | FE/Mobile | 2 | To Do | High |
| Sprint 7 | US-81 | Admin xác minh chứng nhận | 3 | TASK-283 | Thiết kế UI trang Duyệt chứng nhận CMS: danh sách PENDING, xem file, nút Verify/Reject | FE/CMS | 3 | To Do | High |
| Sprint 7 | US-82 | Khai báo nguồn gốc sản phẩm | 5 | TASK-284 | Thiết kế UI form Nguồn gốc: địa điểm SX, phương pháp, nguyên liệu, ngày thu hoạch | FE/CMS | 3 | To Do | High |
| Sprint 7 | US-82 | Khai báo nguồn gốc sản phẩm | 5 | TASK-285 | Tích hợp API POST /api/traceability/origins, pre-fill nếu đã có (upsert) | FE/CMS | 2 | To Do | High |
| Sprint 7 | US-84 | Xem toàn bộ truy xuất nguồn gốc | 3 | TASK-286 | Thiết kế UI trang Truy xuất nguồn gốc (public): hiển thị tổng hợp origin + certificates + thông tin SP | FE/Mobile | 3 | To Do | High |
| Sprint 7 | US-85 | Quản lý nội dung (CRUD) | 5 | TASK-287 | Thiết kế UI trang Quản lý Nội dung CMS: danh sách bài viết, bộ lọc (type, status, author), tìm kiếm | FE/CMS | 4 | To Do | Medium |
| Sprint 7 | US-85 | Quản lý nội dung (CRUD) | 5 | TASK-288 | Thiết kế form Tạo/Sửa bài viết: rich text editor, chọn type (POST/NEWS/ANNOUNCEMENT), upload media | FE/CMS | 4 | To Do | Medium |
| Sprint 7 | US-85 | Quản lý nội dung (CRUD) | 5 | TASK-289 | Tích hợp API CRUD content + API duyệt content | FE/CMS | 3 | To Do | Medium |
| Sprint 7 | US-87 | Xem danh sách đánh giá & khiếu nại | 3 | TASK-290 | Thiết kế UI trang Khiếu nại CMS: 2 tab (Reviews / Complaints), phân trang, lọc status | FE/CMS | 3 | To Do | Medium |
| Sprint 7 | US-88 | Xử lý khiếu nại | 3 | TASK-291 | Thiết kế UI xử lý khiếu nại: chi tiết, form ghi kết quả, nút cập nhật trạng thái | FE/CMS | 2.5 | To Do | Medium |
| Sprint 7 | US-89 | Quản lý hợp đồng đối tác (CRUD) | 5 | TASK-292 | Thiết kế UI trang Hợp đồng: danh sách, lọc type/status, form tạo/sửa (ngày, giá trị, mô tả) | FE/CMS | 4 | To Do | Medium |
| Sprint 7 | US-89 | Quản lý hợp đồng đối tác (CRUD) | 5 | TASK-293 | Tích hợp API CRUD contracts | FE/CMS | 2 | To Do | Medium |
| Sprint 8 | US-90 | Quản lý vùng miền | 3 | TASK-167 | Thiết kế bảng `regions` (id, name, slug, description, is_active, created_at) | Backend | 1 | Done | Medium |
| Sprint 8 | US-90 | Quản lý vùng miền | 3 | TASK-168 | Tạo model Region (SQLAlchemy ORM) | Backend | 0.5 | Done | Medium |
| Sprint 8 | US-90 | Quản lý vùng miền | 3 | TASK-169 | Viết 5 router CRUD: GET /api/regions (phân trang, lọc is_active, search), GET /{id}, POST (tự tạo slug), PUT /{id}, DELETE /{id} | Backend/API | 3 | Done | Medium |
| Sprint 8 | US-91 | Upload file media | 5 | TASK-170 | Thiết kế bảng `medias` (id, file_name, file_url, file_type, file_size, uploaded_by, created_at) | Backend | 1 | Done | High |
| Sprint 8 | US-91 | Upload file media | 5 | TASK-171 | Tạo model Media (SQLAlchemy ORM) | Backend | 0.5 | Done | High |
| Sprint 8 | US-91 | Upload file media | 5 | TASK-172 | Cấu hình Supabase Storage: SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET từ environment | Backend | 1 | Done | High |
| Sprint 8 | US-91 | Upload file media | 5 | TASK-173 | Viết router POST /api/medias/uploads – nhận file (image/video), upload lên Supabase Storage, lưu metadata vào DB, trả public URL | Backend/API | 3.5 | Done | High |
| Sprint 8 | US-92 | Quản lý media (xem, xoá) | 3 | TASK-174 | Viết router GET /api/medias – phân trang, lọc file_type; GET /{media_id} – chi tiết | Backend/API | 2 | Done | Medium |
| Sprint 8 | US-92 | Quản lý media (xem, xoá) | 3 | TASK-175 | Viết router DELETE /api/medias/{media_id} – xoá file trên Supabase Storage và xoá record trong DB | Backend/API | 2 | Done | Medium |
| Sprint 8 | US-93 | Tổng quan hệ thống (Dashboard) | 5 | TASK-176 | Viết router GET /api/dashboard/overview – đếm users theo type, đếm products, pending_products | Backend/API | 2 | Done | High |
| Sprint 8 | US-93 | Tổng quan hệ thống (Dashboard) | 5 | TASK-177 | Bổ sung thống kê orders (total, pending) vào dashboard overview – hiện trả placeholder 0 | Backend | 2 | In Progress | High |
| Sprint 8 | US-93 | Tổng quan hệ thống (Dashboard) | 5 | TASK-178 | Bổ sung thống kê revenue (total, this_month) vào dashboard overview – hiện trả placeholder 0.00 | Backend | 2 | In Progress | High |
| Sprint 8 | US-94 | Thống kê doanh thu | 5 | TASK-179 | Viết router GET /api/dashboard/revenue – nhận period (day/week/month/year) | Backend/API | 1 | Done | High |
| Sprint 8 | US-94 | Thống kê doanh thu | 5 | TASK-180 | Bổ sung logic query Payment/Order theo period, tính total_revenue, platform_commission, seller_revenue – hiện trả placeholder | Backend | 3 | In Progress | High |
| Sprint 8 | US-94 | Thống kê doanh thu | 5 | TASK-181 | Bổ sung chart_data (groupby theo ngày/tuần/tháng) cho biểu đồ doanh thu – hiện trả mảng rỗng | Backend | 3 | To Do | High |
| Sprint 8 | US-95 | Thống kê sản phẩm | 3 | TASK-182 | Viết router GET /api/dashboard/products – đếm Product theo status (pending/approved/rejected) và label (clean_agriculture/traditional_craft/ocop/no_label) | Backend/API | 2 | Done | Medium |
| Sprint 8 | US-96 | Thống kê đơn hàng dashboard | 3 | TASK-183 | Viết router GET /api/dashboard/orders – endpoint tồn tại, trả placeholder | Backend/API | 1 | Done | Medium |
| Sprint 8 | US-96 | Thống kê đơn hàng dashboard | 3 | TASK-184 | Bổ sung logic đếm Order theo status và lấy recent_orders – hiện trả placeholder zeros | Backend | 2 | In Progress | Medium |
| Sprint 8 | US-97 | Thống kê người dùng | 3 | TASK-185 | Viết router GET /api/dashboard/users – đếm User theo type (admin/producer/consumer), by_status (active/inactive), new_users_7days | Backend/API | 2.5 | Done | Medium |
| Sprint 8 | US-98 | Thống kê producer | 3 | TASK-186 | Viết router GET /api/stats/producers – đếm total, active, inactive, new_this_month cho type=producer | Backend/API | 2 | Done | Medium |
| Sprint 8 | US-99 | Thống kê consumer | 3 | TASK-187 | Viết router GET /api/stats/consumers – đếm total, active, new_this_month cho type=consumer | Backend/API | 2 | Done | Medium |
| Sprint 8 | US-100 | Sản phẩm trending | 3 | TASK-188 | Viết router GET /api/stats/trending – query approved products, sắp xếp theo created_at desc (tạm thời) | Backend/API | 1.5 | Done | Low |
| Sprint 8 | US-100 | Sản phẩm trending | 3 | TASK-189 | Bổ sung logic sort theo thực tế order_count và average rating – hiện trả order_count=0, rating=0.0 | Backend | 3 | To Do | Low |
| Sprint 8 | US-101 | Thống kê theo vùng miền | 3 | TASK-190 | Viết router GET /api/stats/regions – endpoint tồn tại, trả mảng rỗng | Backend/API | 1 | Done | Low |
| Sprint 8 | US-101 | Thống kê theo vùng miền | 3 | TASK-191 | Bổ sung logic join Product → Region, GROUP BY region, COUNT products – hiện trả placeholder | Backend | 2.5 | To Do | Low |
| Sprint 8 | US-102 | Thống kê theo danh mục | 3 | TASK-192 | Viết router GET /api/stats/categories – endpoint tồn tại, trả mảng rỗng | Backend/API | 1 | Done | Low |
| Sprint 8 | US-102 | Thống kê theo danh mục | 3 | TASK-193 | Bổ sung logic join Product → Category, GROUP BY category, COUNT products – hiện trả placeholder | Backend | 2.5 | To Do | Low |
| Sprint 8 | US-103 | Xem bài viết công khai (Mobile) | 3 | TASK-194 | Viết router GET /api/mobile/posts – public endpoint, query Content status=APPROVED, phân trang | Backend/API | 2 | Done | High |
| Sprint 8 | US-104 | Quản lý bài viết producer (Mobile) | 5 | TASK-195 | Viết router GET /api/mobile/posts/my – query Content theo author_id = current_user.id | Backend/API | 1.5 | Done | Medium |
| Sprint 8 | US-104 | Quản lý bài viết producer (Mobile) | 5 | TASK-196 | Viết router POST /api/mobile/posts/my – tạo bài viết, hỗ trợ multipart upload ảnh/video, gán status PENDING | Backend/API | 3 | Done | High |
| Sprint 8 | US-104 | Quản lý bài viết producer (Mobile) | 5 | TASK-197 | Viết router PUT /api/mobile/posts/my/{post_id} – cập nhật bài viết, reset status PENDING | Backend/API | 2 | Done | Medium |
| Sprint 8 | US-104 | Quản lý bài viết producer (Mobile) | 5 | TASK-198 | Viết router DELETE /api/mobile/posts/my/{post_id} – xoá bài viết, kiểm tra ownership | Backend/API | 1 | Done | Low |
| Sprint 8 | US-105 | Xem sản phẩm trên app (public) | 3 | TASK-199 | Viết router GET /api/mobile/products – public endpoint, chỉ sản phẩm APPROVED, phân trang | Backend/API | 2 | Done | High |
| Sprint 8 | US-105 | Xem sản phẩm trên app (public) | 3 | TASK-200 | Viết router GET /api/mobile/products/{product_id} – chi tiết sản phẩm APPROVED, public | Backend/API | 1 | Done | High |
| Sprint 8 | US-106 | Đặt hàng trên app (Mobile Checkout) | 8 | TASK-201 | Viết router POST /api/mobile/checkout – tái sử dụng logic checkout: tách đơn theo seller, trừ tồn kho, tính phí sàn, xoá giỏ | Backend/API | 3 | Done | High |
| Sprint 8 | US-107 | Xem đơn hàng trên app | 3 | TASK-202 | Viết router GET /api/mobile/orders/my – query orders theo customer_id = current_user.id, phân trang | Backend/API | 2 | Done | High |
| Sprint 8 | US-107 | Xem đơn hàng trên app | 3 | TASK-203 | Viết router GET /api/mobile/orders/my/{order_id} – chi tiết đơn hàng, join OrderItem | Backend/API | 1.5 | Done | High |
| Sprint 8 | US-108 | Profile người dùng trên app | 3 | TASK-204 | Viết router GET /api/mobile/profile – trả thông tin user hiện tại | Backend/API | 1 | Done | Medium |
| Sprint 8 | US-108 | Profile người dùng trên app | 3 | TASK-205 | Viết router PUT /api/mobile/profile – cập nhật name, gender | Backend/API | 1 | Done | Medium |
| Sprint 8 | US-90 | Quản lý vùng miền | 3 | TASK-294 | Thiết kế UI trang Vùng miền CMS: danh sách, form tạo/sửa, toggle active | FE/CMS | 2.5 | To Do | Medium |
| Sprint 8 | US-90 | Quản lý vùng miền | 3 | TASK-295 | Tích hợp API CRUD regions | FE/CMS | 1.5 | To Do | Medium |
| Sprint 8 | US-91 | Upload file media | 5 | TASK-296 | Thiết kế component Upload Media dùng chung: drag & drop, preview, progress bar, hỗ trợ image/video | FE/CMS | 5 | To Do | High |
| Sprint 8 | US-92 | Quản lý media | 3 | TASK-297 | Thiết kế UI trang Media Library CMS: grid/list view, lọc file_type, nút xoá | FE/CMS | 3 | To Do | Medium |
| Sprint 8 | US-93 | Tổng quan hệ thống (Dashboard) | 5 | TASK-298 | Thiết kế UI trang Dashboard Admin: card thống kê (users, products, orders, revenue), biểu đồ tổng quan | FE/CMS | 6 | To Do | High |
| Sprint 8 | US-93 | Tổng quan hệ thống (Dashboard) | 5 | TASK-299 | Tích hợp API GET /api/dashboard/overview, render biểu đồ (pie chart, bar chart) | FE/CMS | 3 | To Do | High |
| Sprint 8 | US-94 | Thống kê doanh thu | 5 | TASK-300 | Thiết kế UI biểu đồ doanh thu: chọn period (ngày/tuần/tháng/năm), line chart doanh thu | FE/CMS | 4 | To Do | High |
| Sprint 8 | US-94 | Thống kê doanh thu | 5 | TASK-301 | Tích hợp API GET /api/dashboard/revenue, render chart_data | FE/CMS | 2 | To Do | High |
| Sprint 8 | US-95 | Thống kê sản phẩm | 3 | TASK-302 | Thiết kế UI thống kê sản phẩm: pie chart theo status, bar chart theo label | FE/CMS | 3 | To Do | Medium |
| Sprint 8 | US-96 | Thống kê đơn hàng dashboard | 3 | TASK-303 | Thiết kế UI thống kê đơn hàng: doughnut chart theo status, bảng đơn gần đây | FE/CMS | 3 | To Do | Medium |
| Sprint 8 | US-97 | Thống kê người dùng | 3 | TASK-304 | Thiết kế UI thống kê user: card tổng, biểu đồ theo type, biểu đồ user mới 7 ngày | FE/CMS | 3 | To Do | Medium |
| Sprint 8 | US-103 | Xem bài viết công khai (Mobile) | 3 | TASK-305 | Thiết kế màn hình Tin tức/Bài viết: danh sách card bài viết, ảnh đại diện, tiêu đề, tóm tắt | FE/Mobile | 3 | To Do | High |
| Sprint 8 | US-103 | Xem bài viết công khai (Mobile) | 3 | TASK-306 | Thiết kế màn hình Chi tiết bài viết: nội dung full, ảnh/video, thông tin tác giả | FE/Mobile | 2 | To Do | High |
| Sprint 8 | US-103 | Xem bài viết công khai (Mobile) | 3 | TASK-307 | Tích hợp API GET /api/mobile/posts, phân trang infinite scroll | FE/Mobile | 2 | To Do | High |
| Sprint 8 | US-104 | Quản lý bài viết producer (Mobile) | 5 | TASK-308 | Thiết kế màn hình Bài viết của tôi: danh sách, badge status, nút Tạo/Sửa/Xoá | FE/Mobile | 3 | To Do | Medium |
| Sprint 8 | US-104 | Quản lý bài viết producer (Mobile) | 5 | TASK-309 | Thiết kế form Tạo/Sửa bài viết mobile: text input, chụp ảnh/chọn ảnh, quay video | FE/Mobile | 4 | To Do | High |
| Sprint 8 | US-105 | Xem sản phẩm trên app (public) | 3 | TASK-310 | Thiết kế màn hình Danh sách sản phẩm: product card (ảnh, tên, giá, badge label), tìm kiếm, lọc | FE/Mobile | 4 | To Do | High |
| Sprint 8 | US-105 | Xem sản phẩm trên app (public) | 3 | TASK-311 | Thiết kế màn hình Chi tiết sản phẩm: gallery ảnh, mô tả, giá, nút Thêm giỏ, tab Đánh giá / Nguồn gốc | FE/Mobile | 5 | To Do | High |
| Sprint 8 | US-105 | Xem sản phẩm trên app (public) | 3 | TASK-312 | Tích hợp API GET /api/mobile/products và /api/mobile/products/{id} | FE/Mobile | 2 | To Do | High |
| Sprint 8 | US-26 | Giỏ hàng (Mobile) | 3 | TASK-313 | Thiết kế màn hình Giỏ hàng: danh sách items, ảnh SP, tên, giá, +/- số lượng, xoá, tổng tiền | FE/Mobile | 4 | To Do | High |
| Sprint 8 | US-26 | Giỏ hàng (Mobile) | 3 | TASK-314 | Tích hợp API cart: GET, POST add, PUT update, DELETE item | FE/Mobile | 3 | To Do | High |
| Sprint 8 | US-106 | Đặt hàng trên app (Mobile Checkout) | 8 | TASK-315 | Thiết kế màn hình Checkout: xác nhận giỏ, nhập địa chỉ giao, chọn phương thức thanh toán, tổng tiền | FE/Mobile | 5 | To Do | High |
| Sprint 8 | US-106 | Đặt hàng trên app (Mobile Checkout) | 8 | TASK-316 | Tích hợp API POST /api/mobile/checkout, xử lý redirect VNPAY, hiển thị kết quả đặt hàng | FE/Mobile | 4 | To Do | High |
| Sprint 8 | US-107 | Xem đơn hàng trên app | 3 | TASK-317 | Thiết kế màn hình Đơn hàng: danh sách đơn, tab theo trạng thái, card đơn hàng (mã đơn, ngày, tổng tiền) | FE/Mobile | 4 | To Do | High |
| Sprint 8 | US-107 | Xem đơn hàng trên app | 3 | TASK-318 | Thiết kế màn hình Chi tiết đơn: timeline trạng thái, danh sách SP, thông tin shipping | FE/Mobile | 3 | To Do | High |
| Sprint 8 | US-107 | Xem đơn hàng trên app | 3 | TASK-319 | Tích hợp API GET /api/mobile/orders/my và /{order_id} | FE/Mobile | 2 | To Do | High |
| Sprint 8 | US-108 | Profile người dùng trên app | 3 | TASK-320 | Thiết kế màn hình Profile: hiển thị avatar, name, email, gender; form Chỉnh sửa | FE/Mobile | 3 | To Do | Medium |
| Sprint 8 | US-108 | Profile người dùng trên app | 3 | TASK-321 | Tích hợp API GET/PUT /api/mobile/profile | FE/Mobile | 1.5 | To Do | Medium |
| Sprint 8 | – | Thiết kế hệ thống giao diện Mobile | – | TASK-322 | Xây dựng Navigation chính mobile: Bottom Tab Bar (Home, Sản phẩm, Giỏ hàng, Đơn hàng, Profile) | FE/Mobile | 4 | To Do | High |
| Sprint 8 | – | Thiết kế hệ thống giao diện Mobile | – | TASK-323 | Xây dựng bộ component dùng chung mobile: ProductCard, OrderCard, StarRating, LoadingIndicator, EmptyState | FE/Mobile | 5 | To Do | High |
| Sprint 8 | – | Trang Home Mobile | – | TASK-324 | Thiết kế màn hình Home: banner slider, danh mục nổi bật, sản phẩm hot, bài viết mới | FE/Mobile | 5 | To Do | High |
| Sprint 8 | – | Đăng nhập/Đăng ký Mobile | – | TASK-325 | Thiết kế màn hình Đăng nhập/Đăng ký mobile: form email/password, social login placeholder | FE/Mobile | 3 | To Do | High |
| Sprint 8 | – | Đăng nhập/Đăng ký Mobile | – | TASK-326 | Tích hợp API auth (login/register), lưu token Secure Storage, auto-refresh token | FE/Mobile | 3 | To Do | High |
