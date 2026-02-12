# Sprint Backlog - Phân chia Technical Tasks (BE / FE / QA)

> **Ngày tạo:** 05/02/2026  
> **Dự án:** Hệ thống CMS Nông sản

---

## 📋 Quy ước

- **Team**: 🔧 BE (Backend) | 🎨 FE (Frontend) | 🧪 QA (Testing)
- **Priority**: 🔴 Critical | 🟡 High | 🟢 Normal
- **Status**: ✅ Done | 🔄 In Progress | ⏳ To Do


## 📅 SPRINT TIMELINE

| Sprint | Thời gian | Story Points | Status |
|--------|-----------|--------------|--------|
| Sprint 1 | 01/12/2025 - 14/12/2025 | 27 SP | ✅ Done |
| Sprint 2 | 15/12/2025 - 28/12/2025 | 34 SP | ✅ Done |
| Sprint 3 | 29/12/2025 - 11/01/2026 | 33 SP | ✅ Done |
| Sprint 4 | 12/01/2026 - 25/01/2026 | 31 SP | ✅ Done |
| Sprint 5 | 26/01/2026 - 08/02/2026 | 44 SP | ✅ Done |
| Sprint 6 | 09/02/2026 - 22/02/2026 | 38 SP | ✅ Done |
| Sprint 7 | 23/02/2026 - 08/03/2026 | 20 SP | ✅ Done |
| Sprint 8 | 09/03/2026 - 22/03/2026 | 24 SP | ⏳ Planned |
| Sprint 9 | 23/03/2026 - 05/04/2026 | 34 SP | ⏳ Planned |
| Sprint 10 | 06/04/2026 - 19/04/2026 | 29 SP | ⏳ Planned |
| Sprint 11 | 20/04/2026 - 03/05/2026 | 29 SP | ⏳ Planned |
| Sprint 12 | 04/05/2026 - 17/05/2026 | 31 SP | ⏳ Planned |
| Sprint 13 | 18/05/2026 - 31/05/2026 | 28 SP | ⏳ Planned |
| Sprint 14 | 01/06/2026 - 14/06/2026 | 34 SP | ⏳ Planned |

---

# ✅ SPRINT 1 - Authentication & User Management (HOÀN THÀNH)
**📅 01/12/2025 - 14/12/2025** | **27 SP**

## US-AUTH-001: Đăng ký tài khoản (5 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-001-BE-01 | **API POST `/auth/register`**: Nhận email, password, name từ body. Validate: email format (RFC 5322), password min 8 chars + uppercase + number, name không rỗng. Return 201 với user object (không password). Rate limit /3 requests per minute per IP. **AC**: Validation chặt chẽ, response đúng format, rate limit hoạt động. | 🔧 BE | 2h | ✅ |
| AUTH-001-BE-02 | **Hash password với bcrypt**: Sử dụng bcrypt với work factor 12. Salt auto-generated. Không lưu plain password. Constant-time comparison khi verify. **AC**: Password hashed đúng cách, không thể reverse, verify hoạt động. | 🔧 BE | 1h | ✅ |
| AUTH-001-BE-03 | **Check email unique**: Query check email exists trong DB trước khi insert. Return 409 Conflict nếu email đã tồn tại với message rõ ràng. Case-insensitive comparison. **AC**: Duplicate email bị reject, error message thân thiện. | 🔧 BE | 1h | ✅ |
| AUTH-001-FE-01 | **UI Form đăng ký**: Form với fields: name, email, password, confirm password. Layout responsive. Show/hide password toggle. Submit button với loading state. Success redirect to login. Error display inline per field. **AC**: Form đẹp, responsive, UX tốt. | 🎨 FE | 2h | ✅ |
| AUTH-001-FE-02 | **Validation client-side**: Real-time validation khi blur. Email format check. Password strength indicator. Confirm password match check. Disable submit nếu form invalid. Error messages tiếng Việt. **AC**: Validation instant, messages clear, UX mượt. | 🎨 FE | 1h | ✅ |
| AUTH-001-QA-01 | **Test cases register**: Test valid registration. Test duplicate email. Test weak password. Test invalid email. Test empty fields. Test password mismatch. Test rate limiting. **AC**: Tất cả test cases pass, security verified. | 🧪 QA | 1h | ✅ |

## US-AUTH-002: Đăng nhập (3 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-002-BE-01 | **API POST `/auth/login`**: Nhận email, password. Query user by email. Verify password với bcrypt. Return 401 nếu sai với generic message "Invalid credentials" (không reveal email exists). Lock account after 5 failed attempts. **AC**: Login secure, không leak info, lockout hoạt động. | 🔧 BE | 2h | ✅ |
| AUTH-002-BE-02 | **Generate JWT token**: Access token (15 min) + Refresh token (7 days). Payload: user_id, email, roles. Sign với RS256 hoặc HS256. Include iat, exp claims. Store refresh token hash trong DB. **AC**: Tokens valid, expire đúng, refresh stored. | 🔧 BE | 1h | ✅ |
| AUTH-002-FE-01 | **UI Login form**: Form với email, password fields. Remember me checkbox. Forgot password link. Show/hide password. Loading state on submit. Error toast on failure. **AC**: Form clean, UX good, error handling rõ. | 🎨 FE | 2h | ✅ |
| AUTH-002-FE-02 | **Lưu token, redirect**: Lưu access token vào memory, refresh vào httpOnly cookie hoặc secure storage. Redirect to dashboard sau login. Handle "remember me" persistence. Auto-logout khi token expired. **AC**: Token stored secure, redirect đúng, auto-logout hoạt động. | 🎨 FE | 1h | ✅ |
| AUTH-002-QA-01 | **Test login flow**: Test valid login. Test wrong password. Test wrong email. Test account lockout. Test remember me. Test redirect after login. Test token expiry. **AC**: Tất cả test cases pass, security verified. | 🧪 QA | 1h | ✅ |

## US-AUTH-003: Lấy thông tin user (2 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-003-BE-01 | **API GET `/auth/me`**: Require valid access token trong Authorization header. Extract user_id từ token. Query user info từ DB. Return user object (id, email, name, avatar, roles, created_at). Exclude sensitive fields (password hash). **AC**: Auth required, response đúng fields, sensitive data không leak. | 🔧 BE | 1h | ✅ |
| AUTH-003-FE-01 | **Hiển thị user info**: Call /auth/me sau login. Store user trong global state (Context/Redux). Display: avatar, name, email trong header/sidebar. Handle loading state. Update UI khi user info changes. **AC**: User info load đúng, state synced, UI reactive. | 🎨 FE | 1h | ✅ |
| AUTH-003-QA-01 | **Test get user**: Test với valid token. Test với expired token (401). Test với invalid token (401). Test response fields correct. **AC**: Auth enforcement đúng, response accurate. | 🧪 QA | 30m | ✅ |

## US-AUTH-004: Đăng xuất (1 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-004-BE-01 | **API POST `/auth/logout`**: Require valid access token. Invalidate refresh token trong DB (delete hoặc mark revoked). Optional: add access token to blacklist nếu dùng Redis. Return 200 success. **AC**: Refresh token invalidated, subsequent refresh fails. | 🔧 BE | 30m | ✅ |
| AUTH-004-FE-01 | **Xóa token, redirect**: Clear access token từ memory. Clear refresh token từ storage. Clear user state. Redirect to login page. Handle logout từ any page. Confirm dialog optional. **AC**: All tokens cleared, state reset, redirect smooth. | 🎨 FE | 30m | ✅ |

## US-AUTH-005: Refresh token (2 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-005-BE-01 | **API POST `/auth/refresh`**: Nhận refresh token từ body hoặc cookie. Verify token valid và chưa revoked. Generate new access token + new refresh token (rotation). Revoke old refresh token. Return new tokens. **AC**: Token rotation hoạt động, old tokens invalid. | 🔧 BE | 1h | ✅ |
| AUTH-005-FE-01 | **Auto refresh token**: Interceptor check access token expiry trước mỗi request. Nếu sắp expire (< 1 min), call refresh API. Queue concurrent requests while refreshing. Retry original request với new token. Logout nếu refresh fails. **AC**: Seamless refresh, no failed requests due to expiry. | 🎨 FE | 1h | ✅ |

## US-USER-001 → US-USER-006: User Management (14 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| USER-001-BE-01 | **API GET `/users`**: Pagination (page, limit, default 20). Filters: role_id, is_active, search (name/email). Sort by created_at desc. Return: users array + meta (total, page, limit). Admin only access. **AC**: Pagination đúng, filters hoạt động, admin-only enforced. | 🔧 BE | 2h | ✅ |
| USER-002-BE-01 | **API POST `/users`**: Admin create user với: email, name, password, role_ids. Validate email unique. Hash password. Assign roles. Optional: send welcome email. Return created user. **AC**: User created đúng, roles assigned, email sent if configured. | 🔧 BE | 2h | ✅ |
| USER-003-BE-01 | **API PUT `/users/{id}`**: Update user fields: name, email, avatar, is_active. Validate email unique (except self). Partial update support. Admin or self can update. Audit log changes. **AC**: Update works, validation đúng, audit logged. | 🔧 BE | 1h | ✅ |
| USER-004-BE-01 | **API DELETE `/users/{id}`**: Soft delete (set deleted_at, is_active=false). Không xóa data thực. Prevent delete self. Prevent delete last admin. Cascade deactivate sessions. **AC**: Soft delete works, constraints enforced. | 🔧 BE | 1h | ✅ |
| USER-005-BE-01 | **API PUT `/users/{id}/toggle-active`**: Toggle is_active boolean. Active=false invalidates all sessions. Return updated user. Prevent deactivate self. Send email notification. **AC**: Toggle works, sessions invalidated, email sent. | 🔧 BE | 1h | ✅ |
| USER-006-BE-01 | **API PUT `/users/{id}/roles`**: Nhận role_ids array. Replace all current roles. Validate roles exist. Prevent remove all roles. Prevent remove admin role from self. Audit log. **AC**: Roles updated, constraints enforced, audit logged. | 🔧 BE | 2h | ✅ |
| USER-FE-01 | **UI User list với DataTable**: DataTable: avatar, name, email, roles badges, status badge, created date, actions. Filters sidebar: role, status. Search input. Pagination. Export button. Row click → detail. **AC**: Table feature-rich, responsive, performant. | 🎨 FE | 3h | ✅ |
| USER-FE-02 | **UI User form (create/edit)**: Modal hoặc page với: name, email, password (create only), avatar upload, roles multi-select, active toggle. Validation. Loading state. Success toast. **AC**: Form complete, validation works, UX good. | 🎨 FE | 2h | ✅ |
| USER-FE-03 | **UI Assign roles modal**: Modal hiển thị available roles với checkboxes. Current roles pre-selected. Search filter nếu nhiều roles. Save button. Confirm dialog nếu removing critical roles. **AC**: Role assignment smooth, confirmation cho critical changes. | 🎨 FE | 2h | ✅ |
| USER-QA-01 | **Test CRUD users**: Test list với filters. Test create user. Test update user. Test soft delete. Test toggle active. Test role assignment. Test constraints (duplicate email, delete self). **AC**: Tất cả operations tested, business rules verified. | 🧪 QA | 2h | ✅ |

---

# ✅ SPRINT 2 - Products & Categories (HOÀN THÀNH)
**📅 15/12/2025 - 28/12/2025** | **34 SP**

## US-PROD-001 → US-PROD-007: Product Management (24 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| PROD-001-BE-01 | **API GET `/products`**: Pagination (page, limit). Filters: category_id, status (PENDING/APPROVED/REJECTED), seller_id, price_range, label. Full-text search by name/description (PostgreSQL FTS). Sort by: created_at, price, name. Include: images, category, seller info. Cache list 5 min. **AC**: All filters work, search relevant, pagination correct. | 🔧 BE | 3h | ✅ |
| PROD-002-BE-01 | **API GET `/products/{id}`**: Return product với full details: images array, category, seller, reviews summary (avg rating, count), related products. Increment view_count. Cache 15 min, invalidate on update. 404 nếu không tìm thấy hoặc deleted. **AC**: Full details returned, caching works, view count incremented. | 🔧 BE | 1h | ✅ |
| PROD-003-BE-01 | **API POST `/products`**: Create product với: name, description (rich text), price, stock, category_id, images (array URLs), unit. Status default = PENDING_APPROVAL. Seller_id = current user. Validate required fields. Create slug từ name. Notify admin khi có product mới pending. **AC**: Product created, status pending, admin notified. | 🔧 BE | 3h | ✅ |
| PROD-004-BE-01 | **API PUT `/products/{id}`**: Update product fields. Only seller owner hoặc admin can update. Validate fields. Reset status to PENDING nếu thay đổi critical fields (name, price, description). Update slug nếu name changes. Audit log changes. **AC**: Update works, ownership enforced, re-approval triggered. | 🔧 BE | 2h | ✅ |
| PROD-005-BE-01 | **API DELETE `/products/{id}`**: Soft delete (set deleted_at). Only seller owner hoặc admin. Prevent delete nếu có pending orders. Remove from search index. Keep data cho audit purposes. **AC**: Soft delete works, constraints enforced, search updated. | 🔧 BE | 1h | ✅ |
| PROD-006-BE-01 | **API PUT `/products/{id}/approve`**: Admin only. Change status: APPROVED hoặc REJECTED. Nếu reject: require rejection_reason. Notify seller via email/notification. Set approved_at, approved_by. Invalidate cache. **AC**: Approval works, seller notified, audit tracked. | 🔧 BE | 2h | ✅ |
| PROD-007-BE-01 | **API PUT `/products/{id}/label`**: Admin assign labels: ORGANIC, VIETGAP, OCOP, etc. Labels = array of enum values. Validate labels. Update product. Reflect in search filters. **AC**: Labels assigned, filter by label works. | 🔧 BE | 1h | ✅ |
| PROD-FE-01 | **UI Product list với filters**: DataTable với: thumbnail, name, price, stock, status badge, category, seller, actions. Filters: category tree, status, price range slider, labels. Search input. Pagination. Grid/List view toggle. Export CSV. **AC**: Feature-rich list, filters responsive, performant với large datasets. | 🎨 FE | 4h | ✅ |
| PROD-FE-02 | **UI Product detail page**: Image gallery với zoom. Product info sections: description, specs, seller card. Reviews section. Related products carousel. Add to cart/wishlist buttons. Share button. Breadcrumb navigation. **AC**: Beautiful layout, all sections load, responsive. | 🎨 FE | 2h | ✅ |
| PROD-FE-03 | **UI Product form (create/edit)**: Multi-step form: Basic info → Description (WYSIWYG) → Images upload → Pricing & Stock → Review & Submit. Drag-drop image reorder. Draft save. Validation per step. Preview mode. **AC**: Multi-step works, images upload smooth, validation complete. | 🎨 FE | 4h | ✅ |
| PROD-FE-04 | **UI Product approval admin**: List pending products. Quick approve/reject buttons. Reject modal với reason textarea. Bulk approve selected. Filter by date, seller. Show product preview in modal. **AC**: Approval workflow efficient, bulk actions work. | 🎨 FE | 3h | ✅ |
| PROD-QA-01 | **Test product CRUD, approval flow**: Test create product. Test update với ownership. Test delete constraints. Test approval đúng user. Test rejection với reason. Test filters và search. Test image upload. **AC**: Full CRUD tested, approval flow verified, edge cases covered. | 🧪 QA | 3h | ✅ |

## US-CAT-001 → US-CAT-004: Category Management (10 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| CAT-001-BE-01 | **API GET `/categories`**: Return tree structure (recursive). Include: id, name, slug, parent_id, children array, product_count, image_url. Support flat list với query param ?flat=true. Cache tree 30 min. Order by sort_order. **AC**: Tree structure correct, product counts accurate, cache works. | 🔧 BE | 2h | ✅ |
| CAT-002-BE-01 | **API POST `/categories`**: Admin only. Create với: name, slug (auto-generate nếu empty), parent_id (nullable), image_url, sort_order. Validate parent exists. Max depth = 3 levels. Create unique slug. Invalidate cache. **AC**: Category created, hierarchy correct, depth limit enforced. | 🔧 BE | 1h | ✅ |
| CAT-003-BE-01 | **API PUT `/categories/{id}`**: Admin only. Update name, slug, parent_id, image, sort_order. Validate không tạo circular reference. Update child slugs nếu parent changes. Invalidate cache. **AC**: Update works, no circular refs, children updated. | 🔧 BE | 1h | ✅ |
| CAT-004-BE-01 | **API DELETE `/categories/{id}`**: Admin only. Prevent delete nếu có products hoặc children. Option: move products to parent category. Soft delete. Invalidate cache. **AC**: Delete constraints enforced, cache cleared. | 🔧 BE | 1h | ✅ |
| CAT-FE-01 | **UI Category tree view**: Tree component với expand/collapse. Drag-drop để reorder và reparent. Icons per category. Product count badges. Context menu (Edit, Delete, Add child). Search/filter tree. **AC**: Tree interactive, drag-drop works, context menu functional. | 🎨 FE | 3h | ✅ |
| CAT-FE-02 | **UI Category form modal**: Modal với: name, slug (auto-generate), parent selector (tree), image upload, sort order. Validation. Loading state. Success toast. Preview how it appears in tree. **AC**: Form complete, parent selection intuitive, preview helpful. | 🎨 FE | 2h | ✅ |
| CAT-QA-01 | **Test category CRUD**: Test create root và child categories. Test update parent. Test delete với products fail. Test drag-drop reorder. Test max depth. Test circular reference prevention. **AC**: All CRUD tested, constraints verified. | 🧪 QA | 1h | ✅ |

---

# ✅ SPRINT 3 - Orders & Payments (HOÀN THÀNH)
**📅 29/12/2025 - 11/01/2026** | **33 SP**

## US-ORD-001 → US-ORD-004: Order Management (16 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| ORD-001-BE-01 | **API GET `/orders`**: Pagination với cursor-based cho performance. Filters: status (pending/confirmed/shipping/delivered/cancelled), date_range, buyer_id, seller_id. Search by order_code. Sort by created_at desc. Include: items summary, payment status, shipping info. Admin sees all, seller sees own, buyer sees own. **AC**: Filters work, role-based access correct, pagination performant. | 🔧 BE | 3h | ✅ |
| ORD-002-BE-01 | **API GET `/orders/{id}`**: Return full order details: items với product snapshots, buyer info, shipping address, payment details, status history, seller info. Include tracking info nếu có. Access: buyer, seller, admin only. 403 cho unauthorized. **AC**: Full details returned, snapshots preserved, access controlled. | 🔧 BE | 2h | ✅ |
| ORD-003-BE-01 | **API PUT `/orders/{id}/status`**: Update order status với validation state machine: PENDING → CONFIRMED → SHIPPING → DELIVERED. CANCELLED từ PENDING/CONFIRMED. Require reason cho CANCELLED. Update timestamps. Notify buyer via push/email. Trigger payment release nếu DELIVERED. **AC**: State machine enforced, notifications sent, payment triggered. | 🔧 BE | 2h | ✅ |
| ORD-004-BE-01 | **API GET `/orders/statistics`**: Return aggregated stats: total_orders, total_revenue, orders_by_status (counts), revenue_by_period (daily/weekly/monthly). Filters: date_range, seller_id. Cache 15 min. Support comparison với previous period. **AC**: Stats accurate, comparison works, cache hoạt động. | 🔧 BE | 2h | ✅ |
| ORD-FE-01 | **UI Order list**: DataTable: order_code, buyer name, items count, total, status badge (colored), payment badge, date. Filters: status tabs, date picker. Quick actions: view, update status. Export CSV. Bulk status update for sellers. **AC**: List functional, filters work, bulk actions smooth. | 🎨 FE | 3h | ✅ |
| ORD-FE-02 | **UI Order detail**: Header: order code, status timeline. Sections: Items table (image, name, qty, price), Buyer info card, Shipping address card, Payment info card, Status history log. Actions: Update status (với reason modal cho cancel), Print invoice. **AC**: All sections display correctly, actions work, print generates PDF. | 🎨 FE | 3h | ✅ |
| ORD-FE-03 | **UI Update status workflow**: Status selector dropdown với available next statuses only. Confirmation modal. Cancel requires reason textarea. Loading state during update. Optimistic UI update. Toast notifications. Refresh status history. **AC**: State machine enforced in UI, confirmations work, UX smooth. | 🎨 FE | 2h | ✅ |
| ORD-QA-01 | **Test order operations**: Test list với role-based access. Test order detail permissions. Test status transitions valid. Test invalid transitions rejected. Test cancel với reason. Test notifications sent. Test payment trigger on delivered. **AC**: All operations tested, state machine verified above. | 🧪 QA | 2h | ✅ |

## US-PAY-001 → US-PAY-005: Payment Management (17 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| PAY-001-BE-01 | **API GET `/payments`**: List payments với filters: status (pending/completed/failed/refunded), payment_method, date_range, order_id. Include order summary. Pagination. Admin and seller access. Sort by created_at desc. **AC**: Filters work, role access correct, pagination smooth. | 🔧 BE | 2h | ✅ |
| PAY-002-BE-01 | **API GET `/payments/{id}`**: Full payment details: amount, method, status, transaction_id, gateway_response (sanitized), order info, refund history. Audit trail của status changes. Mask sensitive data (card numbers). **AC**: Details complete, sensitive data masked, audit visible. | 🔧 BE | 1h | ✅ |
| PAY-003-BE-01 | **API GET `/payments/reconciliation`**: Daily/weekly reconciliation report: total_collected, platform_fee, seller_payouts, refunds, net_amount. Group by date. Compare với gateway reports. Flag discrepancies. Export ready format. **AC**: Math correct, discrepancies flagged, export works. | 🔧 BE | 3h | ✅ |
| PAY-004-BE-01 | **API POST `/payments/{id}/refund`**: Initiate refund với: amount (partial or full), reason. Validate: refund <= paid amount, order status allows refund. Call payment gateway refund API. Update payment status. Notify buyer. Create refund record. **AC**: Refund processed, constraints enforced, buyer notified. | 🔧 BE | 3h | ✅ |
| PAY-005-BE-01 | **API PUT `/config/platform-fee`**: Admin set platform fee percentage (e.g., 5%). Validate 0-100 range. Apply to new orders only. Audit log changes. Support different fees per category (optional). **AC**: Fee saved, applies to new orders, audit logged. | 🔧 BE | 1h | ✅ |
| PAY-FE-01 | **UI Payment list**: DataTable: payment_id, order_code, amount (formatted VND), method icon, status badge, date. Filters: status, method, date range. Click row → payment detail. Export for accounting. **AC**: List clear, formatted currency, export useful. | 🎨 FE | 2h | ✅ |
| PAY-FE-02 | **UI Reconciliation report**: Date range selector. Summary cards: collected, fees, payouts, refunds, net. Table breakdown by date. Chart visualization. Discrepancy alerts highlighted red. Export PDF/Excel. Print-friendly. **AC**: Report accurate, discrepancies visible, exports work. | 🎨 FE | 3h | ✅ |
| PAY-FE-03 | **UI Refund dialog**: Modal với: current order/payment info, refund amount input (with max validation), reason dropdown + textarea. Preview final amounts. Confirm button. Success/error feedback. **AC**: Validation works, preview accurate, process completes. | 🎨 FE | 2h | ✅ |
| PAY-QA-01 | **Test payment operations**: Test list và filters. Test payment detail với masked data. Test reconciliation accuracy. Test refund full amount. Test refund partial. Test refund exceeds limit fail. Test platform fee applies correctly. **AC**: All payment ops tested, math verified. | 🧪 QA | 2h | ✅ |

---

# ✅ SPRINT 4 - Content & Organizations (HOÀN THÀNH)
**📅 12/01/2026 - 25/01/2026** | **31 SP**

## US-CNT-001 → US-CNT-006: Content Management (18 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| CNT-001-BE-01 | **API GET `/contents`**: List contents với filters: type (news/article/guide), status (draft/pending/published), category_id, author_id. Full-text search by title/body. Pagination. Sort by published_at hoặc created_at. Include: thumbnail, excerpt, author info. **AC**: Filters work, search relevant, pagination correct. | 🔧 BE | 2h | ✅ |
| CNT-002-BE-01 | **API GET `/contents/{id}`**: Return full content: title, body (HTML), thumbnail, images, author, category, tags, published_at, view_count. Increment view_count on each request (debounced). SEO fields: meta_title, meta_description. Related contents. **AC**: Full content returned, view count tracked, SEO fields included. | 🔧 BE | 1h | ✅ |
| CNT-003-BE-01 | **API POST `/contents`**: Create content với: title, body (sanitized HTML), type, category_id, thumbnail, tags, status (draft/pending). Author_id = current user. Generate slug from title. Validate required fields. Save draft auto (optional). **AC**: Content created, HTML sanitized, slug unique. | 🔧 BE | 2h | ✅ |
| CNT-004-BE-01 | **API PUT `/contents/{id}`**: Update content fields. Author or admin only. Track revision history. Reset to pending nếu published content changed significantly. Update slug nếu title changes (with redirect from old). **AC**: Update works, revisions tracked, access controlled. | 🔧 BE | 1h | ✅ |
| CNT-005-BE-01 | **API DELETE `/contents/{id}`**: Soft delete (set deleted_at). Author or admin only. Option to unpublish instead of delete. Keep revision history. **AC**: Soft delete works, access controlled, history preserved. | 🔧 BE | 1h | ✅ |
| CNT-006-BE-01 | **API PUT `/contents/{id}/approve`**: Admin/Editor change status: PENDING → PUBLISHED hoặc REJECTED. Set published_at khi approve. Rejection requires reason. Notify author via email/notification. Schedule publish cho future date (optional). **AC**: Approval works, scheduling works, author notified. | 🔧 BE | 2h | ✅ |
| CNT-FE-01 | **UI Content list**: DataTable: thumbnail, title, type badge, status badge, author, category, date. Filters: type, status, category, author. Search. Pagination. Quick actions: edit, delete, publish (admin). **AC**: List comprehensive, filters work, actions accessible. | 🎨 FE | 2h | ✅ |
| CNT-FE-02 | **UI Content editor (WYSIWYG)**: Rich text editor (TinyMCE/Quill): formatting, headings, lists, links, images, embeds. Side panel: thumbnail upload, category select, tags input, SEO fields. Auto-save drafts every 60s. Preview mode. Word count. **AC**: Editor full-featured, auto-save works, preview accurate. | 🎨 FE | 4h | ✅ |
| CNT-FE-03 | **UI Content approval**: Admin view với pending contents. Inline preview. Approve/Reject buttons. Reject modal với reason. Scheduled publish date picker. Bulk approve. Email preview before send. **AC**: Approval workflow efficient, scheduling works, bulk actions available. | 🎨 FE | 2h | ✅ |
| CNT-QA-01 | **Test content operations**: Test CRUD operations. Test approval workflow. Test scheduling. Test revision history. Test soft delete. Test search. Test access controls. Test auto-save. **AC**: All operations verified, edge cases covered. | 🧪 QA | 2h | ✅ |

## US-ORG-001 → US-ORG-004: Organization Management (13 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| ORG-001-BE-01 | **API GET `/organizations`**: List organizations với filters: type (cooperative/company/association), region_id, is_active. Search by name. Pagination. Include: member_count, product_count, logo. Sort by name hoặc created_at. **AC**: Filters work, counts accurate, pagination correct. | 🔧 BE | 2h | ✅ |
| ORG-002-BE-01 | **API GET `/organizations/{id}`**: Full org details: name, description, type, address, contact info, logo, banner, members list, products, certifications. Statistics: total_products, total_revenue, avg_rating. **AC**: Full details returned, stats accurate. | 🔧 BE | 1h | ✅ |
| ORG-003-BE-01 | **API POST `/organizations`**: Admin create org với: name, type, description, contact, address, region_id, logo. Generate unique slug. Set is_active = true. Assign initial admin member. Validate required fields. **AC**: Org created, slug unique, admin assigned. | 🔧 BE | 2h | ✅ |
| ORG-004-BE-01 | **API POST/DELETE `/organizations/{id}/members`**: Add member: user_id, role (admin/member). Remove member. Org admin hoặc system admin only. Validate user exists. Prevent remove last admin. Notify member via email. **AC**: Member ops work, constraints enforced, notifications sent. | 🔧 BE | 2h | ✅ |
| ORG-FE-01 | **UI Organization list**: DataTable: logo, name, type badge, region, members count, status, actions. Filters: type, region, status. Search. Card view toggle option. Click → org detail. **AC**: List clean, filters work, views toggle. | 🎨 FE | 2h | ✅ |
| ORG-FE-02 | **UI Organization detail**: Header: logo, name, type. Tabs: Overview, Members, Products, Settings. Overview: description, contact, stats cards. Map với location (optional). Edit button cho admins. **AC**: Detail comprehensive, tabs work, edit accessible. | 🎨 FE | 2h | ✅ |
| ORG-FE-03 | **UI Member management**: Members table: avatar, name, email, role badge, joined date. Add member: user search modal. Change role dropdown. Remove với confirmation. Invite new user option. **AC**: Member CRUD works, search functional, confirmations present. | 🎨 FE | 2h | ✅ |
| ORG-QA-01 | **Test organization CRUD**: Test create org. Test add/remove members. Test role changes. Test constraints (last admin, duplicate member). Test notifications. Test access controls. **AC**: All org operations verified. | 🧪 QA | 1h | ✅ |

---

# ✅ SPRINT 5 - System Management & Dashboard (HOÀN THÀNH)
**📅 26/01/2026 - 08/02/2026** | **44 SP**

## US-DASH-001 → US-DASH-005: Dashboard (19 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| DASH-001-BE-01 | **API GET `/dashboard/overview`**: Return aggregated metrics: total_users, total_products, total_orders, total_revenue, pending_approvals. Comparison với period trước (%, absolute change). Breakdown by role / type. Cache 5 min. **AC**: Metrics accurate, comparisons correct, cache works. | 🔧 BE | 3h | ✅ |
| DASH-002-BE-01 | **API GET `/dashboard/revenue`**: Time series revenue data với granularity: daily (30 days), weekly (12 weeks), monthly (12 months). Include: date, revenue, order_count, avg_order_value. Group by category / region (optional). **AC**: Time series correct, grouping works, performance good. | 🔧 BE | 3h | ✅ |
| DASH-003-BE-01 | **API GET `/dashboard/products`**: Product metrics: total, by_category (pie data), by_status (pending/approved), top_selling (limit 10), low_stock alerts. Include trends (new products this week). **AC**: All metrics accurate, top selling sorted correctly. | 🔧 BE | 2h | ✅ |
| DASH-004-BE-01 | **API GET `/dashboard/orders`**: Order metrics: total, by_status (funnel data), recent orders (limit 10), average processing time. Geographic distribution (by region). Trends: orders today vs yesterday. **AC**: Funnel accurate, recent sorted, trends calculated. | 🔧 BE | 2h | ✅ |
| DASH-005-BE-01 | **API GET `/dashboard/users`**: User metrics: total, by_role (pie), new registrations (time series), active users (DAU/MAU). Retention metrics (optional). Geographic distribution. **AC**: User counts accurate, activity tracking works. | 🔧 BE | 2h | ✅ |
| DASH-FE-01 | **UI Dashboard layout**: Responsive grid layout. Header với date range selector. Main content: stat cards row, charts row, tables row. Sidebar widgets (optional). Dark mode support. Print-friendly. **AC**: Layout responsive, date selector updates all widgets, print works. | 🎨 FE | 4h | ✅ |
| DASH-FE-02 | **UI Stats cards**: Card components: icon, metric value (formatted), label, change indicator (% up/down với màu). Animate number changes. Clickable → drill down. Skeleton loading. **AC**: Cards informative, animations smooth, drill down works. | 🎨 FE | 2h | ✅ |
| DASH-FE-03 | **UI Charts (revenue, orders)**: Line chart cho revenue trends. Bar chart cho orders by status. Pie chart cho distribution. Interactive tooltips. Legend với toggle visibility. Responsive sizing. Export as image. **AC**: Charts render correctly, interactions smooth, export works. | 🎨 FE | 4h | ✅ |
| DASH-QA-01 | **Test dashboard data**: Test all API endpoints return accurate data. Test date range filter. Test charts render. Test card drill downs. Test responsiveness. Test performance với large datasets. **AC**: All dashboard data verified accurate. | 🧪 QA | 2h | ✅ |

## US-ROLE-001, US-PERM-001: Role & Permission (10 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| ROLE-BE-01 | **API CRUD `/roles`**: GET list roles với permissions. GET single role. POST create role với: name, description, permission_ids. PUT update role. DELETE role (prevent nếu có users assigned). Validate name unique. Include user_count per role. **AC**: CRUD works, constraints enforced, counts accurate. | 🔧 BE | 3h | ✅ |
| PERM-BE-01 | **API CRUD `/permissions`**: GET list all permissions grouped by module. GET single permission. POST create permission với: name, code (unique), module, description. PUT update. DELETE (prevent nếu assigned to roles). System permissions không thể edit/delete. **AC**: CRUD works, grouping correct, system protected. | 🔧 BE | 3h | ✅ |
| ROLE-FE-01 | **UI Role management**: DataTable: name, description, permissions count, users count, actions. Create/Edit modal với: name, description, permissions multi-select (grouped by module). Clone role button. Permissions preview. **AC**: CRUD works, permissions grouped, clone functional. | 🎨 FE | 3h | ✅ |
| PERM-FE-01 | **UI Permission matrix**: Matrix view: rows = roles, columns = permissions (grouped). Checkbox intersection. Quick save changes. Filter by module. Highlight system roles/permissions. Export matrix. **AC**: Matrix intuitive, quick save works, filters helpful. | 🎨 FE | 3h | ✅ |
| ROLE-QA-01 | **Test role-permission**: Test create role. Test assign permissions. Test remove role với users fail. Test permission matrix updates. Test user inherits permissions. Test API authorization based on permissions. **AC**: RBAC fully tested end-to-end. | 🧪 QA | 2h | ✅ |

## US-REG-001, US-MED-001, US-CON-001: System (15 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| REG-BE-01 | **API CRUD `/regions`**: GET list regions (tree structure cho provinces/districts). POST create region với: name, code, parent_id, coordinates. PUT update. DELETE (prevent nếu có products/users). Import từ VN administrative data. **AC**: Tree structure correct, import works, constraints enforced. | 🔧 BE | 2h | ✅ |
| MED-BE-01 | **API upload/list/delete `/media`**: POST upload single/multiple files với: resize options, folder path. GET list với filters: type (image/video/doc), folder, uploader. DELETE single/bulk. Support: JPEG, PNG, WebP, MP4, PDF. Max 50MB. Cloud storage (S3/GCS). Generate thumbnails cho images. **AC**: Upload works, thumbnails generated, filters functional. | 🔧 BE | 3h | ✅ |
| CON-BE-01 | **API CRUD `/contracts`**: GET list contracts với filters: status, party, date_range. POST create với: title, parties, terms, start/end dates, attachments. PUT update. DELETE soft delete. Contract templates support. Digital signature integration (optional). **AC**: CRUD works, templates apply, filtering correct. | 🔧 BE | 3h | ✅ |
| REG-FE-01 | **UI Region management**: Tree view với provinces/districts/wards. Expand/collapse. Add child region. Edit inline hoặc modal. Drag to reorder (optional). Search filter. Import CSV button. **AC**: Tree navigation smooth, CRUD works, import functional. | 🎨 FE | 2h | ✅ |
| MED-FE-01 | **UI Media library**: Grid view với thumbnails. Folder navigation. Upload dropzone với progress. Multi-select cho bulk delete. Filter by type. Search by name. Preview modal (image zoom, video play, pdf view). Copy URL button. **AC**: Library comprehensive, preview works, bulk actions smooth. | 🎨 FE | 3h | ✅ |
| CON-FE-01 | **UI Contract management**: DataTable: title, parties, status badge, dates, actions. Create/Edit page với: form fields, rich text terms editor, attachment upload, template selector. Status workflow buttons. PDF export. **AC**: Contract CRUD complete, PDF generation works. | 🎨 FE | 3h | ✅ |
| SYS-QA-01 | **Test system modules**: Test region CRUD và hierarchy. Test media upload various types. Test media size limits. Test contract CRUD. Test PDF export. Test constraints all modules. **AC**: All system modules tested thoroughly. | 🧪 QA | 2h | ✅ |

---

# ✅ SPRINT 6 - Mobile App API (HOÀN THÀNH)
**📅 09/02/2026 - 22/02/2026** | **38 SP**

## US-MOB-001 → US-MOB-009: Mobile APIs (38 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| MOB-001-BE-01 | **API GET `/mobile/posts`**: Public endpoint trả list posts cho app. Pagination cursor-based cho infinite scroll. Include: title, excerpt, thumbnail, author, published_at, view_count. Filters: category_id, featured. Sort by latest/trending. Cache 5 min. **AC**: Pagination smooth, cache works, public accessible. | 🔧 BE | 2h | ✅ |
| MOB-002-BE-01 | **API GET `/mobile/posts/{id}`**: Return full post content: title, body (HTML optimized cho mobile), images, author card, related posts. Track view dengan rate limiting. Share URL included. **AC**: Full content returned, mobile-optimized, tracking works. | 🔧 BE | 1h | ✅ |
| MOB-003-BE-01 | **API POST `/mobile/posts`**: Authenticated user create post với: title, body, images (URLs), category_id. Status = PENDING. Validate content length limits. Image upload via separate endpoint. Notify moderators. **AC**: Post created, validation works, notifications sent. | 🔧 BE | 2h | ✅ |
| MOB-004-BE-01 | **API CRUD `/mobile/my-posts`**: GET list posts của current user với status filter. PUT update own posts (chỉ draft/rejected). DELETE soft delete own posts. Include edit history. **AC**: User can manage own posts, status restrictions enforced. | 🔧 BE | 3h | ✅ |
| MOB-005-BE-01 | **API GET `/mobile/products`**: Optimized product list cho mobile: lighter payload, essential fields only. Infinite scroll pagination. Quick filters: category, price_range. Sort: popular, newest, price. Include wishlist status nếu authenticated. **AC**: Light payload, fast response, wishlist integrated. | 🔧 BE | 2h | ✅ |
| MOB-006-BE-01 | **API GET `/mobile/products/{id}`**: Product detail optimized for mobile: all images, description (HTML lite), price, stock, seller mini-card, reviews summary (avg + count), similar products. Add-to-cart ready format. **AC**: Mobile-optimized response, all purchase info included. | 🔧 BE | 1h | ✅ |
| MOB-007-BE-01 | **API POST `/mobile/orders`**: Create order từ cart. Validate: stock available, prices unchanged, shipping address valid. Calculate: subtotal, shipping, discount, total. Create order + order_items. Clear cart. Payment gateway integration ready. Send confirmation email. **AC**: Order created atomically, validations passed, email sent. | 🔧 BE | 4h | ✅ |
| MOB-008-BE-01 | **API GET `/mobile/my-orders`**: List orders của current user với status filter. Include: order_code, items preview (2 items + count), total, status badge, created_at. Pagination. Enable tracking link when shipping. **AC**: User order history complete, tracking accessible. | 🔧 BE | 2h | ✅ |
| MOB-009-BE-01 | **API GET/PUT `/mobile/profile`**: GET current user profile: name, email, phone, avatar, addresses. PUT update profile fields with validation. PUT avatar via separate upload endpoint. Change password separate endpoint. **AC**: Profile CRUD works, validation enforced. | 🔧 BE | 2h | ✅ |
| MOB-FE-01 | **Posts list screen (mobile)**: FlatList với card: thumbnail, title, excerpt, author, date. Pull-to-refresh. Infinite scroll. Skeleton loading. Empty state. Category filter tabs. **AC**: List performant, refresh works, skeleton smooth. | 🎨 FE | 3h | ✅ |
| MOB-FE-02 | **Post detail screen**: Hero image. Title, author card với follow button. Body content (WebView hoặc native render). Share button. Related posts horizontal scroll. Back navigation. **AC**: Content renders cleanly, share works, navigation smooth. | 🎨 FE | 2h | ✅ |
| MOB-FE-03 | **Create post screen**: Form: title input, category picker, body editor (simplified rich text), image picker (multiple). Validation feedback. Draft save. Publish/Submit button. Preview mode. **AC**: Form complete, validations work, drafts persist. | 🎨 FE | 3h | ✅ |
| MOB-FE-04 | **Products list screen**: Grid 2 columns với cards: image, name, price, rating. Category tabs. Sort dropdown. Pull-to-refresh. Infinite scroll. Add to wishlist button. **AC**: Grid performant, filters work, wishlist toggles. | 🎨 FE | 3h | ✅ |
| MOB-FE-05 | **Product detail screen**: Image carousel. Price prominently. Stock indicator. Description accordion. Seller card. Reviews section. Add to cart CTA button (sticky bottom). Quantity selector. **AC**: All info displayed, add to cart works, UX premium. | 🎨 FE | 2h | ✅ |
| MOB-FE-06 | **Checkout flow**: Multi-step: Cart review → Shipping address (select/add) → Payment method → Order summary → Confirm. Progress indicator. Back navigation. Loading states. Error handling. Success screen với order details. **AC**: Flow complete, validation each step, success clear. | 🎨 FE | 4h | ✅ |
| MOB-FE-07 | **My orders screen**: List với order cards: order code, status badge (colored), items preview, total, date. Status filter tabs. Click → order detail. Pull-to-refresh. **AC**: List clear, status colors correct, navigation works. | 🎨 FE | 3h | ✅ |
| MOB-FE-08 | **Profile screen**: Header với avatar, name, email. Stats row: orders, reviews, wishlist counts. Menu sections: My Orders, Addresses, Settings, Logout. Edit profile button. Version info footer. **AC**: Profile comprehensive, navigation to all sections works. | 🎨 FE | 2h | ✅ |
| MOB-QA-01 | **Test mobile flows**: Test post list và detail. Test product list và detail. Test full checkout flow. Test profile update. Test order history. Test offline handling. Test deep links. **AC**: All mobile flows tested end-to-end. | 🧪 QA | 4h | ✅ |

---

# ✅ SPRINT 7 - Complaints & Reviews (HOÀN THÀNH)
**📅 23/02/2026 - 08/03/2026** | **20 SP**

## US-REV-001, US-CMP-001 → US-CMP-002: Reviews & Complaints (11 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| REV-001-BE-01 | **API GET `/reviews`**: List reviews với filters: product_id, user_id, rating (1-5), has_images. Include: user info, product info, rating, comment, images, helpful_count, created_at. Sort by: newest, rating, helpful. Pagination. Admin sees all, others see public. **AC**: Filters work, sorting correct, access appropriate. | 🔧 BE | 2h | ✅ |
| CMP-001-BE-01 | **API GET `/complaints`**: List complaints với filters: status (pending/in_progress/resolved/rejected), type (product/seller/order), severity (low/medium/high), date_range. Include: complainant, subject, description snippet, status, created_at. Admin/support access. **AC**: Filters work, access controlled, pagination correct. | 🔧 BE | 2h | ✅ |
| CMP-002-BE-01 | **API PUT `/complaints/{id}/resolve`**: Update complaint với: resolution (text), status (resolved/rejected). Validate complaint exists và status allows resolution. Assign resolver = current admin. Set resolved_at timestamp. Notify complainant via email. Create resolution history record. **AC**: Resolution recorded, notification sent, history tracked. | 🔧 BE | 2h | ✅ |
| REV-FE-01 | **UI Review list (admin)**: DataTable: product thumbnail, user name, rating stars, comment preview, images count, helpful count, date, actions. Filters: product, rating, has images. Flag/hide actions. Bulk actions. **AC**: List comprehensive, moderation actions work. | 🎨 FE | 2h | ✅ |
| CMP-FE-01 | **UI Complaint list**: DataTable: ID, complainant name, type badge, subject, status badge (colored), severity indicator, assigned to, date, actions. Filters: status tabs, type, severity. Quick assign dropdown. **AC**: List actionable, filters work, assignments smooth. | 🎨 FE | 2h | ✅ |
| CMP-FE-02 | **UI Resolve complaint**: Modal hoặc side panel: complaint details (full), complainant info, related order/product/seller links, attachment preview. Resolution form: status dropdown, resolution textarea. History timeline. Send response preview. **AC**: Full context visible, resolution intuitive, history clear. | 🎨 FE | 2h | ✅ |
| RC-QA-01 | **Test review, complaint**: Test list reviews với filters. Test review moderation (hide/flag). Test complaint list. Test assign complaint. Test resolve complaint. Test reject complaint. Test notifications sent. **AC**: Review và complaint workflows tested. | 🧪 QA | 2h | ✅ |

## US-STAT-001 → US-STAT-003: Statistics (9 SP) ✅

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| STAT-001-BE-01 | **API GET `/stats/producers`**: Producer analytics: total producers, active producers, top producers by revenue/products, producers by region, new producers trend. Include: avg products per producer, avg rating. Filter by date range. **AC**: Stats accurate, top lists correct, trends calculated. | 🔧 BE | 2h | ✅ |
| STAT-002-BE-01 | **API GET `/stats/consumers`**: Consumer analytics: total consumers, active (ordered last 30 days), top buyers by spending, consumers by region, acquisition trend. Include: avg order value, repeat purchase rate. Filter by date range. **AC**: Consumer metrics accurate, cohort analysis works. | 🔧 BE | 2h | ✅ |
| STAT-003-BE-01 | **API GET `/stats/trending-products`**: Trending products algorithm: combination of views, orders, reviews, rating trong specified period. Return top 20 with trend direction (up/down/stable). Include: product info, current rank, previous rank, metrics breakdown. **AC**: Algorithm logical, rankings accurate, trend indicators correct. | 🔧 BE | 2h | ✅ |
| STAT-FE-01 | **UI Producer stats**: Dashboard section: total cards, top producers table/chart, map visualization (by region), trend line chart. Date range selector. Export data. Drill down to producer detail. **AC**: Visualizations clear, drill down works, export functional. | 🎨 FE | 2h | ✅ |
| STAT-FE-02 | **UI Consumer stats**: Dashboard section: metrics cards (totals, avg), top buyers table, geographic chart, acquisition funnel, retention chart. Cohort selector. Date range. Export. **AC**: Consumer insights actionable, charts accurate. | 🎨 FE | 2h | ✅ |
| STAT-FE-03 | **UI Trending products**: List/grid với: rank number, product card, trend arrow (up/down/stable), rank change (+/-), key metric. Period selector (24h, 7d, 30d). Category filter. Share trending list. **AC**: Trending clear, period switching updates data, engaging UI. | 🎨 FE | 2h | ✅ |
| STAT-QA-01 | **Test statistics**: Test producer stats accuracy. Test consumer stats. Test trending algorithm với known data. Test date range filtering. Test export. Test visualizations render. **AC**: All statistics verified accurate against source data. | 🧪 QA | 1h | ✅ |

---

# ⏳ SPRINT 8 - Authentication Enhancement
**📅 09/03/2026 - 22/03/2026** | **24 SP**

## US-AUTH-006: Quên mật khẩu (5 SP) ⏳

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-006-BE-01 | API POST `/auth/forgot-password` | 🔧 BE | 2h | ⏳ |
| AUTH-006-BE-02 | Service gửi email reset | 🔧 BE | 3h | ⏳ |
| AUTH-006-BE-03 | API POST `/auth/reset-password` | 🔧 BE | 2h | ⏳ |
| AUTH-006-FE-01 | UI Forgot password form | 🎨 FE | 2h | ⏳ |
| AUTH-006-FE-02 | UI Reset password form | 🎨 FE | 2h | ⏳ |
| AUTH-006-QA-01 | Test reset password flow | 🧪 QA | 2h | ⏳ |

## US-AUTH-007: Đổi mật khẩu (3 SP) ⏳

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-007-BE-01 | API PUT `/auth/change-password` | 🔧 BE | 2h | ⏳ |
| AUTH-007-FE-01 | UI Change password form | 🎨 FE | 2h | ⏳ |
| AUTH-007-QA-01 | Test change password | 🧪 QA | 1h | ⏳ |

## US-AUTH-008: Xác thực OTP (5 SP) ⏳

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-008-BE-01 | API POST `/auth/send-otp` | 🔧 BE | 2h | ⏳ |
| AUTH-008-BE-02 | API POST `/auth/verify-otp` | 🔧 BE | 2h | ⏳ |
| AUTH-008-FE-01 | UI OTP input (6 digits) | 🎨 FE | 2h | ⏳ |
| AUTH-008-FE-02 | Countdown + resend | 🎨 FE | 1h | ⏳ |
| AUTH-008-QA-01 | Test OTP flow | 🧪 QA | 2h | ⏳ |

## US-AUTH-009: Đăng ký Producer (8 SP) ⏳

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| AUTH-009-BE-01 | API POST `/auth/register-producer` | 🔧 BE | 3h | ⏳ |
| AUTH-009-BE-02 | Upload giấy phép kinh doanh | 🔧 BE | 2h | ⏳ |
| AUTH-009-BE-03 | API PUT `/admin/producers/{id}/approve` | 🔧 BE | 2h | ⏳ |
| AUTH-009-FE-01 | UI Multi-step register form | 🎨 FE | 4h | ⏳ |
| AUTH-009-FE-02 | UI Admin approve producer | 🎨 FE | 3h | ⏳ |
| AUTH-009-QA-01 | Test producer registration | 🧪 QA | 3h | ⏳ |

## US-USER-007: Upload Avatar (3 SP) ⏳

| Task ID | Task Description | Team | Est. | Status |
|---------|------------------|------|------|--------|
| USER-007-BE-01 | API POST `/users/avatar` | 🔧 BE | 2h | ⏳ |
| USER-007-FE-01 | UI Avatar upload + crop | 🎨 FE | 3h | ⏳ |
| USER-007-QA-01 | Test avatar upload | 🧪 QA | 1h | ⏳ |

---

# 🏃 SPRINT 8 - Authentication Enhancement

**Sprint Goal**: Hoàn thiện tính năng xác thực còn thiếu  
**Total Story Points**: 24 SP

---

## US-AUTH-006: Quên mật khẩu (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| AUTH-006-BE-01 | **API POST `/auth/forgot-password`**: Xây dựng endpoint nhận email từ request body, validate định dạng email, kiểm tra email tồn tại trong database. Nếu tồn tại, generate reset token (UUID v4) với thời hạn 30 phút, lưu vào bảng password_reset_tokens và trigger gửi email. Response 200 kể cả email không tồn tại (security). **AC**: Email hợp lệ nhận được link reset, email sai format trả lỗi 422. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-006-BE-02 | **Service gửi email reset password**: Tích hợp SMTP hoặc SendGrid API để gửi email. Tạo email template HTML với branding, chứa link reset dạng `{FRONTEND_URL}/reset-password?token={token}`. Implement retry logic (3 lần), queue email bằng background task. **AC**: Email được gửi trong vòng 30s, chứa đúng link reset. | 🔧 BE | 🔴 | 3h | ⏳ |
| AUTH-006-BE-03 | **API POST `/auth/reset-password`**: Nhận token và new_password từ body. Validate token còn hạn và chưa được sử dụng. Hash password mới với bcrypt (salt rounds=12). Update password trong bảng users, đánh dấu token đã sử dụng. Invalidate tất cả sessions cũ của user. **AC**: Password được đổi thành công, token chỉ dùng 1 lần, token hết hạn trả lỗi 400. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-006-BE-04 | **Tạo bảng `password_reset_tokens`**: Thiết kế schema với các cột: id (UUID PK), user_id (FK references users), token (varchar unique indexed), expires_at (timestamp), used_at (timestamp nullable), created_at. Tạo Alembic migration, thêm index cho token. **AC**: Migration chạy thành công, rollback được. | 🔧 BE | 🔴 | 1h | ⏳ |
| AUTH-006-FE-01 | **UI Form nhập email quên mật khẩu**: Tạo trang /forgot-password với form nhập email. Validation real-time (email format). Submit gọi API, hiển thị loading state. Thông báo thành công yêu cầu check email. Nút quay lại trang login. Responsive mobile/desktop. **AC**: UI theo design system, hiển thị thông báo phù hợp. | 🎨 FE | 🟡 | 2h | ⏳ |
| AUTH-006-FE-02 | **UI Form reset password mới**: Tạo trang /reset-password với 2 input: password mới và xác nhận password. Validation: min 8 ký tự, có chữ hoa/thường/số, 2 password phải khớp. Hiển thị password strength meter. Submit gọi API với token từ URL query. Redirect tới login khi thành công. **AC**: Validation hoạt động đúng, redirect sau reset. | 🎨 FE | 🟡 | 2h | ⏳ |
| AUTH-006-FE-03 | **Xử lý redirect từ email**: Parse token từ URL query params khi vào trang /reset-password. Gọi API validate token ngay khi load page. Nếu token invalid/expired, hiển thị thông báo lỗi với link quay về forgot-password. Lưu token vào state để submit form. **AC**: Token invalid hiện thông báo rõ ràng, không cho submit. | 🎨 FE | 🟡 | 1h | ⏳ |
| AUTH-006-QA-01 | **Test cases reset password flow**: Test email hợp lệ nhận được email, email không tồn tại vẫn trả success (security), email sai format bị reject. Test token hết hạn (sau 30 phút) không reset được. Test password rules: < 8 ký tự fail, không có số fail. Test token chỉ dùng 1 lần. Test confirm password không khớp. **AC**: Tất cả test cases pass, coverage > 80%. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-AUTH-007: Đổi mật khẩu (3 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| AUTH-007-BE-01 | **API PUT `/auth/change-password`**: Endpoint yêu cầu authentication (JWT token). Nhận current_password, new_password, confirm_password từ body. Verify current_password đúng với password trong DB. Validate new_password theo rules: min 8 ký tự, ít nhất 1 chữ hoa, 1 chữ thường, 1 số. Check new_password != current_password. **AC**: Chỉ user đã đăng nhập mới đổi được, password cũ sai trả 401, password mới không hợp lệ trả 422. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-007-BE-02 | **Validate và hash password mới**: Implement password validator service kiểm tra strength (weak/medium/strong). Hash password với bcrypt salt rounds=12. Update bảng users với password mới và updated_at. Ghi audit log cho thay đổi password. **AC**: Password được hash đúng, audit log ghi nhận, session hiện tại vẫn valid. | 🔧 BE | 🔴 | 1h | ⏳ |
| AUTH-007-FE-01 | **UI Form đổi mật khẩu**: Tạo component ChangePasswordForm trong trang Settings/Profile. 3 input fields: mật khẩu hiện tại, mật khẩu mới, xác nhận mật khẩu mới. Toggle show/hide password cho từng field. Password strength indicator realtime. Disable submit khi validation chưa pass. Success message và optional logout/stay. **AC**: UI responsive, validation hiển thị inline, thông báo thành công rõ ràng. | 🎨 FE | 🟡 | 2h | ⏳ |
| AUTH-007-FE-02 | **Validation client-side**: Implement validation rules: min 8 ký tự, match với confirm password, strength check (regex chữ hoa/thường/số). Hiển thị lỗi inline dưới mỗi field khi blur. Debounce validation 300ms khi typing. Disable submit button khi có lỗi. **AC**: Validation ngay khi nhập, không cho submit khi có lỗi, error messages rõ ràng. | 🎨 FE | 🟡 | 1h | ⏳ |
| AUTH-007-QA-01 | **Test cases change password**: Test mật khẩu cũ sai không đổi được. Test mật khẩu mới < 8 ký tự fail. Test mật khẩu không có số fail. Test confirm password không khớp fail. Test đổi thành công có thể login với password mới. Test user chưa đăng nhập không truy cập được API. **AC**: Tất cả test cases pass, security requirements đáp ứng. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-AUTH-008: Xác thực OTP (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| AUTH-008-BE-01 | **API POST `/auth/send-otp`**: Generate mã OTP 6 chữ số ngẫu nhiên (crypto-safe). Lưu OTP vào bảng otp_codes với expires_at = now + 5 phút. Rate limiting: max 3 lần/phút, max 10 lần/giờ per user. Trigger gửi OTP qua email hoặc SMS tùy config. Response thành công không tiết lộ OTP. **AC**: OTP được gửi trong 30s, rate limit hoạt động, OTP hết hạn sau 5 phút. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-008-BE-02 | **API POST `/auth/verify-otp`**: Nhận user_id và otp_code từ body. Query OTP chưa verified và còn hạn từ DB. So sánh OTP (constant-time comparison để tránh timing attack). Nếu đúng, set verified=true. Max 5 lần thử sai sẽ block OTP đó. Trả JWT token nếu verify thành công. **AC**: OTP đúng trả token, OTP sai 5 lần block, OTP hết hạn trả lỗi. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-008-BE-03 | **Tạo bảng `otp_codes`**: Schema gồm: id (UUID PK), user_id (FK), otp_code (varchar 6), purpose (enum: login/verify_phone/verify_email), expires_at (timestamp), verified (boolean default false), attempts (int default 0), created_at. Index trên (user_id, purpose, verified). Alembic migration. **AC**: Migration thành công, có thể rollback, indexes hoạt động. | 🔧 BE | 🔴 | 1h | ⏳ |
| AUTH-008-BE-04 | **Service gửi OTP**: Tích hợp email service (SendGrid/SMTP) và SMS service (Twilio/Nexmo). Template message: "Mã xác thực của bạn là: {OTP}. Mã có hiệu lực trong 5 phút." Fallback từ SMS sang email nếu SMS fail. Ghi log delivery status. **AC**: OTP gửi được qua cả email và SMS, có fallback, có log. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-008-FE-01 | **UI nhập OTP**: Tạo component OTPInput với 6 ô input riêng biệt. Auto-focus ô tiếp theo khi nhập. Hỗ trợ paste toàn bộ OTP. Auto-submit khi nhập đủ 6 số. Validation chỉ cho phép số (0-9). Visual feedback khi OTP đúng/sai. Responsive cho mobile. **AC**: UX mượt mà, auto-focus hoạt động, paste 6 số được. | 🎨 FE | 🟡 | 2h | ⏳ |
| AUTH-008-FE-02 | **Timer countdown + Resend**: Hiển thị countdown từ 60s. Disable nút "Gửi lại mã" trong thời gian countdown. Khi hết thời gian, enable nút resend. Click resend gọi API send-otp và reset countdown. Hiển thị số lần gửi lại còn lại. **AC**: Countdown chính xác, resend hoạt động, giới hạn số lần hiển thị rõ. | 🎨 FE | 🟡 | 1h | ⏳ |
| AUTH-008-QA-01 | **Test OTP flow**: Test OTP hết hạn sau 5 phút không verify được. Test OTP sai 5 lần bị block. Test OTP đúng verify thành công và nhận token. Test rate limiting khi gửi OTP quá nhiều. Test chỉ số được chấp nhận. Test paste OTP hoạt động. **AC**: Tất cả test cases pass, security edge cases được cover. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-AUTH-009: Đăng ký Producer (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| AUTH-009-BE-01 | **API POST `/auth/register-producer`**: Nhận thông tin đăng ký producer: email, password, phone, business_name, tax_code, address, region_id. Validate format và unique constraints. Tạo user với role=PENDING_PRODUCER. Tạo record trong bảng producer_profiles. Response trả user_id và thông báo chờ duyệt. **AC**: User được tạo với status PENDING, không thể login cho đến khi được approve. | 🔧 BE | 🔴 | 3h | ⏳ |
| AUTH-009-BE-02 | **Schema thông tin kinh doanh**: Thiết kế bảng producer_profiles với các cột: id, user_id (FK), business_name (varchar 200), tax_code (varchar 20 unique), business_address (text), region_id (FK), business_license_url (varchar), status (enum: pending/approved/rejected), approved_by (FK nullable), approved_at, rejection_reason, created_at. Alembic migration. **AC**: Schema đầy đủ, migration chạy thành công. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-009-BE-03 | **Upload giấy phép kinh doanh**: API POST `/auth/register-producer/upload-license`. Accept PDF và image files (jpg, png). Max size 10MB. Validate file extension và MIME type. Lưu file lên cloud storage (S3/GCS). Trả về URL để lưu vào producer_profiles. Scan virus nếu có integrate. **AC**: Upload thành công, file được lưu đúng thư mục, URL accessible. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-009-BE-04 | **Notification cho Admin**: Khi đăng ký producer mới, gửi notification tới tất cả admin users. Notification chứa: tên business, thời gian đăng ký, link tới trang approve. Gửi qua cả in-app notification và email. **AC**: Admin nhận được notification, link dẫn đúng trang. | 🔧 BE | 🟡 | 1h | ⏳ |
| AUTH-009-BE-05 | **API PUT `/admin/producers/{id}/approve`**: Endpoint dành cho Admin. Action types: approve hoặc reject. Nếu approve: update status=APPROVED, approved_by, approved_at, gán role PRODUCER cho user. Nếu reject: update status=REJECTED, rejection_reason (required). Gửi email thông báo kết quả cho producer. **AC**: Approve/reject thành công, user nhận email, role được cập nhật khi approve. | 🔧 BE | 🔴 | 2h | ⏳ |
| AUTH-009-FE-01 | **UI Form đăng ký Producer multi-step**: Step 1: Thông tin tài khoản (email, password, phone). Step 2: Thông tin kinh doanh (business_name, tax_code, address, region). Step 3: Upload giấy phép + review và submit. Progress indicator. Lưu draft vào localStorage. Validation từng step. **AC**: Multi-step hoạt động mượt, có thể quay lại sửa, draft được lưu. | 🎨 FE | 🟡 | 4h | ⏳ |
| AUTH-009-FE-02 | **Upload component giấy phép**: Drag-drop zone hoặc click để chọn file. Preview file (hình ảnh hoặc PDF icon). Progress bar khi upload. Validate client-side: max 10MB, chỉ PDF/JPG/PNG. Nút xóa để chọn lại. Error message rõ ràng khi fail. **AC**: Upload mượt, preview đúng, validation hoạt động. | 🎨 FE | 🟡 | 2h | ⏳ |
| AUTH-009-FE-03 | **UI Admin duyệt Producer**: Trang /admin/producers với DataTable: columns: business_name, tax_code, submitted_at, status. Filter theo status. Click row mở modal chi tiết với thông tin đầy đủ và preview giấy phép. Buttons Approve (confirm) và Reject (yêu cầu nhập lý do). Toast notification khi action thành công. **AC**: List load nhanh, filter hoạt động, approve/reject thành công cập nhật list. | 🎨 FE | 🟡 | 3h | ⏳ |
| AUTH-009-QA-01 | **Test producer registration flow**: Test đăng ký với data valid thành công. Test tax_code trùng bị reject. Test upload file > 10MB fail. Test upload file sai format fail. Test admin approve thì producer có thể login. Test admin reject thì producer nhận email có lý do. Test multi-step navigation và draft save. **AC**: Tất cả test cases pass, end-to-end flow hoạt động. | 🧪 QA | 🟢 | 3h | ⏳ |

---

## US-USER-007: Upload Avatar (3 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| USER-007-BE-01 | **API POST `/users/avatar`**: Endpoint yêu cầu authentication. Accept multipart/form-data với field "avatar". Validate: chỉ JPEG, PNG, WebP; max size 5MB; min resolution 100x100. Generate unique filename với UUID. Upload gốc lên cloud storage. Cập nhật avatar_url trong bảng users. Xóa avatar cũ nếu có. Response trả URL mới. **AC**: Upload thành công, avatar cũ được xóa, URL accessible. | 🔧 BE | 🟡 | 2h | ⏳ |
| USER-007-BE-02 | **Crop và resize image server-side**: Sử dụng Pillow hoặc sharp. Tạo 3 sizes: original (max 1024x1024), medium (300x300), thumbnail (150x150). Crop center square nếu không vuông. Optimize quality (85% JPEG). Lưu tất cả sizes lên storage với naming convention: {user_id}/{size}_{filename}. Response trả object với URLs của cả 3 sizes. **AC**: 3 sizes được tạo đúng, quality tốt, file size hợp lý. | 🔧 BE | 🟡 | 2h | ⏳ |
| USER-007-FE-01 | **UI Upload avatar với crop tool**: Tích hợp thư viện react-cropper hoặc tương đương. Click avatar mở file picker. Sau khi chọn file, mở modal crop với fixed aspect ratio 1:1. Zoom in/out slider. Rotate buttons (90°). Preview real-time. Buttons Cancel và Upload. Loading state khi uploading. **AC**: Crop hoạt động mượt, preview đúng, upload thành công cập nhật avatar ngay. | 🎨 FE | 🟡 | 3h | ⏳ |
| USER-007-FE-02 | **Preview avatar trước upload**: Hiển thị preview ngay sau khi crop, trước khi submit. So sánh avatar hiện tại và avatar mới side-by-side. Nút "Xác nhận thay đổi" và "Chọn ảnh khác". Skeleton loading khi fetch avatar hiện tại. Fallback placeholder nếu chưa có avatar. **AC**: Preview rõ ràng, user có thể so sánh trước khi submit. | 🎨 FE | 🟢 | 1h | ⏳ |
| USER-007-QA-01 | **Test avatar upload flow**: Test upload JPEG, PNG, WebP thành công. Test upload file > 5MB fail với error message rõ. Test upload file không phải image (txt, pdf) fail. Test crop hoạt động đúng tỉ lệ. Test avatar cũ bị thay thế. Test user chưa đăng nhập không upload được. Test thumbnail hiển thị đúng ở các vị trí trong app. **AC**: Tất cả test cases pass, UX hoàn chỉnh. | 🧪 QA | 🟢 | 1h | ⏳ |

---

# 🏃 SPRINT 9 - Mobile Shopping Enhancement

**Sprint Goal**: Nâng cao trải nghiệm mua sắm mobile  
**Total Story Points**: 34 SP

---

## US-CART-001: Giỏ hàng (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| CART-001-BE-01 | **API CRUD `/cart`**: GET `/cart` - trả danh sách cart items với product info, prices, subtotal. POST `/cart/items` - thêm sản phẩm (product_id, quantity). PUT `/cart/items/{id}` - update quantity. DELETE `/cart/items/{id}` - xóa item. Tất cả require auth. Response include tổng giá trị giỏ hàng. **AC**: CRUD hoạt động đúng, prices cập nhật realtime, auth required. | 🔧 BE | 🔴 | 4h | ⏳ |
| CART-001-BE-02 | **Tạo bảng `carts` và `cart_items`**: Bảng carts: id (UUID PK), user_id (FK unique), created_at, updated_at. Bảng cart_items: id, cart_id (FK), product_id (FK), quantity (int positive), added_at. Composite unique constraint (cart_id, product_id). Alembic migration với indexes. **AC**: Migration thành công, constraints hoạt động, không cho duplicate product. | 🔧 BE | 🔴 | 1h | ⏳ |
| CART-001-BE-03 | **Validate product availability**: Khi add/update cart item, check product exists và status=ACTIVE. Check quantity <= stock available. Check product còn trong thời gian bán. Trả lỗi 422 với message rõ ràng nếu violate. Khi GET cart, flag items có product đã inactive hoặc hết stock. **AC**: Không cho add/update product inactive, quantity vượt stock trả lỗi rõ. | 🔧 BE | 🔴 | 2h | ⏳ |
| CART-001-FE-01 | **UI Cart page mobile**: FlatList hiển thị cart items với: product image, name, unit price, quantity selector, item subtotal, nút xóa. Sticky footer với: tổng số items, tổng tiền, nút Checkout. Pull-to-refresh để sync. Empty state với CTA "Khám phá sản phẩm". **AC**: UI responsive, scroll mượt, empty state hiển thị đúng. | 🎨 FE | 🟡 | 3h | ⏳ |
| CART-001-FE-02 | **Update quantity controls**: Buttons +/- để tăng giảm số lượng. Input có thể nhập trực tiếp số. Debounce 500ms trước khi gọi API. Optimistic update UI trước khi API response. Rollback nếu API fail. Disable nút - khi quantity=1 (không cho 0, phải delete). Max quantity = stock available. **AC**: Update mượt, không spam API, rollback đúng khi fail. | 🎨 FE | 🟡 | 2h | ⏳ |
| CART-001-FE-03 | **LocalStorage fallback guest users**: Lưu cart vào AsyncStorage khi chưa đăng nhập. Schema: array of {product_id, quantity}. Khi user đăng nhập, merge local cart với server cart (additive). Xóa local cart sau khi merge thành công. Max 50 items trong local cart. **AC**: Guest có thể add to cart, login merge được, không mất cart khi đóng app. | 🎨 FE | 🟡 | 2h | ⏳ |
| CART-001-FE-04 | **Cart badge counter**: Hiển thị số lượng items trong cart trên header icon. Badge màu đỏ, số trắng. Update realtime khi add/remove. Ẩn badge khi cart empty. Số max hiển thị là 99+. Sync với server mỗi khi app focus. **AC**: Badge hiển thị đúng số, update ngay khi thay đổi, 99+ khi vượt. | 🎨 FE | 🟢 | 1h | ⏳ |
| CART-001-QA-01 | **Test cart operations**: Test thêm sản phẩm mới vào cart. Test thêm sản phẩm đã có tăng quantity. Test giảm quantity về 1 không cho giảm thêm. Test xóa item. Test add product inactive fail. Test add quantity > stock fail. Test sync cart sau login. Test badge counter chính xác. **AC**: Tất cả test cases pass, edge cases được handle. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-WISH-001: Yêu thích (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| WISH-001-BE-01 | **API endpoints `/wishlist`**: GET `/wishlist` - trả danh sách sản phẩm yêu thích với full product info, pagination (limit 20). POST `/wishlist` - thêm product_id mới, check duplicate trả success nếu đã có. DELETE `/wishlist/{product_id}` - xóa khỏi wishlist. Tất cả require authentication. Include total count trong response. **AC**: CRUD hoạt động, không duplicate, pagination chính xác. | 🔧 BE | 🔴 | 2h | ⏳ |
| WISH-001-BE-02 | **Tạo bảng `wishlists`**: Schema: id (UUID PK), user_id (FK), product_id (FK), created_at. Composite unique constraint (user_id, product_id) để không duplicate. Index trên user_id để query nhanh. Alembic migration. Cascade delete khi product bị xóa. **AC**: Migration thành công, unique constraint hoạt động, cascade delete đúng. | 🔧 BE | 🔴 | 1h | ⏳ |
| WISH-001-FE-01 | **UI Wishlist page mobile**: FlatList hiển thị sản phẩm yêu thích với: product image, name, price, rating, nút xóa, nút thêm vào giỏ. Pull-to-refresh. Infinite scroll pagination. Empty state với CTA khám phá. Swipe left để xóa (iOS style). **AC**: UI responsive, pagination hoạt động, empty state hiển thị đúng. | 🎨 FE | 🟡 | 2h | ⏳ |
| WISH-001-FE-02 | **Heart icon toggle trên product card**: Icon trái tim trên mỗi product card. Filled = đã yêu thích, outline = chưa. Click toggle state và gọi API. Animation scale khi toggle. Optimistic update, rollback nếu fail. Hiển thị toast khi add/remove thành công. **AC**: Toggle mượt, animation đẹp, sync với server đúng. | 🎨 FE | 🟡 | 1h | ⏳ |
| WISH-001-FE-03 | **Move to cart từ wishlist**: Nút "Thêm vào giỏ" trên mỗi item trong wishlist. Click mở bottom sheet chọn quantity (default 1). Confirm thêm vào cart và tùy chọn xóa khỏi wishlist. Toast success với action "Xem giỏ hàng". **AC**: Add to cart hoạt động, tùy chọn remove from wishlist, navigation đúng. | 🎨 FE | 🟡 | 1h | ⏳ |
| WISH-001-QA-01 | **Test wishlist operations**: Test add sản phẩm mới vào wishlist. Test add sản phẩm đã có không duplicate. Test remove sản phẩm. Test move to cart. Test pagination load more. Test heart icon sync đúng trạng thái. Test user chưa login không access được. **AC**: Tất cả test cases pass, data consistent. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-REV-002: Đánh giá sản phẩm (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| REV-002-BE-01 | **API POST `/reviews`**: Nhận product_id, rating (1-5), comment (max 1000 chars), image_urls (optional array). Validate user đã mua và nhận sản phẩm (order status=DELIVERED). Mỗi user chỉ review 1 lần/product. Tính lại average rating của product sau khi tạo review. Response trả review object đầy đủ. **AC**: Review được tạo, avg rating cập nhật, duplicate review bị reject. | 🔧 BE | 🔴 | 2h | ⏳ |
| REV-002-BE-02 | **Validate user đã mua sản phẩm**: Query bảng orders và order_items để check user_id có order với product_id và status=DELIVERED. Thời gian review: chỉ được review trong 30 ngày sau khi nhận hàng. Trả lỗi 403 nếu chưa mua hoặc quá thời hạn review. **AC**: User chưa mua không review được, quá 30 ngày không review được, message rõ ràng. | 🔧 BE | 🔴 | 1h | ⏳ |
| REV-002-BE-03 | **Upload review images**: API POST `/reviews/upload-images` - accept array tối đa 5 images. Validate: JPEG/PNG, max 5MB/image. Resize xuống max 1200x1200 giữ ratio. Upload lên cloud storage. Response trả array URLs để submit cùng review. Images tự động xóa sau 24h nếu review không được submit. **AC**: Upload 5 ảnh thành công, resize đúng, cleanup hoạt động. | 🔧 BE | 🟡 | 2h | ⏳ |
| REV-002-FE-01 | **UI Form đánh giá**: Modal/screen với star rating (5 sao tap để chọn). Textarea cho comment với character counter. Grid hiển thị ảnh đã upload. Nút "Gửi đánh giá" disabled khi chưa chọn sao. Loading state khi submit. Success animation và tự đóng modal. **AC**: UI đẹp, validation hoạt động, UX mượt. | 🎨 FE | 🟡 | 2h | ⏳ |
| REV-002-FE-02 | **Upload ảnh review**: Nút "Thêm ảnh" mở image picker (camera hoặc gallery). Preview ảnh đã chọn trong grid. Nút X để xóa từng ảnh. Max 5 ảnh, disable nút add khi đủ. Progress bar cho từng ảnh khi upload. Compress ảnh client-side trước upload. **AC**: Upload mượt, có progress, preview đúng, max 5 ảnh. | 🎨 FE | 🟡 | 2h | ⏳ |
| REV-002-FE-03 | **Hiển thị reviews trên product detail**: Section Reviews với: average rating lớn + số reviews. List reviews với: avatar, tên, ngày, rating stars, comment, ảnh (grid clickable mở fullscreen). Pagination load more. Sort by: newest, highest, lowest rating. **AC**: Reviews load nhanh, ảnh mở fullscreen, sort hoạt động. | 🎨 FE | 🟡 | 2h | ⏳ |
| REV-002-QA-01 | **Test review flow**: Test tạo review với rating, comment, ảnh. Test user chưa mua không review được. Test user đã review không review lại được. Test upload > 5 ảnh fail. Test rating 1-5 valid, 0 hoặc 6 invalid. Test average rating cập nhật đúng. Test hiển thị reviews trên product detail. **AC**: Tất cả test cases pass, business rules đúng. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-NOTI-001: Push Notification (13 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| NOTI-001-BE-01 | **Tích hợp Firebase Cloud Messaging**: Cài đặt firebase-admin SDK. Tạo Firebase project và lấy service account key. Implement FirebaseService với methods: sendToDevice(token, payload), sendToMultiple(tokens, payload), sendToTopic(topic, payload). Handle FCM errors (invalid token, expired token). Logging cho mỗi notification gửi. **AC**: SDK hoạt động, gửi notification thành công, logging đầy đủ. | 🔧 BE | 🔴 | 4h | ⏳ |
| NOTI-001-BE-02 | **API endpoint lưu FCM token**: POST `/notifications/register-device` - nhận device_token, platform (ios/android/web), device_info. Lưu vào bảng device_tokens. Update token nếu device đã tồn tại (unique: user_id + platform). DELETE `/notifications/unregister-device` - xóa token khi logout. **AC**: Token được lưu/update đúng, logout xóa token. | 🔧 BE | 🔴 | 1h | ⏳ |
| NOTI-001-BE-03 | **Service gửi push notification**: Implement NotificationService với: sendToUser(user_id, type, data), sendToRole(role, type, data), sendBulk(user_ids, type, data). Queue notifications với background worker (Celery/RQ). Retry logic 3 lần với exponential backoff. Template system cho notification content. **AC**: Notifications queued và gửi đúng, retry hoạt động, templates flexible. | 🔧 BE | 🔴 | 3h | ⏳ |
| NOTI-001-BE-04 | **Trigger notifications cho order events**: Tạo event handlers cho: ORDER_CREATED (gửi seller), ORDER_CONFIRMED, ORDER_SHIPPED, ORDER_DELIVERED (gửi buyer). Notification payload gồm: title, body, data (order_id, action_url). Integrate vào order status update flow. **AC**: Buyer/seller nhận notification đúng lúc, data đủ để navigate. | 🔧 BE | 🔴 | 2h | ⏳ |
| NOTI-001-BE-05 | **Tạo bảng `notifications` và `device_tokens`**: Bảng notifications: id, user_id, type (enum), title, body, data (JSONB), read (boolean), created_at. Bảng device_tokens: id, user_id, token, platform (enum), device_info, created_at, updated_at. Indexes cho query performance. Alembic migrations. **AC**: Migrations thành công, queries nhanh với indexes. | 🔧 BE | 🔴 | 1h | ⏳ |
| NOTI-001-FE-01 | **Setup FCM cho React Native**: Cài đặt @react-native-firebase/messaging. Configure cho cả iOS (APNs) và Android. Request notification permission khi first launch hoặc khi cần. Get FCM token và gọi API register. Handle token refresh event. Background và foreground notification handling. **AC**: FCM hoạt động cả iOS/Android, token được register. | 🎨 FE | 🔴 | 3h | ⏳ |
| NOTI-001-FE-02 | **Request notification permission**: Hiển thị dialog giải thích lý do cần notification trước khi request. Handle cả 3 states: granted, denied, not_determined. Nếu denied, guide user mở Settings. Lưu permission state vào AsyncStorage. Không request lại nếu đã denied. **AC**: Permission flow đúng, không spam request, guide to settings khi denied. | 🎨 FE | 🟡 | 1h | ⏳ |
| NOTI-001-FE-03 | **Handle notification tap (deep linking)**: Parse notification data khi user tap. Navigate tới đúng screen dựa trên action_url hoặc type. Handle cả khi app killed, background, foreground. Implement linking config cho React Navigation. Test tất cả scenarios. **AC**: Tap notification mở đúng screen, hoạt động mọi app states. | 🎨 FE | 🟡 | 2h | ⏳ |
| NOTI-001-QA-01 | **Test push notification flow**: Test FCM token registration thành công. Test nhận notification foreground (in-app banner). Test nhận notification background (system tray). Test tap notification navigate đúng. Test order status changes trigger notification. Test logout xóa token. Test multiple devices same user. **AC**: Tất cả test cases pass, đáng tin cậy. | 🧪 QA | 🟢 | 3h | ⏳ |

---

## US-NOTI-002: Lịch sử thông báo (3 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| NOTI-002-BE-01 | **API GET/PUT notifications**: GET `/notifications` - trả list notifications của user, pagination (limit 20), sort by created_at desc, include unread_count. Filter by type, read status. PUT `/notifications/{id}/read` - đánh dấu đã đọc, update read=true và read_at. PUT `/notifications/read-all` - đánh dấu tất cả đã đọc. **AC**: List có pagination, filter hoạt động, mark read update đúng. | 🔧 BE | 🟡 | 2h | ⏳ |
| NOTI-002-FE-01 | **UI Notification list page**: FlatList hiển thị notifications với: icon theo type, title, body (truncate), time ago (2 phút trước, hôm qua, ...). Visual indicator cho unread (background color hoặc dot). Pull-to-refresh. Infinite scroll pagination. Click item navigate + mark as read. Empty state. **AC**: UI rõ ràng, unread hiển thị khác biệt, navigation đúng. | 🎨 FE | 🟡 | 2h | ⏳ |
| NOTI-002-FE-02 | **Unread badge counter**: Bell icon trên header với badge số unread. Badge màu đỏ, số trắng. Realtime update khi nhận notification mới (qua FCM). Click bell vào notification list. Badge ẩn khi count = 0. Số max 99+. **AC**: Badge chính xác, update khi có notification mới và khi đọc. | 🎨 FE | 🟡 | 1h | ⏳ |
| NOTI-002-QA-01 | **Test notification list**: Test list load với pagination. Test filter by type. Test mark single as read. Test mark all as read. Test unread count update. Test badge counter sync. Test empty state hiển thị. Test time ago format chính xác. **AC**: Tất cả test cases pass, UX mượt. | 🧪 QA | 🟢 | 1h | ⏳ |

---

# 🏃 SPRINT 10 - Order & Delivery Tracking

**Sprint Goal**: Theo dõi đơn hàng và vận chuyển  
**Total Story Points**: 29 SP

---

## US-ORD-005: Tracking vận chuyển (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| ORD-005-BE-01 | **API GET `/orders/{id}/tracking`**: Trả về tracking info của order gồm: shipping_code, carrier_name, current_status, estimated_delivery, tracking_history (array events). Query từ bảng order_tracking_history. Cache response 5 phút. Include link tracking của carrier. **AC**: Tracking data đầy đủ, cache hoạt động, có link external. | 🔧 BE | 🟡 | 2h | ⏳ |
| ORD-005-BE-02 | **Tạo bảng `order_tracking_history`**: Schema: id, order_id (FK), status (enum), location (varchar), description (text), event_time (timestamp), created_at. Index trên order_id. Trigger insert khi order status change. Store cả internal events và carrier events. **AC**: Migration thành công, history lưu đúng chronological order. | 🔧 BE | 🟡 | 1h | ⏳ |
| ORD-005-BE-03 | **Integration đơn vị vận chuyển**: Tích hợp API của GHN và GHTK. Implement CarrierService interface với: createShipment(), getTracking(), calculateFee(). Webhook endpoint nhận tracking updates từ carriers. Parse và normalize response format. Retry logic nếu API fail. **AC**: Cả 2 carriers hoạt động, webhook nhận events, tracking sync đúng. | 🔧 BE | 🟡 | 4h | ⏳ |
| ORD-005-FE-01 | **UI Order tracking timeline**: Vertical timeline hiển thị tracking events. Mỗi event: icon theo status, title, description, datetime. Current status highlight với màu khác. Stepper cho các stages chính: Đang xử lý → Đang giao → Đã giao. Pull-to-refresh. **AC**: Timeline đẹp, dễ đọc, current status rõ ràng. | 🎨 FE | 🟡 | 3h | ⏳ |
| ORD-005-FE-02 | **Map hiển thị vị trí shipper**: Tích hợp Google Maps/Mapbox. Hiển thị polyline route từ origin đến destination. Marker cho current location của shipper (nếu carrier cung cấp). Realtime update nếu có (polling 30s). Fallback hiển thị static map nếu không có realtime. **AC**: Map load nhanh, hiển thị route, realtime nếu available. | 🎨 FE | 🟢 | 3h | ⏳ |
| ORD-005-QA-01 | **Test order tracking**: Test tracking timeline hiển thị đúng chronological. Test integration GHN trả data đúng. Test integration GHTK trả data đúng. Test webhook update tracking. Test map hiển thị route. Test cache hoạt động. **AC**: Tất cả test cases pass, data accurate. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-ORD-006: Hủy đơn hàng (3 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| ORD-006-BE-01 | **API PUT `/orders/{id}/cancel`**: Nhận reason (required) từ body. Validate order status phải là PENDING hoặc CONFIRMED (chưa ship). Update status = CANCELLED, cancelled_at, cancellation_reason, cancelled_by. Gửi notification cho seller. Return order object updated. **AC**: Cancel thành công với status hợp lệ, seller nhận notification. | 🔧 BE | 🔴 | 2h | ⏳ |
| ORD-006-BE-02 | **Validate order status**: Check order.status in [PENDING, CONFIRMED]. Trả lỗi 400 với message rõ nếu order đang SHIPPED hoặc DELIVERED. Check order thuộc về user đang request. Seller cũng có thể cancel nếu cung cấp được lý do hợp lệ. **AC**: Validation chính xác, error messages rõ ràng theo từng case. | 🔧 BE | 🔴 | 1h | ⏳ |
| ORD-006-BE-03 | **Trigger refund nếu đã thanh toán**: Check payment_status của order. Nếu PAID, tạo refund request và update payment.refund_status = PENDING. Gọi payment gateway refund API (async). Gửi email xác nhận refund cho buyer. **AC**: Refund được trigger khi đã thanh toán, buyer nhận email. | 🔧 BE | 🔴 | 1h | ⏳ |
| ORD-006-FE-01 | **UI Cancel order dialog**: Button "Hủy đơn" trên order detail (chỉ hiện khi status hợp lệ). Click mở dialog với dropdown chọn lý do (Đổi ý, Đặt nhầm, Tìm được giá tốt hơn, Khác) + textarea chi tiết. Confirm button với warning về refund policy. Loading state và success/error toast. **AC**: UI rõ ràng, validation reason, feedback đầy đủ. | 🎨 FE | 🟡 | 1h | ⏳ |
| ORD-006-QA-01 | **Test cancel order flow**: Test cancel order PENDING thành công. Test cancel order CONFIRMED thành công. Test cancel order SHIPPED fail với message. Test cancel order đã thanh toán trigger refund. Test seller nhận notification. Test reason required. **AC**: Tất cả test cases pass, business rules đúng. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-ORD-007: Xác nhận nhận hàng (2 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| ORD-007-BE-01 | **API PUT `/orders/{id}/confirm-received`**: Validate order status = SHIPPED. Update status = DELIVERED, delivered_at = now(). Gửi notification cho seller về delivery confirmation. Return updated order. Buyer chỉ confirm được order của mình. **AC**: Confirm thành công, seller nhận notification, timestamps đúng. | 🔧 BE | 🔴 | 1h | ⏳ |
| ORD-007-BE-02 | **Trigger payment to seller**: Khi order DELIVERED, calculate seller payout = order_total - platform_fee. Create record trong bảng seller_payouts với status = PENDING. Schedule payout (T+3 days để allow disputes). Update payout status = COMPLETED sau khi transfer. **AC**: Payout calculated đúng, scheduled correctly, status updates. | 🔧 BE | 🔴 | 1h | ⏳ |
| ORD-007-FE-01 | **UI Confirm received button**: Button "Đã nhận hàng" trên order detail khi status = SHIPPED. Click mở confirm dialog với message thông báo về việc xác nhận và đánh giá. Sau confirm, navigate về order detail với status mới và hiện prompt đánh giá. **AC**: Button hiển thị đúng lúc, dialog rõ ràng, prompt review sau confirm. | 🎨 FE | 🟡 | 1h | ⏳ |
| ORD-007-QA-01 | **Test confirm received flow**: Test confirm order SHIPPED thành công. Test confirm order không phải SHIPPED fail. Test seller nhận notification. Test seller payout được tạo. Test prompt review hiển thị. Test user khác không confirm được order. **AC**: Tất cả test cases pass, security đúng. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-SELL-001: Dashboard Seller (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SELL-001-BE-01 | **API GET `/seller/dashboard/stats`**: Trả về thống kê tổng quan cho seller: total_products, total_orders, total_revenue (lifetime), pending_orders, average_rating. Query với scope = current seller. Cache 15 phút, invalidate khi có order mới. Include so sánh với tháng trước (%). **AC**: Stats chính xác, cache hoạt động, comparison tính đúng. | 🔧 BE | 🟡 | 3h | ⏳ |
| SELL-001-BE-02 | **API GET `/seller/dashboard/revenue`**: Trả time series data cho chart: date, revenue, order_count. Query params: period (daily/weekly/monthly), from_date, to_date. Group by date/week/month tùy period. Support compare với period trước đó. Max range 1 năm. **AC**: Data đúng theo period, compare hoạt động, performance tốt. | 🔧 BE | 🟡 | 2h | ⏳ |
| SELL-001-BE-03 | **API GET `/seller/orders/recent`**: Trả 10 orders mới nhất của seller với basic info: order_code, buyer_name, total, status, created_at. Sort by created_at desc. Cache 5 phút. Include link tới order detail. **AC**: List đúng 10 orders mới nhất của seller, cache hoạt động. | 🔧 BE | 🟡 | 1h | ⏳ |
| SELL-001-FE-01 | **UI Seller Dashboard page**: Layout cards cho stats (số + % change). Section recent orders với mini table. Section revenue chart. Pull-to-refresh toàn page. Skeleton loading khi fetch. Quick actions: Add product, View orders, View reviews. **AC**: Layout clear, data load nhanh, quick actions hoạt động. | 🎨 FE | 🟡 | 4h | ⏳ |
| SELL-001-FE-02 | **Charts revenue và orders**: Line chart cho revenue trend. Bar chart cho order count. Period selector (7 days, 30 days, 90 days, 1 year). Toggle show/hide compare line. Tooltip hiển thị value khi hover/touch. Responsive cho mobile. **AC**: Charts render đẹp, period switch mượt, tooltip hoạt động. | 🎨 FE | 🟡 | 3h | ⏳ |
| SELL-001-QA-01 | **Test seller dashboard**: Test stats hiển thị đúng. Test revenue chart load đúng period. Test compare với period trước đúng. Test recent orders đúng 10 items. Test cache invalidation khi có order mới. Test quick actions navigate đúng. **AC**: Tất cả test cases pass, data accurate. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-SELL-002: Quản lý SP Mobile (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SELL-002-BE-01 | **API `/seller/products`**: GET với scope = current seller only, không cần admin role. Reuse existing product service với filtered query. POST tạo product mới với seller_id = current user. PUT/DELETE chỉ cho products của seller. Status mặc định = PENDING_APPROVAL. **AC**: CRUD scoped đúng seller, không access được product của seller khác. | 🔧 BE | 🔴 | 2h | ⏳ |
| SELL-002-FE-01 | **UI List products của seller**: FlatList với product cards: image, name, price, stock, status badge. Pull-to-refresh. Search bar filter by name. Tabs filter by status (All, Pending, Approved, Rejected). Empty state với CTA add product. Swipe actions (Edit, Delete). **AC**: List load nhanh, filter hoạt động, swipe mượt. | 🎨 FE | 🔴 | 3h | ⏳ |
| SELL-002-FE-02 | **UI Add/Edit product form mobile**: Form với các fields: name, description (rich text lite), price, stock, category (picker), unit. Form validation với error messages. Save draft to local. Submit gọi API. Edit mode load existing data. **AC**: Form đầy đủ fields, validation hoạt động, draft save được. | 🎨 FE | 🔴 | 4h | ⏳ |
| SELL-002-FE-03 | **Product image upload multi**: Image picker cho max 10 ảnh. Drag to reorder (first image = thumbnail). Progress bar per image khi upload. Preview grid với nút X để xóa. Compress trước upload. Retry failed uploads. **AC**: Upload multiple thành công, reorder hoạt động, retry hoạt động. | 🎨 FE | 🟡 | 2h | ⏳ |
| SELL-002-FE-04 | **Status badge component**: Badge với màu theo status: PENDING (vàng), APPROVED (xanh), REJECTED (đỏ). Tooltip/popover giải thích status khi tap. Rejected có link xem rejection reason. Icon indicator phù hợp. **AC**: Màu đúng, tooltip rõ ràng, rejection reason accessible. | 🎨 FE | 🟡 | 1h | ⏳ |
| SELL-002-QA-01 | **Test seller product management**: Test list chỉ hiện products của seller. Test add product mới status = PENDING. Test edit product thành công. Test delete product thành công. Test upload multiple images. Test status filter. Test search. **AC**: Tất cả test cases pass, scope security đúng. | 🧪 QA | 🟢 | 2h | ⏳ |

---

# 🏃 SPRINT 11 - Promotions System

**Sprint Goal**: Hệ thống khuyến mãi  
**Total Story Points**: 29 SP

---

## US-PROMO-001: Tạo Voucher (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| PROMO-001-BE-01 | **Tạo bảng `vouchers`**: Schema: id (UUID PK), code (varchar unique), type (enum: percentage/fixed), value (decimal), min_order_value (decimal), max_discount (decimal, cho % voucher), usage_limit (int), used_count (int default 0), start_date, end_date, status (active/inactive), created_by (FK), created_at. Indexes cho code, status, dates. **AC**: Migration thành công, constraints hoạt động. | 🔧 BE | 🟡 | 1h | ⏳ |
| PROMO-001-BE-02 | **API CRUD `/admin/vouchers`**: GET list với filter (status, type, date range), pagination, search by code. POST tạo voucher mới với validation (code unique, dates logic, value > 0). PUT update voucher (chỉ khi used_count = 0). DELETE soft delete. Generate random code nếu không cung cấp. **AC**: CRUD hoạt động, validations chính xác, search và filter hoạt động. | 🔧 BE | 🟡 | 3h | ⏳ |
| PROMO-001-BE-03 | **Tạo bảng `voucher_usages`**: Schema: id, voucher_id (FK), user_id (FK), order_id (FK), discount_amount, used_at. Composite unique (voucher_id, order_id). Track usage history cho từng voucher. API GET `/admin/vouchers/{id}/usages` trả usage history. **AC**: Table track đúng usages, unique constraint hoạt động, history accessible. | 🔧 BE | 🟡 | 1h | ⏳ |
| PROMO-001-FE-01 | **UI Admin Voucher management page**: DataTable với columns: code, type, value, usage (used/limit), status badge, dates, actions. Filters: type, status. Search by code. Pagination. Row click → detail view. Actions: Edit, Deactivate, Delete. **AC**: List load nhanh, filters hoạt động, actions có confirm dialog. | 🎨 FE | 🟡 | 3h | ⏳ |
| PROMO-001-FE-02 | **Form tạo voucher**: Fields: code (auto-generate option), type radio (% hoặc VNĐ), value, min order value, max discount (chỉ cho %), usage limit, date range picker. Validation: dates phải future, value > 0. Preview discount calculation. **AC**: Form đầy đủ validations, preview chính xác, auto-generate code hoạt động. | 🎨 FE | 🟡 | 2h | ⏳ |
| PROMO-001-QA-01 | **Test voucher management**: Test create voucher % thành công. Test create voucher VNĐ thành công. Test code unique constraint. Test update voucher đã used fail. Test date validation (end > start). Test usage limit enforcement. Test search và filter. **AC**: Tất cả test cases pass, business rules đúng. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-PROMO-002: Áp dụng Voucher (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| PROMO-002-BE-01 | **API POST `/cart/apply-voucher`**: Nhận voucher_code từ body. Query voucher từ DB. Validate và tính discount. Update cart với voucher_id và discount_amount. Trả về cart updated với breakdown giá. API DELETE `/cart/remove-voucher` để xóa voucher đã apply. **AC**: Apply thành công, cart updated đúng, remove hoạt động. | 🔧 BE | 🟡 | 2h | ⏳ |
| PROMO-002-BE-02 | **Validate voucher conditions**: Check: code tồn tại, status = active, within date range, used_count < usage_limit, cart_total >= min_order_value. Check user chưa dùng voucher này (nếu có limit per user). Trả error message rõ ràng cho từng case. **AC**: Tất cả conditions được check, error messages specific cho từng case. | 🔧 BE | 🟡 | 2h | ⏳ |
| PROMO-002-BE-03 | **Calculate discount amount**: Nếu type = percentage: discount = cart_total * value / 100, cap bởi max_discount. Nếu type = fixed: discount = value (nhưng không vượt cart_total). Return calculated discount và final_total. Handle edge cases (empty cart, single item). **AC**: Calculation chính xác cho cả 2 types, edge cases handled. | 🔧 BE | 🟡 | 1h | ⏳ |
| PROMO-002-FE-01 | **UI Input voucher code tại checkout**: Input field + button Apply. Loading state khi checking. Success: hiện tick xanh, applied voucher info. Error: hiện message lý do fail. Nút X để remove voucher đã apply. Persist voucher khi navigate away. **AC**: UX rõ ràng, feedback đầy đủ, persist hoạt động. | 🎨 FE | 🟡 | 1h | ⏳ |
| PROMO-002-FE-02 | **Display discount trong order summary**: Section Order Summary: Subtotal, Shipping, Voucher discount (negative, màu xanh), Total. Animate khi discount applied. Show voucher code và type (%). Clear visual breakdown. **AC**: Summary rõ ràng, discount hiển thị đúng, animation mượt. | 🎨 FE | 🟡 | 1h | ⏳ |
| PROMO-002-QA-01 | **Test apply voucher flow**: Test apply valid voucher thành công. Test voucher expired fail. Test voucher hết lượt fail. Test min order fail. Test % discount tính đúng. Test fixed discount tính đúng. Test remove voucher. Test persist khi navigate. **AC**: Tất cả test cases pass, calculation accurate. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-PROMO-003: Flash Sale (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| PROMO-003-BE-01 | **Tạo bảng `flash_sales`**: Schema: id (UUID PK), product_id (FK unique), sale_price (decimal), original_price (snapshot), stock_quantity (int), sold_quantity (int default 0), start_time (timestamp), end_time (timestamp), status (scheduled/active/ended), created_by, created_at. Indexes cho status, times. **AC**: Migration thành công, unique product constraint hoạt động. | 🔧 BE | 🟢 | 1h | ⏳ |
| PROMO-003-BE-02 | **API CRUD `/admin/flash-sales`**: GET list với filter (status, date range). POST schedule flash sale với validation (times future, sale_price < original, stock > 0). PUT update (chỉ khi status = scheduled). DELETE xóa scheduled. Cron job auto-update status (scheduled → active → ended). **AC**: CRUD hoạt động, status auto-update đúng thời gian. | 🔧 BE | 🟢 | 3h | ⏳ |
| PROMO-003-BE-03 | **API GET `/flash-sales/active`**: Trả list sản phẩm đang flash sale với: product info, sale_price, original_price, discount %, remaining stock, end_time. Sort by end_time asc (sắp hết trước). Public API không cần auth. Cache 1 phút. **AC**: List chính xác sản phẩm active, cache hoạt động, performance tốt. | 🔧 BE | 🟢 | 1h | ⏳ |
| PROMO-003-FE-01 | **UI Admin Flash sale management**: DataTable: product name, original/sale price, discount %, stock, sold, times, status. Actions: Edit (trước khi start), Cancel, View. Form schedule: product picker, sale price, stock, datetime range pickers. **AC**: List rõ ràng, form validation đầy đủ, datetime pickers hoạt động. | 🎨 FE | 🟢 | 2h | ⏳ |
| PROMO-003-FE-02 | **UI Flash sale section trên homepage**: Horizontal scroll list sản phẩm flash sale. Card: image, name, original price (strikethrough), sale price, discount badge (-30%), progress bar sold/total. See all link tới dedicated page. Auto-refresh list mỗi phút. **AC**: Section attractive, progress accurate, auto-refresh hoạt động. | 🎨 FE | 🟢 | 2h | ⏳ |
| PROMO-003-FE-03 | **Countdown timer trên product**: Timer đếm ngược tới end_time: HH:MM:SS. Highlight màu đỏ khi còn < 1h. Update realtime mỗi giây. Hiển thị ENDED khi hết giờ và disable mua. Sync giữa server time và client. **AC**: Timer chính xác, realtime update, ended state đúng. | 🎨 FE | 🟢 | 1h | ⏳ |
| PROMO-003-QA-01 | **Test flash sale flow**: Test schedule flash sale future thành công. Test flash sale auto-activate đúng giờ. Test flash sale auto-end đúng giờ. Test sale price override product price. Test stock giảm khi mua. Test countdown accurate. Test sold out disable mua. **AC**: Tất cả test cases pass, timing accurate. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-MKT-001: Banner quảng cáo (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| MKT-001-BE-01 | **Tạo bảng `banners`**: Schema: id (UUID PK), title (varchar), image_url (varchar), link_url (varchar nullable), link_type (enum: external/product/category/none), display_order (int), is_active (boolean), start_date, end_date (nullable), created_by, created_at, updated_at. Indexes cho is_active, display_order. **AC**: Migration thành công, ordering hoạt động. | 🔧 BE | 🟡 | 1h | ⏳ |
| MKT-001-BE-02 | **API CRUD `/admin/banners`**: GET list all banners. POST upload image và tạo banner với validation. PUT update (re-order với batch update). DELETE soft delete. GET public `/banners/active` trả banners active trong date range, sorted by display_order. Upload image resize và optimize. **AC**: CRUD hoạt động, upload resize đúng, ordering batch update hoạt động. | 🔧 BE | 🟡 | 2h | ⏳ |
| MKT-001-FE-01 | **UI Admin Banner management**: DataTable với preview thumbnail, title, order, status, dates. Drag-drop để reorder. Actions: Edit, Toggle active, Delete. Form: image upload với preview, title, link URL/picker, dates, active toggle. **AC**: Reorder drag-drop mượt, preview hiển thị đúng, dates picker hoạt động. | 🎨 FE | 🟡 | 2h | ⏳ |
| MKT-001-FE-02 | **Banner carousel trên homepage**: Swiper/carousel component hiển thị banners. Auto-slide mỗi 5 giây. Pagination dots. Pause on touch. Click navigate theo link_url. Lazy load images. Skeleton loading. Responsive aspect ratio (mobile/desktop). **AC**: Carousel mượt, auto-play hoạt động, click navigate đúng. | 🎨 FE | 🟡 | 2h | ⏳ |
| MKT-001-QA-01 | **Test banner flow**: Test upload banner image thành công. Test reorder banners. Test active/inactive toggle. Test date range filter. Test carousel rotation. Test click banner navigate. Test banner load performance. **AC**: Tất cả test cases pass, UX mượt. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-MKT-002: SP Nổi bật (3 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| MKT-002-BE-01 | **API PUT `/admin/products/{id}/featured`**: Toggle is_featured flag trên product. Validate product exists và status = APPROVED. Limit tối đa 20 featured products. Trả lỗi nếu vượt limit và đang add. Ghi audit log cho action. **AC**: Toggle hoạt động, limit enforced, audit logged. | 🔧 BE | 🟡 | 1h | ⏳ |
| MKT-002-BE-02 | **API GET `/products/featured`**: Trả list products với is_featured = true. Include full product info (image, price, rating, seller). Sort by featured_at desc (mới nhất trước). Cache 15 phút. Limit 20 items. Public API. **AC**: List đúng featured products, cache hoạt động, sort đúng. | 🔧 BE | 🟡 | 1h | ⏳ |
| MKT-002-FE-01 | **UI Admin toggle featured**: Star icon trên product row trong admin list. Click toggle featured status. Filled star = featured, outline = not featured. Badge counter "Featured (x/20)" ở header. Toast notification khi toggle. **AC**: Toggle nhanh, visual feedback đúng, counter accurate. | 🎨 FE | 🟡 | 1h | ⏳ |
| MKT-002-FE-02 | **Featured section trên homepage**: Section "Sản phẩm nổi bật" với grid 2 columns (mobile) / 4 columns (desktop). Product cards với: image, name, price, rating. "Xem tất cả" link. Skeleton loading. Auto-refresh khi user quay lại app. **AC**: Section đẹp, responsive grid, skeleton smooth. | 🎨 FE | 🟡 | 2h | ⏳ |
| MKT-002-QA-01 | **Test featured products**: Test toggle featured thành công. Test limit 20 enforcement. Test featured section hiển thị đúng products. Test sort by newest. Test cache invalidation khi toggle. **AC**: Tất cả test cases pass, limit enforcement đúng. | 🧪 QA | 🟢 | 1h | ⏳ |

---

# 🏃 SPRINT 12 - Communication & Support

**Sprint Goal**: Giao tiếp và hỗ trợ  
**Total Story Points**: 31 SP

---

## US-CHAT-001: Chat với Seller (13 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| CHAT-001-BE-01 | **Setup WebSocket server**: Sử dụng FastAPI WebSocket hoặc Socket.io. Implement connection manager quản lý active connections per user. Authentication qua JWT token khi connect. Handle disconnect và reconnection. Room-based cho mỗi conversation. Heartbeat để detect dead connections. **AC**: WebSocket hoạt động, auth đúng, room isolation đúng. | 🔧 BE | 🟡 | 4h | ⏳ |
| CHAT-001-BE-02 | **Tạo bảng `conversations` và `messages`**: Conversations: id, participant_1_id, participant_2_id, created_at, updated_at, last_message_at. Messages: id, conversation_id, sender_id, content (text), message_type (text/image), read_at, created_at. Indexes cho performance. Unique constraint cho participant pair. **AC**: Schema đầy đủ, migrations thành công, queries nhanh. | 🔧 BE | 🟡 | 1h | ⏳ |
| CHAT-001-BE-03 | **API chat endpoints**: POST `/conversations` - tạo hoặc get existing conversation với user. GET `/conversations/{id}/messages` - pagination desc, limit 50. POST `/conversations/{id}/messages` - gửi message, broadcast qua WebSocket. PUT `/messages/{id}/read` - đánh dấu đã đọc. **AC**: CRUD hoạt động, WebSocket broadcast realtime, pagination đúng. | 🔧 BE | 🟡 | 3h | ⏳ |
| CHAT-001-BE-04 | **Upload chat images**: POST `/messages/upload-image` - accept JPEG/PNG, max 5MB. Resize và compress. Lưu lên cloud storage. Trả URL để gửi trong message. Cleanup orphan images sau 24h. Thumbnail generation cho list view. **AC**: Upload thành công, resize đúng, cleanup hoạt động. | 🔧 BE | 🟡 | 2h | ⏳ |
| CHAT-001-FE-01 | **UI Chat room component**: Screen chat với header (avatar, name, online status). Message list với bubbles (own = right blue, other = left gray). Input bar với text input, send button, image picker. Auto-scroll to bottom. Load more khi scroll lên. **AC**: UI đẹp như các chat apps, bubbles styled đúng, scroll mượt. | 🎨 FE | 🟡 | 4h | ⏳ |
| CHAT-001-FE-02 | **Real-time message handling**: Connect WebSocket khi vào chat. Listen for new messages, add to list realtime. Show typing indicator. Update message status (sent, delivered, read). Handle reconnection on network change. Optimistic send với rollback on fail. **AC**: Realtime hoạt động, typing indicator đúng, reconnect mượt. | 🎨 FE | 🟡 | 3h | ⏳ |
| CHAT-001-FE-03 | **Image send và preview**: Image picker trong chat. Preview trước send. Upload với progress. Thumbnail trong chat bubble, tap mở fullscreen. Pinch to zoom trong fullscreen. Download image option. **AC**: Upload smooth, preview tốt, fullscreen hoạt động. | 🎨 FE | 🟡 | 2h | ⏳ |
| CHAT-001-QA-01 | **Test chat functionality**: Test create conversation mới. Test send text message realtime. Test send image. Test message pagination load more. Test read receipts. Test typing indicator. Test reconnection sau network drop. Test multiple devices same user. **AC**: Tất cả test cases pass, realtime reliable. | 🧪 QA | 🟢 | 3h | ⏳ |

---

## US-CHAT-002: Danh sách Chat (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| CHAT-002-BE-01 | **API GET `/conversations` với unread count**: Trả list conversations của user với: other_participant info, last_message (content, time, sender), unread_count. Sort by last_message_at desc. Include online status của other participant. Pagination cursor-based. **AC**: List đúng conversations, unread count accurate, sort đúng. | 🔧 BE | 🟡 | 2h | ⏳ |
| CHAT-002-FE-01 | **UI Conversations list**: FlatList với conversation cards: avatar, name, last message snippet (truncate), time (format relative), unread badge. Online dot indicator. Pull-to-refresh. Click navigate to chat room. Empty state với suggestion. **AC**: List đẹp, badge hiển thị đúng, navigation smooth. | 🎨 FE | 🟡 | 2h | ⏳ |
| CHAT-002-FE-02 | **Sort by last message time**: List auto-sort khi có message mới (bubble to top). Animate reorder khi item moves. Update last message preview realtime. Handle case đang ở trong list khi nhận message. **AC**: Sort realtime hoạt động, animation mượt, update đúng. | 🎨 FE | 🟡 | 1h | ⏳ |
| CHAT-002-FE-03 | **Unread badge per conversation**: Badge số unread trên mỗi conversation. Red circle với white number. Max 99+. Clear khi user mở conversation đó. Update realtime khi nhận message mới (nếu không trong chat room đó). **AC**: Badge accurate, clear đúng, realtime update hoạt động. | 🎨 FE | 🟡 | 1h | ⏳ |
| CHAT-002-QA-01 | **Test conversation list**: Test list load đúng conversations. Test sort by newest message. Test unread badge count. Test badge clear khi mở chat. Test realtime update khi nhận message. Test online status. **AC**: Tất cả test cases pass, data accurate. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-SUP-001: Tạo Ticket (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SUP-001-BE-01 | **Tạo bảng `support_tickets`**: Schema: id, user_id (FK), subject (varchar), category (enum: order/payment/product/account/other), description (text), status (enum: open/in_progress/resolved/closed), priority (enum: low/medium/high), assigned_to (FK nullable), created_at, updated_at, resolved_at. Indexes cho status, user_id, assigned_to. **AC**: Migration thành công, all enums defined. | 🔧 BE | 🟡 | 1h | ⏳ |
| SUP-001-BE-02 | **API POST `/support/tickets`**: Nhận subject, category, description, attachment_urls (optional array). Validate required fields. Tạo ticket với status = OPEN, priority auto-set based on category. Gửi email xác nhận cho user. Notify admin team. **AC**: Ticket created, email sent, admin notified. | 🔧 BE | 🟡 | 2h | ⏳ |
| SUP-001-BE-03 | **File attachment support**: API POST `/support/tickets/upload`. Accept images, PDF, max 5 files, max 10MB each. Lưu lên cloud với folder structure: tickets/{ticket_id}/. Trả array URLs để submit cùng ticket. Validate file types. **AC**: Upload multiple files thành công, validation hoạt động. | 🔧 BE | 🟡 | 1h | ⏳ |
| SUP-001-FE-01 | **UI Create ticket form**: Screen/modal với fields: subject input, category picker, description textarea. Attachment section: up to 5 files. Preview attached files với remove option. Submit button. Loading state. Success screen với ticket number. **AC**: Form đầy đủ, validation hoạt động, success feedback rõ. | 🎨 FE | 🟡 | 2h | ⏳ |
| SUP-001-FE-02 | **My tickets list**: Screen hiển thị tickets của user. Cards: subject, category badge, status badge (màu theo status), created date. Filter by status tabs. Click mở ticket detail để xem replies. Empty state. **AC**: List hiển thị đúng, filter hoạt động, badges đúng màu. | 🎨 FE | 🟡 | 1h | ⏳ |
| SUP-001-QA-01 | **Test create ticket flow**: Test tạo ticket thành công. Test attach files. Test attach file > 10MB fail. Test required fields validation. Test email confirmation received. Test ticket list hiển thị ticket mới. **AC**: Tất cả test cases pass, email delivery verified. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-SUP-002: Quản lý Ticket Admin (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SUP-002-BE-01 | **API `/admin/tickets`**: GET list với filters (status, priority, category, assigned_to), search by subject/user, pagination. PUT `/admin/tickets/{id}/assign` - assign to admin user. POST `/admin/tickets/{id}/reply` - add admin reply. PUT `/admin/tickets/{id}/status` - change status. Include reply history. **AC**: CRUD đầy đủ, filters hoạt động, history tracked. | 🔧 BE | 🟡 | 3h | ⏳ |
| SUP-002-FE-01 | **UI Admin ticket list**: DataTable: ID, subject, user name, category, priority badge, status badge, assigned to, created date. Filters dropdowns. Search input. Bulk actions (assign, change status). Click row → detail modal/page. **AC**: List feature-rich, filters và search hoạt động, bulk actions work. | 🎨 FE | 🟡 | 2h | ⏳ |
| SUP-002-FE-02 | **UI Ticket detail + reply**: Modal/page với: ticket info header, description, attachments (clickable). Reply history thread (chronological). Reply form với textarea và attach. Actions: Assign dropdown, Status change buttons (Resolve, Close). **AC**: Thread clear, reply adds to history, actions update ticket. | 🎨 FE | 🟡 | 2h | ⏳ |
| SUP-002-QA-01 | **Test admin ticket management**: Test list load với filters. Test assign ticket to admin. Test reply visible to user. Test status change flow (Open → In Progress → Resolved → Closed). Test user receives email when replied. **AC**: Tất cả test cases pass, workflow complete. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-FAQ-001: Xem FAQ (3 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| FAQ-001-BE-01 | **Tạo bảng `faqs`**: Schema: id (UUID PK), question (varchar 500), answer (text), category (varchar), display_order (int), is_active (boolean default true), created_by, created_at, updated_at. Indexes cho category, is_active, display_order. Seed data với FAQs phổ biến. **AC**: Migration thành công, seed data imported. | 🔧 BE | 🟢 | 1h | ⏳ |
| FAQ-001-BE-02 | **API CRUD FAQs**: GET public `/faqs` - list active FAQs grouped by category, sorted by display_order. GET `/faqs/categories` - list unique categories. Admin: POST/PUT/DELETE `/admin/faqs` - CRUD với reordering support. Search by question. **AC**: Public list grouped đúng, admin CRUD hoạt động, search works. | 🔧 BE | 🟢 | 2h | ⏳ |
| FAQ-001-FE-01 | **UI FAQ page với accordion**: List FAQs grouped by category headers. Each FAQ as accordion: tap question expands answer with animation. Only one expanded at a time (optional). Markdown support trong answer. Deep link support (/faq#question-id). **AC**: Accordion mượt, categories grouped, deep link works. | 🎨 FE | 🟢 | 2h | ⏳ |
| FAQ-001-FE-02 | **Search FAQ**: Search input ở top page. Filter FAQs client-side by question text. Highlight matching text. Clear search button. Show "No results" state. Debounce search 300ms. **AC**: Search filter đúng, highlight visible, no results state đẹp. | 🎨 FE | 🟢 | 1h | ⏳ |
| FAQ-001-QA-01 | **Test FAQ functionality**: Test FAQ list load grouped by category. Test accordion expand/collapse. Test search filter. Test admin CRUD. Test deep link navigation. Test reorder FAQs. **AC**: Tất cả test cases pass, UX smooth. | 🧪 QA | 🟢 | 1h | ⏳ |

---

# 🏃 SPRINT 13 - Analytics & Reporting

**Sprint Goal**: Báo cáo và phân tích  
**Total Story Points**: 28 SP

---

## US-REP-001: Xuất Excel (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| REP-001-BE-01 | **Service export Excel**: Sử dụng openpyxl hoặc pandas. Implement ExportService với methods cho từng report type: orders, products, users, revenue. Format cells: headers bold, auto-width columns, number formatting, date formatting. Support multiple sheets nếu cần. **AC**: Excel files valid, formatting đẹp, performance tốt với large datasets. | 🔧 BE | 🟡 | 3h | ⏳ |
| REP-001-BE-02 | **API GET export**: Endpoint `/admin/reports/export` với query params: type (orders/products/users/revenue), format (excel/pdf), from_date, to_date. Validate date range max 1 năm. Generate file in background cho large exports. Return file download response hoặc job_id cho async. **AC**: Export hoạt động, date validation đúng, async cho large data. | 🔧 BE | 🟡 | 2h | ⏳ |
| REP-001-FE-01 | **UI Export dialog**: Modal với: report type selector, date range pickers, format toggle (Excel/PDF). Validation: from <= to, range <= 1 year. Preview record count before export. Export button disabled while processing. **AC**: Dialog đầy đủ options, validation hoạt động, preview count accurate. | 🎨 FE | 🟡 | 2h | ⏳ |
| REP-001-FE-02 | **Download file handling**: Click export triggers API call. Show progress/loading. On success, trigger browser download. Handle large file (streaming). Show error toast on failure. Option to email download link for large files. **AC**: Download triggers correctly, large files handled, errors shown. | 🎨 FE | 🟡 | 1h | ⏳ |
| REP-001-QA-01 | **Test export functionality**: Test export orders to Excel thành công. Test export với date range filter. Test date range > 1 year fail. Test large export (10k records). Test file content accuracy. Test all report types. **AC**: Tất cả test cases pass, data accuracy verified. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-REP-002: Xuất PDF (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| REP-002-BE-01 | **Service export PDF**: Sử dụng reportlab hoặc weasyprint. Implement PDF generator với: page headers, footers, pagination. Table formatting với borders, alternating row colors. Chart embedding nếu cần. Landscape orientation cho wide tables. **AC**: PDF reader-friendly, tables formatted đẹp, pagination correct. | 🔧 BE | 🟢 | 3h | ⏳ |
| REP-002-BE-02 | **API export PDF**: Reuse `/admin/reports/export?format=pdf`. Apply same filters as Excel. Generate PDF với same data. Optimize for print: page breaks, margins. Limit PDF to 1000 rows (suggest Excel for more). **AC**: PDF generated correctly, print-optimized, row limit enforced. | 🔧 BE | 🟢 | 2h | ⏳ |
| REP-002-BE-03 | **PDF template với branding**: PDF template với: company logo top-left, report title, date generated, footer với page numbers. Consistent fonts (Vietnamese support). Color scheme matching brand. Watermark option cho draft reports. **AC**: Branding applied, Vietnamese hiển thị đúng, watermark option works. | 🔧 BE | 🟢 | 1h | ⏳ |
| REP-002-FE-01 | **PDF export option**: PDF tab trong export dialog. Warning cho > 1000 rows suggesting Excel. Preview first page option. Same date range and type options. Download handling same as Excel. **AC**: PDF option available, warning shown, preview works. | 🎨 FE | 🟢 | 1h | ⏳ |
| REP-002-QA-01 | **Test PDF export**: Test PDF generation thành công. Test PDF với Vietnamese text. Test pagination correct. Test logo và branding. Test row limit warning. Test print preview. **AC**: Tất cả test cases pass, PDF quality good. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-ANA-001: Biểu đồ doanh thu (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| ANA-001-BE-01 | **API GET `/admin/analytics/revenue`**: Trả time series: date/week/month, revenue, order_count, average_order_value. Query params: granularity (day/week/month), from_date, to_date. Aggregate từ orders table. Fill gaps với 0 cho missing dates. Cache heavy queries 15min. **AC**: Data aggregated correctly, gaps filled, cache hoạt động. | 🔧 BE | 🟡 | 2h | ⏳ |
| ANA-001-BE-02 | **Support compare periods**: Thêm query param compare_previous (boolean). Nếu true, trả thêm previous_period data với same duration. Calculate growth percentage. Example: so sánh tháng này vs tháng trước. **AC**: Compare data accurate, growth % calculated correctly, same duration matched. | 🔧 BE | 🟡 | 2h | ⏳ |
| ANA-001-FE-01 | **Line chart component**: Sử dụng Chart.js hoặc Recharts. Dual axis: revenue (left), order count (right). Smooth curves. Tooltip hiển thị formatted values. Responsive sizing. Optional compare line (dashed). Legend tương tác (toggle visibility). **AC**: Chart đẹp, tooltips work, responsive, compare line toggleable. | 🎨 FE | 🟡 | 3h | ⏳ |
| ANA-001-FE-02 | **Period selector**: Tabs hoặc dropdown: Today, Last 7 days, Last 30 days, Last 90 days, Last 12 months, Custom range. Custom range opens date picker. Toggle "Compare to previous period". Auto-refresh data on change. **AC**: All periods work, custom range works, compare toggle works. | 🎨 FE | 🟡 | 1h | ⏳ |
| ANA-001-QA-01 | **Test revenue analytics**: Test data accuracy cho different periods. Test compare với previous period. Test chart render đúng. Test custom date range. Test empty data handling. Test large datasets performance. **AC**: Tất cả test cases pass, data verified against source. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-ANA-002: Phân tích SP (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| ANA-002-BE-01 | **API GET `/admin/analytics/products/top-selling`**: Trả top 10 products by: quantity_sold, revenue. Query params: period (7d/30d/90d), metric (quantity/revenue). Include: product name, image, category, value. Cache 30min. **AC**: Top products accurate, both metrics work, cache hoạt động. | 🔧 BE | 🟡 | 2h | ⏳ |
| ANA-002-BE-02 | **API GET `/admin/analytics/products/by-category`**: Trả breakdown: category_name, product_count, total_revenue, order_count, percentage of total. Support period filter. Sort by revenue desc. **AC**: Category breakdown accurate, percentages correct, sorted properly. | 🔧 BE | 🟡 | 2h | ⏳ |
| ANA-002-FE-01 | **Bar chart top products**: Horizontal bar chart với top 10 products. Bars show metric value. Product name as label. Click bar → navigate to product detail. Toggle metric (quantity/revenue). Period selector. **AC**: Chart clear, clickable bars work, metric toggle works. | 🎨 FE | 🟡 | 2h | ⏳ |
| ANA-002-FE-02 | **Pie/Donut chart by category**: Donut chart với categories. Legend showing category + percentage. Hover shows details. Click segment → filter products by category. Tổng số ở center donut. **AC**: Chart colorful, hover reveals details, click filters work. | 🎨 FE | 🟡 | 1h | ⏳ |
| ANA-002-QA-01 | **Test product analytics**: Test top selling accuracy. Test category breakdown sums to 100%. Test period filter changes data. Test chart interactions. Test empty category handling. **AC**: Tất cả test cases pass, math correct. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-AUD-001: Activity Log (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| AUD-001-BE-01 | **Tạo bảng `audit_logs`**: Schema: id, user_id (FK nullable), action (enum: create/update/delete/login/logout), resource_type (varchar), resource_id (varchar), old_value (JSONB nullable), new_value (JSONB nullable), ip_address (varchar), user_agent (text), created_at. Indexes cho user_id, action, resource_type, created_at. Partition by month nếu expected high volume. **AC**: Schema complete, indexes hoạt động, partition setup if needed. | 🔧 BE | 🟡 | 1h | ⏳ |
| AUD-001-BE-02 | **Middleware log actions**: Implement audit middleware hoặc decorators. Auto-log cho CUD operations on major resources: users, products, orders, payments. Capture old_value trước update. Capture request metadata (IP, user agent). Queue writes to avoid blocking requests. **AC**: Auto-logging hoạt động, old/new values captured, non-blocking. | 🔧 BE | 🟡 | 3h | ⏳ |
| AUD-001-BE-03 | **API GET `/admin/audit-logs`**: Filters: user_id, action, resource_type, date_range. Search by resource_id. Pagination với cursor (timestamp-based). Include user details. Sort by created_at desc. Limit access to Admin role. **AC**: Filters work, pagination smooth, admin-only enforced. | 🔧 BE | 🟡 | 2h | ⏳ |
| AUD-001-BE-04 | **API export audit logs**: Endpoint GET `/admin/audit-logs/export`. Same filters as list. Export to CSV/Excel. Include all fields. Max export 100k rows. Background job cho large exports. **AC**: Export works, all fields included, large export handled. | 🔧 BE | 🟡 | 1h | ⏳ |
| AUD-001-FE-01 | **UI Audit log viewer**: DataTable: timestamp, user name, action badge (colored), resource type, resource ID (linkable), IP. Expandable row shows old/new value diff. Real-time refresh every 30s. **AC**: Table clear, diff view helpful, real-time works. | 🎨 FE | 🟡 | 3h | ⏳ |
| AUD-001-FE-02 | **Filters UI**: Filter bar với: User picker (search), Action multi-select, Resource type dropdown, Date range picker. Clear all filters button. Filter chips showing active filters. Persist filters in URL. **AC**: All filters work, chips clear, URL persistence works. | 🎨 FE | 🟡 | 2h | ⏳ |
| AUD-001-QA-01 | **Test audit logging**: Test create action logged. Test update logs old/new values. Test delete action logged. Test filter by user. Test filter by action. Test filter by date range. Test export accuracy. Test admin-only access. **AC**: Tất cả test cases pass, security enforced. | 🧪 QA | 🟢 | 2h | ⏳ |

---

# 🏃 SPRINT 14 - Advanced Features

**Sprint Goal**: Tính năng nâng cao  
**Total Story Points**: 34 SP

---

## US-SRCH-001: Tìm kiếm nâng cao (8 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SRCH-001-BE-01 | **API GET `/products/search` với multi-filters**: Endpoint search với query params: q (keyword), category_ids (array), price_min, price_max, region_ids (array), labels (array), rating_min, sort_by (relevance/price/rating/newest), sort_order (asc/desc). Combine filters với AND logic. Pagination. Include facet counts cho filters. **AC**: All filters work, combined correctly, facets accurate. | 🔧 BE | 🟡 | 3h | ⏳ |
| SRCH-001-BE-02 | **Full-text search implementation**: Sử dụng PostgreSQL FTS hoặc Elasticsearch. Index product fields: name (weight 1.0), description (weight 0.5), category name (weight 0.3). Support Vietnamese tokenization. Highlight matching terms. Synonym support (cam = quả cam). Typo tolerance. **AC**: Search relevant, Vietnamese works, highlight hoạt động. | 🔧 BE | 🟡 | 4h | ⏳ |
| SRCH-001-FE-01 | **UI Advanced search form**: Search page với: main search input, filters sidebar (collapsible on mobile). Filter sections: Category checkboxes, Price range slider, Region select, Labels badges, Rating stars. Apply filters button. Clear all. Result count. **AC**: Filters groupthể hiện rõ, mobile collapsible works, count updates. | 🎨 FE | 🟡 | 3h | ⏳ |
| SRCH-001-FE-02 | **Filter sidebar**: Sticky sidebar on desktop. Bottom sheet on mobile (tap to open). Remember filter state trong session. Facet counts next to each option. Disable options with 0 results (gray out). Sort dropdown. Grid/List view toggle. **AC**: Sidebar UX good, facets accurate, view toggle works. | 🎨 FE | 🟡 | 2h | ⏳ |
| SRCH-001-QA-01 | **Test search functionality**: Test keyword search returns relevant results. Test category filter. Test price range filter. Test combined filters. Test sort options. Test Vietnamese keywords. Test typo tolerance. Test no results state. **AC**: Tất cả test cases pass, relevance good. | 🧪 QA | 🟢 | 2h | ⏳ |

---

## US-SOC-001: Google Login (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SOC-001-BE-01 | **API POST `/auth/google`**: Nhận id_token từ Google Sign-In. Verify token với Google API (verify signature, aud, iss). Extract email, name, picture từ payload. Check user exists by email. Trả JWT tokens (access + refresh) cho user. **AC**: Token verified correctly, existing user logged in, JWT issued. | 🔧 BE | 🟢 | 2h | ⏳ |
| SOC-001-BE-02 | **Auto-create user nếu chưa tồn tại**: Nếu email chưa có trong DB, create user mới với: email from Google, name from Google, avatar from Google picture, password = null (social login only), email_verified = true. Assign default role CONSUMER. **AC**: New user created correctly, can login after, no password set. | 🔧 BE | 🟢 | 1h | ⏳ |
| SOC-001-FE-01 | **Google Sign-In button (Web)**: Nút "Đăng nhập với Google" trên login page. Sử dụng Google Identity Services. Request profile và email scopes. Get id_token và gọi backend API. Handle errors (user cancelled, popup blocked). Loading state. **AC**: Button styled đúng Google branding, flow works, errors handled. | 🎨 FE | 🟢 | 2h | ⏳ |
| SOC-001-FE-02 | **Google Sign-In (React Native)**: Sử dụng @react-native-google-signin. Configure với Google Cloud OAuth client IDs (iOS + Android). Request serverAuthCode hoặc idToken. Handle sign out. Persist login state. **AC**: Works on both iOS/Android, tokens correct, logout works. | 🎨 FE | 🟢 | 2h | ⏳ |
| SOC-001-QA-01 | **Test Google login flow**: Test login với Google account mới (auto-create). Test login với Google account đã có. Test cancel popup không crash. Test user info populated correctly. Test logout clears session. **AC**: Tất cả test cases pass, UX smooth. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-SOC-002: Facebook Login (5 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SOC-002-BE-01 | **API POST `/auth/facebook`**: Nhận access_token từ Facebook SDK. Verify token bằng gọi Facebook Graph API /me endpoint. Get email, name, picture. Check user exists by email hoặc facebook_id. Trả JWT tokens. **AC**: Token verified via Graph API, user matched correctly, JWT issued. | 🔧 BE | 🟢 | 2h | ⏳ |
| SOC-002-BE-02 | **Auto-create user nếu chưa tồn tại**: Nếu chưa có user, create với: email (có thể null nếu user không share), name, avatar từ profile picture, facebook_id để link account. Handle case email exists nhưng facebook_id khác (potential merge). **AC**: New user created, facebook_id linked, edge cases handled. | 🔧 BE | 🟢 | 1h | ⏳ |
| SOC-002-FE-01 | **Facebook Login button (Web)**: Nút "Đăng nhập với Facebook" với Facebook branding. Sử dụng Facebook JavaScript SDK. Request email permission. Get access_token và gọi backend. Handle login failures. **AC**: Button styled đúng, SDK initialized correctly, flow works. | 🎨 FE | 🟢 | 2h | ⏳ |
| SOC-002-FE-02 | **Facebook Login (React Native)**: Sử dụng react-native-fbsdk-next. Configure với Facebook App ID. Request permissions (public_profile, email). Get access token. Handle limited login (iOS 14+). **AC**: Works on both platforms, iOS 14 handled, tokens correct. | 🎨 FE | 🟢 | 2h | ⏳ |
| SOC-002-QA-01 | **Test Facebook login flow**: Test login với Facebook account mới. Test login với account đã link. Test user không share email. Test logout. Test account linking với existing email. **AC**: Tất cả test cases pass, edge cases handled. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-SHR-001: Chia sẻ sản phẩm (3 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| SHR-001-BE-01 | **API GET `/products/{id}/share-link`**: Generate short link cho product. Lưu vào bảng short_links hoặc sử dụng external service (bit.ly, Firebase Dynamic Links). Include UTM params cho tracking. Link dẫn về product detail với deep link support. Track share counts. **AC**: Short link generated, UTM tracking, deep link works. | 🔧 BE | 🟢 | 1h | ⏳ |
| SHR-001-FE-01 | **Share button với options**: Share icon trên product detail. Click mở share sheet với options: Facebook, Zalo, Messenger, Copy link, More. Each option triggers appropriate sharing. Fallback to native share nếu app không installed. Analytics track share action. **AC**: Share options work, fallback handles missing apps, tracking fires. | 🎨 FE | 🟢 | 2h | ⏳ |
| SHR-001-FE-02 | **Native share sheet (mobile)**: Sử dụng React Native Share API. Share content: product name, description snippet, image, link. Custom share image (product thumbnail). Success callback track share completed. **AC**: Native sheet opens, content pre-filled, image shared. | 🎨 FE | 🟢 | 1h | ⏳ |
| SHR-001-QA-01 | **Test share functionality**: Test share link generates correctly. Test share to Facebook. Test copy link. Test native share sheet. Test deep link opens product. Test tracking fires. **AC**: Tất cả test cases pass, tracking verified. | 🧪 QA | 🟢 | 1h | ⏳ |

---

## US-LANG-001: Đa ngôn ngữ (13 SP)

| Task ID | Task Description | Team | Priority | Estimate | Status |
|---------|------------------|------|----------|----------|--------|
| LANG-001-BE-01 | **API lưu language preference**: PUT `/users/settings/language` - save preferred language (vi/en). Store trong user_settings table. Include language trong user profile response. Default = vi. Guest users use Accept-Language header. **AC**: Preference saved, loaded correctly, guest handling works. | 🔧 BE | 🟢 | 1h | ⏳ |
| LANG-001-BE-02 | **Response translations (error messages)**: Translate all API error messages. Create translations dictionary (JSON file). Middleware detect language từ header hoặc user setting. Return translated messages. Support: validation errors, business errors, system errors. **AC**: All errors translated, language detection works, fallback to English. | 🔧 BE | 🟢 | 2h | ⏳ |
| LANG-001-FE-01 | **Setup i18n framework**: Cài đặt react-i18next cho cả Web và React Native. Configure với: lazy loading translation files, language detection, persistence. Namespace separation: common, auth, products, orders. Context provider wrap app. **AC**: i18n setup complete, namespaces organized, persistence works. | 🎨 FE | 🟢 | 2h | ⏳ |
| LANG-001-FE-02 | **Extract strings to translation files**: Audit toàn bộ app cho hardcoded strings. Replace với t() function calls. Organize keys trong files: vi.json, en.json. Include: labels, buttons, messages, placeholders. Handle pluralization. **AC**: No hardcoded strings, keys organized, plurals work. | 🎨 FE | 🟢 | 8h | ⏳ |
| LANG-001-FE-03 | **Language switcher component**: Dropdown hoặc toggle trong Settings. Options: Tiếng Việt, English. Persist selection. Reload strings immediately (no app restart). Sync với backend API. Show current language flag. **AC**: Switch works instantly, persists, syncs to backend. | 🎨 FE | 🟢 | 1h | ⏳ |
| LANG-001-FE-04 | **Vietnamese translation file**: Complete vi.json với all Vietnamese strings. Review cho natural Vietnamese phrasing. Handle special chars và diacritics. Include formal/informal variants nếu cần. **AC**: File complete, readable Vietnamese, no missing keys. | 🎨 FE | 🟢 | 2h | ⏳ |
| LANG-001-FE-05 | **English translation file**: Complete en.json with all English strings. Review for grammar and clarity. Match keys với vi.json. Placeholder formatting consistent. **AC**: File complete, proper English, matches Vietnamese keys. | 🎨 FE | 🟢 | 2h | ⏳ |
| LANG-001-QA-01 | **Test multilingual support**: Test switch từ VI sang EN và ngược lại. Test all screens display correct language. Test persistence sau restart app. Test backend error messages translated. Test API preference sync. Test missing key fallback. **AC**: Tất cả test cases pass, no missing translations, UX smooth. | 🧪 QA | 🟢 | 3h | ⏳ |

---

# 📊 TỔNG HỢP SPRINT BACKLOG

| Sprint | BE Tasks | FE Tasks | QA Tasks | Total Hours (Est.) |
|--------|----------|----------|----------|-------------------|
| Sprint 8 | 23 tasks | 16 tasks | 5 tasks | ~65h |
| Sprint 9 | 15 tasks | 18 tasks | 5 tasks | ~72h |
| Sprint 10 | 14 tasks | 14 tasks | 5 tasks | ~60h |
| Sprint 11 | 14 tasks | 14 tasks | 5 tasks | ~55h |
| Sprint 12 | 16 tasks | 17 tasks | 5 tasks | ~68h |
| Sprint 13 | 15 tasks | 12 tasks | 5 tasks | ~58h |
| Sprint 14 | 13 tasks | 17 tasks | 5 tasks | ~62h |
| **TOTAL** | **110 tasks** | **108 tasks** | **35 tasks** | **~440h** |

---

## 📈 Phân bổ công việc theo Team

```
Backend (BE):  ████████████████████████████████░░░░ 43% (110 tasks)
Frontend (FE): ███████████████████████████████░░░░░ 43% (108 tasks)
QA/Testing:    ████████████░░░░░░░░░░░░░░░░░░░░░░░░ 14% (35 tasks)
```

---

*Document generated - Last updated: 05/02/2026*
