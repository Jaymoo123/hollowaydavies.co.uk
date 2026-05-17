"""
Seed blog_topics_agency in Supabase from seo-research/blog-ideas.csv.

Maps CSV columns -> table columns and normalises category names to the
canonical form used by the frontend and config_supabase.py POST_CATEGORIES.

Run:
    python pipeline/seed_topics.py            # upsert all rows
    python pipeline/seed_topics.py --dry-run  # print mapped rows, no write
"""
import csv
import os
import sys
import argparse
from pathlib import Path

import httpx

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config_supabase import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE


CSV_PATH = Path(__file__).resolve().parents[1] / "seo-research" / "blog-ideas.csv"

CATEGORY_NORMALISATION = {
    "Agency Accountant Services": "Agency Accountant Services",
    "Agency Finance Essentials": "Agency Finance Essentials",
    "Contractors & IR35": "Contractors and IR35",
    "Growing & Exiting Your Agency": "Growth and Exit",
    "Incorporation & Business Structure": "Incorporation and Structure",
    "International & UAE Agencies": "International Agencies",
    "Making Tax Digital": "Making Tax Digital",
    "Salary Dividends & Profit": "Salary and Dividends",
    "Salary, Dividends & Profit": "Salary and Dividends",
    "Tax & Compliance": "Tax and Compliance",
}

INTENT_MAP = {
    "I": "informational",
    "C": "commercial",
    "L": "local",
    "T": "transactional",
    "N": "navigational",
}

PRIORITY_MAP = {"P1": 3, "P2": 2, "P3": 1}


def parse_int(value: str):
    if not value or value.strip() in ("", "—", "-", "N/A", "n/a"):
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def normalise_intent(raw: str) -> str:
    if not raw:
        return "informational"
    tokens = [t.strip().upper() for t in raw.replace("/", ",").split(",") if t.strip()]
    if not tokens:
        return "informational"
    primary = tokens[0]
    return INTENT_MAP.get(primary, "informational")


def load_rows(csv_path: Path):
    with csv_path.open(encoding="utf-8") as h:
        reader = csv.DictReader(h)
        rows = []
        skipped = []
        for raw in reader:
            title = (raw.get("Title") or "").strip()
            if not title:
                continue
            raw_cat = (raw.get("Category") or "").strip()
            category = CATEGORY_NORMALISATION.get(raw_cat)
            if not category:
                skipped.append((title, f"unmapped category '{raw_cat}'"))
                continue

            row = {
                "topic": title,
                "category": category,
                "primary_keyword": (raw.get("Target Keyword") or "").strip() or None,
                "target_search_volume": parse_int(raw.get("Estimated Vol", "")),
                "keyword_difficulty": parse_int(raw.get("Difficulty", "")),
                "user_intent": normalise_intent(raw.get("Intent", "")),
                "publish_priority": PRIORITY_MAP.get(
                    (raw.get("Priority") or "").strip().upper(), 1
                ),
                "content_tier": "cluster",
                "suggested_slug": (raw.get("Slug") or "").strip() or None,
                "notes": (raw.get("Notes") or "").strip() or None,
                "keyword_source": "blog-ideas-csv-v1",
                "used": False,
            }
            rows.append(row)
    return rows, skipped


def upsert_rows(rows):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    params = {"on_conflict": "topic"}
    inserted, updated, errors = 0, 0, 0
    for i in range(0, len(rows), 25):
        batch = rows[i : i + 25]
        r = httpx.post(url, headers=headers, params=params, json=batch, timeout=30.0)
        if r.status_code in (200, 201):
            body = r.json()
            for item in body:
                if item.get("used_at"):
                    updated += 1
                else:
                    inserted += 1
        else:
            errors += len(batch)
            print(f"[ERROR] batch {i}-{i+len(batch)}: {r.status_code} {r.text[:300]}")
    return inserted, updated, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print mapped rows, no DB write")
    args = parser.parse_args()

    print(f"Loading topics from {CSV_PATH}")
    rows, skipped = load_rows(CSV_PATH)
    print(f"  parsed: {len(rows)} | skipped: {len(skipped)}")
    for title, reason in skipped:
        print(f"  SKIP: {title}  ({reason})")

    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], 0)
        by_cat[r["category"]] += 1
    print("\nBy category:")
    for cat, n in sorted(by_cat.items()):
        print(f"  {n:>3}  {cat}")

    by_pri = {}
    for r in rows:
        by_pri.setdefault(r["publish_priority"], 0)
        by_pri[r["publish_priority"]] += 1
    print("\nBy publish_priority:")
    for p in sorted(by_pri.keys(), reverse=True):
        print(f"  P{p}: {by_pri[p]}")

    if args.dry_run:
        print("\n[dry-run] First 3 mapped rows:")
        for r in rows[:3]:
            print(r)
        return

    print(f"\nUpserting {len(rows)} rows to {SUPABASE_TABLE}...")
    inserted, updated, errors = upsert_rows(rows)
    print(f"  inserted: {inserted}  updated: {updated}  errors: {errors}")


if __name__ == "__main__":
    main()
