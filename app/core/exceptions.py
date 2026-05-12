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


def _add_cors_headers(response: JSONResponse, request: Request) -> JSONResponse:
    """
    Thêm CORS headers vào error response.
    CORSMiddleware của Starlette KHÔNG tự động thêm CORS headers vào error responses
    được tạo bởi exception handlers — phải thêm thủ công tại đây.
    """
    try:
        from app.core.config import settings
        origin = request.headers.get("origin", "")
        allowed = settings.cors_origins_list
        # Nếu origin hợp lệ → echo lại đúng origin, nếu không → trả về origin đầu tiên trong list
        if origin in allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in allowed:
            response.headers["Access-Control-Allow-Origin"] = "*"
        # Không thêm header nếu origin không hợp lệ (tránh lỗi bảo mật)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Vary"] = "Origin"
    except Exception:
        pass  # Không để lỗi CORS phá vỡ error response gốc
    return response


# Xác thực cho from như các trường email, name, user
# request: request mà client gửi lên (có thể lấy URL, method, headers...)
# exc: object lỗi validate chứa chi tiết lỗi
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors(xử lý Xác thực lỗi )"""
    response = JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation error",
            "errors": jsonable_encoder(exc.errors()),
        },
    )
    return _add_cors_headers(response, request)

# Nghĩa là lỗi kiểu business logic: user không tồn tại, sai mật khẩu, không đủ quyền,...
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
        },
    )
    return _add_cors_headers(response, request)
    

# Bug hệ thống Bug code DB down ,NoneType has no attribute ,Chia cho 0, Timeout
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    # Log full traceback để debug - luôn ghi vào server log
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}\n"
        f"{traceback.format_exc()}"
    )
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if request.app.debug else None,
        },
    )
    return _add_cors_headers(response, request)
""" 
Dùng để xử lý lỗi hệ thống (HTTP 500)
Ví dụ:
    DB bị down
    code bug NoneType has no attribute
    chia cho 0
    timeout API
    lỗi server bất ngờ
"""
