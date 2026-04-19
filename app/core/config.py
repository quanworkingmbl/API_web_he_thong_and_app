from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union, Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DIRECT_URL: str = ""
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_SECRET_KEY: str = ""
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # App
    APP_NAME: str = "CMS API"
    APP_VERSION: str = "1.0.0"
    DEBUG: Union[bool, str] = True
    SHOW_DOCS: Union[bool, str] = True  # Hiển thị /docs, /redoc độc lập với DEBUG

    # API Secret Header (X-Quan-Secret)
    API_SECRET_KEY: str = "VLU15122004"

    # AWS S3 Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""

    # SSL for AWS RDS
    DB_SSL_CERT: str = ""  # Path to RDS global-bundle.pem

    # VNPAY Payment Gateway
    VNPAY_TMN_CODE: str = ""
    VNPAY_HASH_SECRET: str = ""
    VNPAY_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL: str = "http://localhost:8000/api/payments/vnpay/return"
    VNPAY_IPN_URL: str = "http://localhost:8000/api/payments/vnpay/ipn"

    # GHN Shipping
    GHN_TOKEN: str = ""
    GHN_SHOP_ID: str = ""
    GHN_URL: str = "https://dev-online-gateway.ghn.vn/shiip/public-api"

    # --- Google Vertex AI (Gemini) ---
    VERTEX_PROJECT_ID: str = ""
    VERTEX_LOCATION: str = "asia-southeast1"
    # VERTEX_MODERATION_MODEL_ID: str = "gemini-1.5-flash"
    # VERTEX_CREATIVE_MODEL_ID: str = "gemini-1.5-flash"
    VERTEX_MODERATION_MODEL_ID: str = "gemini-2.5-flash"
    VERTEX_CREATIVE_MODEL_ID: str = "gemini-2.5-flash"
    VERTEX_EMBEDDING_MODEL_ID: str = "text-embedding-005"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # AI Operation Settings
    AI_MODERATION_TIMEOUT: int = 6          # seconds
    AI_DESCRIPTION_TIMEOUT: int = 15        # seconds
    AI_BLOG_TIMEOUT: int = 30               # seconds
    AI_EMBEDDING_TIMEOUT: int = 5           # seconds
    AI_MAX_RETRIES: int = 2
    AI_DAILY_BUDGET_USD: float = 5.0        # Cost guardrail - auto-downgrade khi vượt
    AI_CACHE_TTL_HOURS: int = 24            # Cache expiration

    # Google reCAPTCHA v3
    RECAPTCHA_ENABLED: Union[bool, str] = True
    RECAPTCHA_SECRET_KEY: str = ""
    RECAPTCHA_VERIFY_URL: str = "https://www.google.com/recaptcha/api/siteverify"
    RECAPTCHA_MIN_SCORE: float = 0.5
    RECAPTCHA_EXPECTED_ACTION: str = "login"
    RECAPTCHA_BYPASS_ENABLED: Union[bool, str] = False
    RECAPTCHA_BYPASS_SECRET_KEY: str = ""
    RECAPTCHA_BYPASS_CLIENTS: str = "mobile,postman"

    
    @field_validator('DEBUG', 'SHOW_DOCS', 'RECAPTCHA_ENABLED', 'RECAPTCHA_BYPASS_ENABLED', mode='before')
    @classmethod
    def parse_debug(cls, v: Union[bool, str, int]) -> bool:
        """Parse DEBUG/SHOW_DOCS từ nhiều kiểu dữ liệu"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        if isinstance(v, int):
            return bool(v)
        return True  # Default to True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def refresh_token_secret_key(self) -> str:
        # Fall back to access-token secret to keep backward compatibility.
        return self.REFRESH_TOKEN_SECRET_KEY or self.SECRET_KEY
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Bỏ qua các biến môi trường lạ (PORT, NODE_ENV từ Node.js...)

settings = Settings()
