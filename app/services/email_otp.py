"""
app/services/email_otp.py
=========================
Email OTP Service — Gửi và xác thực mã OTP qua email.

Sử dụng:
  - Resend (resend.com)        : Gửi email OTP đẹp, đáng tin cậy
  - Upstash Redis (cloud)      : Lưu OTP tạm thời với TTL tự động

Luồng:
  1. send_otp(email, purpose)  → Tạo OTP → Lưu Redis (TTL 5 phút) → Gửi email
  2. verify_otp(email, otp)    → Lấy Redis → So sánh → Xóa nếu đúng
"""

import resend
import redis
import random
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Khởi tạo Resend ────────────────────────────────────────────────────────
resend.api_key = settings.RESEND_API_KEY

# ─── Khởi tạo Redis (Upstash TLS) ───────────────────────────────────────────
# Upstash dùng rediss:// (2 chữ s = TLS). ssl_cert_reqs="none" để bỏ verify cert.
_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            ssl_cert_reqs="none",   # Upstash self-signed cert
        )
    return _redis_client


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_otp() -> str:
    """Tạo mã OTP 6 chữ số ngẫu nhiên."""
    return str(random.randint(100000, 999999))


def _redis_key(email: str, purpose: str) -> str:
    """Key Redis: otp:{purpose}:{email_lowercase}"""
    return f"otp:{purpose}:{email.strip().lower()}"


def _subject(purpose: str) -> str:
    mapping = {
        "seller_register": "🔐 Mã xác thực đăng ký Seller — MBL CMS",
        "reset_password":  "🔑 Mã đặt lại mật khẩu — MBL CMS",
        "email_change":    "📧 Xác thực thay đổi email — MBL CMS",
    }
    return mapping.get(purpose, "🔐 Mã xác thực — MBL CMS")


def _purpose_label(purpose: str) -> str:
    mapping = {
        "seller_register": "đăng ký tài khoản Seller",
        "reset_password":  "đặt lại mật khẩu",
        "email_change":    "thay đổi địa chỉ email",
    }
    return mapping.get(purpose, "xác thực tài khoản")


# ─── GỬI OTP ─────────────────────────────────────────────────────────────────

def send_otp(email: str, purpose: str = "seller_register") -> dict:
    """
    Tạo OTP, lưu Redis với TTL, gửi email qua Resend.

    Args:
        email:   Email người nhận
        purpose: seller_register | reset_password | email_change

    Returns:
        {"success": True, "expires_in": 300}

    Raises:
        Exception nếu gửi email thất bại
    """
    otp = _make_otp()
    key = _redis_key(email, purpose)
    r   = _get_redis()

    # Lưu OTP vào Redis kèm số lần thử
    payload = json.dumps({"otp": otp, "attempts": 0})
    r.setex(key, settings.OTP_EXPIRE_SECONDS, payload)

    # Gửi email
    expire_min = settings.OTP_EXPIRE_SECONDS // 60
    try:
        resp = resend.Emails.send({
            "from":    f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to":      [email],
            "subject": _subject(purpose),
            "html":    _html_template(otp, purpose, expire_min),
        })
        logger.info("[OTP] Sent to %s | purpose=%s | id=%s", email, purpose, resp.get("id"))
    except Exception as exc:
        # Rollback: xóa OTP khỏi Redis nếu gửi thất bại
        r.delete(key)
        logger.error("[OTP] Failed to send email to %s: %s", email, exc)
        raise

    return {"success": True, "expires_in": settings.OTP_EXPIRE_SECONDS}


# ─── XÁC THỰC OTP ────────────────────────────────────────────────────────────

def verify_otp(email: str, otp_input: str, purpose: str = "seller_register") -> dict:
    """
    Xác thực mã OTP người dùng nhập.

    Returns:
        {"valid": True/False, "message": str}
    """
    key = _redis_key(email, purpose)
    r   = _get_redis()
    raw = r.get(key)

    if raw is None:
        return {"valid": False, "message": "Mã OTP đã hết hạn hoặc không tồn tại. Vui lòng yêu cầu mã mới."}

    data = json.loads(raw)

    # Vượt quá số lần thử → xóa luôn
    if data["attempts"] >= settings.OTP_MAX_ATTEMPTS:
        r.delete(key)
        return {
            "valid":   False,
            "message": f"Đã vượt quá {settings.OTP_MAX_ATTEMPTS} lần thử. Vui lòng yêu cầu mã mới.",
        }

    # Tăng counter attempts, ghi lại với TTL còn lại
    data["attempts"] += 1
    ttl = r.ttl(key)
    if ttl > 0:
        r.setex(key, ttl, json.dumps(data))

    if data["otp"] != otp_input.strip():
        remaining = settings.OTP_MAX_ATTEMPTS - data["attempts"]
        return {
            "valid":   False,
            "message": f"Mã OTP không đúng. Còn {remaining} lần thử.",
        }

    # ✅ Đúng → xóa OTP (dùng 1 lần duy nhất)
    r.delete(key)
    logger.info("[OTP] Verified OK for %s | purpose=%s", email, purpose)
    return {"valid": True, "message": "Xác thực thành công."}


# ─── HTML EMAIL TEMPLATE ──────────────────────────────────────────────────────

def _html_template(otp: str, purpose: str, expire_min: int) -> str:
    label = _purpose_label(purpose)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Mã xác thực OTP</title>
</head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:16px;overflow:hidden;
                    box-shadow:0 8px 32px rgba(0,0,0,0.10);">

        <!-- Header gradient -->
        <tr>
          <td style="background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);
                     padding:36px 40px;text-align:center;">
            <div style="font-size:32px;margin-bottom:8px;">🛍️</div>
            <h1 style="color:#ffffff;margin:0;font-size:22px;font-weight:700;
                       letter-spacing:0.5px;">MBL CMS</h1>
            <p style="color:rgba(255,255,255,0.80);margin:6px 0 0;font-size:13px;">
              Hệ thống quản lý bán hàng
            </p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px 40px 32px;text-align:center;">
            <p style="color:#374151;font-size:16px;margin:0 0 6px;">
              Mã xác thực cho việc
            </p>
            <p style="color:#111827;font-size:17px;font-weight:600;margin:0 0 28px;">
              {label}
            </p>

            <!-- OTP Box -->
            <div style="background:#f5f3ff;border:2px solid #8b5cf6;border-radius:14px;
                        padding:28px 32px;display:inline-block;margin-bottom:28px;">
              <span style="font-size:44px;font-weight:800;color:#4f46e5;
                           letter-spacing:14px;font-family:'Courier New',monospace;">
                {otp}
              </span>
            </div>

            <p style="color:#6b7280;font-size:14px;margin:0 0 8px;">
              ⏰ Mã có hiệu lực trong <strong style="color:#374151;">{expire_min} phút</strong>
            </p>
            <p style="color:#9ca3af;font-size:13px;margin:0;">
              Không chia sẻ mã này với bất kỳ ai.<br>
              Đội ngũ MBL CMS sẽ <strong>không bao giờ</strong> hỏi mã OTP của bạn.
            </p>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #f3f4f6;"></td></tr>

        <!-- Footer -->
        <tr>
          <td style="padding:20px 40px 28px;text-align:center;">
            <p style="color:#d1d5db;font-size:12px;margin:0;">
              Nếu bạn không yêu cầu mã này, hãy bỏ qua email này.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ─── GỬI EMAIL KYC SELLER ─────────────────────────────────────────────────────

def send_kyc_approved_email(
    email: str,
    seller_name: str,
    business_name: str,
    temp_password: str | None = None,
) -> dict:
    """Gửi email thông báo duyệt hồ sơ KYC seller thành công.
    
    Args:
        email:         Email người nhận (seller)
        seller_name:   Tên seller
        business_name: Tên hộ kinh doanh
        temp_password: Mật khẩu tạm do admin cấp (None = không gửi MK)
    """
    try:
        resp = resend.Emails.send({
            "from":    f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to":      [email],
            "subject": "🎉 Hồ sơ Seller đã được duyệt — MBL CMS",
            "html":    _kyc_approved_html(seller_name, business_name, email, temp_password),
        })
        logger.info("[KYC Email] Approved sent to %s | id=%s", email, resp.get("id"))
        return {"success": True}
    except Exception as exc:
        logger.error("[KYC Email] Failed approved email to %s: %s", email, exc)
        raise


def send_kyc_rejected_email(
    email: str,
    seller_name: str,
    rejection_reason: str,
) -> dict:
    """Gửi email thông báo từ chối hồ sơ KYC seller."""
    try:
        resp = resend.Emails.send({
            "from":    f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to":      [email],
            "subject": "❌ Hồ sơ Seller chưa được duyệt — MBL CMS",
            "html":    _kyc_rejected_html(seller_name, rejection_reason),
        })
        logger.info("[KYC Email] Rejected sent to %s | id=%s", email, resp.get("id"))
        return {"success": True}
    except Exception as exc:
        logger.error("[KYC Email] Failed rejected email to %s: %s", email, exc)
        raise


# ─── HTML TEMPLATES KYC ───────────────────────────────────────────────────────

def _kyc_approved_html(
    seller_name: str,
    business_name: str,
    email: str,
    temp_password: str | None,
) -> str:
    cms_url = settings.CMS_URL
    login_url = f"{cms_url}/login"
    reset_url = f"{cms_url}/reset-password"

    if temp_password:
        login_block = f"""
        <div style="background:#f6ffed;border:1.5px solid #b7eb8f;border-radius:12px;
                    padding:20px 24px;margin:20px 0;text-align:left;">
          <p style="font-size:13px;color:#555;margin:0 0 10px;font-weight:600;">🔐 Thông tin đăng nhập CMS</p>
          <table style="width:100%;font-size:14px;">
            <tr><td style="color:#888;padding:4px 0;width:140px;">Tài khoản (Email):</td>
                <td style="color:#111;font-weight:600;">{email}</td></tr>
            <tr><td style="color:#888;padding:4px 0;">Mật khẩu tạm:</td>
                <td><code style="background:#fff;border:1px solid #d9d9d9;border-radius:6px;
                               padding:3px 10px;font-size:15px;color:#4f46e5;font-weight:700;
                               letter-spacing:2px;">{temp_password}</code></td></tr>
          </table>
          <p style="font-size:12px;color:#d46b08;margin:10px 0 0;">
            ⚠️ Vui lòng đổi mật khẩu ngay sau khi đăng nhập lần đầu tiên.
          </p>
        </div>"""
    else:
        login_block = f"""
        <div style="background:#f6ffed;border:1.5px solid #b7eb8f;border-radius:12px;
                    padding:20px 24px;margin:20px 0;text-align:left;">
          <p style="font-size:13px;color:#555;margin:0 0 10px;font-weight:600;">🔐 Thông tin đăng nhập CMS</p>
          <table style="width:100%;font-size:14px;">
            <tr><td style="color:#888;padding:4px 0;width:140px;">Tài khoản (Email):</td>
                <td style="color:#111;font-weight:600;">{email}</td></tr>
            <tr><td style="color:#888;padding:4px 0;">Mật khẩu:</td>
                <td style="color:#555;font-size:13px;">Dùng mật khẩu ứng dụng hiện tại của bạn</td></tr>
          </table>
          <p style="font-size:12px;color:#1677ff;margin:10px 0 0;">
            🔑 Quên mật khẩu? <a href="{reset_url}" style="color:#1677ff;">Cập nhật tại đây</a>.
          </p>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>Hồ sơ Seller được duyệt</title></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 0;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:16px;overflow:hidden;
                  box-shadow:0 8px 32px rgba(0,0,0,.10);">
      <tr><td style="background:linear-gradient(135deg,#16a34a,#15803d);
                     padding:36px 40px;text-align:center;">
        <div style="font-size:40px;margin-bottom:8px;">🎉</div>
        <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">MBL CMS</h1>
        <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:14px;">Hệ thống quản lý bán hàng</p>
      </td></tr>
      <tr><td style="padding:36px 40px 28px;text-align:center;">
        <h2 style="color:#16a34a;font-size:20px;margin:0 0 8px;">Chúc mừng, {seller_name}!</h2>
        <p style="color:#374151;font-size:15px;margin:0 0 6px;">
          Hồ sơ đăng ký Seller của bạn đã <strong style="color:#16a34a;">được phê duyệt thành công</strong>!
        </p>
        <p style="color:#6b7280;font-size:14px;margin:0 0 20px;">
          Cơ sở kinh doanh: <strong style="color:#111;">{business_name}</strong>
        </p>
        {login_block}
        <a href="{login_url}"
           style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed);
                  color:#fff;font-size:15px;font-weight:700;text-decoration:none;
                  padding:14px 36px;border-radius:10px;margin:8px 0 20px;
                  box-shadow:0 4px 12px rgba(79,70,229,.35);">
          🚀 Vào Trang Quản Lý Ngay
        </a>
        <p style="color:#6b7280;font-size:13px;margin:0 0 4px;">
          Hoặc truy cập: <a href="{cms_url}" style="color:#4f46e5;">{cms_url}</a>
        </p>
        <hr style="border:none;border-top:1px solid #f3f4f6;margin:24px 0 16px;">
        <p style="color:#9ca3af;font-size:12px;margin:0;text-align:left;">
          Bạn có thể bắt đầu đăng sản phẩm và bán hàng ngay tại CMS.
        </p>
      </td></tr>
      <tr><td style="padding:16px 40px 24px;text-align:center;background:#f9fafb;">
        <p style="color:#d1d5db;font-size:12px;margin:0;">Email tự động từ MBL CMS. Vui lòng không trả lời.</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


# ─── GỬI EMAIL THAY ĐỔI TRẠNG THÁI TÀI KHOẢN ────────────────────────────────

def send_user_status_change_email(
    email: str,
    user_name: str,
    new_status: str,
    reason: str | None = None,
    expire_at: str | None = None,
) -> dict:
    """Gửi email thông báo khi admin thay đổi trạng thái tài khoản (SUSPENDED/BANNED/ACTIVE).

    Args:
        email:      Email người nhận
        user_name:  Tên người dùng
        new_status: ACTIVE | SUSPENDED | BANNED
        reason:     Lý do thay đổi (bắt buộc với SUSPENDED/BANNED)
        expire_at:  Thời hạn tạm khóa (ISO string, chỉ dùng với SUSPENDED)
    """
    status_upper = (new_status or "").upper()
    if status_upper == "ACTIVE":
        subject = "✅ Tài khoản của bạn đã được mở khóa — MBL CMS"
    elif status_upper == "SUSPENDED":
        subject = "⚠️ Tài khoản của bạn bị tạm khóa — MBL CMS"
    else:
        subject = "🚫 Tài khoản của bạn bị khóa vĩnh viễn — MBL CMS"

    try:
        resp = resend.Emails.send({
            "from":    f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to":      [email],
            "subject": subject,
            "html":    _user_status_change_html(user_name, status_upper, reason, expire_at),
        })
        logger.info("[Status Email] Sent to %s | status=%s | id=%s", email, new_status, resp.get("id"))
        return {"success": True}
    except Exception as exc:
        logger.error("[Status Email] Failed to send to %s: %s", email, exc)
        raise


def _user_status_change_html(
    user_name: str,
    status: str,
    reason: str | None,
    expire_at: str | None,
) -> str:
    cms_url = settings.CMS_URL

    if status == "ACTIVE":
        header_bg = "linear-gradient(135deg,#16a34a,#15803d)"
        icon = "✅"
        header_title = "Tài khoản đã được mở khóa"
        main_color = "#16a34a"
        body_msg = f"Tài khoản của bạn (<strong>{user_name}</strong>) đã được <strong style='color:#16a34a;'>mở khóa</strong> và có thể sử dụng bình thường."
        extra_block = f"""
        <div style="background:#f6ffed;border:1.5px solid #b7eb8f;border-radius:12px;
                    padding:18px 22px;text-align:left;margin:20px 0;">
          <p style="font-size:14px;color:#374151;margin:0;line-height:1.7;">
            Bạn có thể đăng nhập lại vào hệ thống ngay bây giờ.
          </p>
        </div>
        <a href="{cms_url}"
           style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed);
                  color:#fff;font-size:15px;font-weight:700;text-decoration:none;
                  padding:14px 36px;border-radius:10px;margin:8px 0 20px;
                  box-shadow:0 4px 12px rgba(79,70,229,.35);">
          Đăng nhập ngay
        </a>"""
    elif status == "SUSPENDED":
        header_bg = "linear-gradient(135deg,#d97706,#b45309)"
        icon = "⚠️"
        header_title = "Tài khoản bị tạm khóa"
        main_color = "#d97706"
        expire_info = f"<br><strong>Thời hạn khóa:</strong> {expire_at}" if expire_at else ""
        body_msg = f"Tài khoản của bạn (<strong>{user_name}</strong>) đã bị <strong style='color:#d97706;'>tạm khóa</strong>."
        reason_display = reason or "Không có lý do cụ thể"
        extra_block = f"""
        <div style="background:#fffbeb;border:1.5px solid #fde68a;border-radius:12px;
                    padding:18px 22px;text-align:left;margin:20px 0;">
          <p style="font-size:13px;color:#92400e;font-weight:700;margin:0 0 8px;">📋 Chi tiết:</p>
          <p style="font-size:14px;color:#374151;margin:0;line-height:1.7;">
            <strong>Lý do:</strong> {reason_display}{expire_info}
          </p>
        </div>
        <div style="background:#fefce8;border:1.5px solid #fde047;border-radius:12px;
                    padding:14px 18px;text-align:left;margin-bottom:20px;">
          <p style="font-size:13px;color:#713f12;margin:0;line-height:1.6;">
            💡 Nếu bạn cho rằng đây là nhầm lẫn, vui lòng liên hệ quản trị viên qua email này.
          </p>
        </div>"""
    else:
        header_bg = "linear-gradient(135deg,#dc2626,#b91c1c)"
        icon = "🚫"
        header_title = "Tài khoản bị khóa vĩnh viễn"
        main_color = "#dc2626"
        body_msg = f"Tài khoản của bạn (<strong>{user_name}</strong>) đã bị <strong style='color:#dc2626;'>khóa vĩnh viễn</strong>."
        reason_display = reason or "Không có lý do cụ thể"
        extra_block = f"""
        <div style="background:#fff2f0;border:1.5px solid #fca5a5;border-radius:12px;
                    padding:18px 22px;text-align:left;margin:20px 0;">
          <p style="font-size:13px;color:#dc2626;font-weight:700;margin:0 0 8px;">❌ Lý do khóa:</p>
          <p style="font-size:14px;color:#374151;margin:0;line-height:1.7;">{reason_display}</p>
        </div>
        <div style="background:#fff7ed;border:1.5px solid #fed7aa;border-radius:12px;
                    padding:14px 18px;text-align:left;margin-bottom:20px;">
          <p style="font-size:13px;color:#9a3412;margin:0;line-height:1.6;">
            💡 Nếu bạn cần khiếu nại, vui lòng phản hồi email này để liên hệ với quản trị viên.
          </p>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>Thông báo trạng thái tài khoản</title></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 0;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:16px;overflow:hidden;
                  box-shadow:0 8px 32px rgba(0,0,0,.10);">
      <tr><td style="background:{header_bg};padding:36px 40px;text-align:center;">
        <div style="font-size:40px;margin-bottom:8px;">{icon}</div>
        <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">MBL CMS</h1>
        <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:14px;">Thông báo tài khoản</p>
      </td></tr>
      <tr><td style="padding:36px 40px 28px;text-align:center;">
        <h2 style="color:{main_color};font-size:20px;margin:0 0 12px;">{header_title}</h2>
        <p style="color:#374151;font-size:15px;margin:0 0 4px;">{body_msg}</p>
        {extra_block}
        <hr style="border:none;border-top:1px solid #f3f4f6;margin:20px 0 14px;">
        <p style="color:#9ca3af;font-size:12px;margin:0;text-align:left;">
          Email này được gửi tự động từ hệ thống MBL CMS. Vui lòng không trả lời trực tiếp.
        </p>
      </td></tr>
      <tr><td style="padding:16px 40px 24px;text-align:center;background:#f9fafb;">
        <p style="color:#d1d5db;font-size:12px;margin:0;">© MBL CMS — Hệ thống quản lý bán hàng nông sản</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


def _kyc_rejected_html(seller_name: str, rejection_reason: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<title>Hồ sơ Seller chưa được duyệt</title></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 0;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#fff;border-radius:16px;overflow:hidden;
                  box-shadow:0 8px 32px rgba(0,0,0,.10);">
      <tr><td style="background:linear-gradient(135deg,#dc2626,#b91c1c);
                     padding:36px 40px;text-align:center;">
        <div style="font-size:40px;margin-bottom:8px;">📋</div>
        <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">MBL CMS</h1>
        <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:14px;">Thông báo kết quả hồ sơ</p>
      </td></tr>
      <tr><td style="padding:36px 40px 28px;text-align:center;">
        <h2 style="color:#dc2626;font-size:20px;margin:0 0 8px;">Xin chào {seller_name},</h2>
        <p style="color:#374151;font-size:15px;margin:0 0 20px;">
          Hồ sơ đăng ký Seller của bạn <strong style="color:#dc2626;">chưa được phê duyệt</strong>.
        </p>
        <div style="background:#fff7f7;border:1.5px solid #fca5a5;border-radius:12px;
                    padding:20px 24px;text-align:left;margin-bottom:20px;">
          <p style="font-size:13px;color:#dc2626;font-weight:700;margin:0 0 8px;">❌ Lý do từ chối:</p>
          <p style="font-size:14px;color:#374151;margin:0;line-height:1.6;">{rejection_reason}</p>
        </div>
        <div style="background:#fffbeb;border:1.5px solid #fde68a;border-radius:12px;
                    padding:20px 24px;text-align:left;margin-bottom:20px;">
          <p style="font-size:13px;color:#92400e;font-weight:700;margin:0 0 8px;">💡 Bước tiếp theo:</p>
          <p style="font-size:14px;color:#374151;margin:0;line-height:1.6;">
            Mở ứng dụng và vào phần <strong>Hồ sơ Seller</strong> để bổ sung thông tin và nộp lại.
          </p>
        </div>
        <hr style="border:none;border-top:1px solid #f3f4f6;margin:20px 0 16px;">
        <p style="color:#9ca3af;font-size:12px;margin:0;text-align:left;">
          Liên hệ đội ngũ nếu cần hỗ trợ.
        </p>
      </td></tr>
      <tr><td style="padding:16px 40px 24px;text-align:center;background:#f9fafb;">
        <p style="color:#d1d5db;font-size:12px;margin:0;">© MBL CMS — Hệ thống quản lý bán hàng nông sản</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""
