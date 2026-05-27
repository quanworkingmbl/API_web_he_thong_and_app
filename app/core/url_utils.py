"""
Utility để parse DATABASE_URL an toàn.
Module này KHÔNG import database engine — tránh circular import khi alembic dùng.
"""
import re
import logging
from urllib.parse import quote, unquote, parse_qs, urlencode

logger = logging.getLogger(__name__)


def build_safe_database_url(raw_url: str) -> str:
    """
    Parse và rebuild DATABASE_URL an toàn:
    - Xử lý ký tự đặc biệt trong password (;  [  ]  @  etc.)
    - Chuẩn hoá scheme postgres:// → postgresql://
    - Loại bỏ ?pgbouncer=true
    """
    if not raw_url:
        raise ValueError("DATABASE_URL is not set.")

    url = raw_url.strip()

    # Chuẩn hoá scheme
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    # Loại bỏ pgbouncer param thô (trước khi parse)
    url = re.sub(r'[?&]pgbouncer=true', '', url)

    # Regex parse URL — xử lý được @ trong password nhờ backtracking
    pattern = re.compile(
        r'^(?P<scheme>[a-z+]+)://'
        r'(?P<user>[^:@/]+)'
        r'(?::(?P<password>.+?))?'
        r'@(?P<host>[^/:?@]+)'
        r'(?::(?P<port>\d+))?'
        r'(?P<path>/[^?]*)?'
        r'(?:\?(?P<query>.*))?$',
        re.DOTALL
    )
    match = pattern.match(url)
    if not match:
        logger.warning("Cannot parse DATABASE_URL with regex; using as-is.")
        return url

    scheme   = match.group('scheme') or 'postgresql'
    user     = match.group('user') or ''
    password = match.group('password') or ''
    host     = match.group('host') or ''
    port     = match.group('port') or '5432'
    path     = match.group('path') or '/cms_db'
    query    = match.group('query') or ''

    # Decode trước để tránh double-encode, rồi encode lại chuẩn
    safe_user = quote(unquote(user), safe='')
    safe_pass = quote(unquote(password), safe='')

    # Loại bỏ pgbouncer khỏi query params nếu còn sót
    if query:
        params = parse_qs(query, keep_blank_values=True)
        params.pop('pgbouncer', None)
        query = urlencode(params, doseq=True)

    if query:
        return f"{scheme}://{safe_user}:{safe_pass}@{host}:{port}{path}?{query}"
    return f"{scheme}://{safe_user}:{safe_pass}@{host}:{port}{path}"
