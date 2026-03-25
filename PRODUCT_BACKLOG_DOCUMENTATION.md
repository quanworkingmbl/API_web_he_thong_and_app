# Product Backlog - Acceptance Criteria Documentation
## Hệ thống E-Commerce Marketplace - Sản phẩm đặc sản và thủ công mỹ nghệ

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mô tả hệ thống
Hệ thống là một nền tảng marketplace thương mại điện tử cho phép nhiều người bán (multi-seller) kinh doanh các sản phẩm đặc sản và thủ công mỹ nghệ từ các vùng miền khác nhau tại Việt Nam. Hệ thống tập trung vào việc xây dựng lòng tin người tiêu dùng thông qua xác thực người bán, truy xuất nguồn gốc sản phẩm và chứng nhận chất lượng.

### 1.2 Công nghệ sử dụng
- **Backend Framework**: FastAPI 0.109.0 (Python 3.11+)
- **Database**: PostgreSQL qua Supabase
- **ORM**: SQLAlchemy 2.0.25 với Alembic migrations
- **Authentication**: JWT với Argon2/Bcrypt password hashing
- **Storage**: Supabase Storage (S3-compatible)
- **Payment Gateway**: VNPay (Vietnamese payment provider)
- **Shipping Integration**: GHN - Giao Hàng Nhanh (Vietnamese logistics)
- **Server**: Uvicorn/Gunicorn ASGI
- **Deployment**: Railway cloud platform

### 1.3 Các thành phần chính
- **Admin Web Portal**: Quản trị hệ thống, duyệt sản phẩm, xử lý đơn hàng
- **Mobile App API**: Giao diện người dùng cuối (khách hàng và người bán)
- **Backend API**: Xử lý logic nghiệp vụ và tích hợp bên ngoài

---

## 2. HỆ THỐNG PHÂN QUYỀN VÀ BẢO MẬT

### 2.1 Xác thực người dùng (Authentication)

#### 2.1.1 Đăng ký tài khoản
- **Acceptance Criteria**:
  - Người dùng có thể đăng ký với email và mật khẩu
  - Mật khẩu tối thiểu 8 ký tự
  - Email phải hợp lệ và không trùng trong hệ thống
  - Mật khẩu được mã hóa bằng Argon2 hoặc Bcrypt
  - Người dùng chọn loại tài khoản: Người tiêu dùng (Consumer) hoặc Người bán (Producer)
  - Thông tin cơ bản được lưu trữ: họ tên, số điện thoại, địa chỉ
  - Hệ thống tạo user ID tự động

#### 2.1.2 Đăng nhập
- **Acceptance Criteria**:
  - Người dùng đăng nhập bằng email và mật khẩu
  - Hệ thống xác thực thông tin đăng nhập
  - Khi thành công, hệ thống trả về JWT access token
  - Token có thời hạn mặc định 30 phút
  - Token được ký bằng HMAC-SHA256 với SECRET_KEY
  - Token chứa thông tin user_id, email, và roles

#### 2.1.3 Phân loại người dùng
- **User Types**:
  - **CONSUMER**: Người tiêu dùng/khách hàng
  - **PRODUCER**: Người bán/nhà sản xuất
  - **ADMIN**: Quản trị viên hệ thống
  - **COOPERATIVE_STAFF**: Nhân viên hợp tác xã
  - **OPERATION_COORDINATOR**: Điều phối viên vận hành

### 2.2 Phân quyền dựa trên vai trò (RBAC)

#### 2.2.1 Các vai trò hệ thống
- **Acceptance Criteria**:
  - **Admin**: Toàn quyền quản trị hệ thống
    - Truy cập tất cả chức năng
    - Quản lý người dùng, vai trò, quyền
    - Duyệt sản phẩm, nội dung, đơn hàng
    - Xử lý khiếu nại và hoàn trả
    - Quản lý thanh toán và đối soát

  - **Content Manager**: Quản lý nội dung
    - Duyệt sản phẩm mới từ người bán
    - Duyệt nội dung (posts, descriptions)
    - Không có quyền quản lý thanh toán hoặc hợp đồng

  - **Operation Coordinator**: Điều phối vận hành
    - Quản lý thanh toán và đối soát
    - Xử lý khiếu nại
    - Quản lý hợp đồng đối tác
    - Không có quyền duyệt nội dung

  - **Cooperative Staff**: Nhân viên
    - Quyền hạn giới hạn theo cấu hình

#### 2.2.2 Hệ thống phân quyền chi tiết
- **Acceptance Criteria**:
  - Mỗi quyền (Permission) có code duy nhất và mô tả
  - Quyền có thể có cấu trúc phân cấp (parent-child relationship)
  - Vai trò (Role) chứa nhiều quyền
  - Người dùng có thể có nhiều vai trò
  - Kiểm tra quyền theo vai trò của người dùng hiện tại
  - Một số quyền chính:
    - `PRODUCT_VIEW`, `PRODUCT_APPROVE`, `PRODUCT_EDIT`, `PRODUCT_LABEL`
    - `PAYMENT_VIEW`, `PAYMENT_CONFIG`, `PAYMENT_RECONCILIATION`, `PAYMENT_REFUND`
    - `CONTENT_VIEW`, `CONTENT_APPROVE`
    - `CONTRACT_VIEW`, `CONTRACT_MANAGE`
    - `COMPLAINT_VIEW`, `COMPLAINT_HANDLE`
    - `SYSTEM_CONTROL`

#### 2.2.3 Bảo mật token
- **Acceptance Criteria**:
  - JWT token được truyền qua Authorization header với định dạng "Bearer {token}"
  - Token được xác thực trước khi xử lý request
  - Token hết hạn sau thời gian cấu hình (mặc định 30 phút)
  - Token không hợp lệ trả về lỗi 401 Unauthorized
  - Token chứa đủ thông tin để xác định người dùng và vai trò

---

## 3. QUẢN LÝ NGƯỜI BÁN VÀ XÁC THỰC

### 3.1 Quy trình onboarding người bán

#### 3.1.1 Đăng ký làm người bán
- **Acceptance Criteria**:
  - Người dùng đăng ký với user_type là PRODUCER
  - Sau khi đăng ký, người bán tạo hồ sơ (SellerProfile)
  - Hồ sơ bao gồm:
    - Thông tin cá nhân/doanh nghiệp
    - Loại hình kinh doanh (Individual, Household, Cooperative, Company)
    - Địa chỉ kinh doanh chi tiết
  - Trạng thái ban đầu: PENDING (Chờ xác thực)

#### 3.1.2 Upload tài liệu xác thực
- **Acceptance Criteria**:
  - Người bán upload các tài liệu cần thiết:
    - **ID Card/CCCD**: Ảnh mặt trước và mặt sau chứng minh thư
    - **Business License**: Giấy phép kinh doanh (nếu là doanh nghiệp)
    - **Tax Code**: Mã số thuế (nếu có)
  - File được upload qua Supabase Storage
  - Hệ thống lưu URL của các file đã upload
  - Định dạng file hỗ trợ: JPG, PNG, PDF

#### 3.1.3 Thông tin tài khoản ngân hàng
- **Acceptance Criteria**:
  - Người bán cung cấp thông tin tài khoản để nhận thanh toán:
    - Tên ngân hàng
    - Số tài khoản
    - Tên chủ tài khoản
    - Chi nhánh ngân hàng
  - Thông tin được mã hóa và lưu trữ an toàn
  - Thông tin này dùng cho việc chi trả sau này

#### 3.1.4 Quy trình xác thực
- **Acceptance Criteria**:
  - Admin hoặc Operation Coordinator xem xét hồ sơ
  - Kiểm tra tính hợp lệ của tài liệu
  - Xác thực thông tin kinh doanh
  - Quyết định:
    - **VERIFIED**: Cho phép người bán hoạt động
    - **REJECTED**: Từ chối với lý do cụ thể
  - Người bán nhận thông báo về kết quả xác thực
  - Chỉ người bán VERIFIED mới có thể đăng bán sản phẩm

### 3.2 Quản lý ví người bán (Seller Wallet)

#### 3.2.1 Cấu trúc ví
- **Acceptance Criteria**:
  - Mỗi người bán có một ví điện tử (SellerWallet)
  - Ví theo dõi:
    - **Pending Balance**: Số dư chờ đối soát (từ đơn hàng chưa hoàn tất)
    - **Available Balance**: Số dư khả dụng (đã đối soát, có thể rút)
    - **Total Withdrawn**: Tổng số tiền đã rút
  - Ví được tạo tự động khi người bán được xác thực
  - Tất cả giao dịch được ghi log đầy đủ

#### 3.2.2 Cập nhật số dư
- **Acceptance Criteria**:
  - Khi đơn hàng hoàn tất → Tiền vào pending_balance
  - Khi settlement được duyệt → Tiền chuyển sang available_balance
  - Khi payout thành công → Trừ available_balance, cộng total_withdrawn
  - Mọi thay đổi số dư được audit trail

---

## 4. QUẢN LÝ SẢN PHẨM VÀ DANH MỤC

### 4.1 Danh mục sản phẩm (Categories)

#### 4.1.1 Cấu trúc danh mục
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ danh mục phân cấp (hierarchical categories)
  - Mỗi danh mục có:
    - Tên danh mục
    - Mô tả
    - Parent category (danh mục cha, nullable)
    - Thứ tự hiển thị
  - Admin có thể tạo, sửa, xóa danh mục
  - Danh mục con kế thừa từ danh mục cha

#### 4.1.2 Các loại sản phẩm chính
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ các danh mục:
    - Rau củ quả (Vegetables & Fruits)
    - Thủ công mỹ nghệ (Handicrafts)
    - Sản phẩm chế biến (Processed Products)
    - Sản phẩm OCOP
    - Và các danh mục khác
  - Mỗi sản phẩm thuộc ít nhất một danh mục

### 4.2 Quản lý sản phẩm

#### 4.2.1 Tạo sản phẩm
- **Acceptance Criteria**:
  - Chỉ người bán đã VERIFIED mới có thể tạo sản phẩm
  - Thông tin sản phẩm bắt buộc:
    - Tên sản phẩm
    - Mô tả chi tiết
    - Giá bán (price)
    - Số lượng tồn kho (stock_quantity)
    - Danh mục (category_id)
    - Khu vực/vùng miền (region_id)
  - Thông tin tùy chọn:
    - Ảnh sản phẩm (nhiều ảnh, lưu dưới dạng JSON array)
    - Đơn vị tính (unit: kg, cái, bó, v.v.)
    - Trọng lượng (weight)
    - Nhãn sản phẩm (label)
  - Trạng thái ban đầu: PENDING (chờ duyệt)
  - Sản phẩm chưa duyệt không hiển thị trên marketplace

#### 4.2.2 Upload ảnh sản phẩm
- **Acceptance Criteria**:
  - Người bán upload ảnh qua endpoint riêng biệt (/api/medias/uploads)
  - Hệ thống lưu trữ ảnh trên Supabase Storage
  - Trả về public URL của ảnh đã upload
  - URL được lưu vào trường images của sản phẩm dưới dạng JSON array
  - Hỗ trợ nhiều ảnh cho mỗi sản phẩm
  - Định dạng hỗ trợ: JPG, PNG, JPEG

#### 4.2.3 Nhãn sản phẩm (Product Labels)
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ các nhãn đặc biệt:
    - **CLEAN_AGRICULTURE**: Nông nghiệp sạch
    - **TRADITIONAL_CRAFT**: Thủ công truyền thống
    - **OCOP**: Sản phẩm OCOP
    - **ORGANIC**: Hữu cơ
  - Admin có quyền gán nhãn cho sản phẩm
  - Nhãn giúp người tiêu dùng dễ dàng nhận biết sản phẩm đặc biệt
  - Sản phẩm có thể có một hoặc không có nhãn

### 4.3 Quy trình duyệt sản phẩm

#### 4.3.1 Review và kiểm duyệt
- **Acceptance Criteria**:
  - Content Manager hoặc Admin xem xét sản phẩm PENDING
  - Kiểm tra các tiêu chí:
    - **description_check**: Mô tả đầy đủ, chính xác
    - **price_check**: Giá cả hợp lý
    - **image_check**: Ảnh sản phẩm rõ ràng, đúng sản phẩm
  - Tạo ProductApproval record ghi lại kết quả kiểm tra
  - Ghi chú (notes) cho từng tiêu chí nếu có vấn đề

#### 4.3.2 Phê duyệt sản phẩm
- **Acceptance Criteria**:
  - Admin/Content Manager quyết định:
    - **APPROVED**: Sản phẩm được hiển thị trên marketplace
    - **REJECTED**: Sản phẩm bị từ chối với lý do cụ thể
  - Khi APPROVED:
    - Trạng thái sản phẩm chuyển sang APPROVED
    - Sản phẩm hiển thị cho người tiêu dùng
    - Người bán nhận thông báo
  - Khi REJECTED:
    - Trạng thái sản phẩm chuyển sang REJECTED
    - Người bán nhận lý do từ chối
    - Người bán có thể chỉnh sửa và gửi lại

#### 4.3.3 Chỉnh sửa sản phẩm đã duyệt
- **Acceptance Criteria**:
  - Người bán có thể chỉnh sửa sản phẩm đã APPROVED
  - Sau khi chỉnh sửa, sản phẩm quay về trạng thái PENDING
  - Cần được duyệt lại trước khi hiển thị thay đổi
  - Đảm bảo chất lượng sản phẩm luôn được kiểm soát

### 4.4 Khu vực địa lý (Regions)

#### 4.4.1 Quản lý vùng miền
- **Acceptance Criteria**:
  - Hệ thống quản lý các khu vực địa lý (Regions)
  - Mỗi khu vực có:
    - Tên khu vực (ví dụ: Miền Bắc, Miền Trung, Miền Nam)
    - Mã khu vực (code)
    - Mô tả đặc điểm khu vực
  - Sản phẩm được gắn với khu vực nguồn gốc
  - Khách hàng có thể tìm kiếm sản phẩm theo khu vực

---

## 5. TRUY XUẤT NGUỒN GỐC VÀ CHỨNG NHẬN

### 5.1 Thông tin nguồn gốc sản phẩm (Product Origin)

#### 5.1.1 Đăng ký nguồn gốc
- **Acceptance Criteria**:
  - Người bán cung cấp thông tin nguồn gốc cho sản phẩm
  - Thông tin bao gồm:
    - **origin_village**: Làng nghề/khu vực sản xuất
    - **batch_number**: Số lô sản xuất
    - **production_date**: Ngày sản xuất
    - **expiry_date**: Hạn sử dụng (nếu có)
    - **ingredients**: Thành phần/nguyên liệu (dạng text hoặc JSON)
    - **production_process**: Quy trình sản xuất
  - Một sản phẩm có thể có nhiều bản ghi nguồn gốc (theo từng lô)
  - Thông tin được lưu trữ trong bảng ProductOrigin

#### 5.1.2 Hiển thị truy xuất nguồn gốc
- **Acceptance Criteria**:
  - Khách hàng có thể xem thông tin nguồn gốc của sản phẩm
  - Thông tin minh bạch, dễ hiểu
  - Bao gồm:
    - Nơi sản xuất
    - Thời gian sản xuất
    - Nguyên liệu và quy trình
  - Tăng độ tin cậy cho người tiêu dùng

### 5.2 Chứng nhận sản phẩm (Product Certificates)

#### 5.2.1 Các loại chứng nhận
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ các loại chứng nhận:
    - **VietGAP**: Tiêu chuẩn nông nghiệp Việt Nam
    - **GlobalGAP**: Tiêu chuẩn nông nghiệp quốc tế
    - **OCOP**: Chương trình OCOP
    - **ISO**: Các chứng nhận ISO
    - **HACCP**: An toàn thực phẩm
    - **ORGANIC**: Sản phẩm hữu cơ
    - **GEOGRAPHICAL_INDICATION**: Chỉ dẫn địa lý
  - Mỗi chứng nhận có:
    - Loại chứng nhận (certificate_type)
    - Số chứng nhận (certificate_number)
    - Ngày cấp (issued_date)
    - Ngày hết hạn (expiry_date)
    - Tổ chức cấp (issued_by)
    - File chứng nhận (document_url)

#### 5.2.2 Xác thực chứng nhận
- **Acceptance Criteria**:
  - Người bán upload chứng nhận cho sản phẩm
  - Trạng thái ban đầu: PENDING
  - Admin xác thực chứng nhận:
    - **VERIFIED**: Chứng nhận hợp lệ
    - **REJECTED**: Chứng nhận không hợp lệ
  - Chỉ chứng nhận VERIFIED mới hiển thị công khai
  - Chứng nhận hết hạn được đánh dấu tự động

#### 5.2.3 Hiển thị chứng nhận cho khách hàng
- **Acceptance Criteria**:
  - Khách hàng xem danh sách chứng nhận của sản phẩm
  - Hiển thị: Loại chứng nhận, số chứng nhận, ngày hết hạn
  - Có thể xem file chứng nhận gốc
  - Badge/icon cho các loại chứng nhận được hiển thị trên sản phẩm
  - Tăng độ tin cậy và giá trị sản phẩm

---

## 6. GIỎ HÀNG VÀ ĐẶT HÀNG

### 6.1 Quản lý giỏ hàng (Shopping Cart)

#### 6.1.1 Thêm sản phẩm vào giỏ
- **Acceptance Criteria**:
  - Người dùng đã đăng nhập có thể thêm sản phẩm vào giỏ
  - Giỏ hàng được lưu trữ trên server (không phải local storage)
  - Mỗi người dùng có một giỏ hàng
  - CartItem bao gồm:
    - Sản phẩm (product_id)
    - Số lượng (quantity)
    - Giá tại thời điểm thêm (unit_price)
  - Kiểm tra tồn kho trước khi thêm
  - Không cho phép thêm quá số lượng tồn kho

#### 6.1.2 Cập nhật và xóa giỏ hàng
- **Acceptance Criteria**:
  - Người dùng có thể:
    - Thay đổi số lượng sản phẩm trong giỏ
    - Xóa sản phẩm khỏi giỏ
    - Xóa toàn bộ giỏ hàng
  - Kiểm tra tồn kho khi tăng số lượng
  - Tự động cập nhật tổng giá trị giỏ hàng

#### 6.1.3 Xem giỏ hàng
- **Acceptance Criteria**:
  - Hiển thị tất cả items trong giỏ hàng
  - Thông tin mỗi item:
    - Tên sản phẩm
    - Ảnh sản phẩm
    - Giá đơn vị
    - Số lượng
    - Thành tiền
  - Tổng giá trị giỏ hàng
  - Người bán của từng sản phẩm

### 6.2 Quy trình đặt hàng

#### 6.2.1 Tạo đơn hàng từ giỏ hàng
- **Acceptance Criteria**:
  - Khách hàng checkout từ giỏ hàng
  - Hệ thống tạo Order với thông tin:
    - **Customer Info**: Tên, email, số điện thoại, địa chỉ giao hàng
    - **Seller Info**: Lấy từ sản phẩm
    - **Order Items**: Copy từ giỏ hàng với snapshot giá
    - **Subtotal**: Tổng giá sản phẩm
    - **Shipping Fee**: Phí vận chuyển (tính từ GHN API)
    - **Discount**: Giảm giá (nếu có)
    - **Total**: Tổng thanh toán = Subtotal + Shipping - Discount
  - Trạng thái ban đầu: PENDING
  - Sau khi tạo order, xóa items khỏi giỏ hàng

#### 6.2.2 Platform fee và seller amount
- **Acceptance Criteria**:
  - Hệ thống tự động tính:
    - **Platform Fee**: Phí nền tảng (mặc định 5% của subtotal)
    - **Seller Amount**: Số tiền người bán nhận = Total - Platform Fee
  - Platform fee có thể cấu hình theo phần trăm
  - Seller amount được lưu trong order để đối soát sau này

#### 6.2.3 Trạng thái đơn hàng
- **Acceptance Criteria**:
  - Đơn hàng đi qua các trạng thái:
    1. **PENDING**: Chờ xác nhận
    2. **CONFIRMED**: Admin/Người bán xác nhận
    3. **PROCESSING**: Đang chuẩn bị hàng
    4. **SHIPPING**: Đang giao hàng
    5. **DELIVERED**: Đã giao hàng thành công
    6. **CANCELLED**: Đã hủy
  - Mỗi chuyển đổi trạng thái được ghi log với timestamp
  - Chỉ admin và người bán liên quan mới có quyền cập nhật trạng thái
  - Không thể chuyển ngược trạng thái (ví dụ: từ DELIVERED về PROCESSING)

#### 6.2.4 Snapshot thông tin sản phẩm
- **Acceptance Criteria**:
  - OrderItem lưu giữ thông tin sản phẩm tại thời điểm đặt hàng:
    - product_snapshot: Lưu tên, giá, mô tả sản phẩm
  - Đảm bảo dữ liệu đơn hàng không bị ảnh hưởng khi sản phẩm thay đổi giá
  - Khách hàng và người bán luôn thấy thông tin nhất quán với lúc đặt hàng

---

## 7. THANH TOÁN VÀ TÍCH HỢP CỔNG THANH TOÁN

### 7.1 Phương thức thanh toán

#### 7.1.1 Các phương thức được hỗ trợ
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ các phương thức thanh toán:
    - **COD**: Thanh toán khi nhận hàng (Cash on Delivery)
    - **BANK_TRANSFER**: Chuyển khoản ngân hàng
    - **VNPAY**: Cổng thanh toán VNPay
    - **MOMO**: Ví điện tử MoMo
    - **ZALOPAY**: Ví điện tử ZaloPay
  - Khách hàng chọn phương thức khi checkout
  - Mỗi phương thức có flow xử lý riêng

### 7.2 Tích hợp VNPay

#### 7.2.1 Tạo payment URL
- **Acceptance Criteria**:
  - Khi khách hàng chọn VNPay, hệ thống:
    - Tạo Payment record với trạng thái PENDING
    - Generate payment URL với các tham số:
      - Số tiền (vnp_Amount)
      - Mã đơn hàng (vnp_TxnRef)
      - Thông tin đơn hàng (vnp_OrderInfo)
      - IP khách hàng (vnp_IpAddr)
      - Thời gian tạo (vnp_CreateDate)
      - Thời gian hết hạn (15 phút)
    - Tạo secure hash bằng HMAC-SHA512
    - Trả về URL để redirect khách hàng
  - URL hợp lệ trong 15 phút

#### 7.2.2 Xử lý callback từ VNPay
- **Acceptance Criteria**:
  - VNPay gửi callback sau khi khách thanh toán
  - Hệ thống:
    - Xác thực secure hash từ VNPay
    - Kiểm tra mã response (vnp_ResponseCode)
    - Nếu thành công (00):
      - Cập nhật Payment status → COMPLETED
      - Tạo PaymentTransaction record
      - Cập nhật Order status → CONFIRMED
      - Cập nhật Seller Wallet pending_balance
    - Nếu thất bại:
      - Cập nhật Payment status → FAILED
      - Ghi log lý do thất bại
  - Đảm bảo idempotency (không xử lý trùng lặp)

#### 7.2.3 IPN (Instant Payment Notification)
- **Acceptance Criteria**:
  - VNPay gửi IPN để thông báo kết quả thanh toán
  - Hệ thống xử lý tương tự callback
  - Đảm bảo xử lý cả callback và IPN (trong trường hợp một trong hai thất bại)
  - Trả về response code cho VNPay theo định dạng

### 7.3 Quản lý Payment

#### 7.3.1 Payment record
- **Acceptance Criteria**:
  - Mỗi Order có một Payment record
  - Payment chứa:
    - Đơn hàng liên kết (order_id)
    - Phương thức thanh toán (payment_method)
    - Số tiền thanh toán (amount)
    - Platform fee
    - Seller amount (amount - platform_fee)
    - Trạng thái (status)
    - Transaction reference
  - Tất cả giao dịch được audit trail

#### 7.3.2 Trạng thái thanh toán
- **Acceptance Criteria**:
  - Các trạng thái Payment:
    - **PENDING**: Chờ thanh toán
    - **COMPLETED**: Đã thanh toán thành công
    - **FAILED**: Thanh toán thất bại
    - **REFUNDED**: Đã hoàn tiền
  - Mỗi thay đổi trạng thái tạo PaymentTransaction
  - PaymentTransaction ghi lại:
    - Trạng thái cũ và mới
    - Số tiền giao dịch
    - Transaction ID từ gateway
    - Thời gian giao dịch

#### 7.3.3 Hoàn tiền (Refund)
- **Acceptance Criteria**:
  - Admin/Operation Coordinator có thể xử lý hoàn tiền
  - Khi refund:
    - Payment status → REFUNDED
    - Tạo PaymentTransaction với loại REFUND
    - Trừ số tiền từ Seller Wallet (nếu đã settlement)
    - Ghi log lý do hoàn tiền
  - Hỗ trợ hoàn tiền một phần hoặc toàn bộ

---

## 8. VẬN CHUYỂN VÀ LOGISTICS

### 8.1 Tích hợp GHN (Giao Hàng Nhanh)

#### 8.1.1 Tính phí vận chuyển
- **Acceptance Criteria**:
  - Khi khách hàng checkout, hệ thống tự động tính phí ship
  - Gọi GHN API với thông tin:
    - Địa chỉ gửi (seller address)
    - Địa chỉ nhận (customer address)
    - Trọng lượng (weight)
    - Loại dịch vụ (service_type_id)
  - Trả về phí vận chuyển
  - Phí được cộng vào tổng đơn hàng
  - Hỗ trợ mock mode nếu không có GHN config

#### 8.1.2 Tạo đơn giao hàng
- **Acceptance Criteria**:
  - Khi Order status → CONFIRMED:
    - Tạo Shipment record
    - Gọi GHN API để tạo order
    - Nhận tracking code từ GHN
    - Lưu tracking code vào Shipment
  - Thông tin shipment:
    - Mã vận đơn (tracking_code)
    - Nhà vận chuyển (provider: GHN, GHTK, VNPost, Manual)
    - Trạng thái (status)
    - Phí vận chuyển
    - Thời gian dự kiến giao hàng

#### 8.1.3 Theo dõi vận đơn
- **Acceptance Criteria**:
  - Các trạng thái vận đơn:
    - **PENDING**: Chờ tạo vận đơn
    - **CREATED**: Đã tạo vận đơn
    - **PICKED_UP**: Đã lấy hàng
    - **IN_TRANSIT**: Đang vận chuyển
    - **DELIVERED**: Đã giao hàng
    - **RETURNED**: Hoàn trả
    - **CANCELLED**: Đã hủy
  - Khách hàng và người bán có thể tra cứu trạng thái
  - Cập nhật trạng thái Order tương ứng khi Shipment thay đổi
  - Webhook từ GHN để cập nhật real-time (nếu có cấu hình)

#### 8.1.4 Xử lý giao hàng thất bại
- **Acceptance Criteria**:
  - Khi Shipment RETURNED hoặc thất bại:
    - Cập nhật Order status → CANCELLED hoặc RETURN_PROCESSING
    - Thông báo cho khách hàng và người bán
    - Khách hàng có thể yêu cầu giao lại hoặc hoàn tiền
  - Ghi log lý do giao hàng thất bại

### 8.2 Nhiều nhà vận chuyển

#### 8.2.1 Hỗ trợ đa nhà vận chuyển
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ:
    - **GHN**: Giao hàng nhanh (primary)
    - **GHTK**: Giao hàng tiết kiệm
    - **VNPOST**: Bưu điện Việt Nam
    - **MANUAL**: Giao hàng thủ công
  - Người bán hoặc admin chọn nhà vận chuyển
  - Mỗi nhà vận chuyển có flow tích hợp riêng
  - Tracking code format khác nhau tùy nhà vận chuyển

---

## 9. ĐỐI SOÁT VÀ CHI TRẢ

### 9.1 Settlement (Đối soát)

#### 9.1.1 Chu kỳ đối soát
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ chu kỳ đối soát:
    - **WEEKLY**: Hàng tuần
    - **MONTHLY**: Hàng tháng
  - Admin cấu hình chu kỳ mặc định
  - Mỗi Settlement bao gồm:
    - Người bán (seller_id)
    - Chu kỳ (period_start, period_end)
    - Số đơn hàng (total_orders)
    - Tổng doanh thu (total_amount)
    - Tổng platform fee (total_platform_fee)
    - Số tiền người bán nhận (seller_amount)

#### 9.1.2 Tạo settlement
- **Acceptance Criteria**:
  - Admin hoặc hệ thống tự động tạo Settlement
  - Tổng hợp tất cả đơn hàng DELIVERED trong khoảng thời gian
  - Tính toán:
    - Tổng doanh thu từ các đơn hàng
    - Tổng platform fee
    - Seller amount = Total - Platform Fee
  - Trạng thái ban đầu: PENDING
  - Có thể tạo Settlement thủ công hoặc tự động theo lịch

#### 9.1.3 Phê duyệt settlement
- **Acceptance Criteria**:
  - Admin hoặc Operation Coordinator xem xét Settlement
  - Kiểm tra tính chính xác của số liệu
  - Phê duyệt:
    - **APPROVED**: Di chuyển tiền từ pending_balance sang available_balance của Seller Wallet
    - **REJECTED**: Yêu cầu kiểm tra lại
  - Sau khi APPROVED, seller có thể rút tiền

#### 9.1.4 Hoàn tất settlement
- **Acceptance Criteria**:
  - Khi Settlement status → COMPLETED:
    - Seller Wallet available_balance được cập nhật
    - Tạo ghi chú lịch sử settlement
    - Gửi thông báo cho người bán
  - Settlement không thể chỉnh sửa sau khi COMPLETED

### 9.2 Payout (Chi trả)

#### 9.2.1 Yêu cầu rút tiền
- **Acceptance Criteria**:
  - Người bán có thể yêu cầu rút tiền từ available_balance
  - Thông tin payout:
    - Số tiền muốn rút (amount)
    - Tài khoản ngân hàng (lấy từ SellerProfile)
    - Phương thức (BANK_TRANSFER)
  - Kiểm tra:
    - Số dư available_balance đủ
    - Thông tin tài khoản đầy đủ
  - Trạng thái ban đầu: PENDING
  - Tạo Payout record

#### 9.2.2 Xử lý payout
- **Acceptance Criteria**:
  - Admin hoặc Operation Coordinator xử lý yêu cầu rút tiền
  - Các bước:
    1. **PENDING**: Chờ xử lý
    2. **PROCESSING**: Đang thực hiện chuyển khoản
    3. **SUCCESS**: Đã chuyển khoản thành công
    4. **FAILED**: Thất bại (lý do: sai thông tin TK, v.v.)
  - Khi SUCCESS:
    - Trừ available_balance
    - Cộng total_withdrawn
    - Lưu transaction_reference (mã giao dịch ngân hàng)
  - Khi FAILED:
    - Không trừ balance
    - Ghi lý do thất bại
    - Người bán có thể tạo yêu cầu mới

#### 9.2.3 Lịch sử giao dịch
- **Acceptance Criteria**:
  - Người bán xem lịch sử payout
  - Thông tin hiển thị:
    - Số tiền
    - Thời gian yêu cầu
    - Trạng thái
    - Tài khoản nhận
    - Transaction reference (nếu có)
  - Admin xem tất cả payout trong hệ thống
  - Hỗ trợ filter theo trạng thái, thời gian, người bán

---

## 10. KHIẾU NẠI VÀ HOÀN TRẢ

### 10.1 Hệ thống hoàn trả (Returns)

#### 10.1.1 Tạo yêu cầu hoàn trả
- **Acceptance Criteria**:
  - Khách hàng có thể yêu cầu hoàn trả sau khi nhận hàng
  - Các loại hoàn trả:
    - **FULL_RETURN**: Trả hàng toàn bộ và hoàn tiền
    - **EXCHANGE**: Đổi sản phẩm khác
  - Thông tin yêu cầu:
    - Đơn hàng liên quan (order_id)
    - Loại hoàn trả (return_type)
    - Lý do (reason)
    - Ảnh chứng minh (evidence_images)
  - Trạng thái ban đầu: PENDING
  - Chỉ cho phép hoàn trả trong thời gian quy định (ví dụ: 7 ngày)

#### 10.1.2 Xử lý hoàn trả
- **Acceptance Criteria**:
  - Admin xem xét yêu cầu hoàn trả
  - Kiểm tra:
    - Lý do hoàn trả hợp lệ
    - Ảnh chứng minh
    - Chính sách hoàn trả của sản phẩm
  - Quyết định:
    - **APPROVED**: Chấp nhận hoàn trả
      - Khách hàng gửi hàng về
      - Status → RECEIVED khi người bán nhận hàng
      - Status → REFUNDED sau khi hoàn tiền
    - **REJECTED**: Từ chối với lý do
  - Thông báo cho khách hàng và người bán

#### 10.1.3 Hoàn tiền cho khách hàng
- **Acceptance Criteria**:
  - Khi ReturnRequest → REFUNDED:
    - Tạo refund transaction
    - Cập nhật Payment status → REFUNDED
    - Trừ tiền từ Seller Wallet (nếu đã settlement)
    - Hoàn tiền cho khách hàng qua phương thức ban đầu
  - Ghi log đầy đủ quá trình hoàn tiền

### 10.2 Hệ thống khiếu nại (Complaints)

#### 10.2.1 Tạo khiếu nại
- **Acceptance Criteria**:
  - Khách hàng có thể tạo khiếu nại
  - Các loại khiếu nại:
    - **PRODUCT**: Về sản phẩm (chất lượng, không đúng mô tả)
    - **PAYMENT**: Về thanh toán
    - **SERVICE**: Về dịch vụ (giao hàng, hỗ trợ)
  - Thông tin khiếu nại:
    - Đơn hàng liên quan (order_id, optional)
    - Loại khiếu nại (complaint_type)
    - Tiêu đề (title)
    - Mô tả chi tiết (description)
  - Trạng thái ban đầu: PENDING

#### 10.2.2 Xử lý khiếu nại
- **Acceptance Criteria**:
  - Admin hoặc Operation Coordinator xử lý khiếu nại
  - Các trạng thái:
    - **PENDING**: Chờ xử lý
    - **IN_PROGRESS**: Đang xử lý
    - **RESOLVED**: Đã giải quyết
    - **CLOSED**: Đã đóng
  - Có thể assign handler (người xử lý)
  - Ghi chú quá trình xử lý (resolution_notes)
  - Khách hàng nhận thông báo khi có cập nhật

#### 10.2.3 Resolution và follow-up
- **Acceptance Criteria**:
  - Khi khiếu nại RESOLVED:
    - Ghi lại giải pháp (resolution_notes)
    - Khách hàng có thể comment/feedback
    - Nếu hài lòng → Status CLOSED
    - Nếu chưa hài lòng → Reopen khiếu nại
  - Tất cả khiếu nại được tracking để cải thiện dịch vụ

### 10.3 Đánh giá sản phẩm (Reviews)

#### 10.3.1 Tạo đánh giá
- **Acceptance Criteria**:
  - Khách hàng có thể đánh giá sản phẩm đã mua
  - Chỉ cho phép đánh giá sau khi order DELIVERED
  - Mỗi khách hàng chỉ đánh giá một lần cho mỗi sản phẩm
  - Thông tin đánh giá:
    - Điểm rating (1-5 sao)
    - Nội dung bình luận (comment)
  - Rating và comment hiển thị công khai

#### 10.3.2 Hiển thị đánh giá
- **Acceptance Criteria**:
  - Sản phẩm hiển thị:
    - Điểm trung bình (average rating)
    - Tổng số đánh giá
    - Danh sách đánh giá gần nhất
  - Người bán có thể xem tất cả đánh giá sản phẩm của mình
  - Sắp xếp theo thời gian (mới nhất trước)

---

## 11. QUẢN LÝ NỘI DUNG

### 11.1 Content approval system

#### 11.1.1 Tạo nội dung
- **Acceptance Criteria**:
  - Người dùng (đặc biệt là người bán) có thể tạo nội dung:
    - Bài viết giới thiệu sản phẩm
    - Bài viết về làng nghề
    - Nội dung marketing
  - Thông tin content:
    - Tiêu đề (title)
    - Nội dung (body)
    - Ảnh và video (images, videos)
    - Loại nội dung (content_type)
  - Trạng thái ban đầu: PENDING
  - Nội dung chưa duyệt không hiển thị công khai

#### 11.1.2 Duyệt nội dung
- **Acceptance Criteria**:
  - Content Manager hoặc Admin duyệt nội dung
  - Kiểm tra:
    - Nội dung phù hợp, không vi phạm
    - Ảnh và video hợp lệ
    - Không có thông tin sai lệch
  - Quyết định:
    - **APPROVED**: Nội dung được công khai
    - **REJECTED**: Từ chối với lý do
  - Người tạo nhận thông báo kết quả

#### 11.1.3 Upload media
- **Acceptance Criteria**:
  - Hỗ trợ upload ảnh và video
  - Upload qua endpoint /api/medias/uploads
  - File được lưu trên Supabase Storage
  - Trả về public URL
  - URL được lưu trong trường images/videos dạng JSON array
  - Giới hạn kích thước file (configurable)
  - Định dạng hỗ trợ: JPG, PNG, MP4, MOV

---

## 12. HỢP ĐỒNG ĐỐI TÁC

### 12.1 Quản lý hợp đồng (Partner Contracts)

#### 12.1.1 Tạo hợp đồng
- **Acceptance Criteria**:
  - Admin hoặc Operation Coordinator tạo hợp đồng
  - Các loại hợp đồng:
    - **ADVERTISING**: Hợp đồng quảng cáo
    - **PARTNERSHIP**: Hợp đồng đối tác
  - Thông tin hợp đồng:
    - Đối tác (partner_id - user_id)
    - Loại hợp đồng (contract_type)
    - Ngày bắt đầu (start_date)
    - Ngày kết thúc (end_date)
    - Điều khoản (terms)
    - Giá trị hợp đồng (value, nếu có)
  - Trạng thái ban đầu: DRAFT

#### 12.1.2 Trạng thái hợp đồng
- **Acceptance Criteria**:
  - Các trạng thái hợp đồng:
    - **DRAFT**: Nháp, chưa kích hoạt
    - **ACTIVE**: Đang có hiệu lực
    - **EXPIRED**: Hết hạn
    - **CANCELLED**: Đã hủy
  - Tự động chuyển sang EXPIRED khi quá end_date
  - Admin có thể CANCEL hợp đồng bất kỳ lúc nào
  - Ghi log người tạo và thời gian tạo

#### 12.1.3 Quản lý đối tác
- **Acceptance Criteria**:
  - Xem danh sách hợp đồng theo đối tác
  - Xem lịch sử hợp đồng
  - Filter theo trạng thái, loại hợp đồng
  - Export báo cáo hợp đồng

---

## 13. TỔ CHỨC VÀ QUẢN LÝ NHÓM

### 13.1 Quản lý tổ chức (Organizations)

#### 13.1.1 Cấu trúc tổ chức
- **Acceptance Criteria**:
  - Hệ thống hỗ trợ quản lý các tổ chức (hợp tác xã, công ty, v.v.)
  - Thông tin tổ chức:
    - Tên tổ chức (name)
    - Loại tổ chức (type: COOPERATIVE, COMPANY, ASSOCIATION)
    - Mã số thuế (tax_code)
    - Địa chỉ
    - Thông tin liên hệ
  - Admin có thể tạo và quản lý tổ chức

#### 13.1.2 Thành viên tổ chức
- **Acceptance Criteria**:
  - Người dùng có thể thuộc nhiều tổ chức
  - Bảng UserOrganization quản lý quan hệ nhiều-nhiều
  - Mỗi thành viên có vai trò trong tổ chức (role_in_org)
  - Ngày tham gia được ghi nhận (joined_at)
  - Admin tổ chức quản lý thành viên

---

## 14. DASHBOARD VÀ BÁO CÁO

### 14.1 Dashboard Admin

#### 14.1.1 Tổng quan hệ thống
- **Acceptance Criteria**:
  - Hiển thị các chỉ số quan trọng:
    - Tổng số đơn hàng (theo trạng thái)
    - Doanh thu trong kỳ
    - Tổng platform fee thu được
    - Số lượng người bán active
    - Số lượng sản phẩm đang chờ duyệt
    - Số khiếu nại chưa xử lý
  - Biểu đồ thống kê theo thời gian
  - So sánh với kỳ trước

#### 14.1.2 Báo cáo đơn hàng
- **Acceptance Criteria**:
  - Thống kê đơn hàng theo:
    - Thời gian (ngày, tuần, tháng)
    - Trạng thái
    - Người bán
    - Khu vực
  - Hiển thị:
    - Số lượng đơn hàng
    - Giá trị đơn hàng
    - Tỷ lệ thành công
    - Tỷ lệ hủy/hoàn trả
  - Export báo cáo Excel/CSV

#### 14.1.3 Báo cáo thanh toán
- **Acceptance Criteria**:
  - Thống kê thanh toán:
    - Theo phương thức thanh toán
    - Theo trạng thái
    - Theo người bán
  - Hiển thị:
    - Tổng giá trị thanh toán
    - Platform fee thu được
    - Số tiền chờ đối soát
    - Số tiền đã chi trả
  - Biểu đồ dòng tiền (cash flow)

#### 14.1.4 Báo cáo người bán
- **Acceptance Criteria**:
  - Thống kê hiệu suất người bán:
    - Top người bán theo doanh thu
    - Số lượng đơn hàng
    - Tỷ lệ hủy đơn
    - Điểm đánh giá trung bình
    - Số khiếu nại
  - Ranking người bán
  - Xác định người bán cần hỗ trợ

### 14.2 Dashboard người bán

#### 14.2.1 Tổng quan bán hàng
- **Acceptance Criteria**:
  - Người bán xem dashboard cá nhân:
    - Tổng đơn hàng trong kỳ
    - Doanh thu (sau trừ platform fee)
    - Số dư ví (pending, available)
    - Sản phẩm đang bán
    - Đơn hàng cần xử lý
  - Biểu đồ doanh thu theo thời gian
  - Top sản phẩm bán chạy

### 14.3 Statistics API

#### 14.3.1 Thống kê real-time
- **Acceptance Criteria**:
  - API cung cấp dữ liệu thống kê real-time
  - Hỗ trợ filter theo:
    - Khoảng thời gian (start_date, end_date)
    - Người bán (seller_id)
    - Danh mục (category_id)
    - Khu vực (region_id)
  - Dữ liệu được cache để tối ưu performance
  - Refresh cache theo interval (configurable)

---

## 15. MOBILE APP API

### 15.1 API cho ứng dụng di động

#### 15.1.1 API dành cho khách hàng
- **Acceptance Criteria**:
  - Mobile app sử dụng các API riêng biệt tại /api/mobile-app
  - Chức năng chính:
    - Xem danh sách sản phẩm (có phân trang, filter)
    - Xem chi tiết sản phẩm
    - Thêm vào giỏ hàng
    - Checkout và thanh toán
    - Theo dõi đơn hàng
    - Đánh giá sản phẩm
    - Xem lịch sử đơn hàng
  - Response format tối ưu cho mobile
  - Hỗ trợ pagination và lazy loading

#### 15.1.2 API dành cho người bán
- **Acceptance Criteria**:
  - Người bán quản lý qua mobile app:
    - Xem danh sách đơn hàng
    - Cập nhật trạng thái đơn hàng
    - Quản lý sản phẩm (thêm, sửa)
    - Xem doanh thu và ví
    - Nhận thông báo đơn hàng mới
  - Push notification cho sự kiện quan trọng

---

## 16. CẤU HÌNH HỆ THỐNG

### 16.1 Biến môi trường (Environment Variables)

#### 16.1.1 Database configuration
- **Acceptance Criteria**:
  - Cấu hình kết nối PostgreSQL/Supabase:
    - `DATABASE_URL`: URL kết nối database
    - `SUPABASE_URL`: URL Supabase project
    - `SUPABASE_KEY`: Supabase anon key
    - `SUPABASE_SERVICE_KEY`: Supabase service role key
  - Connection pool configuration
  - Timeout settings

#### 16.1.2 JWT configuration
- **Acceptance Criteria**:
  - Cấu hình JWT:
    - `SECRET_KEY`: Key để ký JWT (phải bảo mật)
    - `ALGORITHM`: HS256
    - `ACCESS_TOKEN_EXPIRE_MINUTES`: Thời gian hết hạn token (mặc định 30)
  - Key được generate ngẫu nhiên, độ dài tối thiểu 32 bytes
  - Không được hardcode trong source code

#### 16.1.3 VNPay configuration
- **Acceptance Criteria**:
  - Cấu hình VNPay:
    - `VNPAY_TMN_CODE`: Mã website VNPay cung cấp
    - `VNPAY_HASH_SECRET`: Secret key để hash
    - `VNPAY_URL`: URL thanh toán VNPay
    - `VNPAY_RETURN_URL`: URL callback sau thanh toán
  - Hỗ trợ môi trường sandbox và production
  - Hash secret phải được bảo mật tuyệt đối

#### 16.1.4 GHN configuration
- **Acceptance Criteria**:
  - Cấu hình GHN:
    - `GHN_API_TOKEN`: Token để gọi GHN API
    - `GHN_SHOP_ID`: ID cửa hàng trên GHN
    - `GHN_API_URL`: URL GHN API
  - Hỗ trợ mock mode khi không có config
  - Token cần được bảo mật

#### 16.1.5 Supabase Storage configuration
- **Acceptance Criteria**:
  - Cấu hình storage:
    - `SUPABASE_STORAGE_BUCKET`: Tên bucket lưu trữ
    - Access key và secret key
  - Cấu hình public access cho ảnh sản phẩm
  - Private access cho tài liệu xác thực

### 16.2 Platform settings

#### 16.2.1 Platform fee configuration
- **Acceptance Criteria**:
  - Admin cấu hình phần trăm platform fee
  - Mặc định: 5% của subtotal
  - Có thể thay đổi theo thời gian
  - Áp dụng cho đơn hàng mới
  - Lưu lịch sử thay đổi fee

#### 16.2.2 Settlement cycle configuration
- **Acceptance Criteria**:
  - Admin cấu hình chu kỳ settlement
  - Tùy chọn: WEEKLY hoặc MONTHLY
  - Cấu hình ngày chạy settlement tự động
  - Có thể tạo settlement thủ công bất kỳ lúc nào

---

## 17. MÔ HÌNH DỮ LIỆU

### 17.1 User Management Models

#### 17.1.1 User
- **Các trường dữ liệu**:
  - `id`: UUID, primary key
  - `email`: String, unique, not null
  - `password_hash`: String, mã hóa
  - `full_name`: String
  - `phone`: String
  - `address`: Text
  - `user_type`: Enum (CONSUMER, PRODUCER, ADMIN, etc.)
  - `is_active`: Boolean
  - `created_at`, `updated_at`: Timestamp

#### 17.1.2 Role
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `name`: String, unique (admin, content_manager, operation_coordinator)
  - `description`: Text
  - `is_system_role`: Boolean (true cho các role mặc định)
  - `created_at`, `updated_at`: Timestamp

#### 17.1.3 Permission
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `name`: String, unique
  - `code`: String, unique (PRODUCT_VIEW, PAYMENT_CONFIG, etc.)
  - `description`: Text
  - `parent_id`: Integer, nullable (cho phân cấp)
  - `created_at`, `updated_at`: Timestamp

#### 17.1.4 UserRole (Many-to-Many)
- **Các trường dữ liệu**:
  - `user_id`: UUID, FK to User
  - `role_id`: Integer, FK to Role
  - `assigned_at`: Timestamp
  - Composite primary key (user_id, role_id)

#### 17.1.5 RolePermission (Many-to-Many)
- **Các trường dữ liệu**:
  - `role_id`: Integer, FK to Role
  - `permission_id`: Integer, FK to Permission
  - Composite primary key (role_id, permission_id)

### 17.2 Product Models

#### 17.2.1 Product
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `seller_id`: UUID, FK to User
  - `name`: String, not null
  - `description`: Text
  - `price`: Decimal(10,2)
  - `stock_quantity`: Integer
  - `unit`: String (kg, cái, bó)
  - `weight`: Decimal (for shipping calculation)
  - `images`: Text (JSON array of URLs)
  - `category_id`: Integer, FK to Category
  - `region_id`: Integer, FK to Region
  - `status`: Enum (PENDING, APPROVED, REJECTED)
  - `label`: Enum (CLEAN_AGRICULTURE, TRADITIONAL_CRAFT, OCOP, ORGANIC)
  - `is_active`: Boolean
  - `created_at`, `updated_at`: Timestamp

#### 17.2.2 Category
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `name`: String, unique
  - `description`: Text
  - `parent_id`: Integer, FK to Category (nullable)
  - `display_order`: Integer
  - `created_at`, `updated_at`: Timestamp

#### 17.2.3 Region
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `name`: String (Miền Bắc, Miền Trung, Miền Nam)
  - `code`: String, unique
  - `description`: Text
  - `created_at`, `updated_at`: Timestamp

#### 17.2.4 ProductApproval
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `product_id`: Integer, FK to Product
  - `approver_id`: UUID, FK to User
  - `status`: Enum (APPROVED, REJECTED)
  - `description_check`: Boolean
  - `price_check`: Boolean
  - `image_check`: Boolean
  - `notes`: Text
  - `approved_at`: Timestamp

### 17.3 Traceability Models

#### 17.3.1 ProductOrigin
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `product_id`: Integer, FK to Product
  - `origin_village`: String (làng nghề)
  - `batch_number`: String (số lô)
  - `production_date`: Date
  - `expiry_date`: Date, nullable
  - `ingredients`: Text/JSON
  - `production_process`: Text
  - `created_at`, `updated_at`: Timestamp

#### 17.3.2 ProductCertificate
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `product_id`: Integer, FK to Product
  - `certificate_type`: Enum (VietGAP, GlobalGAP, OCOP, ISO, HACCP, ORGANIC, GEOGRAPHICAL_INDICATION)
  - `certificate_number`: String
  - `issued_date`: Date
  - `expiry_date`: Date
  - `issued_by`: String (tổ chức cấp)
  - `document_url`: String (file chứng nhận)
  - `verification_status`: Enum (PENDING, VERIFIED, REJECTED)
  - `created_at`, `updated_at`: Timestamp

### 17.4 Order Models

#### 17.4.1 Order
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `customer_id`: UUID, FK to User
  - `seller_id`: UUID, FK to User
  - `customer_name`: String
  - `customer_email`: String
  - `customer_phone`: String
  - `shipping_address`: Text
  - `subtotal`: Decimal(10,2)
  - `shipping_fee`: Decimal(10,2)
  - `discount`: Decimal(10,2)
  - `total`: Decimal(10,2)
  - `platform_fee`: Decimal(10,2)
  - `seller_amount`: Decimal(10,2)
  - `status`: Enum (PENDING, CONFIRMED, PROCESSING, SHIPPING, DELIVERED, CANCELLED)
  - `notes`: Text
  - `created_at`, `updated_at`: Timestamp

#### 17.4.2 OrderItem
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `order_id`: Integer, FK to Order
  - `product_id`: Integer, FK to Product
  - `product_snapshot`: JSON (lưu thông tin sản phẩm tại thời điểm đặt)
  - `quantity`: Integer
  - `unit_price`: Decimal(10,2)
  - `total_price`: Decimal(10,2)
  - `created_at`: Timestamp

### 17.5 Payment Models

#### 17.5.1 Payment
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `order_id`: Integer, FK to Order, unique
  - `payment_method`: Enum (COD, BANK_TRANSFER, VNPAY, MOMO, ZALOPAY)
  - `amount`: Decimal(10,2)
  - `platform_fee`: Decimal(10,2)
  - `seller_amount`: Decimal(10,2)
  - `status`: Enum (PENDING, COMPLETED, FAILED, REFUNDED)
  - `transaction_reference`: String (mã GD từ gateway)
  - `created_at`, `updated_at`: Timestamp

#### 17.5.2 PaymentTransaction
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `payment_id`: Integer, FK to Payment
  - `transaction_type`: Enum (PAYMENT, REFUND)
  - `amount`: Decimal(10,2)
  - `status`: Enum (PENDING, SUCCESS, FAILED)
  - `gateway_response`: JSON (response từ payment gateway)
  - `created_at`: Timestamp

### 17.6 Seller Models

#### 17.6.1 SellerProfile
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `user_id`: UUID, FK to User, unique
  - `business_name`: String
  - `business_type`: Enum (INDIVIDUAL, HOUSEHOLD, COOPERATIVE, COMPANY)
  - `tax_code`: String, nullable
  - `business_address`: Text
  - `id_card_front_url`: String (ảnh CCCD mặt trước)
  - `id_card_back_url`: String (ảnh CCCD mặt sau)
  - `business_license_url`: String (giấy phép KD)
  - `bank_name`: String
  - `bank_account_number`: String
  - `bank_account_name`: String
  - `bank_branch`: String
  - `verification_status`: Enum (PENDING, VERIFIED, REJECTED)
  - `verification_notes`: Text (lý do reject nếu có)
  - `verified_at`: Timestamp, nullable
  - `verified_by`: UUID, FK to User, nullable
  - `created_at`, `updated_at`: Timestamp

#### 17.6.2 SellerWallet
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `seller_id`: UUID, FK to User, unique
  - `pending_balance`: Decimal(12,2) (tiền chờ đối soát)
  - `available_balance`: Decimal(12,2) (tiền có thể rút)
  - `total_withdrawn`: Decimal(12,2) (tổng đã rút)
  - `last_settlement_at`: Timestamp, nullable
  - `created_at`, `updated_at`: Timestamp

### 17.7 Financial Models

#### 17.7.1 Settlement
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `seller_id`: UUID, FK to User
  - `period_start`: Date
  - `period_end`: Date
  - `total_orders`: Integer (số đơn hàng trong kỳ)
  - `total_amount`: Decimal(12,2) (tổng doanh thu)
  - `total_platform_fee`: Decimal(12,2)
  - `seller_amount`: Decimal(12,2) (tiền seller nhận)
  - `status`: Enum (PENDING, APPROVED, COMPLETED)
  - `approved_by`: UUID, FK to User, nullable
  - `approved_at`: Timestamp, nullable
  - `notes`: Text
  - `created_at`, `updated_at`: Timestamp

#### 17.7.2 Payout
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `seller_id`: UUID, FK to User
  - `amount`: Decimal(12,2)
  - `payment_method`: Enum (BANK_TRANSFER)
  - `bank_name`: String
  - `bank_account_number`: String
  - `bank_account_name`: String
  - `status`: Enum (PENDING, PROCESSING, SUCCESS, FAILED)
  - `transaction_reference`: String (mã GD ngân hàng)
  - `processed_by`: UUID, FK to User, nullable
  - `processed_at`: Timestamp, nullable
  - `failure_reason`: Text, nullable
  - `created_at`, `updated_at`: Timestamp

### 17.8 Shipping Models

#### 17.8.1 Shipment
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `order_id`: Integer, FK to Order, unique
  - `provider`: Enum (GHN, GHTK, VNPOST, MANUAL)
  - `tracking_code`: String, unique
  - `status`: Enum (PENDING, CREATED, PICKED_UP, IN_TRANSIT, DELIVERED, RETURNED, CANCELLED)
  - `shipping_fee`: Decimal(10,2)
  - `estimated_delivery_date`: Date, nullable
  - `actual_delivery_date`: Date, nullable
  - `notes`: Text
  - `created_at`, `updated_at`: Timestamp

### 17.9 Complaint & Return Models

#### 17.9.1 ReturnRequest
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `order_id`: Integer, FK to Order
  - `customer_id`: UUID, FK to User
  - `return_type`: Enum (FULL_RETURN, EXCHANGE)
  - `reason`: Text
  - `evidence_images`: Text (JSON array)
  - `status`: Enum (PENDING, APPROVED, REJECTED, RECEIVED, REFUNDED, EXCHANGED)
  - `admin_notes`: Text
  - `processed_by`: UUID, FK to User, nullable
  - `created_at`, `updated_at`: Timestamp

#### 17.9.2 Complaint
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `customer_id`: UUID, FK to User
  - `order_id`: Integer, FK to Order, nullable
  - `complaint_type`: Enum (PRODUCT, PAYMENT, SERVICE)
  - `title`: String
  - `description`: Text
  - `status`: Enum (PENDING, IN_PROGRESS, RESOLVED, CLOSED)
  - `handler_id`: UUID, FK to User, nullable
  - `resolution_notes`: Text
  - `resolved_at`: Timestamp, nullable
  - `created_at`, `updated_at`: Timestamp

#### 17.9.3 Review
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `product_id`: Integer, FK to Product
  - `user_id`: UUID, FK to User
  - `order_id`: Integer, FK to Order, nullable
  - `rating`: Integer (1-5)
  - `comment`: Text
  - `created_at`, `updated_at`: Timestamp
  - Unique constraint (product_id, user_id)

### 17.10 Other Models

#### 17.10.1 Cart & CartItem
- **Cart**:
  - `id`: Integer, primary key
  - `user_id`: UUID, FK to User, unique
  - `created_at`, `updated_at`: Timestamp
- **CartItem**:
  - `id`: Integer, primary key
  - `cart_id`: Integer, FK to Cart
  - `product_id`: Integer, FK to Product
  - `quantity`: Integer
  - `unit_price`: Decimal(10,2)
  - `created_at`, `updated_at`: Timestamp

#### 17.10.2 Content
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `creator_id`: UUID, FK to User
  - `title`: String
  - `body`: Text
  - `content_type`: String
  - `images`: Text (JSON array)
  - `videos`: Text (JSON array)
  - `status`: Enum (PENDING, APPROVED, REJECTED)
  - `approved_by`: UUID, FK to User, nullable
  - `approved_at`: Timestamp, nullable
  - `created_at`, `updated_at`: Timestamp

#### 17.10.3 PartnerContract
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `partner_id`: UUID, FK to User
  - `contract_type`: Enum (ADVERTISING, PARTNERSHIP)
  - `start_date`: Date
  - `end_date`: Date
  - `terms`: Text
  - `value`: Decimal(12,2), nullable
  - `status`: Enum (DRAFT, ACTIVE, EXPIRED, CANCELLED)
  - `created_by`: UUID, FK to User
  - `created_at`, `updated_at`: Timestamp

#### 17.10.4 Organization
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `name`: String, unique
  - `type`: Enum (COOPERATIVE, COMPANY, ASSOCIATION)
  - `tax_code`: String
  - `address`: Text
  - `contact_info`: JSON
  - `created_at`, `updated_at`: Timestamp

#### 17.10.5 UserOrganization (Many-to-Many)
- **Các trường dữ liệu**:
  - `user_id`: UUID, FK to User
  - `organization_id`: Integer, FK to Organization
  - `role_in_org`: String
  - `joined_at`: Timestamp
  - Composite primary key (user_id, organization_id)

#### 17.10.6 Media
- **Các trường dữ liệu**:
  - `id`: Integer, primary key
  - `uploader_id`: UUID, FK to User
  - `file_name`: String
  - `file_url`: String (public URL)
  - `file_type`: String (image/jpeg, video/mp4)
  - `file_size`: Integer (bytes)
  - `created_at`: Timestamp

---

## 18. QUY TRÌNH NGHIỆP VỤ CHI TIẾT

### 18.1 Quy trình hoàn chỉnh từ đăng ký đến bán hàng

#### 18.1.1 Flow người bán mới
```
1. Đăng ký tài khoản (user_type=PRODUCER)
   ↓
2. Tạo SellerProfile với thông tin kinh doanh
   ↓
3. Upload tài liệu xác thực (CCCD, giấy phép KD)
   ↓
4. Cung cấp thông tin tài khoản ngân hàng
   ↓
5. Admin xem xét và xác thực (VERIFIED/REJECTED)
   ↓
6. Nếu VERIFIED:
   - Tạo SellerWallet tự động
   - Người bán có thể đăng sản phẩm
   ↓
7. Tạo sản phẩm đầu tiên (status=PENDING)
   ↓
8. Admin duyệt sản phẩm (APPROVED/REJECTED)
   ↓
9. Sản phẩm APPROVED hiển thị trên marketplace
```

#### 18.1.2 Flow khách hàng mua hàng
```
1. Khách hàng đăng ký/đăng nhập (user_type=CONSUMER)
   ↓
2. Duyệt sản phẩm trên marketplace
   ↓
3. Xem chi tiết sản phẩm (giá, mô tả, nguồn gốc, chứng nhận)
   ↓
4. Thêm sản phẩm vào giỏ hàng
   ↓
5. Checkout:
   - Nhập địa chỉ giao hàng
   - Hệ thống tính phí ship (GHN API)
   - Chọn phương thức thanh toán
   ↓
6. Tạo Order (status=PENDING)
   ↓
7a. Nếu chọn VNPay:
    - Redirect đến VNPay
    - Thanh toán
    - VNPay callback → Order status=CONFIRMED
   ↓
7b. Nếu chọn COD:
    - Order status=CONFIRMED trực tiếp
   ↓
8. Người bán xác nhận và chuẩn bị hàng (status=PROCESSING)
   ↓
9. Tạo vận đơn GHN (status=SHIPPING)
   ↓
10. GHN giao hàng (Shipment status updates)
    ↓
11. Khách hàng nhận hàng (Order status=DELIVERED)
    ↓
12. Khách hàng đánh giá sản phẩm (Review)
```

#### 18.1.3 Flow đối soát và chi trả
```
1. Đơn hàng DELIVERED → Tiền vào Seller Wallet pending_balance
   ↓
2. Cuối chu kỳ (weekly/monthly):
   - Admin tạo Settlement cho từng seller
   - Tổng hợp tất cả đơn DELIVERED trong kỳ
   ↓
3. Admin xem xét và phê duyệt Settlement
   ↓
4. Settlement APPROVED:
   - Tiền chuyển từ pending_balance → available_balance
   ↓
5. Người bán yêu cầu rút tiền (Payout):
   - Tạo Payout record
   - Nhập số tiền (≤ available_balance)
   ↓
6. Admin xử lý Payout:
   - Chuyển khoản qua bank
   - Cập nhật status → SUCCESS
   - Trừ available_balance
   - Cộng total_withdrawn
   ↓
7. Người bán nhận tiền vào tài khoản ngân hàng
```

### 18.2 Quy trình xử lý khiếu nại và hoàn trả

#### 18.2.1 Flow hoàn trả sản phẩm
```
1. Khách hàng tạo ReturnRequest:
   - Chọn đơn hàng cần trả
   - Chọn loại: FULL_RETURN hoặc EXCHANGE
   - Mô tả lý do
   - Upload ảnh chứng minh
   - Status = PENDING
   ↓
2. Admin xem xét:
   - Kiểm tra lý do và ảnh chứng minh
   - Kiểm tra chính sách hoàn trả
   ↓
3a. Nếu APPROVED:
    - Thông báo cho khách hàng gửi hàng về
    - Cung cấp địa chỉ trả hàng
    ↓
    - Người bán nhận hàng → Status=RECEIVED
    ↓
    - Admin xác nhận sản phẩm OK
    ↓
    - Nếu FULL_RETURN:
      * Hoàn tiền cho khách hàng
      * Status=REFUNDED
      * Payment status=REFUNDED
    - Nếu EXCHANGE:
      * Gửi sản phẩm mới cho khách hàng
      * Status=EXCHANGED
   ↓
3b. Nếu REJECTED:
    - Thông báo lý do từ chối
    - Không xử lý hoàn trả
```

#### 18.2.2 Flow xử lý khiếu nại
```
1. Khách hàng tạo Complaint:
   - Chọn loại: PRODUCT/PAYMENT/SERVICE
   - Nhập tiêu đề và mô tả
   - Liên kết Order (nếu có)
   - Status = PENDING
   ↓
2. Admin assign handler:
   - Chọn người xử lý (handler_id)
   - Status = IN_PROGRESS
   ↓
3. Handler điều tra và xử lý:
   - Liên hệ khách hàng và người bán
   - Thu thập thông tin
   - Đưa ra giải pháp
   ↓
4. Giải quyết xong:
   - Ghi resolution_notes
   - Status = RESOLVED
   - Thông báo cho khách hàng
   ↓
5. Khách hàng xác nhận hài lòng:
   - Status = CLOSED
   ↓
6. Hoặc khách hàng không hài lòng:
   - Reopen khiếu nại
   - Status quay về IN_PROGRESS
```

---

## 19. BẢO MẬT VÀ KIỂM SOÁT

### 19.1 Bảo mật mật khẩu

#### 19.1.1 Password hashing
- **Acceptance Criteria**:
  - Sử dụng Argon2 hoặc Bcrypt để hash mật khẩu
  - Không lưu trữ mật khẩu plaintext
  - Argon2 parameters:
    - time_cost: 2
    - memory_cost: 65536
    - parallelism: 1
  - Bcrypt rounds: 12
  - Tự động detect và verify cả Argon2 và Bcrypt hash

#### 19.1.2 Password requirements
- **Acceptance Criteria**:
  - Mật khẩu tối thiểu 8 ký tự
  - Khuyến khích sử dụng ký tự đặc biệt, số, chữ hoa
  - Không cho phép mật khẩu phổ biến (ví dụ: password123)
  - Người dùng có thể đổi mật khẩu
  - Yêu cầu xác thực mật khẩu cũ khi đổi

### 19.2 Bảo vệ dữ liệu nhạy cảm

#### 19.2.1 Sensitive data handling
- **Acceptance Criteria**:
  - Dữ liệu nhạy cảm không bao giờ log
  - Thông tin tài khoản ngân hàng:
    - Chỉ hiển thị cho chủ tài khoản và admin có quyền
    - Mask số tài khoản khi hiển thị (ví dụ: ****1234)
  - Secret keys trong environment variables
  - Không commit secrets vào git

#### 19.2.2 CORS và API security
- **Acceptance Criteria**:
  - CORS configuration cho phép origins hợp lệ
  - Rate limiting để tránh abuse
  - Input validation cho tất cả endpoints
  - SQL injection prevention (qua SQLAlchemy ORM)
  - XSS prevention (sanitize user input)

### 19.3 Audit logging

#### 19.3.1 Audit trail
- **Acceptance Criteria**:
  - Tất cả thay đổi quan trọng được log:
    - Thay đổi trạng thái đơn hàng
    - Phê duyệt sản phẩm
    - Settlement và payout
    - Thay đổi quyền người dùng
  - Log bao gồm:
    - Hành động (action)
    - User thực hiện (user_id)
    - Thời gian (timestamp)
    - Dữ liệu cũ và mới
  - Log không thể xóa hoặc chỉnh sửa

---

## 20. XỬ LÝ LỖI VÀ THÔNG BÁO

### 20.1 Error handling

#### 20.1.1 HTTP error responses
- **Acceptance Criteria**:
  - Hệ thống trả về mã lỗi HTTP chuẩn:
    - 400: Bad Request (input không hợp lệ)
    - 401: Unauthorized (chưa đăng nhập)
    - 403: Forbidden (không có quyền)
    - 404: Not Found (resource không tồn tại)
    - 409: Conflict (trùng lặp dữ liệu)
    - 500: Internal Server Error
  - Error response format:
    ```json
    {
      "detail": "Mô tả lỗi chi tiết",
      "error_code": "ERROR_CODE" (nếu có)
    }
    ```

#### 20.1.2 Validation errors
- **Acceptance Criteria**:
  - Pydantic validation cho tất cả input
  - Trả về lỗi cụ thể cho từng trường không hợp lệ
  - Message lỗi dễ hiểu, bằng tiếng Việt
  - Không expose thông tin nội bộ trong error message

### 20.2 Notification system

#### 20.2.1 Thông báo quan trọng
- **Acceptance Criteria**:
  - Hệ thống gửi thông báo cho các sự kiện:
    - Đơn hàng mới (cho người bán)
    - Thay đổi trạng thái đơn hàng (cho khách hàng)
    - Sản phẩm được duyệt/từ chối (cho người bán)
    - Settlement được duyệt (cho người bán)
    - Payout thành công (cho người bán)
    - Khiếu nại được xử lý (cho khách hàng)
  - Thông báo qua:
    - In-app notification
    - Email (nếu cấu hình)
    - Push notification mobile (nếu có)

---

## 21. MIGRATION VÀ DATABASE MANAGEMENT

### 21.1 Alembic migrations

#### 21.1.1 Quản lý schema changes
- **Acceptance Criteria**:
  - Tất cả thay đổi database qua Alembic migrations
  - Migration files trong thư mục alembic/versions/
  - Mỗi migration có:
    - Version ID duy nhất
    - Mô tả rõ ràng
    - Upgrade function (áp dụng thay đổi)
    - Downgrade function (rollback)
  - Test migration trước khi deploy production

#### 21.1.2 Initial schema
- **Acceptance Criteria**:
  - Initial migration tạo tất cả bảng cần thiết
  - Foreign key constraints được định nghĩa đầy đủ
  - Indexes cho các trường thường query
  - Default values hợp lý
  - Không null constraints cho trường bắt buộc

### 21.2 Database indexing

#### 21.2.1 Performance indexes
- **Acceptance Criteria**:
  - Index trên các trường:
    - User.email (unique)
    - Product.seller_id, Product.status, Product.category_id
    - Order.customer_id, Order.seller_id, Order.status
    - Payment.order_id
    - Shipment.tracking_code
  - Composite indexes cho queries phức tạp
  - Regular review và optimize slow queries

---

## 22. DEPLOYMENT VÀ OPERATIONS

### 22.1 Môi trường triển khai

#### 22.1.1 Railway deployment
- **Acceptance Criteria**:
  - Application deploy trên Railway platform
  - Cấu hình:
    - Build command: Tạo dependencies
    - Start command: Gunicorn with Uvicorn workers
    - Environment variables config
  - Auto-deploy khi merge vào main branch
  - Health check endpoint để Railway monitor

#### 22.1.2 Environment separation
- **Acceptance Criteria**:
  - Các môi trường riêng biệt:
    - **Development**: Local development
    - **Staging**: Test trước khi production
    - **Production**: Môi trường live
  - Mỗi môi trường có:
    - Database riêng
    - Environment variables riêng
    - Payment gateway config riêng (sandbox vs production)

### 22.2 Monitoring và logging

#### 22.2.1 Application logging
- **Acceptance Criteria**:
  - Log tất cả requests và responses
  - Log errors với stack trace
  - Log các sự kiện nghiệp vụ quan trọng
  - Log level: DEBUG, INFO, WARNING, ERROR
  - Log rotation để tránh đầy disk

#### 22.2.2 Health checks
- **Acceptance Criteria**:
  - Health check endpoint: /health hoặc /
  - Kiểm tra:
    - Database connection
    - External services (VNPay, GHN)
  - Trả về status 200 nếu healthy
  - Trả về 503 nếu có vấn đề

---

## 23. TÍNH NĂNG BỔ SUNG

### 23.1 Search và filtering

#### 23.1.1 Tìm kiếm sản phẩm
- **Acceptance Criteria**:
  - Khách hàng tìm kiếm sản phẩm theo:
    - Từ khóa (tên sản phẩm, mô tả)
    - Danh mục
    - Khu vực
    - Khoảng giá (price_min, price_max)
    - Nhãn sản phẩm (label)
  - Hỗ trợ full-text search
  - Kết quả được phân trang
  - Sắp xếp theo: giá, độ phổ biến, mới nhất

#### 23.1.2 Filter và sort
- **Acceptance Criteria**:
  - Hỗ trợ filter combo:
    - Nhiều danh mục cùng lúc
    - Nhiều nhãn cùng lúc
    - Khu vực + danh mục
  - Sort options:
    - Giá tăng dần/giảm dần
    - Mới nhất/cũ nhất
    - Bán chạy nhất
    - Đánh giá cao nhất
  - Kết quả real-time

### 23.2 Pagination

#### 23.2.1 API pagination
- **Acceptance Criteria**:
  - Tất cả list APIs hỗ trợ pagination
  - Parameters:
    - `page`: Số trang (bắt đầu từ 1)
    - `page_size`: Số items mỗi trang (mặc định 20, max 100)
  - Response bao gồm:
    - `items`: Danh sách items
    - `total`: Tổng số items
    - `page`: Trang hiện tại
    - `page_size`: Số items mỗi trang
    - `total_pages`: Tổng số trang
  - Consistent pagination cho tất cả endpoints

---

## 24. KẾT LUẬN

### 24.1 Tính năng chính của hệ thống

Hệ thống marketplace e-commerce này cung cấp một nền tảng toàn diện cho việc kinh doanh sản phẩm đặc sản và thủ công mỹ nghệ với các tính năng nổi bật:

1. **Xác thực người bán nghiêm ngặt**: Đảm bảo chất lượng người bán và bảo vệ quyền lợi khách hàng
2. **Truy xuất nguồn gốc minh bạch**: Xây dựng lòng tin qua thông tin nguồn gốc và chứng nhận
3. **Quy trình duyệt sản phẩm chặt chẽ**: Đảm bảo chất lượng sản phẩm trên nền tảng
4. **Tích hợp thanh toán và vận chuyển**: Trải nghiệm mua hàng liền mạch
5. **Hệ thống đối soát và chi trả tự động**: Quản lý tài chính minh bạch
6. **Xử lý khiếu nại và hoàn trả hiệu quả**: Bảo vệ quyền lợi người tiêu dùng
7. **RBAC phân quyền linh hoạt**: Quản trị đa cấp độ an toàn
8. **Dashboard và báo cáo chi tiết**: Hỗ trợ ra quyết định kinh doanh

### 24.2 Yêu cầu kỹ thuật

- **Backend**: Python 3.11+ với FastAPI framework
- **Database**: PostgreSQL (Supabase)
- **Storage**: S3-compatible storage (Supabase Storage)
- **External Services**: VNPay (payment), GHN (shipping)
- **Deployment**: Railway cloud platform
- **Security**: JWT authentication, RBAC authorization, encrypted sensitive data

### 24.3 Quy mô hệ thống

Hệ thống được thiết kế để xử lý:
- Hàng nghìn người bán đồng thời
- Hàng chục nghìn sản phẩm
- Hàng trăm nghìn đơn hàng mỗi tháng
- Tích hợp với các dịch vụ bên ngoài (payment gateway, logistics)
- Hỗ trợ cả web portal và mobile application

---

**Tài liệu này được tạo tự động từ source code của dự án để phục vụ mục đích Product Backlog và Acceptance Criteria. Mọi cập nhật về tính năng cần được phản ánh vào tài liệu này.**
