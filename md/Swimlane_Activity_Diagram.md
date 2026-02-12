### 1. Quy trình Vận hành Tổng thể - Swimlane Flowchart
Quy trình vận hành từ lúc sản phẩm được tạo ra đến khi đến tay người tiêu dùng và nông dân nhận được thanh toán.

```mermaid
flowchart TB
    subgraph PRODUCER["NGƯỜI SẢN XUẤT"]
        direction LR
        P1["1. Đăng ký tài khoản"]
        P2["3. Đăng sản phẩm mới"]
        P3["12. Xác nhận đơn hàng"]
        P4["13. Đóng gói và giao ship"]
    end

    subgraph SYSTEM["HỆ THỐNG"]
        direction LR
        S1["2. Kích hoạt tài khoản"]
        S2["4. Lưu SP - Status: PENDING"]
        S3["7. Hiển thị SP đã duyệt"]
        S4["9. Tạo giỏ hàng"]
        S5["11. Tạo đơn hàng"]
        S6["14. Cập nhật trạng thái giao hàng"]
        S7["17. Tính toán đối soát"]
    end

    subgraph ADMIN["QUẢN TRỊ VIÊN"]
        direction LR
        A1{"5. Kiểm duyệt SP"}
        A2["16. Chạy báo cáo đối soát"]
        A3["18. Chuyển tiền cho Nông dân"]
    end

    subgraph CONSUMER["NGƯỜI TIÊU DÙNG"]
        direction LR
        C1["6. Tìm kiếm sản phẩm"]
        C2["8. Thêm vào giỏ hàng"]
        C3["10. Thanh toán"]
        C4["15. Nhận hàng và đánh giá"]
    end

    subgraph PAYMENT["CỔNG THANH TOÁN"]
        direction LR
        PG1["10a. Xử lý thanh toán"]
        PG2["10b. Trả kết quả"]
    end

    %% Flow connections
    P1 --> S1
    S1 --> P2
    P2 --> S2
    S2 --> A1
    A1 -->|Duyệt| S3
    A1 -->|Từ chối| P2
    S3 --> C1
    C1 --> C2
    C2 --> S4
    S4 --> C3
    C3 --> PG1
    PG1 --> PG2
    PG2 --> S5
    S5 --> P3
    P3 --> P4
    P4 --> S6
    S6 --> C4
    C4 --> A2
    A2 --> S7
    S7 --> A3
    A3 --> P1

    %% Styling
    style PRODUCER fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style CONSUMER fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style ADMIN fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    style PAYMENT fill:#fce4ec,stroke:#e91e63,stroke-width:2px
```

---

### 2. Authentication & Authorization (Auth)
Quy trình xác thực người dùng, đăng ký, đăng nhập và cấp lại token.

```mermaid
flowchart TB
    subgraph CLIENT["NGƯỜI DÙNG (CLIENT)"]
        direction TB
        C1("1. Yêu cầu Đăng ký")
        C2("1. Yêu cầu Đăng nhập")
        C3("Lưu Token (Local Storage)")
        C4("Gửi Request + Token")
        C5("Yêu cầu Refresh Token")
        C6("Logout")
    end

    subgraph SYSTEM["HỆ THỐNG (API)"]
        direction TB
        S1{"Kiểm tra Email tồn tại?"}
        S2["Tạo User (Status: Active/Pending)"]
        S3{"Kiểm tra Email & Password"}
        S4{"Tài khoản Activated?"}
        S5["Tạo Access Token & Expire Time"]
        S6{"Xác thực Token (Middleware)"}
        S7["Xử lý Business Logic"]
        S8["Tạo Token mới"]
        S9["Xác nhận Logout (Client tự xóa)"]
    end

    subgraph DB["CƠ SỞ DỮ LIỆU"]
        direction TB
        D1[("User Table")]
    end

    %% Register Flow
    C1 --> S1
    S1 -- "Đã tồn tại" --> C1
    S1 -- "Chưa tồn tại" --> S2
    S2 --> D1
    
    %% Login Flow
    C2 --> S3
    S3 -- "Sai" --> C2
    S3 -- "Đúng" --> S4
    S4 -- "Chưa kích hoạt" --> C2
    S4 -- "OK" --> S5
    S5 --> C3
    
    %% Authenticated Request
    C4 --> S6
    S6 -- "Token Hợp lệ" --> S7
    S7 --> D1
    S6 -- "Token Hết hạn" --> C5
    
    %% Refresh Token
    C5 --> S8
    S8 --> C3
    
    %% Logout
    C6 --> S9
    
    %% Styling
    style CLIENT fill:#e3f2fd,stroke:#2196f3
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0
    style DB fill:#fff3e0,stroke:#ff9800
```

### 3. Product Management (Quản lý Sản phẩm)
Quy trình Producer tạo sản phẩm, Admin duyệt và xuất bản.

```mermaid
flowchart TB
    subgraph PRODUCER["NHÀ SẢN XUẤT"]
        P1("1. Tạo sản phẩm mới")
        P2("Cập nhật thông tin")
        P3("Xóa sản phẩm")
    end

    subgraph SYSTEM["HỆ THỐNG"]
        S1["Validate Dữ liệu"]
        S2["Lưu SP - Status: PENDING"]
        S3["Cập nhật SP"]
        S4["Soft Delete SP"]
        S5["Update Status & Log Approval"]
    end

    subgraph ADMIN["QUẢN TRỊ VIÊN"]
        A1("2. Xem danh sách PENDING")
        A2{"Duyệt sản phẩm?"}
        A3("Gán nhãn (OCOP, VietGAP...)")
    end

    subgraph DB["DATABASE"]
        D1[("Product Table")]
        D2[("Product Approval Log")]
    end

    P1 --> S1
    S1 --> S2
    S2 --> D1
    
    S2 -.-> A1
    A1 --> A2
    
    A2 -- "APPROVED" --> S5
    A2 -- "REJECTED" --> S5
    
    S5 --> D1
    S5 --> D2
    
    P2 --> S3
    S3 --> D1
    
    P3 --> S4
    S4 --> D1
    
    A3 --> S3

    style PRODUCER fill:#e8f5e9,stroke:#4caf50
    style ADMIN fill:#fff3e0,stroke:#ff9800
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0
    style DB fill:#eceff1,stroke:#607d8b
```

### 4. Order Processing (Xử lý Đơn hàng)
Quy trình từ lúc đặt hàng đến khi giao hàng thành công.

```mermaid
flowchart TB
    subgraph CUSTOMER["KHÁCH HÀNG"]
        C1("1. Đặt hàng (Checkout)")
        C2("Thanh toán (COD/Online)")
        C3("Nhận hàng")
        C4("Hủy đơn")
    end

    subgraph SYSTEM["HỆ THỐNG"]
        S1["Tạo Đơn hàng (PENDING)"]
        S2["Xác nhận Thanh toán"]
        S3["Cập nhật Status: CONFIRMED"]
        S4["Cập nhật Status: SHIPPING"]
        S5["Cập nhật Status: DELIVERED"]
        S6["Cập nhật Status: CANCELLED"]
        S7["Tính toán doanh thu/phí"]
    end

    subgraph SELLER["NGƯỜI BÁN / ADMIN"]
        A1("2. Xác nhận đơn hàng")
        A2("3. Giao cho vận chuyển")
        A3("4. Xác nhận giao thành công")
    end

    C1 --> S1
    S1 --> A1
    
    A1 --> S3
    S3 --> A2
    A2 --> S4
    S4 --> C3
    C3 --> A3
    A3 --> S5
    S5 --> S7
    
    C4 --> S6
    S1 -- "Khách hủy" --> S6
    A1 -- "Hết hàng/Hủy" --> S6

    style CUSTOMER fill:#e3f2fd,stroke:#2196f3
    style SELLER fill:#fff3e0,stroke:#ff9800
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0
```

### 5. User & Access Control (Quản lý User & Phân quyền)
Quản lý người dùng, gán vai trò (Role) và quyền hạn (Permission).

```mermaid
flowchart TB
    subgraph ADMIN["QUẢN TRỊ VIÊN"]
        A1("Tạo User mới")
        A2("Cập nhật User")
        A3("Kích hoạt/Khóa User")
        A4("Gán Roles cho User")
    end

    subgraph SYSTEM["HỆ THỐNG"]
        S1["Hash Password"]
        S2["Lưu User"]
        S3["Cập nhật trạng thái"]
        S4["Xóa Roles cũ -> Gán Roles mới"]
    end

    subgraph DB["DATABASE"]
        D1[("User Table")]
        D2[("UserRole Table")]
        D3[("Role Table")]
    end

    A1 --> S1 --> S2 --> D1
    A2 --> S2
    A3 --> S3 --> D1
    A4 --> S4 --> D2
    D2 -.-> D3

    style ADMIN fill:#fff3e0,stroke:#ff9800
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0
    style DB fill:#eceff1,stroke:#607d8b
```

### 6. Contract Management (Quản lý Hợp đồng)
Quản lý hợp đồng hợp tác giữa các bên.

```mermaid
flowchart TB
    subgraph ADMIN["QUẢN TRỊ VIÊN"]
        A1("Tạo Hợp đồng (DRAFT)")
        A2("Cập nhật Hợp đồng")
        A3("Ký kết / Chốt Hợp đồng")
        A4("Hủy Hợp đồng")
    end

    subgraph SYSTEM["HỆ THỐNG"]
        S1["Tạo Record PartnerContract"]
        S2["Validate Partner"]
        S3["Update Status"]
    end

    subgraph PARTNER["ĐỐI TÁC"]
        P1("Xem Hợp đồng")
    end

    A1 --> S2 --> S1
    A2 --> S1
    A3 --> S3
    A4 --> S3
    
    S1 -.-> P1

    style ADMIN fill:#fff3e0,stroke:#ff9800
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0
    style PARTNER fill:#e8f5e9,stroke:#4caf50
```

### 7. Complaint Handling (Xử lý Khiếu nại)
Quy trình xử lý phản hồi và khiếu nại từ khách hàng.

```mermaid
flowchart TB
    subgraph CUSTOMER["KHÁCH HÀNG"]
        C1("Gửi Khiếu nại")
        C2("Xem trạng thái/Kết quả")
    end

    subgraph SYSTEM["HỆ THỐNG"]
        S1["Lưu Complaint (Status: PENDING)"]
        S2["Cập nhật Status & Resolution"]
    end

    subgraph ADMIN["CS SUPPORT"]
        A1("Tiếp nhận Khiếu nại")
        A2("Xử lý / Đưa ra giải pháp")
        A3("Đóng khiếu nại (RESOLVED)")
    end

    C1 --> S1
    S1 --> A1
    A1 --> A2
    A2 --> A3
    A3 --> S2
    S2 --> C2

    style CUSTOMER fill:#e3f2fd,stroke:#2196f3
    style ADMIN fill:#fff3e0,stroke:#ff9800
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0
```

### 8. Organization Management (Quản lý Tổ chức)
Quản lý các Hợp tác xã, Làng nghề và thành viên.

```mermaid
flowchart TB
    subgraph ADMIN["QUẢN TRỊ VIÊN"]
        A1("Tạo Tổ chức (HTX/Làng nghề)")
        A2("Thêm Thành viên vào Tổ chức")
        A3("Xóa Thành viên")
        A4("Xóa Tổ chức")
    end

    subgraph SYSTEM["HỆ THỐNG"]
        S1["Kiểm tra tên tồn tại"]
        S2["Tạo Organization"]
        S3["Kiểm tra User tồn tại"]
        S4["Tạo UserOrganization"]
        S5["Kiểm tra số lượng thành viên > 0?"]
    end

    subgraph DB["DATABASE"]
        D1[("Organization Table")]
        D2[("UserOrganization Table")]
    end

    A1 --> S1 --> S2 --> D1
    A2 --> S3 --> S4 --> D2
    A3 --> D2
    A4 --> S5
    S5 -- "Còn thành viên" --> A4
    S5 -- "Trống" --> D1

    style ADMIN fill:#fff3e0,stroke:#ff9800
    style SYSTEM fill:#f3e5f5,stroke:#9c27b0
    style DB fill:#eceff1,stroke:#607d8b
```
