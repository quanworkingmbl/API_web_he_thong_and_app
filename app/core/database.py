from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, quote
from app.core.config import settings
import re
import logging

logger = logging.getLogger(__name__)


def build_safe_database_url(raw_url: str) -> str:
    """
    Safely parse and clean the DATABASE_URL.
    - Handles special characters in password (;, [, ], @, etc.)
    - Removes pgbouncer=true query param
    - Ensures postgresql:// scheme (not postgres://)
    """
    if not raw_url:
        raise ValueError("DATABASE_URL is not set. Please configure it in Cloud Run secrets.")

    # Normalize scheme: postgres:// → postgresql://
    url = raw_url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    # Remove pgbouncer param inline (before full parse, to avoid parse errors)
    url = re.sub(r'[?&]pgbouncer=true', '', url)

    # Use regex to extract parts without relying on urlparse for broken URLs
    # Pattern: scheme://user:pass@host:port/dbname?query
    pattern = re.compile(
        r'^(?P<scheme>[a-z+]+)://'
        r'(?P<user>[^:@]+)?'
        r'(?::(?P<password>.+?))?'
        r'@(?P<host>[^/:?]+)'
        r'(?::(?P<port>\d+))?'
        r'(?P<path>/[^?]*)?'
        r'(?:\?(?P<query>.*))?$',
        re.DOTALL
    )
    match = pattern.match(url)
    if not match:
        # Cannot parse — return as-is and let SQLAlchemy handle it
        logger.warning("Could not parse DATABASE_URL with regex; using raw value.")
        return url

    scheme   = match.group('scheme') or 'postgresql'
    user     = match.group('user') or ''
    password = match.group('password') or ''
    host     = match.group('host') or ''
    port     = match.group('port') or '5432'
    path     = match.group('path') or '/cms_db'
    query    = match.group('query') or ''

    # URL-encode user & password to handle special chars (; [ ] @ etc.)
    safe_user = quote(user, safe='')
    safe_pass = quote(password, safe='')

    # Remove pgbouncer from query params
    if query:
        params = parse_qs(query, keep_blank_values=True)
        params.pop('pgbouncer', None)
        query = urlencode(params, doseq=True)

    # Rebuild the URL
    if query:
        clean = f"{scheme}://{safe_user}:{safe_pass}@{host}:{port}{path}?{query}"
    else:
        clean = f"{scheme}://{safe_user}:{safe_pass}@{host}:{port}{path}"

    return clean


# Build safe DATABASE_URL
try:
    clean_url = build_safe_database_url(settings.DATABASE_URL)
    logger.info(f"Database URL constructed successfully (host masked).")
except Exception as e:
    logger.error(f"FATAL: Could not build DATABASE_URL: {e}")
    raise

# Create engine — Cloud Run: keep pool small to avoid Cloud SQL connection limits
# db-g1-small max_connections ≈ 100; with 3 instances × pool=3 = 9 connections max
engine = create_engine(
    clean_url,
    pool_pre_ping=True,   # Detect stale connections
    pool_size=3,          # Small pool per instance (Cloud Run stateless)
    max_overflow=5,       # Allow brief bursts
    pool_timeout=30,
    pool_recycle=1800,    # Recycle connections every 30 min
    connect_args={
        "connect_timeout": 10,
        "sslmode": "require",  # Cloud SQL public IP requires SSL
    }
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
