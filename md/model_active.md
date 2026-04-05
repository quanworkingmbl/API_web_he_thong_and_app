# 📘 Tài liệu Models – Dự án CMS Thương Mại Điện Tử

> **Mục đích:** Giải thích từng model (bảng dữ liệu) trong thư mục `app/models/`,
> ý nghĩa từng trường và cách các model liên kết với nhau trong hệ thống.

---

## 🗺️ Sơ đồ tổng quan

```
User ─┬─► UserRole ──► Role
      ├─► UserOrganization ──► Organization
      ├─► SellerProfile
      └─► Store (multi-store)

Product ─┬─► ProductVariant (biến thể: màu, size, khối lượng)
         ├─► ProductOption / ProductOptionValue
         ├─► ProductApproval (duyệt sản phẩm)
         ├─► ProductCertificate (VietGAP, OCOP...)
         ├─► ProductOrigin (truy xuất nguồn gốc)
         ├─► ProductPriceLog (audit giá)
         ├─► ProductMedia (ảnh/video)
         └─► InventoryMovement / StockReservation (kho)

Order ─┬─► OrderItem ──► ProductVariant, Store, OrderPackage
       ├─► OrderPackage (sub-order theo seller)
       ├─► OrderStatusLog (audit trạng thái)
       ├─► Shipment (vận chuyển GHN/GHTK)
       └─► ReturnRequest (đổi/trả hàng)

Payment ─┬─► PaymentTransaction (từng giao dịch)
         └─► PaymentAuditLog (audit refund, config...)

Complaint ─┬─► ComplaintComment (thread trao đổi)
           └─► ComplaintStatusLog (audit trạng thái)

Settlement ─┬─► SellerWallet (ví người bán)
            ├─► Payout (chi trả)
            └─► SettlementItem

Promotion ──► PromotionUsage (lịch sử dùng mã)
Cart ──► CartItem
```

---

## 1. 👤 User – Người dùng

**File:** `app/models/user.py` | **Bảng:** `users`

Model trung tâm của toàn hệ thống. Dùng cho cả buyer (khách mua), seller (người bán) và admin.

| Trường | Kiểu | Ý nghĩa |
|--------|------|---------|
| `id` | int | Khóa chính |
| `email` | string | Email đăng nhập (unique) |
| `password_hash` | string | Mật khẩu đã mã hóa bcrypt (không lưu thật) |
| `name` | string | Tên hiển thị |
| `gender` | string | Giới tính (male/female/other) |
| `activated` | int | `1` = tài khoản đã kích hoạt, `0` = chưa kích hoạt |
| `type` | string | Vai trò nhanh: `admin`, `seller`, `consumer`, `content_manager` |
| `status` | enum | `ACTIVE` / `SUSPENDED` / `BANNED` |
| `status_reason` | text | Lý do khóa tài khoản |
| `status_expire_at` | datetime | Thời hạn khóa (nếu tạm khóa có thời hạn) |
| `created_at / updated_at` | datetime | Thời gian tạo / cập nhật |
| `deleted_at` | datetime | Soft-delete (xóa mềm) |

### UserRole – Gán quyền cho user

**Bảng:** `user_roles` — Bảng trung gian nối `User` ↔ `Role` (nhiều-nhiều).

### UserOrganization – Thành viên tổ chức

**Bảng:** `user_organizations` — Nối `User` ↔ `Organization` (HTX, làng nghề...).

---

## 2. 🏪 SellerProfile – Hồ sơ người bán

**File:** `app/models/seller_profile.py` | **Bảng:** `seller_profiles`

Lưu thông tin kinh doanh, giấy tờ pháp lý của seller. Mỗi user seller có **1 profile**.

| Trường | Ý nghĩa |
|--------|---------|
| `user_id` | FK → User (1-1) |
| `business_name` | Tên cơ sở / shop (VD: "Nông sản Trần Thị Bình") |
| `business_type` | Loại hình: `INDIVIDUAL` / `HOUSEHOLD` / `COOPERATIVE` / `COMPANY` |
| `slug` | URL cửa hàng (VD: `nongsantranbinh`) |
| `shop_phone / shop_email` | Liên hệ công khai của shop |
| `id_card_number` | Số CCCD/CMND để xác minh danh tính |
| `id_card_front_url / back_url` | Ảnh CCCD mặt trước/sau |
| `business_license_url` | File giấy phép kinh doanh |
| `tax_id` | Mã số thuế (MST) |
| `bank_name / bank_account_number / bank_account_name` | Tài khoản ngân hàng nhận tiền |
| `verification_status` | `PENDING` / `VERIFIED` / `REJECTED` – trạng thái xét duyệt hồ sơ |
| `verified_by / verified_at` | Admin nào đã duyệt, khi nào |
| `rejection_reason` | Lý do từ chối (nếu bị reject) |

---

## 3. 🏬 Store – Cửa hàng / Chi nhánh

**File:** `app/models/store.py` | **Bảng:** `stores`

Một seller có thể mở **nhiều cửa hàng** (VD: shop Hà Nội + shop TP.HCM).

| Trường | Ý nghĩa |
|--------|---------|
| `seller_id` | FK → User (chủ cửa hàng) |
| `store_name / slug` | Tên và URL cửa hàng |
| `logo_url / description` | Logo và mô tả cửa hàng |
| `pickup_address / province / district / ward` | Địa chỉ lấy hàng (cho vận chuyển) |
| `contact_phone / contact_email` | Liên hệ cửa hàng |
| `shipping_config` | JSON cấu hình vận chuyển (ngưỡng freeship, bảng giá...) |
| `is_active` | Cửa hàng đang hoạt động hay đã đóng |

---

## 4. 📦 Product – Sản phẩm

**File:** `app/models/product.py` | **Bảng:** `products`

Sản phẩm được đăng bán. Phải qua **xét duyệt** trước khi hiển thị.

| Trường | Ý nghĩa |
|--------|---------|
| `name` | Tên sản phẩm |
| `description` | Mô tả chi tiết |
| `price` | Giá bán gốc (VND) |
| `producer_id` | FK → User (seller đăng sản phẩm) |
| `category_id` | FK → Category (danh mục: Rau củ, Gốm sứ...) |
| `store_id` | FK → Store (cửa hàng thuộc seller nào) |
| `sku` | Mã SKU – định danh duy nhất cho sản phẩm gốc |
| `slug` | URL thân thiện SEO (VD: `cam-sanh-ha-giang`) |
| `weight` | Trọng lượng (gram) — dùng tính phí ship |
| `dimensions` | JSON `{length, width, height}` (cm) — tính phí ship |
| `unit` | Đơn vị: `kg`, `piece`, `box`... |
| `vat_rate` | Thuế VAT (%) |
| `status` | `PENDING` / `APPROVED` / `REJECTED` — trạng thái phê duyệt |
| `label` | Nhãn đặc biệt: `OCOP` / `CLEAN_AGRICULTURE` / `TRADITIONAL_CRAFT` |
| `is_active` | `True` = đang bán; `False` = ngừng bán (soft-delete) |
| `published_at / unpublished_at` | Lên lịch hiển thị / ẩn tự động |
| `stock_quantity` | Tồn kho tổng (hoặc tồn kho của sản phẩm gốc nếu không dùng variants) |
| `images` | JSON array URL ảnh (legacy, đang migrate sang `product_media`) |
| `seo_title / description / keywords` | Tối ưu SEO cho trang sản phẩm |

### ProductApproval – Bảng duyệt sản phẩm

**Bảng:** `product_approvals` — Admin hoặc content manager duyệt sản phẩm.

| Trường | Ý nghĩa |
|--------|---------|
| `product_id / approver_id` | Sản phẩm nào, ai duyệt |
| `status` | Kết quả: APPROVED / REJECTED / PENDING |
| `notes` | Nhận xét của người duyệt |
| `checked_description / checked_price / checked_images` | Đã kiểm tra mô tả / giá / ảnh chưa |

### ProductPriceLog – Audit thay đổi giá

**Bảng:** `product_price_logs` — Ghi lại mỗi lần giá sản phẩm thay đổi để phát hiện gian lận.

| Trường | Ý nghĩa |
|--------|---------|
| `old_price / new_price` | Giá trước và sau khi đổi |
| `changed_by` | FK → User (ai đổi) |
| `reason` | Lý do thay đổi giá |

---

## 5. 🎨 ProductVariant – Biến thể sản phẩm

**File:** `app/models/product_variant.py` | **Bảng:** `product_variants`

Mỗi sản phẩm có thể có nhiều **biến thể** (size, màu, khối lượng...).
Mỗi biến thể có **giá và tồn kho riêng**.

| Trường | Ý nghĩa |
|--------|---------|
| `product_id` | FK → Product (thuộc sản phẩm nào) |
| `sku` | Mã SKU riêng của biến thể (unique toàn hệ thống) |
| `variant_name` | Tên biến thể (VD: "Đỏ - XL", "500g", "Hộp 12 viên") |
| `price` | Giá riêng của biến thể này |
| `stock_quantity` | Tồn kho riêng của biến thể |
| `weight / dimensions` | Thông tin vật lý riêng (nếu khác sản phẩm gốc) |
| `image_url` | Ảnh riêng của biến thể (VD: ảnh màu đỏ) |
| `is_active` | Biến thể này còn bán hay không |

### ProductOption / ProductOptionValue – Tùy chọn

- **ProductOption**: Tên nhóm tùy chọn (VD: "Màu sắc", "Kích thước")
- **ProductOptionValue**: Giá trị cụ thể (VD: "Đỏ", "XL") gắn với variant

### InventoryMovement – Lịch sử xuất nhập kho

**Bảng:** `inventory_movements`

| Trường | Ý nghĩa |
|--------|---------|
| `movement_type` | `IN` (nhập kho) / `OUT` (xuất kho) / `ADJUSTMENT` (điều chỉnh) |
| `quantity` | Số lượng (dương: nhập, âm: xuất) |
| `reference_type / reference_id` | Nguồn gốc: ORDER, PURCHASE, ADJUSTMENT + ID tương ứng |

### StockReservation – Tạm giữ hàng

**Bảng:** `stock_reservations` — Khi khách đặt hàng, tạm giữ tồn kho để tránh oversell.

| Trường | Ý nghĩa |
|--------|---------|
| `quantity` | Số lượng đang giữ |
| `status` | `ACTIVE` (đang giữ) / `RELEASED` (đã giải phóng) / `FULFILLED` (đã xuất) |
| `expires_at` | Hết giờ này tự giải phóng nếu đơn chưa thanh toán |

---

## 6. 🛒 Cart – Giỏ hàng

**File:** `app/models/cart.py` | **Bảng:** `carts` + `cart_items`

| Trường CartItem | Ý nghĩa |
|-----------------|---------|
| `cart_id` | FK → Cart (giỏ hàng của ai) |
| `product_id` | Sản phẩm thêm vào giỏ |
| `quantity` | Số lượng |
| `unit_price` | Giá tại thời điểm thêm vào giỏ (snapshot) |

---

## 7. 📋 Order – Đơn hàng

**File:** `app/models/order.py` | **Bảng:** `orders`

Đơn hàng được tạo khi khách **checkout** từ giỏ hàng.

| Trường | Ý nghĩa |
|--------|---------|
| `order_number` | Mã đơn hàng duy nhất (VD: `ORD-2026-001`) |
| `customer_id` | FK → User (người mua) |
| `customer_name / phone / email` | Snapshot thông tin khách tại thời điểm đặt |
| `shipping_address / province / district / ward` | Địa chỉ giao hàng đầy đủ |
| `seller_id` | FK → User (người bán — đơn thuộc 1 seller) |
| `subtotal` | Tổng tiền hàng (chưa tính phí ship, giảm giá) |
| `shipping_fee` | Phí vận chuyển |
| `discount_amount` | Số tiền được giảm (từ mã voucher...) |
| `total_amount` | Tổng cuối cùng khách phải trả |
| `platform_fee_percentage / amount` | Phí nền tảng thu từ seller (mặc định 5%) |
| `seller_amount` | Số tiền seller thực nhận sau trừ phí |
| `status` | Trạng thái đơn: `PENDING` → `CONFIRMED` → `PROCESSING` → `SHIPPING` → `DELIVERED` / `CANCELLED` |
| `payment_method` | Phương thức TT: `COD` / `VNPAY` / `MOMO` / `BANK_TRANSFER` / `ZALOPAY` |
| `payment_status` | `UNPAID` / `PAID` / `REFUNDED` |
| `currency` | Tiền tệ (mặc định `VND`) |
| `channel` | Kênh đặt hàng: `WEB` / `MOBILE_APP` / `THIRD_PARTY` |
| `coupon_code` | Mã giảm giá đã dùng |
| `customer_note / seller_note / admin_note` | Ghi chú của từng bên |
| `cancel_reason` | Lý do hủy đơn |
| `is_active` | `False` = đã xóa mềm (không hiển thị nhưng giữ lịch sử) |
| `confirmed_at / shipped_at / delivered_at / cancelled_at` | Timestamp từng mốc vòng đời |

### OrderItem – Chi tiết sản phẩm trong đơn

**Bảng:** `order_items`

| Trường | Ý nghĩa |
|--------|---------|
| `order_id` | FK → Order |
| `product_id` | FK → Product |
| `seller_id / store_id` | Seller và store của item này (multi-seller) |
| `variant_id` | FK → ProductVariant (nếu chọn biến thể) |
| `package_id` | FK → OrderPackage (nhóm items theo seller) |
| `product_name / product_image / unit_price` | **Snapshot** tại thời điểm đặt — không bị ảnh hưởng nếu seller sửa sau |
| `quantity / total_price` | Số lượng và thành tiền |
| `tax_amount / discount_amount` | Thuế và giảm giá cấp item |
| `tracking_code` | Mã tracking riêng nếu item giao tách biệt |

### OrderStatusLog – Audit trail trạng thái đơn hàng

**Bảng:** `order_status_logs`

Ghi lại **mỗi lần trạng thái đơn thay đổi** — ai đổi, từ trạng thái nào, sang trạng thái nào, khi nào.

| Trường | Ý nghĩa |
|--------|---------|
| `old_status / new_status` | Trạng thái trước và sau |
| `actor_id` | FK → User (ai thực hiện; NULL = hệ thống/webhook) |
| `role` | Vai trò: `consumer` / `seller` / `admin` / `system` |
| `note` | Ghi chú thêm (VD: "Tạo vận đơn GHN-123") |
| `timestamp` | Mốc thời gian chính xác |

### OrderPackage – Sub-order theo seller (Multi-seller)

**Bảng:** `order_packages`

Khi 1 giỏ hàng có sản phẩm của **nhiều seller**, mỗi seller có 1 package riêng.

---

## 8. 🚚 Shipment – Vận chuyển

**File:** `app/models/shipment.py` | **Bảng:** `shipments`

Mỗi đơn hàng có **1 bản ghi shipment** chứa thông tin vận chuyển.

| Trường | Ý nghĩa |
|--------|---------|
| `order_id` | FK → Order (1-1) |
| `provider` | Đơn vị vận chuyển: `GHN` / `GHTK` / `VNPOST` / `MANUAL` |
| `tracking_code` | Mã tracking khách dùng để tra cứu |
| `provider_order_code` | Mã của GHN/GHTK (dùng để gọi API hủy/cập nhật) |
| `status` | `PENDING` → `CREATED` → `PICKED_UP` → `IN_TRANSIT` → `DELIVERED` / `FAILED` / `RETURNED` |
| `shipper_name / phone` | Thông tin tài xế giao hàng |
| `cod_amount` | Số tiền cần thu hộ (cho COD) |
| `fee` | Phí vận chuyển thực tế |
| `weight` | Trọng lượng kiện hàng (gram) |
| `estimated_delivery / actual_delivery` | Ngày dự kiến và thực tế giao |
| `width / height / length` | Kích thước kiện hàng (cm) |
| `insurance_value` | Giá trị bảo hiểm hàng |
| `webhook_signature` | Chữ ký để validate callback từ GHN/GHTK |
| `tracking_detail` | JSON log chi tiết từng bước vận chuyển |

---

## 9. 💳 Payment – Thanh toán

**File:** `app/models/payment.py` | **Bảng:** `payments`

Bản ghi thanh toán được tạo sau khi **VNPAY/gateway xác nhận** thành công.

| Trường | Ý nghĩa |
|--------|---------|
| `order_id / customer_id / seller_id` | Liên kết đơn hàng và 2 bên |
| `payment_method_id` | FK → PaymentMethodType (COD, VNPAY...) |
| `gateway_transaction_id` | Mã giao dịch từ cổng thanh toán |
| `payment_channel` | Kênh TT: `card` / `bank` / `wallet` / `cod` |
| `vnpay_transaction_no` | Mã giao dịch VNPAY (dùng idempotency check) |
| `vnpay_response_code` | Mã phản hồi VNPAY (`00` = thành công) |
| `vnpay_bank_code` | Mã ngân hàng (VD: `NCB`, `BIDV`) |
| `amount` | Số tiền theo đơn hàng |
| `amount_from_gateway` | Số tiền **thực tế** gateway trả về (để so sánh) |
| `amount_mismatch` | `True` nếu 2 số tiền trên **lệch nhau** (cảnh báo gian lận) |
| `platform_fee_percentage / amount` | Phí nền tảng thu |
| `seller_amount` | Tiền seller nhận |
| `bank_code / card_brand` | Ngân hàng / loại thẻ |
| `status` | `PENDING` / `COMPLETED` / `FAILED` / `REFUNDED` / `PARTIAL_REFUNDED` |
| `failure_code / message` | Mã lỗi và mô tả khi thất bại |
| `gateway_response` | JSON đầy đủ từ gateway (cho debug/audit) |
| `refunded_amount` | Tổng tiền đã hoàn (hỗ trợ hoàn từng phần) |
| `refund_note` | Lý do hoàn tiền |
| `refunded_at` | Thời điểm hoàn tiền |

### PaymentTransaction – Từng giao dịch con

**Bảng:** `payment_transactions` — 1 Payment có thể có nhiều transaction (PAYMENT + REFUND).

| Trường | Ý nghĩa |
|--------|---------|
| `transaction_type` | `PAYMENT` / `REFUND` / `PARTIAL_REFUND` |
| `amount` | Số tiền của giao dịch này |
| `gateway_ref` | Mã tham chiếu từ gateway |

### PaymentAuditLog – Audit trail thanh toán

**Bảng:** `payment_audit_logs`

| Trường | Ý nghĩa |
|--------|---------|
| `action` | Hành động: `REFUND` / `IPN_RECEIVED` / `CONFIG_FEE` / `VNPAY_RETURN`... |
| `actor_id` | Ai thực hiện (NULL = hệ thống) |
| `amount` | Số tiền liên quan |
| `ip_address / user_agent` | IP và trình duyệt (dùng điều tra nếu có gian lận) |

---

## 10. 📣 Complaint – Khiếu nại

**File:** `app/models/complaint.py` | **Bảng:** `complaints`

| Trường | Ý nghĩa |
|--------|---------|
| `order_id / product_id` | Khiếu nại liên quan đến đơn nào / sản phẩm nào |
| `user_id` | Buyer gửi khiếu nại |
| `category` | Phân loại: `DELIVERY` / `QUALITY` / `REFUND` / `FRAUD` / `SERVICE` / `OTHER` |
| `priority` | Mức độ ưu tiên: `LOW` / `MEDIUM` / `HIGH` / `URGENT` |
| `title / description` | Tiêu đề (≥10 ký tự) và nội dung (≥30 ký tự) |
| `images` | JSON array URL ảnh bằng chứng |
| `status` | `PENDING` → `ASSIGNED` → `IN_PROGRESS` → `RESOLVED` / `CLOSED` / `REJECTED` |
| `handled_by` | FK → User (CS/admin đang xử lý) |
| `resolution` | Nội dung giải quyết |
| `resolution_type` | Kết quả: `REFUND` / `RETURN` / `REPLACEMENT` / `NONE` |
| `return_request_id` | FK → ReturnRequest (nếu giải quyết bằng đổi/trả hàng) |
| `assigned_at` | Khi nào được giao cho CS |
| `first_response_at` | Khi nào CS phản hồi lần đầu (SLA tracking) |
| `resolved_at / closed_at` | Mốc giải quyết và đóng |

### ComplaintComment – Thread trao đổi

**Bảng:** `complaint_comments` — Cho phép buyer ↔ seller ↔ CS trao đổi qua lại.

| Trường | Ý nghĩa |
|--------|---------|
| `role` | Vai trò người gửi: `buyer` / `seller` / `admin` / `system` |
| `message` | Nội dung tin nhắn |
| `attachments` | JSON array URL file đính kèm |
| `is_internal` | `True` = ghi chú nội bộ, chỉ admin/CS thấy |

### ComplaintStatusLog – Audit trail khiếu nại

**Bảng:** `complaint_status_logs` — Tương tự OrderStatusLog nhưng cho khiếu nại.

---

## 11. 📝 Review – Đánh giá sản phẩm

**Bảng:** `reviews` (trong `complaint.py`)

| Trường | Ý nghĩa |
|--------|---------|
| `product_id / user_id` | Đánh giá sản phẩm nào, ai đánh giá |
| `order_item_id` | Xác minh đã mua hàng (chỉ người mua mới review được) |
| `rating` | Điểm 1–5 cho sản phẩm |
| `seller_rating` | Điểm 1–5 cho dịch vụ của seller |
| `comment` | Nội dung đánh giá |
| `moderation_status` | `PENDING` / `APPROVED` / `REJECTED` — kiểm duyệt nội dung |
| `moderated_by / at / note` | Ai duyệt, khi nào, ghi chú |

> **Ràng buộc quan trọng:** 1 user chỉ được review 1 sản phẩm **1 lần** (unique constraint).

---

## 12. 💸 Settlement – Đối soát & Chi trả

**File:** `app/models/settlement.py`

### SellerWallet – Ví người bán

**Bảng:** `seller_wallets`

| Trường | Ý nghĩa |
|--------|---------|
| `pending_balance` | Tiền chờ đối soát (đơn đã giao nhưng chưa thanh toán cho seller) |
| `available_balance` | Tiền đã đối soát, seller rút được |
| `total_withdrawn` | Tổng đã rút từ trước đến nay |

### Settlement – Kỳ đối soát

**Bảng:** `settlements` — Hệ thống tổng kết doanh thu của seller **theo kỳ** (tuần/tháng).

| Trường | Ý nghĩa |
|--------|---------|
| `period_start / end` | Kỳ đối soát từ ngày nào đến ngày nào |
| `total_orders` | Số đơn trong kỳ |
| `total_amount` | Tổng giá trị đơn |
| `total_platform_fee` | Tổng phí nền tảng thu |
| `total_seller_amount` | Tiền seller được nhận |
| `status` | `PENDING` → `APPROVED` → `COMPLETED` |

### Payout – Chi trả

**Bảng:** `payouts` — Lệnh chuyển tiền thực tế cho seller.

| Trường | Ý nghĩa |
|--------|---------|
| `amount` | Số tiền chuyển |
| `bank_name / account` | Thông tin ngân hàng (snapshot tại thời điểm chuyển) |
| `status` | `PENDING` → `PROCESSING` → `SUCCESS` / `FAILED` |
| `transaction_ref` | Mã tham chiếu ngân hàng |

---

## 13. 🔄 ReturnRequest – Đổi/Trả hàng

**File:** `app/models/return_request.py` | **Bảng:** `return_requests`

| Trường | Ý nghĩa |
|--------|---------|
| `order_id / user_id` | Đơn hàng nào, ai yêu cầu |
| `order_item_id` | Trả cụ thể item nào (hỗ trợ trả từng sản phẩm) |
| `return_type` | `RETURN` (trả hàng-hoàn tiền) / `EXCHANGE` (đổi hàng) |
| `reason` | Lý do đổi/trả |
| `images` | JSON array ảnh chứng minh hàng lỗi |
| `refund_amount / method` | Số tiền và hình thức hoàn (ORIGINAL, BANK_TRANSFER, WALLET) |
| `return_shipping_code` | Mã vận đơn trả hàng về cho seller |
| `status` | `PENDING` → `APPROVED` → `RECEIVED` → `REFUNDED` / `EXCHANGED` |

---

## 14. 🎁 Promotion – Khuyến mãi

**File:** `app/models/promotion.py` | **Bảng:** `promotions`

| Trường | Ý nghĩa |
|--------|---------|
| `code` | Mã voucher (VD: `WELCOME10`) |
| `promotion_type` | `PERCENTAGE` (giảm %) / `FIXED_AMOUNT` (giảm số tiền cố định) |
| `discount_value` | Giá trị giảm (10 = 10% hoặc 50000 = 50.000đ) |
| `min_order_amount` | Đơn tối thiểu mới được dùng mã |
| `max_discount_amount` | Giảm tối đa (giới hạn cho loại PERCENTAGE) |
| `applicable_to` | Áp dụng cho: `ALL` / `SELLER` / `PRODUCT` / `CATEGORY` |
| `usage_limit` | Tổng số lượt dùng tối đa |
| `usage_limit_per_user` | Mỗi user dùng tối đa bao nhiêu lần |
| `used_count` | Số lần đã sử dụng |
| `start_date / end_date` | Thời gian hiệu lực |
| `status` | `ACTIVE` / `INACTIVE` / `EXPIRED` |
| `is_public` | `True` = hiển thị công khai cho buyer tìm thấy |

---

## 15. 🔖 Traceability – Truy xuất nguồn gốc

**File:** `app/models/traceability.py`

### ProductCertificate – Chứng nhận

**Bảng:** `product_certificates`

| Trường | Ý nghĩa |
|--------|---------|
| `certificate_name` | Tên chứng nhận: VietGAP, OCOP 4 sao, ISO 22000... |
| `certificate_number` | Số chứng nhận |
| `issued_by` | Cơ quan cấp (VD: "Sở NN&PTNT Hà Giang") |
| `issue_date / expiry_date` | Ngày cấp và hết hạn |
| `document_url` | File scan chứng nhận |
| `verification_status` | Admin xác minh: PENDING / VERIFIED / REJECTED / EXPIRED |

### ProductOrigin – Nguồn gốc

**Bảng:** `product_origins`

| Trường | Ý nghĩa |
|--------|---------|
| `village_name` | Làng nghề / vùng sản xuất (VD: "Làng nghề Bát Tràng") |
| `region_id` | FK → Region (tỉnh/thành phố) |
| `producer_name` | Hộ / HTX sản xuất |
| `batch_number` | Mã lô sản xuất |
| `production_date / expiry_date` | Ngày sản xuất và hạn sử dụng |
| `ingredients` | Thành phần nguyên liệu |
| `process_summary` | Mô tả quy trình sản xuất |

---

## 16. 💰 PaymentMethod – Phương thức thanh toán

**File:** `app/models/payment_method.py`

### PaymentProvider – Nhà cung cấp cổng TT
**Bảng:** `payment_providers` — Lưu cấu hình API của VNPAY, MoMo, ZaloPay (API key, endpoint).

### PaymentMethodType – Loại phương thức TT
**Bảng:** `payment_methods` — COD, BANK_TRANSFER, MOMO, VNPAY — cấu hình phí, giới hạn.

### OrderAdjustment – Điều chỉnh đơn hàng
**Bảng:** `order_adjustments` — Ghi nhận từng khoản điều chỉnh: thuế, phí, giảm giá, hoàn tiền.

---

## 17. Các model phụ trợ khác

| Model | File | Tác dụng |
|-------|------|---------|
| `Category` | `category.py` | Danh mục sản phẩm có cấu trúc cây (parent_id) |
| `Region` | `region.py` | Tỉnh/thành phố kèm tọa độ địa lý |
| `Organization` | `organization.py` | HTX, làng nghề, hiệp hội |
| `Role` | `role.py` | Vai trò hệ thống (admin, seller, customer...) |
| `Content` | `content.py` | Bài viết, video giới thiệu sản phẩm/người bán |
| `Media` | `media.py` | File ảnh/video upload lên hệ thống |
| `ProductMedia` | `product_media.py` | Ảnh/video của sản phẩm (thay thế `images` JSON cũ) |
| `ReviewImage` | `review_image.py` | Ảnh đính kèm trong đánh giá |
| `Address` | `address.py` | Sổ địa chỉ của user (tỉnh/quận/phường chuẩn hóa) |
| `PartnerContract` | `partner_contract.py` | Hợp đồng giữa nền tảng và seller |
| `Permission` | `permission.py` | Phân quyền chi tiết theo module |
| `ShippingService` | `shipping_service.py` | Bảng dịch vụ vận chuyển theo tuyến |
| `SettlementItem` | `settlement_item.py` | Chi tiết từng đơn trong kỳ đối soát |
| `PromotionUsage` | `promotion_usage.py` | Lịch sử dùng mã khuyến mãi của từng user |

---

## 📌 Quy tắc chung trong toàn bộ Models

| Quy tắc | Áp dụng |
|---------|---------|
| **Soft-delete** | `orders.is_active`, `products.is_active` — xóa mềm, giữ lịch sử |
| **Snapshot** | `order_items.product_name/price` — lưu lại thông tin tại thời điểm đặt, không bị ảnh hưởng khi seller chỉnh sửa sau |
| **Audit log** | `order_status_logs`, `complaint_status_logs`, `payment_audit_logs`, `product_price_logs` — mọi thay đổi quan trọng đều có người chịu trách nhiệm |
| **SELECT FOR UPDATE** | Checkout trừ tồn kho dùng row-level lock để tránh race condition |
| **Idempotency** | `vnpay_transaction_no` được check trùng trước khi ghi Payment, tránh xử lý IPN 2 lần |
