# Function API List

> Tài liệu được tạo tự động từ source code project. Cập nhật lần cuối: 2026-03-12

| STT | Module | Function | Endpoint/Mô tả | Method | Trạng thái | Priority |
|-----|--------|----------|-----------------|--------|------------|----------|
| 1 | Auth | Đăng ký tài khoản | `POST /api/auth/register` – Đăng ký tài khoản mới (consumer/producer). Producer cần duyệt hồ sơ trước khi bán | POST | Implemented | High |
| 2 | Auth | Đăng nhập | `POST /api/auth/login` – Xác thực email/password, trả về Bearer token | POST | Implemented | High |
| 3 | Auth | Xem thông tin user hiện tại | `GET /api/auth/me` – Lấy thông tin user đang đăng nhập kèm roles & permissions | GET | Implemented | High |
| 4 | Auth | Đăng xuất | `POST /api/auth/logout` – Đăng xuất (client tự xoá token) | POST | Implemented | Medium |
| 5 | Auth | Làm mới token | `POST /api/auth/refresh` – Làm mới access token với thời hạn mới | POST | Implemented | Medium |
| 6 | User | Danh sách user | `GET /api/users` – Lấy danh sách user có phân trang, lọc theo type, activated, search | GET | Implemented | High |
| 7 | User | Tạo user | `POST /api/users` – Admin tạo user mới | POST | Implemented | High |
| 8 | User | Chi tiết user | `GET /api/users/{user_id}` – Lấy thông tin user theo ID | GET | Implemented | Medium |
| 9 | User | Cập nhật user | `PUT /api/users/{user_id}` – Cập nhật thông tin user | PUT | Implemented | High |
| 10 | User | Xoá user (soft delete) | `DELETE /api/users/{user_id}` – Soft delete user (đánh dấu deleted_at) | DELETE | Implemented | Medium |
| 11 | User | Kích hoạt/vô hiệu hoá user | `PUT /api/users/{user_id}/activate` – Thay đổi trạng thái activated (0/1) | PUT | Implemented | Medium |
| 12 | User | Gán role cho user | `POST /api/users/{user_id}/roles` – Xoá roles cũ và gán danh sách roles mới | POST | Implemented | Medium |
| 13 | User | Xem role của user | `GET /api/users/{user_id}/roles` – Lấy danh sách roles đã gán cho user | GET | Implemented | Medium |
| 14 | Role | Danh sách role | `GET /api/admin/roles` – Lấy danh sách role có phân trang và search | GET | Implemented | Medium |
| 15 | Role | Tạo role | `POST /api/admin/roles` – Tạo role mới | POST | Implemented | Medium |
| 16 | Role | Cập nhật role | `PUT /api/admin/roles/{role_id}` – Cập nhật thông tin role | PUT | Implemented | Medium |
| 17 | Role | Xoá role | `DELETE /api/admin/roles/{role_id}` – Xoá role | DELETE | Implemented | Low |
| 18 | Permission | Danh sách permission | `GET /api/admin/permissions` – Lấy danh sách permissions có phân trang và search | GET | Implemented | Medium |
| 19 | Permission | Tạo permission | `POST /api/admin/permissions` – Tạo permission mới | POST | Implemented | Medium |
| 20 | Permission | Cập nhật permission | `PUT /api/admin/permissions/{permission_id}` – Cập nhật permission | PUT | Implemented | Medium |
| 21 | Permission | Xoá permission | `DELETE /api/admin/permissions/{permission_id}` – Xoá permission | DELETE | Implemented | Low |
| 22 | Organization | Danh sách tổ chức | `GET /api/org` – Lấy danh sách tổ chức (HTX, Làng nghề) có phân trang và search | GET | Implemented | Medium |
| 23 | Organization | Chi tiết tổ chức | `GET /api/org/{org_id}` – Lấy thông tin tổ chức theo ID | GET | Implemented | Medium |
| 24 | Organization | Tạo tổ chức | `POST /api/org` – Tạo tổ chức mới | POST | Implemented | Medium |
| 25 | Organization | Cập nhật tổ chức | `PUT /api/org/{org_id}` – Cập nhật thông tin tổ chức | PUT | Implemented | Medium |
| 26 | Organization | Xoá tổ chức | `DELETE /api/org/{org_id}` – Xoá tổ chức (phải xoá thành viên trước) | DELETE | Implemented | Low |
| 27 | Organization | Danh sách thành viên | `GET /api/org/{org_id}/members` – Lấy danh sách thành viên tổ chức | GET | Implemented | Medium |
| 28 | Organization | Thêm thành viên | `POST /api/org/{org_id}/members` – Thêm user vào tổ chức | POST | Implemented | Medium |
| 29 | Organization | Xoá thành viên | `DELETE /api/org/{org_id}/members/{user_id}` – Xoá thành viên khỏi tổ chức | DELETE | Implemented | Low |
| 30 | Category | Danh sách danh mục | `GET /api/categories` – Lấy danh sách danh mục có phân trang, lọc parent_id, is_active, search | GET | Implemented | High |
| 31 | Category | Chi tiết danh mục | `GET /api/categories/{category_id}` – Lấy danh mục theo ID | GET | Implemented | Medium |
| 32 | Category | Tạo danh mục | `POST /api/categories` – Tạo danh mục mới (tự tạo slug) | POST | Implemented | High |
| 33 | Category | Cập nhật danh mục | `PUT /api/categories/{category_id}` – Cập nhật danh mục | PUT | Implemented | Medium |
| 34 | Category | Xoá danh mục | `DELETE /api/categories/{category_id}` – Xoá danh mục (không xoá được nếu có danh mục con) | DELETE | Implemented | Medium |
| 35 | Product | Danh sách sản phẩm | `GET /api/products` – Lấy danh sách sản phẩm có phân trang, lọc status, producer_id, label, search | GET | Implemented | High |
| 36 | Product | Chi tiết sản phẩm | `GET /api/products/{product_id}` – Lấy chi tiết sản phẩm theo ID | GET | Implemented | High |
| 37 | Product | Tạo sản phẩm | `POST /api/products` – Tạo sản phẩm mới (trạng thái PENDING) | POST | Implemented | High |
| 38 | Product | Cập nhật sản phẩm | `PUT /api/products/{product_id}` – Cập nhật thông tin sản phẩm | PUT | Implemented | High |
| 39 | Product | Xoá sản phẩm | `DELETE /api/products/{product_id}` – Xoá sản phẩm | DELETE | Implemented | Medium |
| 40 | Product | Duyệt sản phẩm | `POST /api/products/{product_id}/approve` – Admin duyệt/từ chối sản phẩm, tạo approval record | POST | Implemented | High |
| 41 | Product | Cập nhật nhãn sản phẩm | `PUT /api/products/{product_id}/label` – Gán nhãn CLEAN_AGRICULTURE/TRADITIONAL_CRAFT/OCOP | PUT | Implemented | Medium |
| 42 | Order | Danh sách đơn hàng | `GET /api/orders` – Lấy danh sách đơn hàng có phân quyền (consumer/producer/admin), phân trang, lọc | GET | Implemented | High |
| 43 | Order | Chi tiết đơn hàng | `GET /api/orders/{order_id}` – Lấy chi tiết đơn hàng theo ID kèm danh sách items | GET | Implemented | High |
| 44 | Order | Cập nhật trạng thái đơn hàng | `PUT /api/orders/{order_id}/status` – Cập nhật trạng thái đơn hàng có phân quyền | PUT | Implemented | High |
| 45 | Order | Thống kê đơn hàng | `GET /api/orders/stats/overview` – Thống kê tổng quan đơn hàng (theo status, revenue) | GET | Implemented | Medium |
| 46 | Cart | Xem giỏ hàng | `GET /api/cart` – Lấy giỏ hàng của user đang đăng nhập | GET | Implemented | High |
| 47 | Cart | Thêm vào giỏ hàng | `POST /api/cart/items` – Thêm sản phẩm vào giỏ, cộng dồn nếu đã có | POST | Implemented | High |
| 48 | Cart | Cập nhật số lượng | `PUT /api/cart/items/{item_id}` – Cập nhật số lượng sản phẩm trong giỏ | PUT | Implemented | High |
| 49 | Cart | Xoá sản phẩm khỏi giỏ | `DELETE /api/cart/items/{item_id}` – Xoá 1 item khỏi giỏ hàng | DELETE | Implemented | Medium |
| 50 | Cart | Xoá toàn bộ giỏ | `DELETE /api/cart` – Xoá toàn bộ giỏ hàng | DELETE | Implemented | Medium |
| 51 | Payment | Tạo thanh toán VNPAY | `POST /api/payments/vnpay/create` – Tạo URL thanh toán VNPAY cho đơn hàng | POST | Implemented | High |
| 52 | Payment | VNPAY Return | `GET /api/payments/vnpay/return` – VNPAY redirect về sau thanh toán, cập nhật trạng thái đơn | GET | Implemented | High |
| 53 | Payment | VNPAY IPN Webhook | `POST /api/payments/vnpay/ipn` – VNPAY IPN server-to-server, xác nhận giao dịch | POST | Implemented | High |
| 54 | Payment | Danh sách payment | `GET /api/payments` – Lấy danh sách payment có phân trang, lọc status, customer, seller | GET | Implemented | Medium |
| 55 | Payment | Trạng thái payment | `GET /api/payments/{payment_id}/status` – Lấy trạng thái thanh toán theo ID | GET | Implemented | Medium |
| 56 | Payment | Đối soát thanh toán | `GET /api/payments/reconciliation` – Báo cáo đối soát: tổng thu, hoa hồng, seller amount | GET | Implemented | Medium |
| 57 | Payment | Hoàn tiền | `POST /api/payments/refund` – Xử lý hoàn tiền, tạo refund transaction | POST | Implemented | Medium |
| 58 | Payment | Khiếu nại thanh toán | `POST /api/payments/complaint` – Tạo khiếu nại thanh toán | POST | Partial | Low |
| 59 | Payment | Cấu hình phí sàn | `PUT /api/payments/config/fee` – Cập nhật phần trăm phí sàn (global config) | PUT | Partial | Medium |
| 60 | Payment | Cấu hình chu kỳ thanh toán | `PUT /api/payments/config/cycle` – Cập nhật chu kỳ thanh toán (WEEKLY/MONTHLY) | PUT | Partial | Medium |
| 61 | Content | Danh sách content | `GET /api/content` – Lấy danh sách bài viết/nội dung có phân trang, lọc status, author, type, search | GET | Implemented | Medium |
| 62 | Content | Chi tiết content | `GET /api/content/{content_id}` – Lấy nội dung theo ID | GET | Implemented | Medium |
| 63 | Content | Tạo content | `POST /api/content` – Tạo nội dung mới (POST/PRODUCT_DESCRIPTION/NEWS/ANNOUNCEMENT) | POST | Implemented | Medium |
| 64 | Content | Cập nhật content | `PUT /api/content/{content_id}` – Cập nhật nội dung | PUT | Implemented | Medium |
| 65 | Content | Xoá content | `DELETE /api/content/{content_id}` – Xoá nội dung | DELETE | Implemented | Low |
| 66 | Content | Duyệt content | `POST /api/content/{content_id}/approve` – Admin duyệt hoặc từ chối nội dung | POST | Implemented | Medium |
| 67 | Complaint | Danh sách review | `GET /api/complaints/reviews` – Lấy danh sách đánh giá sản phẩm có phân trang | GET | Implemented | Medium |
| 68 | Complaint | Danh sách khiếu nại | `GET /api/complaints/complaints` – Lấy danh sách khiếu nại có phân trang, lọc status, type | GET | Implemented | Medium |
| 69 | Complaint | Xử lý khiếu nại | `PUT /api/complaints/complaints/{complaint_id}/handle` – Admin xử lý khiếu nại | PUT | Implemented | Medium |
| 70 | Contract | Danh sách hợp đồng | `GET /api/contracts` – Lấy danh sách hợp đồng đối tác có phân trang, lọc status, type, search | GET | Implemented | Medium |
| 71 | Contract | Chi tiết hợp đồng | `GET /api/contracts/{contract_id}` – Lấy hợp đồng theo ID | GET | Implemented | Medium |
| 72 | Contract | Tạo hợp đồng | `POST /api/contracts` – Tạo hợp đồng đối tác mới (ADVERTISING/PARTNERSHIP/DISTRIBUTION/OTHER) | POST | Implemented | Medium |
| 73 | Contract | Cập nhật hợp đồng | `PUT /api/contracts/{contract_id}` – Cập nhật hợp đồng | PUT | Implemented | Medium |
| 74 | Contract | Xoá hợp đồng | `DELETE /api/contracts/{contract_id}` – Xoá hợp đồng | DELETE | Implemented | Low |
| 75 | Region | Danh sách vùng miền | `GET /api/regions` – Lấy danh sách vùng miền có phân trang, lọc is_active, search | GET | Implemented | Medium |
| 76 | Region | Chi tiết vùng miền | `GET /api/regions/{region_id}` – Lấy vùng miền theo ID | GET | Implemented | Medium |
| 77 | Region | Tạo vùng miền | `POST /api/regions` – Tạo vùng miền mới (tự tạo slug) | POST | Implemented | Medium |
| 78 | Region | Cập nhật vùng miền | `PUT /api/regions/{region_id}` – Cập nhật vùng miền | PUT | Implemented | Medium |
| 79 | Region | Xoá vùng miền | `DELETE /api/regions/{region_id}` – Xoá vùng miền | DELETE | Implemented | Low |
| 80 | Media | Danh sách media | `GET /api/medias` – Lấy danh sách file đã upload có phân trang, lọc file_type | GET | Implemented | Medium |
| 81 | Media | Chi tiết media | `GET /api/medias/{media_id}` – Lấy media theo ID | GET | Implemented | Low |
| 82 | Media | Upload file | `POST /api/medias/uploads` – Upload file (image/video) lên Supabase Storage, trả về public URL | POST | Implemented | High |
| 83 | Media | Xoá media | `DELETE /api/medias/{media_id}` – Xoá media trên Supabase Storage và DB | DELETE | Implemented | Medium |
| 84 | Dashboard | Tổng quan hệ thống | `GET /api/dashboard/overview` – Thống kê tổng quan: users, products, orders, revenue | GET | Partial | High |
| 85 | Dashboard | Thống kê doanh thu | `GET /api/dashboard/revenue` – Thống kê doanh thu theo thời gian (day/week/month/year) | GET | Partial | High |
| 86 | Dashboard | Thống kê sản phẩm | `GET /api/dashboard/products` – Thống kê sản phẩm theo trạng thái và nhãn | GET | Implemented | Medium |
| 87 | Dashboard | Thống kê đơn hàng | `GET /api/dashboard/orders` – Thống kê đơn hàng theo trạng thái | GET | Partial | Medium |
| 88 | Dashboard | Thống kê người dùng | `GET /api/dashboard/users` – Thống kê user theo loại, trạng thái, user mới 7 ngày | GET | Implemented | Medium |
| 89 | Stats | Thống kê producer | `GET /api/stats/producers` – Thống kê người sản xuất (total, active, inactive, mới trong tháng) | GET | Implemented | Medium |
| 90 | Stats | Thống kê consumer | `GET /api/stats/consumers` – Thống kê người tiêu dùng (total, active, mới trong tháng) | GET | Implemented | Medium |
| 91 | Stats | Sản phẩm trending | `GET /api/stats/trending` – Lấy sản phẩm trending (tạm theo sản phẩm mới nhất) | GET | Partial | Low |
| 92 | Stats | Thống kê theo vùng | `GET /api/stats/regions` – Thống kê sản phẩm theo vùng miền | GET | Partial | Low |
| 93 | Stats | Thống kê theo danh mục | `GET /api/stats/categories` – Thống kê sản phẩm theo danh mục | GET | Partial | Low |
| 94 | Seller | Dashboard seller | `GET /api/seller/dashboard` – Thống kê tổng quan cho seller: đơn hàng, doanh thu, sản phẩm | GET | Implemented | High |
| 95 | Seller | Đơn hàng của seller | `GET /api/seller/orders` – Danh sách đơn hàng thuộc shop của seller | GET | Implemented | High |
| 96 | Seller | Xác nhận đơn hàng | `PUT /api/seller/orders/{order_id}/confirm` – Seller xác nhận đơn PENDING → CONFIRMED, trừ tồn kho | PUT | Implemented | High |
| 97 | Seller | Từ chối đơn hàng | `PUT /api/seller/orders/{order_id}/reject` – Seller từ chối/huỷ đơn → CANCELLED, hoàn tồn kho | PUT | Implemented | High |
| 98 | Seller | Chuyển trạng thái giao hàng | `PUT /api/seller/orders/{order_id}/ship` – Seller đánh dấu đơn đang giao hàng → SHIPPING | PUT | Implemented | High |
| 99 | Seller | Sản phẩm của seller | `GET /api/seller/products` – Danh sách sản phẩm của seller đang đăng nhập | GET | Implemented | High |
| 100 | Seller | Cập nhật tồn kho | `PUT /api/seller/products/{product_id}/stock` – Cập nhật số lượng tồn kho sản phẩm | PUT | Implemented | High |
| 101 | Seller | Profile seller | `GET /api/seller/profile` – Thông tin shop/profile kèm thống kê sản phẩm, đơn hàng | GET | Implemented | Medium |
| 102 | Seller Onboarding | Đăng ký hồ sơ kinh doanh | `POST /api/seller/register` – Seller nộp hồ sơ kinh doanh (CCCD, giấy phép, ngân hàng) | POST | Implemented | High |
| 103 | Seller Onboarding | Trạng thái xác minh | `GET /api/seller/verification-status` – Seller xem trạng thái duyệt hồ sơ | GET | Implemented | High |
| 104 | Seller Onboarding | Admin duyệt hồ sơ seller | `PUT /api/seller/verify/{user_id}` – Admin xác minh/từ chối hồ sơ, cập nhật activated | PUT | Implemented | High |
| 105 | Seller Onboarding | Danh sách hồ sơ chờ duyệt | `GET /api/seller/applications` – Admin xem danh sách hồ sơ seller chờ duyệt | GET | Implemented | High |
| 106 | Shipping | Tính phí vận chuyển | `POST /api/shipping/fee` – Tính phí vận chuyển GHN theo địa chỉ và trọng lượng | POST | Implemented | High |
| 107 | Shipping | Tạo vận đơn GHN | `POST /api/shipping/create` – Tạo vận đơn tại GHN cho đơn hàng, cập nhật status → SHIPPING | POST | Implemented | High |
| 108 | Shipping | Tra cứu vận đơn | `GET /api/shipping/{shipment_id}/track` – Tra cứu trạng thái vận chuyển chi tiết | GET | Implemented | High |
| 109 | Shipping | Vận đơn theo đơn hàng | `GET /api/shipping/order/{order_id}` – Xem vận đơn theo mã đơn hàng | GET | Implemented | Medium |
| 110 | Shipping | GHN Webhook | `POST /api/shipping/webhook` – GHN gọi webhook khi trạng thái vận đơn thay đổi | POST | Implemented | High |
| 111 | Review | Tạo đánh giá | `POST /api/reviews` – Tạo đánh giá sản phẩm (phải có đơn DELIVERED) | POST | Implemented | High |
| 112 | Review | Đánh giá sản phẩm (public) | `GET /api/reviews/product/{product_id}` – Lấy reviews kèm thống kê, điểm trung bình, phân bố sao | GET | Implemented | High |
| 113 | Review | Cập nhật đánh giá | `PUT /api/reviews/{review_id}` – Cập nhật đánh giá của mình | PUT | Implemented | Medium |
| 114 | Review | Xoá đánh giá | `DELETE /api/reviews/{review_id}` – Xoá đánh giá của mình | DELETE | Implemented | Low |
| 115 | Return | Tạo yêu cầu đổi/trả | `POST /api/returns` – Khách hàng tạo yêu cầu đổi/trả (chỉ đơn DELIVERED) | POST | Implemented | High |
| 116 | Return | Yêu cầu đổi/trả của tôi | `GET /api/returns/my` – Khách hàng xem danh sách yêu cầu đổi/trả của mình | GET | Implemented | Medium |
| 117 | Return | [Admin] Danh sách yêu cầu đổi/trả | `GET /api/returns` – Admin xem tất cả yêu cầu đổi/trả | GET | Implemented | Medium |
| 118 | Return | [Admin] Duyệt yêu cầu đổi/trả | `PUT /api/returns/{return_id}/approve` – Admin duyệt → APPROVED | PUT | Implemented | High |
| 119 | Return | [Admin] Từ chối yêu cầu đổi/trả | `PUT /api/returns/{return_id}/reject` – Admin từ chối → REJECTED | PUT | Implemented | Medium |
| 120 | Return | [Admin] Đã nhận hàng trả về | `PUT /api/returns/{return_id}/received` – Admin đánh dấu đã nhận hàng trả → RECEIVED | PUT | Implemented | Medium |
| 121 | Settlement | Xem ví seller | `GET /api/settlement/wallet` – Seller xem ví: pending, available, đã rút | GET | Implemented | High |
| 122 | Settlement | Lịch sử đối soát | `GET /api/settlement/history` – Lịch sử kỳ đối soát (seller xem của mình, admin xem tất cả) | GET | Implemented | High |
| 123 | Settlement | Tạo kỳ đối soát | `POST /api/settlement/create` – Admin tạo kỳ đối soát: tổng hợp đơn DELIVERED trong khoảng thời gian | POST | Implemented | High |
| 124 | Settlement | Duyệt kỳ đối soát | `POST /api/settlement/{settlement_id}/approve` – Admin duyệt, chuyển tiền pending → available | POST | Implemented | High |
| 125 | Settlement | Chi trả cho seller | `POST /api/settlement/{settlement_id}/payout` – Admin chi trả, trừ available, cộng withdrawn | POST | Implemented | High |
| 126 | Settlement | Lịch sử payout | `GET /api/settlement/payouts` – Lịch sử chi trả (seller xem của mình, admin xem tất cả) | GET | Implemented | Medium |
| 127 | Traceability | Thêm chứng nhận | `POST /api/traceability/certificates` – Seller thêm chứng nhận cho sản phẩm (chờ admin xác minh) | POST | Implemented | High |
| 128 | Traceability | Xem chứng nhận sản phẩm (public) | `GET /api/traceability/certificates/product/{product_id}` – Lấy chứng nhận đã xác minh | GET | Implemented | High |
| 129 | Traceability | Admin xác minh chứng nhận | `PUT /api/traceability/certificates/{cert_id}/verify` – Admin xác minh/từ chối chứng nhận | PUT | Implemented | High |
| 130 | Traceability | Khai báo nguồn gốc | `POST /api/traceability/origins` – Seller khai báo nguồn gốc sản phẩm (cập nhật nếu đã có) | POST | Implemented | High |
| 131 | Traceability | Xem nguồn gốc sản phẩm (public) | `GET /api/traceability/origins/product/{product_id}` – Lấy thông tin nguồn gốc sản phẩm | GET | Implemented | High |
| 132 | Traceability | Xem toàn bộ truy xuất (public) | `GET /api/traceability/product/{product_id}` – Xem tất cả: nguồn gốc + chứng nhận + thông tin SP | GET | Implemented | High |
| 133 | Mobile App | Bài viết công khai | `GET /api/mobile/posts` – Lấy danh sách bài viết đã duyệt (public, không cần đăng nhập) | GET | Implemented | High |
| 134 | Mobile App | Bài viết của tôi | `GET /api/mobile/posts/my` – Producer xem bài viết của mình | GET | Implemented | Medium |
| 135 | Mobile App | Tạo bài viết | `POST /api/mobile/posts/my` – Producer tạo bài viết (hỗ trợ upload ảnh/video multipart) | POST | Implemented | High |
| 136 | Mobile App | Chi tiết bài viết (public) | `GET /api/mobile/posts/{post_id}` – Xem chi tiết bài viết đã duyệt | GET | Implemented | Medium |
| 137 | Mobile App | Cập nhật bài viết | `PUT /api/mobile/posts/my/{post_id}` – Producer cập nhật bài viết (reset PENDING) | PUT | Implemented | Medium |
| 138 | Mobile App | Xoá bài viết | `DELETE /api/mobile/posts/my/{post_id}` – Producer xoá bài viết của mình | DELETE | Implemented | Low |
| 139 | Mobile App | Sản phẩm công khai | `GET /api/mobile/products` – Lấy danh sách sản phẩm đã duyệt (public, không cần đăng nhập) | GET | Implemented | High |
| 140 | Mobile App | Chi tiết sản phẩm (public) | `GET /api/mobile/products/{product_id}` – Xem chi tiết sản phẩm đã duyệt | GET | Implemented | High |
| 141 | Mobile App | Đặt hàng (Checkout) | `POST /api/mobile/checkout` – Tạo đơn hàng từ giỏ, tự động tách đơn theo seller, trừ tồn kho | POST | Implemented | High |
| 142 | Mobile App | Đơn hàng của tôi | `GET /api/mobile/orders/my` – Lấy danh sách đơn hàng của user đang đăng nhập | GET | Implemented | High |
| 143 | Mobile App | Chi tiết đơn hàng | `GET /api/mobile/orders/my/{order_id}` – Xem chi tiết đơn hàng kèm danh sách items | GET | Implemented | High |
| 144 | Mobile App | Profile người dùng | `GET /api/mobile/profile` – Lấy thông tin profile người dùng | GET | Implemented | Medium |
| 145 | Mobile App | Cập nhật profile | `PUT /api/mobile/profile` – Cập nhật tên, giới tính | PUT | Implemented | Medium |
