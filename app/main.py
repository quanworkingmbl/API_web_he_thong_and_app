from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1 import api_router
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.core.middleware import LoggingMiddleware, ApiSecretMiddleware
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    # title, version information API
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    
    docs_url="/docs" if settings.SHOW_DOCS else None,       # Dùng SHOW_DOCS, độc lập với DEBUG
    redoc_url="/redoc" if settings.SHOW_DOCS else None,     # Dùng SHOW_DOCS, độc lập với DEBUG
    openapi_url="/openapi.json" if settings.SHOW_DOCS else None,  # Dùng SHOW_DOCS, độc lập với DEBUG
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# API Secret Header Middleware
# NOTE: FastAPI/Starlette uses LIFO order — middleware added FIRST runs LAST.
# So: ApiSecretMiddleware added first → CORSMiddleware added second → CORS runs first, then secret check.
app.add_middleware(ApiSecretMiddleware)

# CORS Middleware (added last → runs first, handles OPTIONS preflight before secret check)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "CMS API", "version": settings.APP_VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}

