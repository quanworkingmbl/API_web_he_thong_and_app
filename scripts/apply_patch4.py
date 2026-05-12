import psycopg2

conn = psycopg2.connect(
    host="35.240.182.133",
    port=5432,
    dbname="cms_db",
    user="cms_user",
    password="QuanCMS2026@Secure",
    sslmode="require"
)
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

# Verify
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
