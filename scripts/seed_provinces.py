"""
Seed Vietnamese administrative data (Tỉnh/Huyện/Xã) into the database.

Source: https://provinces.open-api.vn/api/?depth=3
Usage:
    cd Du_an_cms_API
    python scripts/seed_provinces.py

Options:
    --check     Only print current record counts, do not insert.
    --clear     Drop existing data before seeding (use with caution).
    --force     Skip confirmation prompt.
"""
import sys
import os
import argparse
import time

# ── Allow running from project root ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import urllib.error
import json

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.address import Province, District, Ward


# ── Config ────────────────────────────────────────────────────────────────────
API_URL = "https://provinces.open-api.vn/api/?depth=3"
REQUEST_TIMEOUT = 60  # seconds
BATCH_SIZE = 200      # rows per commit


def _fetch_data(url: str) -> list:
    print(f"  Fetching: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "seed-script/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError(f"Expected list, got {type(data)}")
            print(f"  Got {len(data)} provinces from API.")
            return data
    except urllib.error.URLError as exc:
        print(f"  ERROR: {exc}")
        raise


def _count(db: Session) -> tuple[int, int, int]:
    p = db.query(Province).count()
    d = db.query(District).count()
    w = db.query(Ward).count()
    return p, d, w


def main():
    parser = argparse.ArgumentParser(description="Seed Vietnamese provinces/districts/wards")
    parser.add_argument("--check", action="store_true", help="Only print counts")
    parser.add_argument("--clear", action="store_true", help="Delete existing data first")
    parser.add_argument("--force", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        p, d, w = _count(db)
        print(f"\n📊 Current DB state:")
        print(f"   Provinces : {p:,}")
        print(f"   Districts : {d:,}")
        print(f"   Wards     : {w:,}")

        if args.check:
            return

        if p > 0 and not args.clear and not args.force:
            print("\n⚠️  Provinces table already has data.")
            ans = input("   Continue and add/update? [y/N] ").strip().lower()
            if ans != "y":
                print("Aborted.")
                return

        print("\n🌐 Fetching data from provinces.open-api.vn …")
        data = _fetch_data(API_URL)

        if args.clear:
            if not args.force:
                ans = input("⚠️  This will DELETE all provinces/districts/wards. Are you sure? [y/N] ").strip().lower()
                if ans != "y":
                    print("Aborted.")
                    return
            print("🗑️  Clearing existing data …")
            db.query(Ward).delete()
            db.query(District).delete()
            db.query(Province).delete()
            db.commit()
            print("   Done.")

        # ── Seed ─────────────────────────────────────────────────────────────
        existing_province_codes = {r.code for r in db.query(Province.code).all()}
        existing_district_codes = {r.code for r in db.query(District.code).all()}
        existing_ward_codes = {r.code for r in db.query(Ward.code).all()}

        provinces_added = 0
        districts_added = 0
        wards_added = 0
        total_districts = sum(len(p.get("districts", [])) for p in data)
        total_wards = sum(
            len(d.get("wards", []))
            for p in data
            for d in p.get("districts", [])
        )

        print(f"\n📝 Inserting data …")
        print(f"   Provinces: {len(data)}")
        print(f"   Districts: {total_districts}")
        print(f"   Wards    : {total_wards}")
        print()

        t0 = time.time()
        batch: list = []

        for prov_raw in data:
            pcode = str(prov_raw.get("code", "")).zfill(2)
            pname = prov_raw.get("name", "").strip()

            if not pcode or not pname:
                continue

            if pcode not in existing_province_codes:
                batch.append(Province(code=pcode, name=pname))
                provinces_added += 1

            for dist_raw in prov_raw.get("districts", []):
                dcode = str(dist_raw.get("code", "")).zfill(3)
                dname = dist_raw.get("name", "").strip()

                if not dcode or not dname:
                    continue

                if dcode not in existing_district_codes:
                    batch.append(District(code=dcode, name=dname, province_code=pcode))
                    districts_added += 1

                for ward_raw in dist_raw.get("wards", []):
                    wcode = str(ward_raw.get("code", "")).zfill(5)
                    wname = ward_raw.get("name", "").strip()

                    if not wcode or not wname:
                        continue

                    if wcode not in existing_ward_codes:
                        batch.append(Ward(code=wcode, name=wname, district_code=dcode))
                        wards_added += 1

                if len(batch) >= BATCH_SIZE:
                    db.add_all(batch)
                    db.commit()
                    batch = []

        if batch:
            db.add_all(batch)
            db.commit()

        elapsed = time.time() - t0
        print(f"✅ Done in {elapsed:.1f}s")
        print(f"   Provinces added : {provinces_added:,}")
        print(f"   Districts added : {districts_added:,}")
        print(f"   Wards added     : {wards_added:,}")

        p2, d2, w2 = _count(db)
        print(f"\n📊 Updated DB state:")
        print(f"   Provinces : {p2:,}")
        print(f"   Districts : {d2:,}")
        print(f"   Wards     : {w2:,}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
