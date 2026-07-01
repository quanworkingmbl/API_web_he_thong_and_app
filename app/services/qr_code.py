"""
QRCodeService – Tạo mã QR truy xuất nguồn gốc sản phẩm

QR code sẽ chứa URL dạng:
    {FRONTEND_URL}/#/trace/{product_id}

Dùng Hash URL (#/) vì React web đang dùng createHashRouter.
"""

import qrcode
from io import BytesIO
from typing import Optional


class QRCodeService:

    @staticmethod
    def generate_product_trace_qr(
        product_id: int,
        base_url: str,
        batch_number: Optional[str] = None,
    ) -> BytesIO:
        """
        Tạo ảnh QR code PNG chứa URL trang truy xuất nguồn gốc sản phẩm.

        Args:
            product_id:   ID sản phẩm cần truy xuất
            base_url:     Domain frontend (vd: https://yourdomain.com)
            batch_number: Mã lô sản xuất (optional, thêm vào query string)

        Returns:
            BytesIO buffer chứa ảnh PNG sẵn sàng để trả về HTTP response
        """
        # Hash router → dùng /#/ để React xử lý được
        url = f"{base_url}/#/trace/{product_id}"
        if batch_number:
            url += f"?batch={batch_number}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # ~15% phục hồi lỗi
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
