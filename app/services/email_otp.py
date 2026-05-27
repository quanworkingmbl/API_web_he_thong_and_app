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
