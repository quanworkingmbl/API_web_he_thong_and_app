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

