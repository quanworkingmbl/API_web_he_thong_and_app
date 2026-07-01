"""
So sánh schema DB thực tế vs SQLAlchemy models.
Xuất ra tất cả cột đang thiếu trên production DB.
"""
import os
from sqlalchemy import create_engine, text, inspect
from app.core.url_utils import build_safe_database_url

# Import tất cả models để SQLAlchemy biết schema cần có
from app.models import *  # noqa
from app.core.database import Base

url = build_safe_database_url(os.environ["DATABASE_URL"])
engine = create_engine(url)
inspector = inspect(engine)

# Lấy tất cả bảng thực tế trong DB
db_tables = set(inspector.get_table_names())

# Lấy tất cả bảng từ SQLAlchemy models
model_tables = {t.name: t for t in Base.metadata.sorted_tables}

print("=" * 70)
print("SCHEMA DIFF REPORT")
print("=" * 70)

missing_tables = []
missing_columns = []

for table_name, table in model_tables.items():
    if table_name not in db_tables:
        missing_tables.append(table_name)
        continue

    db_cols = {c["name"]: c for c in inspector.get_columns(table_name)}
    model_cols = {c.name: c for c in table.columns}

    for col_name, col in model_cols.items():
        if col_name not in db_cols:
            col_type = str(col.type)
            nullable = col.nullable
            default = col.default.arg if col.default is not None else None
            missing_columns.append({
                "table": table_name,
                "column": col_name,
                "type": col_type,
                "nullable": nullable,
                "default": default,
            })

print(f"\n[MISSING TABLES] {len(missing_tables)}")
for t in missing_tables:
    print(f"  - {t}")

print(f"\n[MISSING COLUMNS] {len(missing_columns)}")
for c in missing_columns:
    default_str = f" DEFAULT {c['default']}" if c['default'] is not None else ""
    nullable_str = "" if c["nullable"] else " NOT NULL"
    print(f"  {c['table']}.{c['column']}  ({c['type']}{nullable_str}{default_str})")

# Xuất SQL patch tự động
print("\n" + "=" * 70)
print("AUTO-GENERATED SQL PATCH")
print("=" * 70)
for c in missing_columns:
    col_type_map = {
        "VARCHAR": "VARCHAR(255)",
        "INTEGER": "INTEGER",
        "BOOLEAN": "BOOLEAN",
        "FLOAT": "FLOAT",
        "TEXT": "TEXT",
        "TIMESTAMP": "TIMESTAMP",
        "JSON": "TEXT",
        "JSONB": "JSONB",
    }
    raw_type = str(c["type"]).upper()
    sql_type = raw_type if raw_type not in col_type_map else col_type_map[raw_type]
    default_part = ""
    if c["default"] is not None:
        d = c["default"]
        if isinstance(d, bool):
            default_part = f" DEFAULT {'TRUE' if d else 'FALSE'}"
        elif isinstance(d, str):
            default_part = f" DEFAULT '{d}'"
        else:
            default_part = f" DEFAULT {d}"
    print(f"ALTER TABLE {c['table']} ADD COLUMN IF NOT EXISTS {c['column']} {sql_type}{default_part};")
