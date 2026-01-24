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
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    # title, version information API
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    
    docs_url="/docs" if settings.DEBUG else None,  # path Swagger UI 
    redoc_url="/redoc" if settings.DEBUG else None,  # Hide redoc in production
    openapi_url="/openapi.json" if settings.DEBUG else None,  # Hide openapi in production
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS Middleware
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

