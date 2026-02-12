# Sprint Backlog - Technical Tasks (BE / FE / QA)

> **Ngày tạo:** 05/02/2026 | **Dự án:** Hệ thống CMS Nông sản

---

## 📅 SPRINT TIMELINE

| Sprint | Thời gian | SP | Status |
|--------|-----------|-----|--------|
| Sprint 1 | 01/12 - 14/12/2025 | 27 | ✅ |
| Sprint 2 | 15/12 - 28/12/2025 | 34 | ✅ |
| Sprint 3 | 29/12 - 11/01/2026 | 33 | ✅ |
| Sprint 4 | 12/01 - 25/01/2026 | 31 | ✅ |
| Sprint 5 | 26/01 - 08/02/2026 | 44 | ✅ |
| Sprint 6 | 09/02 - 22/02/2026 | 38 | ✅ |
| Sprint 7 | 23/02 - 08/03/2026 | 20 | ✅ |
| Sprint 8 | 09/03 - 22/03/2026 | 24 | ⏳ |
| Sprint 9 | 23/03 - 05/04/2026 | 34 | ⏳ |
| Sprint 10 | 06/04 - 19/04/2026 | 29 | ⏳ |
| Sprint 11 | 20/04 - 03/05/2026 | 29 | ⏳ |
| Sprint 12 | 04/05 - 17/05/2026 | 31 | ⏳ |
| Sprint 13 | 18/05 - 31/05/2026 | 28 | ⏳ |
| Sprint 14 | 01/06 - 14/06/2026 | 34 | ⏳ |

---

# ✅ SPRINT 1 - Authentication & User Management
**📅 01/12/2025 - 14/12/2025** | **27 SP** | ✅ DONE

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| AUTH-001-BE-01 | API POST `/auth/register` | 🔧 BE | 2h | ✅ |
| AUTH-001-BE-02 | Hash password bcrypt | 🔧 BE | 1h | ✅ |
| AUTH-001-BE-03 | Validate email unique | 🔧 BE | 1h | ✅ |
| AUTH-001-FE-01 | UI Register form | 🎨 FE | 2h | ✅ |
| AUTH-001-FE-02 | Validation client-side | 🎨 FE | 1h | ✅ |
| AUTH-002-BE-01 | API POST `/auth/login` | 🔧 BE | 2h | ✅ |
| AUTH-002-BE-02 | Generate JWT token | 🔧 BE | 1h | ✅ |
| AUTH-002-FE-01 | UI Login form | 🎨 FE | 2h | ✅ |
| AUTH-002-FE-02 | Save token, redirect | 🎨 FE | 1h | ✅ |
| AUTH-003-BE-01 | API GET `/auth/me` | 🔧 BE | 1h | ✅ |
| AUTH-003-FE-01 | Display user info | 🎨 FE | 1h | ✅ |
| AUTH-004-BE-01 | API POST `/auth/logout` | 🔧 BE | 30m | ✅ |
| AUTH-004-FE-01 | Clear token, redirect | 🎨 FE | 30m | ✅ |
| AUTH-005-BE-01 | API POST `/auth/refresh` | 🔧 BE | 1h | ✅ |
| AUTH-005-FE-01 | Auto refresh token | 🎨 FE | 1h | ✅ |
| USER-001-BE-01 | API GET `/users` filter, pagination | 🔧 BE | 2h | ✅ |
| USER-002-BE-01 | API POST `/users` | 🔧 BE | 2h | ✅ |
| USER-003-BE-01 | API PUT `/users/{id}` | 🔧 BE | 1h | ✅ |
| USER-004-BE-01 | API DELETE `/users/{id}` soft delete | 🔧 BE | 1h | ✅ |
| USER-005-BE-01 | API PUT `/users/{id}/toggle-active` | 🔧 BE | 1h | ✅ |
| USER-006-BE-01 | API PUT `/users/{id}/roles` | 🔧 BE | 2h | ✅ |
| USER-FE-01 | UI User list DataTable | 🎨 FE | 3h | ✅ |
| USER-FE-02 | UI User form create/edit | 🎨 FE | 2h | ✅ |
| USER-FE-03 | UI Assign roles modal | 🎨 FE | 2h | ✅ |
| AUTH-QA-01 | Test auth flows | 🧪 QA | 2h | ✅ |
| USER-QA-01 | Test user CRUD | 🧪 QA | 2h | ✅ |

---

# ✅ SPRINT 2 - Products & Categories
**📅 15/12/2025 - 28/12/2025** | **34 SP** | ✅ DONE

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| PROD-001-BE-01 | API GET `/products` filter, search, pagination | 🔧 BE | 3h | ✅ |
| PROD-002-BE-01 | API GET `/products/{id}` | 🔧 BE | 1h | ✅ |
| PROD-003-BE-01 | API POST `/products` status PENDING | 🔧 BE | 3h | ✅ |
| PROD-004-BE-01 | API PUT `/products/{id}` | 🔧 BE | 2h | ✅ |
| PROD-005-BE-01 | API DELETE `/products/{id}` | 🔧 BE | 1h | ✅ |
| PROD-006-BE-01 | API PUT `/products/{id}/approve` | 🔧 BE | 2h | ✅ |
| PROD-007-BE-01 | API PUT `/products/{id}/label` | 🔧 BE | 1h | ✅ |
| PROD-FE-01 | UI Product list with filters | 🎨 FE | 4h | ✅ |
| PROD-FE-02 | UI Product detail page | 🎨 FE | 2h | ✅ |
| PROD-FE-03 | UI Product form create/edit | 🎨 FE | 4h | ✅ |
| PROD-FE-04 | UI Product approval admin | 🎨 FE | 3h | ✅ |
| CAT-001-BE-01 | API GET `/categories` tree structure | 🔧 BE | 2h | ✅ |
| CAT-002-BE-01 | API POST `/categories` | 🔧 BE | 1h | ✅ |
| CAT-003-BE-01 | API PUT `/categories/{id}` | 🔧 BE | 1h | ✅ |
| CAT-004-BE-01 | API DELETE `/categories/{id}` | 🔧 BE | 1h | ✅ |
| CAT-FE-01 | UI Category tree view | 🎨 FE | 3h | ✅ |
| CAT-FE-02 | UI Category form modal | 🎨 FE | 2h | ✅ |
| PROD-QA-01 | Test product CRUD, approval | 🧪 QA | 3h | ✅ |
| CAT-QA-01 | Test category CRUD | 🧪 QA | 1h | ✅ |

---

# ✅ SPRINT 3 - Orders & Payments
**📅 29/12/2025 - 11/01/2026** | **33 SP** | ✅ DONE

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| ORD-001-BE-01 | API GET `/orders` filter, pagination | 🔧 BE | 3h | ✅ |
| ORD-002-BE-01 | API GET `/orders/{id}` with items, payment | 🔧 BE | 2h | ✅ |
| ORD-003-BE-01 | API PUT `/orders/{id}/status` | 🔧 BE | 2h | ✅ |
| ORD-004-BE-01 | API GET `/orders/statistics` | 🔧 BE | 2h | ✅ |
| ORD-FE-01 | UI Order list | 🎨 FE | 3h | ✅ |
| ORD-FE-02 | UI Order detail | 🎨 FE | 3h | ✅ |
| ORD-FE-03 | UI Update status workflow | 🎨 FE | 2h | ✅ |
| PAY-001-BE-01 | API GET `/payments` | 🔧 BE | 2h | ✅ |
| PAY-002-BE-01 | API GET `/payments/{id}` | 🔧 BE | 1h | ✅ |
| PAY-003-BE-01 | API GET `/payments/reconciliation` | 🔧 BE | 3h | ✅ |
| PAY-004-BE-01 | API POST `/payments/{id}/refund` | 🔧 BE | 3h | ✅ |
| PAY-005-BE-01 | API PUT `/config/platform-fee` | 🔧 BE | 1h | ✅ |
| PAY-FE-01 | UI Payment list | 🎨 FE | 2h | ✅ |
| PAY-FE-02 | UI Reconciliation report | 🎨 FE | 3h | ✅ |
| PAY-FE-03 | UI Refund dialog | 🎨 FE | 2h | ✅ |
| ORD-QA-01 | Test order operations | 🧪 QA | 2h | ✅ |
| PAY-QA-01 | Test payment operations | 🧪 QA | 2h | ✅ |

---

# ✅ SPRINT 4 - Content & Organizations
**📅 12/01/2026 - 25/01/2026** | **31 SP** | ✅ DONE

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| CNT-001-BE-01 | API GET `/contents` with filter | 🔧 BE | 2h | ✅ |
| CNT-002-BE-01 | API GET `/contents/{id}` | 🔧 BE | 1h | ✅ |
| CNT-003-BE-01 | API POST `/contents` | 🔧 BE | 2h | ✅ |
| CNT-004-BE-01 | API PUT `/contents/{id}` | 🔧 BE | 1h | ✅ |
| CNT-005-BE-01 | API DELETE `/contents/{id}` | 🔧 BE | 1h | ✅ |
| CNT-006-BE-01 | API PUT `/contents/{id}/approve` | 🔧 BE | 2h | ✅ |
| CNT-FE-01 | UI Content list | 🎨 FE | 2h | ✅ |
| CNT-FE-02 | UI Content editor WYSIWYG | 🎨 FE | 4h | ✅ |
| CNT-FE-03 | UI Content approval | 🎨 FE | 2h | ✅ |
| ORG-001-BE-01 | API GET `/organizations` | 🔧 BE | 2h | ✅ |
| ORG-002-BE-01 | API GET `/organizations/{id}` | 🔧 BE | 1h | ✅ |
| ORG-003-BE-01 | API POST `/organizations` | 🔧 BE | 2h | ✅ |
| ORG-004-BE-01 | API POST/DELETE `/organizations/{id}/members` | 🔧 BE | 2h | ✅ |
| ORG-FE-01 | UI Organization list | 🎨 FE | 2h | ✅ |
| ORG-FE-02 | UI Organization detail | 🎨 FE | 2h | ✅ |
| ORG-FE-03 | UI Member management | 🎨 FE | 2h | ✅ |
| CNT-QA-01 | Test content operations | 🧪 QA | 2h | ✅ |
| ORG-QA-01 | Test organization CRUD | 🧪 QA | 1h | ✅ |

---

# ✅ SPRINT 5 - System Management & Dashboard
**📅 26/01/2026 - 08/02/2026** | **44 SP** | ✅ DONE

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| DASH-001-BE-01 | API GET `/dashboard/overview` | 🔧 BE | 3h | ✅ |
| DASH-002-BE-01 | API GET `/dashboard/revenue` | 🔧 BE | 3h | ✅ |
| DASH-003-BE-01 | API GET `/dashboard/products` | 🔧 BE | 2h | ✅ |
| DASH-004-BE-01 | API GET `/dashboard/orders` | 🔧 BE | 2h | ✅ |
| DASH-005-BE-01 | API GET `/dashboard/users` | 🔧 BE | 2h | ✅ |
| DASH-FE-01 | UI Dashboard layout | 🎨 FE | 4h | ✅ |
| DASH-FE-02 | UI Stats cards | 🎨 FE | 2h | ✅ |
| DASH-FE-03 | UI Charts revenue, orders | 🎨 FE | 4h | ✅ |
| ROLE-BE-01 | API CRUD `/roles` | 🔧 BE | 3h | ✅ |
| PERM-BE-01 | API CRUD `/permissions` | 🔧 BE | 3h | ✅ |
| ROLE-FE-01 | UI Role management | 🎨 FE | 3h | ✅ |
| PERM-FE-01 | UI Permission matrix | 🎨 FE | 3h | ✅ |
| REG-BE-01 | API CRUD `/regions` | 🔧 BE | 2h | ✅ |
| MED-BE-01 | API upload/list/delete `/media` | 🔧 BE | 3h | ✅ |
| CON-BE-01 | API CRUD `/contracts` | 🔧 BE | 3h | ✅ |
| REG-FE-01 | UI Region management | 🎨 FE | 2h | ✅ |
| MED-FE-01 | UI Media library | 🎨 FE | 3h | ✅ |
| CON-FE-01 | UI Contract management | 🎨 FE | 3h | ✅ |
| DASH-QA-01 | Test dashboard | 🧪 QA | 2h | ✅ |
| ROLE-QA-01 | Test role-permission | 🧪 QA | 2h | ✅ |
| SYS-QA-01 | Test system modules | 🧪 QA | 2h | ✅ |

---

# ✅ SPRINT 6 - Mobile App API
**📅 09/02/2026 - 22/02/2026** | **38 SP** | ✅ DONE

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| MOB-001-BE-01 | API GET `/mobile/posts` public | 🔧 BE | 2h | ✅ |
| MOB-002-BE-01 | API GET `/mobile/posts/{id}` | 🔧 BE | 1h | ✅ |
| MOB-003-BE-01 | API POST `/mobile/posts` | 🔧 BE | 2h | ✅ |
| MOB-004-BE-01 | API CRUD `/mobile/my-posts` | 🔧 BE | 3h | ✅ |
| MOB-005-BE-01 | API GET `/mobile/products` | 🔧 BE | 2h | ✅ |
| MOB-006-BE-01 | API GET `/mobile/products/{id}` | 🔧 BE | 1h | ✅ |
| MOB-007-BE-01 | API POST `/mobile/orders` | 🔧 BE | 4h | ✅ |
| MOB-008-BE-01 | API GET `/mobile/my-orders` | 🔧 BE | 2h | ✅ |
| MOB-009-BE-01 | API GET/PUT `/mobile/profile` | 🔧 BE | 2h | ✅ |
| MOB-FE-01 | Posts list screen | 🎨 FE | 3h | ✅ |
| MOB-FE-02 | Post detail screen | 🎨 FE | 2h | ✅ |
| MOB-FE-03 | Create post screen | 🎨 FE | 3h | ✅ |
| MOB-FE-04 | Products list screen | 🎨 FE | 3h | ✅ |
| MOB-FE-05 | Product detail screen | 🎨 FE | 2h | ✅ |
| MOB-FE-06 | Checkout flow | 🎨 FE | 4h | ✅ |
| MOB-FE-07 | My orders screen | 🎨 FE | 3h | ✅ |
| MOB-FE-08 | Profile screen | 🎨 FE | 2h | ✅ |
| MOB-QA-01 | Test mobile flows | 🧪 QA | 4h | ✅ |

---

# ✅ SPRINT 7 - Complaints & Reviews
**📅 23/02/2026 - 08/03/2026** | **20 SP** | ✅ DONE

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| REV-001-BE-01 | API GET `/reviews` | 🔧 BE | 2h | ✅ |
| CMP-001-BE-01 | API GET `/complaints` | 🔧 BE | 2h | ✅ |
| CMP-002-BE-01 | API PUT `/complaints/{id}/resolve` | 🔧 BE | 2h | ✅ |
| REV-FE-01 | UI Review list | 🎨 FE | 2h | ✅ |
| CMP-FE-01 | UI Complaint list | 🎨 FE | 2h | ✅ |
| CMP-FE-02 | UI Resolve complaint | 🎨 FE | 2h | ✅ |
| STAT-001-BE-01 | API GET `/stats/producers` | 🔧 BE | 2h | ✅ |
| STAT-002-BE-01 | API GET `/stats/consumers` | 🔧 BE | 2h | ✅ |
| STAT-003-BE-01 | API GET `/stats/trending-products` | 🔧 BE | 2h | ✅ |
| STAT-FE-01 | UI Producer stats | 🎨 FE | 2h | ✅ |
| STAT-FE-02 | UI Consumer stats | 🎨 FE | 2h | ✅ |
| STAT-FE-03 | UI Trending products | 🎨 FE | 2h | ✅ |
| RC-QA-01 | Test review, complaint | 🧪 QA | 2h | ✅ |
| STAT-QA-01 | Test statistics | 🧪 QA | 1h | ✅ |

---

# ⏳ SPRINT 8 - Authentication Enhancement
**📅 09/03/2026 - 22/03/2026** | **24 SP** | ⏳ PLANNED

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| AUTH-006-BE-01 | API POST `/auth/forgot-password` | 🔧 BE | 2h | ⏳ |
| AUTH-006-BE-02 | Email reset password service | 🔧 BE | 3h | ⏳ |
| AUTH-006-BE-03 | API POST `/auth/reset-password` | 🔧 BE | 2h | ⏳ |
| AUTH-006-BE-04 | Table `password_reset_tokens` | 🔧 BE | 1h | ⏳ |
| AUTH-006-FE-01 | UI Forgot password form | 🎨 FE | 2h | ⏳ |
| AUTH-006-FE-02 | UI Reset password form | 🎨 FE | 2h | ⏳ |
| AUTH-007-BE-01 | API PUT `/auth/change-password` | 🔧 BE | 2h | ⏳ |
| AUTH-007-FE-01 | UI Change password form | 🎨 FE | 2h | ⏳ |
| AUTH-008-BE-01 | API POST `/auth/send-otp` | 🔧 BE | 2h | ⏳ |
| AUTH-008-BE-02 | API POST `/auth/verify-otp` | 🔧 BE | 2h | ⏳ |
| AUTH-008-BE-03 | Table `otp_codes` | 🔧 BE | 1h | ⏳ |
| AUTH-008-FE-01 | UI OTP input 6 digits | 🎨 FE | 2h | ⏳ |
| AUTH-008-FE-02 | Countdown + resend | 🎨 FE | 1h | ⏳ |
| AUTH-009-BE-01 | API POST `/auth/register-producer` | 🔧 BE | 3h | ⏳ |
| AUTH-009-BE-02 | Upload business license | 🔧 BE | 2h | ⏳ |
| AUTH-009-BE-03 | API PUT `/admin/producers/{id}/approve` | 🔧 BE | 2h | ⏳ |
| AUTH-009-FE-01 | UI Multi-step register form | 🎨 FE | 4h | ⏳ |
| AUTH-009-FE-02 | UI Admin approve producer | 🎨 FE | 3h | ⏳ |
| USER-007-BE-01 | API POST `/users/avatar` | 🔧 BE | 2h | ⏳ |
| USER-007-BE-02 | Crop image thumbnail | 🔧 BE | 2h | ⏳ |
| USER-007-FE-01 | UI Avatar upload + crop | 🎨 FE | 3h | ⏳ |
| AUTH-QA-02 | Test forgot/reset password | 🧪 QA | 2h | ⏳ |
| AUTH-QA-03 | Test OTP flow | 🧪 QA | 2h | ⏳ |
| AUTH-QA-04 | Test producer registration | 🧪 QA | 2h | ⏳ |

---

# ⏳ SPRINT 9 - Mobile Shopping Enhancement
**📅 23/03/2026 - 05/04/2026** | **34 SP** | ⏳ PLANNED

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| CART-001-BE-01 | API CRUD `/cart` | 🔧 BE | 4h | ⏳ |
| CART-001-BE-02 | Tables `carts`, `cart_items` | 🔧 BE | 1h | ⏳ |
| CART-001-BE-03 | Validate product availability | 🔧 BE | 2h | ⏳ |
| CART-001-FE-01 | UI Cart page mobile | 🎨 FE | 3h | ⏳ |
| CART-001-FE-02 | Update quantity, remove item | 🎨 FE | 2h | ⏳ |
| CART-001-FE-03 | LocalStorage for guest | 🎨 FE | 2h | ⏳ |
| CART-001-FE-04 | Cart badge counter | 🎨 FE | 1h | ⏳ |
| WISH-001-BE-01 | API `/wishlist` get, add, remove | 🔧 BE | 2h | ⏳ |
| WISH-001-BE-02 | Table `wishlists` | 🔧 BE | 1h | ⏳ |
| WISH-001-FE-01 | UI Wishlist page | 🎨 FE | 2h | ⏳ |
| WISH-001-FE-02 | Heart toggle on product | 🎨 FE | 1h | ⏳ |
| WISH-001-FE-03 | Move to cart | 🎨 FE | 1h | ⏳ |
| REV-002-BE-01 | API POST `/reviews` | 🔧 BE | 2h | ⏳ |
| REV-002-BE-02 | Validate user purchased | 🔧 BE | 1h | ⏳ |
| REV-002-BE-03 | Upload review images | 🔧 BE | 2h | ⏳ |
| REV-002-FE-01 | UI Review form star + comment | 🎨 FE | 2h | ⏳ |
| REV-002-FE-02 | Upload review images | 🎨 FE | 2h | ⏳ |
| REV-002-FE-03 | Display reviews on product | 🎨 FE | 2h | ⏳ |
| NOTI-001-BE-01 | Firebase FCM integration | 🔧 BE | 4h | ⏳ |
| NOTI-001-BE-02 | API save FCM token | 🔧 BE | 1h | ⏳ |
| NOTI-001-BE-03 | Push notification service | 🔧 BE | 3h | ⏳ |
| NOTI-001-BE-04 | Trigger on order status | 🔧 BE | 2h | ⏳ |
| NOTI-001-BE-05 | Tables notifications, device_tokens | 🔧 BE | 1h | ⏳ |
| NOTI-001-FE-01 | Setup FCM React Native | 🎨 FE | 3h | ⏳ |
| NOTI-001-FE-02 | Request permission | 🎨 FE | 1h | ⏳ |
| NOTI-001-FE-03 | Deep linking on tap | 🎨 FE | 2h | ⏳ |
| NOTI-002-BE-01 | API GET/PUT `/notifications` | 🔧 BE | 2h | ⏳ |
| NOTI-002-FE-01 | UI Notification list | 🎨 FE | 2h | ⏳ |
| NOTI-002-FE-02 | Mark read + badge | 🎨 FE | 1h | ⏳ |
| CART-QA-01 | Test cart operations | 🧪 QA | 2h | ⏳ |
| WISH-QA-01 | Test wishlist | 🧪 QA | 1h | ⏳ |
| REV-QA-01 | Test reviews | 🧪 QA | 2h | ⏳ |
| NOTI-QA-01 | Test notifications | 🧪 QA | 3h | ⏳ |

---

# ⏳ SPRINT 10 - Order & Delivery Tracking
**📅 06/04/2026 - 19/04/2026** | **29 SP** | ⏳ PLANNED

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| ORD-005-BE-01 | API GET `/orders/{id}/tracking` | 🔧 BE | 2h | ⏳ |
| ORD-005-BE-02 | Table `order_tracking_history` | 🔧 BE | 1h | ⏳ |
| ORD-005-BE-03 | Integration GHN, GHTK | 🔧 BE | 4h | ⏳ |
| ORD-005-FE-01 | UI Tracking timeline | 🎨 FE | 3h | ⏳ |
| ORD-005-FE-02 | Map shipper location | 🎨 FE | 3h | ⏳ |
| ORD-006-BE-01 | API PUT `/orders/{id}/cancel` | 🔧 BE | 2h | ⏳ |
| ORD-006-BE-02 | Validate status PENDING | 🔧 BE | 1h | ⏳ |
| ORD-006-BE-03 | Trigger refund if paid | 🔧 BE | 1h | ⏳ |
| ORD-006-FE-01 | UI Cancel dialog with reason | 🎨 FE | 1h | ⏳ |
| ORD-007-BE-01 | API PUT `/orders/{id}/confirm-received` | 🔧 BE | 1h | ⏳ |
| ORD-007-BE-02 | Trigger payment to seller | 🔧 BE | 1h | ⏳ |
| ORD-007-FE-01 | UI Confirm received button | 🎨 FE | 1h | ⏳ |
| SELL-001-BE-01 | API GET `/seller/dashboard/stats` | 🔧 BE | 3h | ⏳ |
| SELL-001-BE-02 | API GET `/seller/dashboard/revenue` | 🔧 BE | 2h | ⏳ |
| SELL-001-BE-03 | API GET `/seller/orders/recent` | 🔧 BE | 1h | ⏳ |
| SELL-001-FE-01 | UI Seller Dashboard | 🎨 FE | 4h | ⏳ |
| SELL-001-FE-02 | Charts revenue, orders | 🎨 FE | 3h | ⏳ |
| SELL-002-BE-01 | API `/seller/products` scoped | 🔧 BE | 2h | ⏳ |
| SELL-002-FE-01 | UI Seller products list | 🎨 FE | 3h | ⏳ |
| SELL-002-FE-02 | UI Add/Edit product mobile | 🎨 FE | 4h | ⏳ |
| SELL-002-FE-03 | Multi image upload | 🎨 FE | 2h | ⏳ |
| SELL-002-FE-04 | Status badge | 🎨 FE | 1h | ⏳ |
| ORD-QA-02 | Test tracking, cancel | 🧪 QA | 2h | ⏳ |
| SELL-QA-01 | Test seller dashboard | 🧪 QA | 2h | ⏳ |
| SELL-QA-02 | Test seller products | 🧪 QA | 2h | ⏳ |

---

# ⏳ SPRINT 11 - Promotions System
**📅 20/04/2026 - 03/05/2026** | **29 SP** | ⏳ PLANNED

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| PROMO-001-BE-01 | Table `vouchers` | 🔧 BE | 1h | ⏳ |
| PROMO-001-BE-02 | API CRUD `/admin/vouchers` | 🔧 BE | 3h | ⏳ |
| PROMO-001-BE-03 | Table `voucher_usages` | 🔧 BE | 1h | ⏳ |
| PROMO-001-FE-01 | UI Admin Voucher list | 🎨 FE | 3h | ⏳ |
| PROMO-001-FE-02 | UI Voucher form | 🎨 FE | 2h | ⏳ |
| PROMO-002-BE-01 | API POST `/cart/apply-voucher` | 🔧 BE | 2h | ⏳ |
| PROMO-002-BE-02 | Validate voucher conditions | 🔧 BE | 2h | ⏳ |
| PROMO-002-BE-03 | Calculate discount | 🔧 BE | 1h | ⏳ |
| PROMO-002-FE-01 | UI Input voucher checkout | 🎨 FE | 1h | ⏳ |
| PROMO-002-FE-02 | Display discount, new total | 🎨 FE | 1h | ⏳ |
| PROMO-003-BE-01 | Table `flash_sales` | 🔧 BE | 1h | ⏳ |
| PROMO-003-BE-02 | API CRUD `/admin/flash-sales` | 🔧 BE | 3h | ⏳ |
| PROMO-003-BE-03 | API GET `/flash-sales/active` | 🔧 BE | 1h | ⏳ |
| PROMO-003-FE-01 | UI Admin Flash sale | 🎨 FE | 2h | ⏳ |
| PROMO-003-FE-02 | UI Flash sale homepage | 🎨 FE | 2h | ⏳ |
| PROMO-003-FE-03 | Countdown timer | 🎨 FE | 1h | ⏳ |
| MKT-001-BE-01 | Table `banners` | 🔧 BE | 1h | ⏳ |
| MKT-001-BE-02 | API CRUD `/admin/banners` | 🔧 BE | 2h | ⏳ |
| MKT-001-FE-01 | UI Admin Banner list | 🎨 FE | 2h | ⏳ |
| MKT-001-FE-02 | Banner carousel homepage | 🎨 FE | 2h | ⏳ |
| MKT-002-BE-01 | API PUT `/admin/products/{id}/featured` | 🔧 BE | 1h | ⏳ |
| MKT-002-BE-02 | API GET `/products/featured` | 🔧 BE | 1h | ⏳ |
| MKT-002-FE-01 | UI Toggle featured | 🎨 FE | 1h | ⏳ |
| MKT-002-FE-02 | Featured section homepage | 🎨 FE | 2h | ⏳ |
| PROMO-QA-01 | Test voucher operations | 🧪 QA | 2h | ⏳ |
| PROMO-QA-02 | Test flash sale | 🧪 QA | 2h | ⏳ |
| MKT-QA-01 | Test banner, featured | 🧪 QA | 1h | ⏳ |

---

# ⏳ SPRINT 12 - Communication & Support
**📅 04/05/2026 - 17/05/2026** | **31 SP** | ⏳ PLANNED

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| CHAT-001-BE-01 | WebSocket server setup | 🔧 BE | 4h | ⏳ |
| CHAT-001-BE-02 | Tables conversations, messages | 🔧 BE | 1h | ⏳ |
| CHAT-001-BE-03 | API chat endpoints | 🔧 BE | 3h | ⏳ |
| CHAT-001-BE-04 | Chat image upload | 🔧 BE | 2h | ⏳ |
| CHAT-001-FE-01 | UI Chat room | 🎨 FE | 4h | ⏳ |
| CHAT-001-FE-02 | Real-time message | 🎨 FE | 3h | ⏳ |
| CHAT-001-FE-03 | Image send + preview | 🎨 FE | 2h | ⏳ |
| CHAT-002-BE-01 | API GET `/conversations` | 🔧 BE | 2h | ⏳ |
| CHAT-002-FE-01 | UI Conversations list | 🎨 FE | 2h | ⏳ |
| CHAT-002-FE-02 | Sort by last message | 🎨 FE | 1h | ⏳ |
| CHAT-002-FE-03 | Unread badge | 🎨 FE | 1h | ⏳ |
| SUP-001-BE-01 | Table `support_tickets` | 🔧 BE | 1h | ⏳ |
| SUP-001-BE-02 | API POST `/support/tickets` | 🔧 BE | 2h | ⏳ |
| SUP-001-BE-03 | File attachment | 🔧 BE | 1h | ⏳ |
| SUP-001-FE-01 | UI Create ticket form | 🎨 FE | 2h | ⏳ |
| SUP-001-FE-02 | My tickets list | 🎨 FE | 1h | ⏳ |
| SUP-002-BE-01 | API `/admin/tickets` CRUD | 🔧 BE | 3h | ⏳ |
| SUP-002-FE-01 | UI Admin ticket list | 🎨 FE | 2h | ⏳ |
| SUP-002-FE-02 | UI Ticket detail + reply | 🎨 FE | 2h | ⏳ |
| FAQ-001-BE-01 | Table `faqs` | 🔧 BE | 1h | ⏳ |
| FAQ-001-BE-02 | API CRUD `/faqs` | 🔧 BE | 2h | ⏳ |
| FAQ-001-FE-01 | UI FAQ accordion | 🎨 FE | 2h | ⏳ |
| FAQ-001-FE-02 | Search FAQ | 🎨 FE | 1h | ⏳ |
| CHAT-QA-01 | Test chat features | 🧪 QA | 3h | ⏳ |
| SUP-QA-01 | Test ticket system | 🧪 QA | 2h | ⏳ |
| FAQ-QA-01 | Test FAQ | 🧪 QA | 1h | ⏳ |

---

# ⏳ SPRINT 13 - Analytics & Reporting
**📅 18/05/2026 - 31/05/2026** | **28 SP** | ⏳ PLANNED

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| REP-001-BE-01 | Excel export service | 🔧 BE | 3h | ⏳ |
| REP-001-BE-02 | API `/admin/reports/export?format=excel` | 🔧 BE | 2h | ⏳ |
| REP-001-FE-01 | UI Export dialog | 🎨 FE | 2h | ⏳ |
| REP-001-FE-02 | Download file handling | 🎨 FE | 1h | ⏳ |
| REP-002-BE-01 | PDF export service | 🔧 BE | 3h | ⏳ |
| REP-002-BE-02 | API `/admin/reports/export?format=pdf` | 🔧 BE | 2h | ⏳ |
| REP-002-BE-03 | PDF template logo, header | 🔧 BE | 1h | ⏳ |
| REP-002-FE-01 | PDF export option | 🎨 FE | 1h | ⏳ |
| ANA-001-BE-01 | API GET `/admin/analytics/revenue` | 🔧 BE | 2h | ⏳ |
| ANA-001-BE-02 | Compare periods YoY | 🔧 BE | 2h | ⏳ |
| ANA-001-FE-01 | Line chart component | 🎨 FE | 3h | ⏳ |
| ANA-001-FE-02 | Period selector | 🎨 FE | 1h | ⏳ |
| ANA-002-BE-01 | API `/admin/analytics/products/top-selling` | 🔧 BE | 2h | ⏳ |
| ANA-002-BE-02 | API `/admin/analytics/products/by-category` | 🔧 BE | 2h | ⏳ |
| ANA-002-FE-01 | Bar chart top products | 🎨 FE | 2h | ⏳ |
| ANA-002-FE-02 | Pie chart by category | 🎨 FE | 1h | ⏳ |
| AUD-001-BE-01 | Table `audit_logs` | 🔧 BE | 1h | ⏳ |
| AUD-001-BE-02 | Middleware log actions | 🔧 BE | 3h | ⏳ |
| AUD-001-BE-03 | API GET `/admin/audit-logs` | 🔧 BE | 2h | ⏳ |
| AUD-001-BE-04 | API export audit logs | 🔧 BE | 1h | ⏳ |
| AUD-001-FE-01 | UI Audit log viewer | 🎨 FE | 3h | ⏳ |
| AUD-001-FE-02 | Filters user, action, date | 🎨 FE | 2h | ⏳ |
| REP-QA-01 | Test export Excel, PDF | 🧪 QA | 2h | ⏳ |
| ANA-QA-01 | Test analytics charts | 🧪 QA | 2h | ⏳ |
| AUD-QA-01 | Test audit log | 🧪 QA | 2h | ⏳ |

---

# ⏳ SPRINT 14 - Advanced Features
**📅 01/06/2026 - 14/06/2026** | **34 SP** | ⏳ PLANNED

| Task ID | Description | Team | Est. | Status |
|---------|-------------|------|------|--------|
| SRCH-001-BE-01 | API GET `/products/search` multi-filters | 🔧 BE | 3h | ⏳ |
| SRCH-001-BE-02 | Full-text search Elasticsearch/FTS | 🔧 BE | 4h | ⏳ |
| SRCH-001-FE-01 | UI Advanced search form | 🎨 FE | 3h | ⏳ |
| SRCH-001-FE-02 | Filter sidebar | 🎨 FE | 2h | ⏳ |
| SOC-001-BE-01 | API POST `/auth/google` verify token | 🔧 BE | 2h | ⏳ |
| SOC-001-BE-02 | Auto-create user | 🔧 BE | 1h | ⏳ |
| SOC-001-FE-01 | Google Sign-In Web | 🎨 FE | 2h | ⏳ |
| SOC-001-FE-02 | Google Sign-In React Native | 🎨 FE | 2h | ⏳ |
| SOC-002-BE-01 | API POST `/auth/facebook` verify token | 🔧 BE | 2h | ⏳ |
| SOC-002-BE-02 | Auto-create user | 🔧 BE | 1h | ⏳ |
| SOC-002-FE-01 | Facebook Login Web | 🎨 FE | 2h | ⏳ |
| SOC-002-FE-02 | Facebook Login React Native | 🎨 FE | 2h | ⏳ |
| SHR-001-BE-01 | API GET `/products/{id}/share-link` | 🔧 BE | 1h | ⏳ |
| SHR-001-FE-01 | Share button options | 🎨 FE | 2h | ⏳ |
| SHR-001-FE-02 | Native share sheet | 🎨 FE | 1h | ⏳ |
| LANG-001-BE-01 | API save language preference | 🔧 BE | 1h | ⏳ |
| LANG-001-BE-02 | Response translations | 🔧 BE | 2h | ⏳ |
| LANG-001-FE-01 | Setup i18n | 🎨 FE | 2h | ⏳ |
| LANG-001-FE-02 | Extract strings to files | 🎨 FE | 8h | ⏳ |
| LANG-001-FE-03 | Language switcher | 🎨 FE | 1h | ⏳ |
| LANG-001-FE-04 | Vietnamese translations | 🎨 FE | 2h | ⏳ |
| LANG-001-FE-05 | English translations | 🎨 FE | 2h | ⏳ |
| SRCH-QA-01 | Test search | 🧪 QA | 2h | ⏳ |
| SOC-QA-01 | Test social login | 🧪 QA | 2h | ⏳ |
| SHR-QA-01 | Test share | 🧪 QA | 1h | ⏳ |
| LANG-QA-01 | Test multi-language | 🧪 QA | 3h | ⏳ |

---

# 📊 TỔNG HỢP TOÀN DỰ ÁN

| Sprint | Goal | BE | FE | QA | SP | Status |
|--------|------|----|----|----|----|--------|
| 1 | Auth & User | 16 | 8 | 2 | 27 | ✅ |
| 2 | Products & Categories | 10 | 6 | 2 | 34 | ✅ |
| 3 | Orders & Payments | 10 | 6 | 2 | 33 | ✅ |
| 4 | Content & Orgs | 10 | 8 | 2 | 31 | ✅ |
| 5 | Dashboard & System | 13 | 11 | 3 | 44 | ✅ |
| 6 | Mobile API | 9 | 8 | 1 | 38 | ✅ |
| 7 | Reviews & Stats | 8 | 6 | 2 | 20 | ✅ |
| 8 | Auth Enhancement | 17 | 10 | 4 | 24 | ⏳ |
| 9 | Mobile Shopping | 17 | 15 | 4 | 34 | ⏳ |
| 10 | Order Tracking | 14 | 11 | 3 | 29 | ⏳ |
| 11 | Promotions | 14 | 12 | 3 | 29 | ⏳ |
| 12 | Chat & Support | 15 | 14 | 3 | 31 | ⏳ |
| 13 | Analytics | 15 | 11 | 3 | 28 | ⏳ |
| 14 | Advanced | 12 | 17 | 4 | 34 | ⏳ |
| **TOTAL** | | **180** | **143** | **38** | **436** | **50%** |

---

*Last updated: 05/02/2026*
