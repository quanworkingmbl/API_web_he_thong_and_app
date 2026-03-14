"""
GHN (Giao Hàng Nhanh) Shipping Service
API Docs: https://api.ghn.vn/home/docs/detail

Môi trường Sandbox: https://dev-online-gateway.ghn.vn
Môi trường Production: https://online-gateway.ghn.vn
"""

import os
import httpx
from typing import Optional


class GHNService:
    """Wrapper cho GHN Shipping API."""

    def __init__(self):
        self.token = os.getenv("GHN_TOKEN", "")
        self.shop_id = os.getenv("GHN_SHOP_ID", "")
        self.base_url = os.getenv(
            "GHN_URL",
            "https://dev-online-gateway.ghn.vn/shiip/public-api"
        )

    @property
    def _headers(self) -> dict:
        return {
            "Token": self.token,
            "ShopId": str(self.shop_id),
            "Content-Type": "application/json"
        }

    async def calculate_fee(
        self,
        to_district_id: int,
        to_ward_code: str,
        weight: int = 500,
        from_district_id: int = 1454,  # Default: Quận 1, HCM
        service_type_id: int = 2  # 2 = Standard Express
    ) -> dict:
        """
        Tính phí vận chuyển GHN.

        Args:
            to_district_id: Mã quận/huyện người nhận (GHN district ID)
            to_ward_code: Mã phường/xã người nhận
            weight: Trọng lượng gói hàng (gram)
            from_district_id: Mã quận/huyện người gửi
            service_type_id: Loại dịch vụ GHN

        Returns:
            dict với `fee`, `expected_delivery_time`
        """
        if not self.token:
            # Trả về phí mặc định nếu chưa config GHN
            return {
                "success": True,
                "fee": 30000,
                "expected_delivery_time": None,
                "note": "Using default fee (GHN not configured)"
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/v2/shipping-order/available-services",
                    headers=self._headers,
                    params={
                        "shop_id": int(self.shop_id),
                        "from_district": from_district_id,
                        "to_district": to_district_id
                    }
                )
                resp.raise_for_status()
                services = resp.json().get("data", [])

                if not services:
                    return {"success": False, "error": "Không tìm thấy dịch vụ vận chuyển phù hợp"}

                service_id = services[0]["service_id"]

                # Tính phí
                fee_resp = await client.post(
                    f"{self.base_url}/v2/shipping-order/fee",
                    headers=self._headers,
                    json={
                        "service_id": service_id,
                        "insurance_value": 0,
                        "from_district_id": from_district_id,
                        "to_district_id": to_district_id,
                        "to_ward_code": to_ward_code,
                        "weight": weight
                    }
                )
                fee_resp.raise_for_status()
                fee_data = fee_resp.json().get("data", {})

                return {
                    "success": True,
                    "service_id": service_id,
                    "fee": fee_data.get("total", 30000),
                    "expected_delivery_time": fee_data.get("expected_delivery_time")
                }

        except httpx.HTTPError as e:
            return {"success": False, "error": str(e), "fee": 30000}

    async def create_order(self, order_data: dict) -> dict:
        """
        Tạo vận đơn trên GHN.

        Args:
            order_data: Thông tin đơn hàng GHN format

        Returns:
            dict với `order_code`, `expected_delivery_time`, `fee`
        """
        if not self.token:
            # Trả về mock data nếu chưa config
            import uuid
            return {
                "success": True,
                "order_code": f"GHN-MOCK-{uuid.uuid4().hex[:8].upper()}",
                "expected_delivery_time": None,
                "fee": 30000,
                "note": "Mock order (GHN not configured)"
            }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.base_url}/v2/shipping-order/create",
                    headers=self._headers,
                    json=order_data
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                return {
                    "success": True,
                    "order_code": data.get("order_code"),
                    "expected_delivery_time": data.get("expected_delivery_time"),
                    "fee": data.get("total_fee", 30000)
                }
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    async def get_tracking(self, order_code: str) -> dict:
        """
        Tra cứu trạng thái vận đơn GHN.

        Args:
            order_code: Mã vận đơn GHN

        Returns:
            dict với status, log list
        """
        if not self.token:
            return {
                "success": True,
                "status": "MOCK_TRACKING",
                "logs": [],
                "note": "Mock tracking (GHN not configured)"
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.base_url}/v2/shipping-order/detail",
                    headers=self._headers,
                    json={"order_code": order_code}
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                return {
                    "success": True,
                    "order_code": order_code,
                    "status": data.get("status"),
                    "current_status": data.get("status_name"),
                    "logs": data.get("log", []),
                    "estimated_delivery": data.get("leadtime")
                }
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}


# Singleton instance
ghn_service = GHNService()
