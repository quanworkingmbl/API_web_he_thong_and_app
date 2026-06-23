"""
Custom middleware for logging, error handling, etc.
"""
import time
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

logger = logging.getLogger(__name__)

# Paths that are excluded from X-Quan-Secret check
_PUBLIC_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}

# VNPAY callback paths – VNPAY Gateway and browser never send X-Quan-Secret
# Covers both /payments/ and /deposit/ VNPAY callbacks
_VNPAY_CALLBACK_PREFIXES = (
    "/api/payments/vnpay/ipn",
    "/api/payments/vnpay/return",
    "/api/deposit/vnpay/ipn",
    "/api/deposit/vnpay/return",
)

# Public API paths – accessed by end-users without app credentials
# (e.g. customers scanning QR codes to view product traceability)
_PUBLIC_API_PREFIXES = (
    "/api/traceability/",
)

class ApiSecretMiddleware(BaseHTTPMiddleware):
    """Middleware that validates the X-Quan-Secret header on every request.
    
    Public paths (/, /health, /docs, /redoc, /openapi.json) are exempted.
    All other requests must include:
        X-Quan-Secret: <API_SECRET_KEY>
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow preflight CORS requests through
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip check for public paths
        if path in _PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
            return await call_next(request)

        # Skip check for VNPAY callback paths (IPN + return URL)
        # VNPAY Gateway never sends custom headers – exempting these prevents 403
        if any(path.startswith(prefix) for prefix in _VNPAY_CALLBACK_PREFIXES):
            return await call_next(request)

        # Skip check for public API paths (e.g. traceability for QR scan customers)
        if any(path.startswith(prefix) for prefix in _PUBLIC_API_PREFIXES):
            return await call_next(request)

        secret = request.headers.get("X-Quan-Secret")
        if not secret or secret != settings.API_SECRET_KEY:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "Forbidden: Invalid or missing X-Quan-Secret header."},
            )

        return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate process time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Add process time to response header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

