"""
FCM Push Service – Gửi push notification qua Firebase Cloud Messaging (HTTP v1)

Thiết kế:
- Không dùng firebase-admin SDK (tránh dependency nặng)
- Dùng requests + Service Account JSON để lấy OAuth2 access token
- Hỗ trợ gửi đơn lẻ và gửi bulk (multicast)

Cài đặt:
1. Tạo file .env với FIREBASE_SA_JSON_PATH hoặc FIREBASE_SA_JSON
2. Download service account JSON từ Firebase Console → Project Settings → Service accounts

Config môi trường (.env):
    FIREBASE_PROJECT_ID=your-project-id
    FIREBASE_SA_JSON_PATH=/path/to/service-account.json
    # Hoặc inline base64:
    FIREBASE_SA_JSON={"type":"service_account", ...}
"""

import json
import logging
import os
import time
from typing import Optional, List

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lazy-load: tránh crash khi chưa cấu hình Firebase
# ─────────────────────────────────────────────────────────────────────────────
_ACCESS_TOKEN_CACHE: dict = {"token": None, "expires_at": 0}


def _get_sa_credentials() -> Optional[dict]:
    """Đọc Service Account JSON từ env."""
    raw = os.getenv("FIREBASE_SA_JSON")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    path = os.getenv("FIREBASE_SA_JSON_PATH")
    if path and os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return None


def _get_access_token() -> Optional[str]:
    """Lấy OAuth2 access token dùng JWT (Google Service Account)."""
    now = time.time()
    if _ACCESS_TOKEN_CACHE["token"] and now < _ACCESS_TOKEN_CACHE["expires_at"] - 60:
        return _ACCESS_TOKEN_CACHE["token"]

    creds = _get_sa_credentials()
    if not creds:
        logger.warning("[FCM] Service Account chưa được cấu hình. Set FIREBASE_SA_JSON_PATH hoặc FIREBASE_SA_JSON.")
        return None

    try:
        import base64
        import hashlib
        import hmac
        import urllib.request
        import urllib.parse

        # Tạo JWT thủ công để không cần google-auth
        header = {"alg": "RS256", "typ": "JWT"}
        issued_at = int(now)
        payload = {
            "iss": creds["client_email"],
            "scope": "https://www.googleapis.com/auth/firebase.messaging",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": issued_at,
            "exp": issued_at + 3600,
        }

        def b64(d: dict) -> str:
            return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()

        segments = f"{b64(header)}.{b64(payload)}"

        # Ký JWT bằng RSA private key (yêu cầu cryptography package)
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding

            private_key = serialization.load_pem_private_key(
                creds["private_key"].encode(), password=None
            )
            signature = private_key.sign(segments.encode(), padding.PKCS1v15(), hashes.SHA256())
            jwt = f"{segments}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"
        except ImportError:
            logger.error("[FCM] 'cryptography' package chưa được cài. Chạy: pip install cryptography")
            return None

        # Đổi JWT lấy access token
        data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt,
        }).encode()
        req = urllib.request.Request(
            "https://oauth2.googleapis.com/token", data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())

        token = result.get("access_token")
        expires_in = result.get("expires_in", 3600)
        _ACCESS_TOKEN_CACHE["token"] = token
        _ACCESS_TOKEN_CACHE["expires_at"] = now + expires_in
        return token

    except Exception as e:
        logger.error(f"[FCM] Lỗi lấy access token: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def send_fcm_push(
    token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    image_url: Optional[str] = None,
) -> bool:
    """
    Gửi push notification đến một FCM token cụ thể.

    Args:
        token: FCM device token của người nhận
        title: Tiêu đề thông báo
        body: Nội dung thông báo
        data: Dict key-value tùy ý gửi kèm (all values must be strings)
        image_url: URL ảnh thumbnail (optional)

    Returns:
        True nếu gửi thành công, False nếu thất bại
    """
    if not token:
        return False

    project_id = os.getenv("FIREBASE_PROJECT_ID")
    if not project_id:
        logger.debug("[FCM] FIREBASE_PROJECT_ID chưa cấu hình. Bỏ qua push.")
        return False

    access_token = _get_access_token()
    if not access_token:
        return False

    try:
        import urllib.request

        message: dict = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "android": {
                    "priority": "high",
                    "notification": {
                        "channel_id": "agrarian_default",
                        "sound": "default",
                        **({"image_url": image_url} if image_url else {}),
                    },
                },
                "apns": {
                    "payload": {
                        "aps": {
                            "alert": {"title": title, "body": body},
                            "sound": "default",
                            "badge": 1,
                        }
                    }
                },
            }
        }

        if data:
            # FCM data payload phải là dict[str, str]
            message["message"]["data"] = {k: str(v) for k, v in data.items()}

        payload = json.dumps(message).encode()
        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            logger.debug(f"[FCM] Sent OK: {result.get('name')}")
            return True

    except Exception as e:
        # Token hết hạn hoặc invalid → không raise, chỉ log
        logger.warning(f"[FCM] Gửi push thất bại: {e}")
        return False


def send_fcm_bulk(
    tokens: List[str],
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> dict:
    """
    Gửi push notification đến nhiều FCM tokens (sequential, không dùng multicast).

    Returns:
        {"sent": int, "failed": int}
    """
    sent, failed = 0, 0
    for token in tokens:
        if send_fcm_push(token, title, body, data):
            sent += 1
        else:
            failed += 1
    return {"sent": sent, "failed": failed}
