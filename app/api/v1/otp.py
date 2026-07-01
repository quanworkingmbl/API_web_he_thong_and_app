"""
app/api/v1/otp.py
=================
OTP Endpoints — Gửi và xác thực mã OTP qua email.

Endpoints:
  POST /api/v1/otp/send    → Gửi OTP đến email
  POST /api/v1/otp/verify  → Xác thực mã OTP người dùng nhập

Dùng cho:
  - Đăng ký tài khoản Seller  (purpose: seller_register)
  - Đặt lại mật khẩu          (purpose: reset_password)
  - Thay đổi email             (purpose: email_change)
"""

import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from app.services.email_otp import send_otp, verify_otp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/otp", tags=["📧 OTP Verification"])

# ─── Cho phép các purpose hợp lệ ─────────────────────────────────────────────
VALID_PURPOSES = {"seller_register", "reset_password", "email_change"}


# ─── Request Schemas ──────────────────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    email:   EmailStr
    purpose: str = "seller_register"

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v: str) -> str:
        if v not in VALID_PURPOSES:
            raise ValueError(f"purpose phải là một trong: {', '.join(VALID_PURPOSES)}")
        return v


class VerifyOTPRequest(BaseModel):
    email:   EmailStr
    otp:     str
    purpose: str = "seller_register"

    @field_validator("otp")
    @classmethod
    def validate_otp_format(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Mã OTP phải là 6 chữ số.")
        return v

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v: str) -> str:
        if v not in VALID_PURPOSES:
            raise ValueError(f"purpose phải là một trong: {', '.join(VALID_PURPOSES)}")
        return v


# ─── Response Schemas ─────────────────────────────────────────────────────────

class SendOTPResponse(BaseModel):
    success:    bool
    message:    str
    expires_in: int   # Seconds


class VerifyOTPResponse(BaseModel):
    valid:   bool
    message: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/send",
    response_model=SendOTPResponse,
    summary="Gửi mã OTP qua email",
    description="Tạo mã OTP 6 số và gửi đến email. Mã có hiệu lực 5 phút.",
)
async def send_otp_endpoint(body: SendOTPRequest):
    """
    Gửi OTP đến email người dùng.

    - **email**: Địa chỉ email nhận mã
    - **purpose**: Mục đích (seller_register / reset_password / email_change)
    """
    try:
        result = send_otp(str(body.email), body.purpose)
        return SendOTPResponse(
            success=True,
            message=f"Mã OTP đã được gửi đến {body.email}. Kiểm tra hộp thư (kể cả Spam).",
            expires_in=result["expires_in"],
        )
    except Exception as exc:
        logger.error("[OTP API] send failed for %s: %s", body.email, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể gửi email lúc này. Vui lòng thử lại sau.",
        )


@router.post(
    "/verify",
    response_model=VerifyOTPResponse,
    summary="Xác thực mã OTP",
    description="Kiểm tra mã OTP người dùng nhập có khớp không. Mã chỉ dùng được 1 lần.",
)
async def verify_otp_endpoint(body: VerifyOTPRequest):
    """
    Xác thực mã OTP.

    - **email**: Email đã nhận OTP
    - **otp**: Mã 6 số người dùng nhập
    - **purpose**: Phải khớp với purpose khi gọi /send
    """
    result = verify_otp(str(body.email), body.otp, body.purpose)
    if not result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"],
        )
    return VerifyOTPResponse(valid=True, message=result["message"])
