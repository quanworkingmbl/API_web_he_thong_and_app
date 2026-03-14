"""
VNPAY Payment Gateway Service
Tài liệu VNPAY: https://vnpay.vn/dich-vu-thanh-toan/
Sandbox: https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
"""

import hashlib
import hmac
import urllib.parse
from datetime import datetime
import os


class VNPayService:
    """Helper tích hợp cổng thanh toán VNPAY."""

    def __init__(self):
        self.tmn_code = os.getenv("VNPAY_TMN_CODE", "")
        self.hash_secret = os.getenv("VNPAY_HASH_SECRET", "")
        self.payment_url = os.getenv(
            "VNPAY_URL",
            "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
        )
        self.return_url = os.getenv("VNPAY_RETURN_URL", "http://localhost:8000/api/payments/vnpay/return")
        self.ipn_url = os.getenv("VNPAY_IPN_URL", "http://localhost:8000/api/payments/vnpay/ipn")

    def _build_secure_hash(self, params: dict) -> str:
        """Tạo secure hash theo chuẩn VNPAY (HMAC-SHA512)."""
        # Sắp xếp theo key alphabet
        sorted_params = sorted(params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        hash_value = hmac.new(
            self.hash_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()
        return hash_value

    def create_payment_url(
        self,
        order_id: int,
        amount: float,
        order_info: str,
        client_ip: str,
        locale: str = "vn"
    ) -> str:
        """
        Tạo URL thanh toán VNPAY.

        Args:
            order_id: ID đơn hàng
            amount: Số tiền (VND)
            order_info: Mô tả đơn hàng (ví dụ: "Thanh toan don hang #ORD-20240101")
            client_ip: IP của khách hàng
            locale: Ngôn ngữ ("vn" hoặc "en")

        Returns:
            URL redirect đến cổng thanh toán VNPAY
        """
        now = datetime.now()
        create_date = now.strftime("%Y%m%d%H%M%S")
        expire_date = now.replace(
            minute=now.minute + 15
        ).strftime("%Y%m%d%H%M%S")

        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(int(amount * 100)),  # Đơn vị: đồng × 100
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": f"{order_id}_{create_date}",  # Mã giao dịch unique
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "other",
            "vnp_Locale": locale,
            "vnp_ReturnUrl": self.return_url,
            "vnp_IpAddr": client_ip,
            "vnp_CreateDate": create_date,
            "vnp_ExpireDate": expire_date,
        }

        # Tạo secure hash
        secure_hash = self._build_secure_hash(params)
        params["vnp_SecureHash"] = secure_hash

        # Build URL
        query_string = urllib.parse.urlencode(params)
        payment_url = f"{self.payment_url}?{query_string}"
        return payment_url

    def verify_return_url(self, params: dict) -> dict:
        """
        Verify callback từ VNPAY (GET return URL hoặc IPN).

        Args:
            params: Query params từ VNPAY callback

        Returns:
            dict với `is_valid` (bool), `response_code`, `order_ref`, `amount`
        """
        # Lấy secure hash từ params
        vnp_secure_hash = params.get("vnp_SecureHash", "")

        # Loại bỏ hash params để verify
        verify_params = {
            k: v for k, v in params.items()
            if k not in ("vnp_SecureHash", "vnp_SecureHashType")
        }

        # Tính lại hash
        expected_hash = self._build_secure_hash(verify_params)
        is_valid = hmac.compare_digest(
            expected_hash.lower(),
            vnp_secure_hash.lower()
        )

        # Parse order_id từ TxnRef (format: "order_id_datetime")
        txn_ref = params.get("vnp_TxnRef", "")
        order_id = int(txn_ref.split("_")[0]) if txn_ref and "_" in txn_ref else None

        return {
            "is_valid": is_valid,
            "response_code": params.get("vnp_ResponseCode", ""),
            "transaction_status": params.get("vnp_TransactionStatus", ""),
            "order_id": order_id,
            "txn_ref": txn_ref,
            "amount": int(params.get("vnp_Amount", "0")) / 100,  # Chuyển về VND
            "bank_code": params.get("vnp_BankCode", ""),
            "transaction_no": params.get("vnp_TransactionNo", ""),
            "pay_date": params.get("vnp_PayDate", ""),
        }

    def is_payment_success(self, response_code: str, transaction_status: str) -> bool:
        """Kiểm tra giao dịch thành công."""
        return response_code == "00" and transaction_status == "00"


# Singleton instance
vnpay_service = VNPayService()
