"""
One-off migration helper — kết nối DB qua DATABASE_URL (.env), không hardcode credential.
"""
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

database_url = os.environ.get("DATABASE_URL", "").strip()
if not database_url:
    raise SystemExit("DATABASE_URL is required. Set it in Du_an_cms_API/.env")

conn = psycopg2.connect(database_url)
cur = conn.cursor()

statements = [
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS wallet_credited BOOLEAN NOT NULL DEFAULT FALSE",
    "CREATE INDEX IF NOT EXISTS ix_orders_wallet_credited ON orders(wallet_credited)",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS seller_amount NUMERIC(12,2)",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS platform_fee NUMERIC(12,2)",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS settlement_status VARCHAR(50) DEFAULT 'pending'",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS settled_at TIMESTAMP WITH TIME ZONE",
]

for stmt in statements:
    try:
        cur.execute(stmt)
        print(f"OK: {stmt[:80]}")
    except Exception as e:
        print(f"SKIP/ERROR: {e}")

conn.commit()

cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'orders'
      AND column_name IN ('wallet_credited', 'seller_amount', 'platform_fee', 'settlement_status', 'settled_at')
    ORDER BY column_name
""")
rows = cur.fetchall()
print("\n=== Verification ===")
for r in rows:
    print(r)

cur.close()
conn.close()
print("\nDone!")
