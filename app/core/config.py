from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DIRECT_URL: str = ""
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # App
    APP_NAME: str = "CMS API"
    APP_VERSION: str = "1.0.0"
    DEBUG: Union[bool, str] = True

    # API Secret Header (X-Quan-Secret)
    API_SECRET_KEY: str = "VLU15122004"

    # AWS S3 Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
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

    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v: Union[bool, str, int]) -> bool:
        """Parse DEBUG from various formats"""
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
