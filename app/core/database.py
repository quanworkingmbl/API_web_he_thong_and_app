from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.url_utils import build_safe_database_url
import logging

logger = logging.getLogger(__name__)

# Re-export để alembic/env.py cũ không bị lỗi nếu còn import từ đây
__all__ = ["engine", "SessionLocal", "Base", "get_db", "build_safe_database_url"]

# Build safe URL
try:
    clean_url = build_safe_database_url(settings.DATABASE_URL)
    logger.info("Database URL built successfully.")
except Exception as e:
    logger.error(f"FATAL: Cannot build DATABASE_URL: {e}")
    raise

# Engine — pool nhỏ phù hợp Cloud Run (stateless, scale-to-0)
engine = create_engine(
    clean_url,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
