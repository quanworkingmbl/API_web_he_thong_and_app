"""
VNPAY Payment Gateway Service
==============================
Tài liệu: https://sandbox.vnpayment.vn/apis/docs/thanh-toan-pay/pay.html
Sandbox:   https://sandbox.vnpayment.vn/paymentv2/vpcpay.html

Credentials (Sandbox):
  vnp_TmnCode  = 92AOP4PI
  vnp_HashSecret = 0D4P1LRI7K1BV36PGJE9UGRBQVKZGIA1

Lưu ý:
  - VNPAY Amount = số tiền VND × 100 (không có dấu phẩy/chấm)
  - Secure hash: HMAC-SHA512, sort key ASC (không encode dấu cách thành '+')
  - expire_date phải dùng timedelta, KHÔNG dùng datetime.replace (bug khi minute ≥ 45)
"""

import hashlib
import hmac
import urllib.parse
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


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
          2. Nối thành query string với urllib.parse.urlencode
             (safe='' để encode cả ký tự đặc biệt, dấu cách → %20 không phải +).
          3. HMAC-SHA512 với key = hash_secret (UTF-8).
        """
        # Lọc bỏ các params rỗng để tránh ảnh hưởng checksum
        filtered = {k: v for k, v in params.items() if v is not None and v != ""}
        sorted_params = sorted(filtered.items())
        # VNPAY yêu cầu dấu cách → %20, không dùng quote_plus
        query_string = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
        hash_value = hmac.new(
            self.hash_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()
        logger.debug("[VNPAY] hash_input=%s | hash=%s", query_string[:80] + "...", hash_value[:16] + "...")
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
        expire_minutes: int = 15,
    ) -> str:
        """
        Tạo URL thanh toán VNPAY.

        Args:
            order_id:       ID đơn hàng (dùng để tạo vnp_TxnRef unique)
            amount:         Số tiền VND (ví dụ: 100000.0)
            order_info:     Mô tả đơn hàng (ASCII, ≤ 255 ký tự)
            client_ip:      IP của khách hàng (bắt buộc theo VNPAY)
            locale:         "vn" hoặc "en"
            expire_minutes: Thời gian hết hạn URL (mặc định 15 phút)

        Returns:
            URL redirect đến cổng thanh toán VNPAY
        """
        now = datetime.now()
        create_date  = now.strftime("%Y%m%d%H%M%S")
        # ✅ FIX: dùng timedelta thay vì replace() để tránh crash khi minute ≥ 45
        expire_dt    = now + timedelta(minutes=expire_minutes)
        expire_date  = expire_dt.strftime("%Y%m%d%H%M%S")

        # vnp_TxnRef phải unique mỗi giao dịch — dùng order_id + timestamp
        txn_ref = f"{order_id}_{create_date}"

        params = {
            "vnp_Version":    "2.1.0",
            "vnp_Command":    "pay",
            "vnp_TmnCode":    self.tmn_code,
            "vnp_Amount":     str(int(amount * 100)),  # VNPAY: VND × 100
            "vnp_CurrCode":   "VND",
            "vnp_TxnRef":     txn_ref,
            "vnp_OrderInfo":  order_info[:255],         # giới hạn 255 ký tự
            "vnp_OrderType":  "other",
            "vnp_Locale":     locale,
            "vnp_ReturnUrl":  self.return_url,
            "vnp_IpAddr":     client_ip,
            "vnp_CreateDate": create_date,
            "vnp_ExpireDate": expire_date,
        }

        # Tạo secure hash và gắn vào params
        params["vnp_SecureHash"] = self._build_secure_hash(params)

        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        payment_url  = f"{self.payment_url}?{query_string}"

        logger.info(
            "[VNPAY] create_payment_url | order_id=%s | txn_ref=%s | amount=%s VND | expire=%s",
            order_id, txn_ref, amount, expire_date
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
