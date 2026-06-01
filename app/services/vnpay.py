"""
VNPAY Payment Gateway Service
==============================
Tài liệu: https://sandbox.vnpayment.vn/apis/docs/thanh-toan-pay/pay.html
Sandbox:   https://sandbox.vnpayment.vn/paymentv2/vpcpay.html

Credentials (Sandbox): xem VNPAY_TMN_CODE / VNPAY_HASH_SECRET trong .env

Lưu ý:
  - VNPAY Amount = số tiền VND × 100 (không có dấu phẩy/chấm)
  - Secure hash: HMAC-SHA512, sort key ASC (không encode dấu cách thành '+')
  - expire_date phải dùng timedelta, KHÔNG dùng datetime.replace (bug khi minute ≥ 45)
"""

import hashlib
import hmac
import urllib.parse
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from fastapi import Request

# Múi giờ Việt Nam UTC+7
_TZ_VN = timezone(timedelta(hours=7))

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """IP client thực (Cloud Run / Cloudflare: X-Forwarded-For)."""
    xff = request.headers.get("X-Forwarded-For", "")
    real_ip = request.headers.get("X-Real-IP", "")
    if xff:
        ip = xff.split(",")[0].strip()
    elif real_ip:
        ip = real_ip.strip()
    elif request.client:
        ip = request.client.host
    else:
        ip = "127.0.0.1"
    return ip


class VNPayService:
    """Helper tích hợp cổng thanh toán VNPAY."""

    def __init__(self):
        self.tmn_code   = os.getenv("VNPAY_TMN_CODE", "")
        self.hash_secret = os.getenv("VNPAY_HASH_SECRET", "")
        self.payment_url = os.getenv(
            "VNPAY_URL",
            "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
        )
        self.return_url = os.getenv(
            "VNPAY_RETURN_URL",
            "https://api.quancmsbe.site/api/payments/vnpay/return"
        )
        self.ipn_url = os.getenv(
            "VNPAY_IPN_URL",
            "https://api.quancmsbe.site/api/payments/vnpay/ipn"
        )
        self.app_deep_link_scheme = os.getenv("VNPAY_APP_DEEP_LINK_SCHEME", "agrarian")

        if not self.tmn_code or not self.hash_secret:
            logger.warning(
                "[VNPAY] VNPAY_TMN_CODE hoặc VNPAY_HASH_SECRET chưa được cấu hình trong .env!"
            )

    # ──────────────────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def _build_secure_hash(self, params: dict) -> str:
        """
        Tạo secure hash theo chuẩn VNPAY (HMAC-SHA512).

        Quy tắc:
          1. Sắp xếp params theo key tăng dần (A-Z).
          2. Nối thành query string với urllib.parse.quote_plus
             (VNPAY server dùng PHP urlencode: spaces → '+', không phải '%20').
          3. HMAC-SHA512 với key = hash_secret (UTF-8).
        """
        # Lọc bỏ các params rỗng để tránh ảnh hưởng checksum
        filtered = {k: v for k, v in params.items() if v is not None and v != ""}
        sorted_params = sorted(filtered.items())
        # FIX: VNPAY dùng quote_plus (spaces→'+'), không phải quote (spaces→'%20')
        query_string = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote_plus)
        hash_value = hmac.new(
            self.hash_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()
        # LOG INFO để thấy trong Cloud Run (thay vì debug)
        logger.info("[VNPAY] hash_input_full=%s", query_string)
        logger.info("[VNPAY] hash_value=%s", hash_value)
        return hash_value

    # ──────────────────────────────────────────────────────────────────────────
    # CREATE PAYMENT URL
    # ──────────────────────────────────────────────────────────────────────────

    def create_payment_url(
        self,
        order_id: int,
        amount: float,
        order_info: str,
        client_ip: str,
        locale: str = "vn",
        expire_minutes: int = 20,
        return_url: Optional[str] = None,
        txn_ref: Optional[str] = None,
    ) -> str:
        """
        Tạo URL thanh toán VNPAY.

        Args:
            order_id:       ID đơn hàng (dùng để tạo vnp_TxnRef unique)
            amount:         Số tiền VND (ví dụ: 100000.0)
            order_info:     Mô tả đơn hàng (ASCII, ≤ 255 ký tự)
            client_ip:      IP của khách hàng (bắt buộc theo VNPAY)
            locale:         "vn" hoặc "en"
            expire_minutes: Thời gian hết hạn URL (mặc định 20 phút)
            return_url:     Override vnp_ReturnUrl (phải set trước khi ký hash)
            txn_ref:        Override vnp_TxnRef (mặc định: {order_id}_{create_date})

        Returns:
            URL redirect đến cổng thanh toán VNPAY
        """
        # ✅ VNPAY Sandbox yêu cầu thời gian UTC+7 (giờ Việt Nam)
        #    Nếu gửi UTC (kém 7 tiếng) → VNPAY thấy giao dịch đã "hết hạn" → timeout ngay lập tức
        now = datetime.now(_TZ_VN)
        create_date  = now.strftime("%Y%m%d%H%M%S")
        # ✅ FIX: dùng timedelta thay vì replace() để tránh crash khi minute ≥ 45
        expire_dt    = now + timedelta(minutes=expire_minutes)
        expire_date  = expire_dt.strftime("%Y%m%d%H%M%S")

        # vnp_TxnRef phải unique mỗi giao dịch
        if not txn_ref:
            txn_ref = f"{order_id}_{create_date}"

        # FIX: Sanitize order_info — chỉ giữ ASCII để tránh encoding khác biệt
        safe_order_info = order_info[:255].encode("ascii", errors="replace").decode("ascii")

        # FIX: Đảm bảo IP là IPv4 hợp lệ (không phải IPv6 như ::1 hay ::ffff:x.x.x.x)
        safe_ip = client_ip
        if ":" in client_ip:  # IPv6
            if client_ip.startswith("::ffff:"):
                safe_ip = client_ip[7:]   # lấy phần IPv4 sau prefix
            else:
                safe_ip = "127.0.0.1"    # fallback

        params = {
            "vnp_Version":    "2.1.0",
            "vnp_Command":    "pay",
            "vnp_TmnCode":    self.tmn_code,
            "vnp_Amount":     str(int(amount * 100)),  # VNPAY: VND × 100
            "vnp_CurrCode":   "VND",
            "vnp_TxnRef":     txn_ref,
            "vnp_OrderInfo":  safe_order_info,
            "vnp_OrderType":  "other",
            "vnp_Locale":     locale,
            "vnp_ReturnUrl":  return_url or self.return_url,
            "vnp_IpAddr":     safe_ip,
            "vnp_CreateDate": create_date,
            "vnp_ExpireDate": expire_date,
        }

        # Tạo secure hash và gắn vào params
        params["vnp_SecureHash"] = self._build_secure_hash(params)

        # FIX: Dùng cùng quote_plus để URL nhất quán với hash
        # VNPay server sẽ decode URL → re-encode bằng PHP urlencode (=quote_plus) → so khớp hash
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
        payment_url  = f"{self.payment_url}?{query_string}"

        logger.info(
            "[VNPAY] payment_url=%s",
            payment_url
        )
        return payment_url

    # ──────────────────────────────────────────────────────────────────────────
    # VERIFY RETURN / IPN
    # ──────────────────────────────────────────────────────────────────────────

    def verify_return_url(self, params: dict) -> dict:
        """
        Verify callback từ VNPAY (GET return URL hoặc IPN POST query params).

        Args:
            params: Query params từ VNPAY callback (dict)

        Returns:
            dict chứa:
              is_valid        (bool)  – chữ ký hợp lệ
              response_code   (str)   – vnp_ResponseCode
              transaction_status (str)
              order_id        (int | None)
              txn_ref         (str)
              amount          (float) – Số tiền VND thực (đã chia 100)
              bank_code       (str)
              transaction_no  (str)
              pay_date        (str)
        """
        vnp_secure_hash = params.get("vnp_SecureHash", "")

        # Loại bỏ hash params trước khi tính lại
        verify_params = {
            k: v for k, v in params.items()
            if k not in ("vnp_SecureHash", "vnp_SecureHashType")
        }

        expected_hash = self._build_secure_hash(verify_params)
        is_valid = hmac.compare_digest(
            expected_hash.lower(),
            vnp_secure_hash.lower()
        )

        if not is_valid:
            logger.warning(
                "[VNPAY] Invalid signature! Expected=%s | Got=%s",
                expected_hash[:20], vnp_secure_hash[:20]
            )

        # Parse order_id từ TxnRef (format: "order_id_YYYYMMDDHHMMSS")
        txn_ref  = params.get("vnp_TxnRef", "")
        order_id = None
        if txn_ref and "_" in txn_ref:
            try:
                order_id = int(txn_ref.split("_")[0])
            except (ValueError, IndexError):
                logger.warning("[VNPAY] Cannot parse order_id from txn_ref: %s", txn_ref)

        # VNPAY trả amount × 100 → chia 100 để lấy VND thực
        try:
            raw_amount = int(params.get("vnp_Amount", "0"))
            amount_vnd = raw_amount / 100
        except (ValueError, TypeError):
            amount_vnd = 0.0

        return {
            "is_valid":          is_valid,
            "response_code":     params.get("vnp_ResponseCode", ""),
            "transaction_status": params.get("vnp_TransactionStatus", ""),
            "order_id":          order_id,
            "txn_ref":           txn_ref,
            "amount":            amount_vnd,
            "bank_code":         params.get("vnp_BankCode", ""),
            "transaction_no":    params.get("vnp_TransactionNo", ""),
            "pay_date":          params.get("vnp_PayDate", ""),
            "card_type":         params.get("vnp_CardType", ""),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def is_payment_success(self, response_code: str, transaction_status: str) -> bool:
        """
        Giao dịch thành công khi:
          - vnp_ResponseCode == "00"  (VNPAY xác nhận)
          - vnp_TransactionStatus == "00"  (Merchant xác nhận)
        """
        return response_code == "00" and transaction_status == "00"

    def build_deep_link(self, success: bool, order_id: int | None,
                        payment_id: int | None = None,
                        response_code: str = "") -> str:
        """
        Tạo deep link về Flutter App sau khi thanh toán.

        Format: agrarian://payment/vnpay/result?status=success&order_id=123&...
        """
        status = "success" if success else "failed"
        params = {"status": status}
        if order_id:
            params["order_id"] = str(order_id)
        if payment_id:
            params["payment_id"] = str(payment_id)
        if response_code and not success:
            params["code"] = response_code

        qs = urllib.parse.urlencode(params)
        return f"{self.app_deep_link_scheme}://payment/vnpay/result?{qs}"


# Singleton instance
vnpay_service = VNPayService()
