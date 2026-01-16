from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from app.core.config import settings

def clean_database_url(url: str) -> str:
    """Remove pgbouncer parameter from connection string"""
    if not url:
        return url
    # Remove ?pgbouncer=true if present
    if '?pgbouncer=true' in url:
        url = url.replace('?pgbouncer=true', '')
    elif '&pgbouncer=true' in url:
        url = url.replace('&pgbouncer=true', '')
    # Parse and clean query parameters
    parsed = urlparse(url)
    if parsed.query:
        params = parse_qs(parsed.query)
        # Remove pgbouncer from params
        params.pop('pgbouncer', None)
        # Rebuild URL
        new_query = urlencode(params, doseq=True) if params else ''
        parsed = parsed._replace(query=new_query)
        url = urlunparse(parsed)
    return url

# Clean DATABASE_URL
clean_url = clean_database_url(settings.DATABASE_URL)

# Create engine
engine = create_engine(
    clean_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

