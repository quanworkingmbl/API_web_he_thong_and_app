"""
Custom exception handlers
"""
import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)

# Xác thực cho from như các trường email, name, user
# request: request mà client gửi lên (có thể lấy URL, method, headers...)
# exc: object lỗi validate chứa chi tiết lỗi
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors(xử lý Xác thực lỗi )"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation error",
            "errors": jsonable_encoder(exc.errors()),
        },
    )

# Nghĩa là lỗi kiểu business logic: user không tồn tại, sai mật khẩu, không đủ quyền,...
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
        },
    )
    

# Bug hệ thống Bug code DB down ,NoneType has no attribute ,Chia cho 0, Timeout
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    # Log full traceback để debug - luôn ghi vào server log
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}\n"
        f"{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if request.app.debug else None,
        },
    )   
""" 
Dùng để xử lý lỗi hệ thống (HTTP 500)
Ví dụ:
    DB bị down
    code bug NoneType has no attribute
    chia cho 0
    timeout API
    lỗi server bất ngờ
"""
