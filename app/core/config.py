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
