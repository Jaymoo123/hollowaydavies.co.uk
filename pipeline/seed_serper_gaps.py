"""Push the 50 Serper-derived gap ideas into blog_topics_agency."""
import csv
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from config_supabase import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE

CSV_PATH = Path(__file__).resolve().parents[1] / "seo-research" / "serper-gap-ideas.csv"


def main():
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Run serper_gap_ideate.py first.")
        sys.exit(1)
    rows = []
    with CSV_PATH.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            title = (r.get("title") or "").strip()
            cat = (r.get("category") or "").strip()
            if not title or not cat:
                continue
            rows.append({
                "topic": title,
                "category": cat,
                "primary_keyword": (r.get("primary_keyword") or "").strip() or None,
                "publish_priority": 2,
                "content_tier": "cluster",
                "keyword_source": "serper-gap-v1",
                "notes": (r.get("rationale") or "").strip() or None,
                "used": False,
            })
    print(f"Loaded {len(rows)} gap ideas")

    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    params = {"on_conflict": "topic"}
    inserted = updated = errors = 0
    for i in range(0, len(rows), 25):
        batch = rows[i:i + 25]
        r = httpx.post(url, headers=headers, params=params, json=batch, timeout=30.0)
        if r.status_code in (200, 201):
            for item in r.json():
                if item.get("used_at"):
                    updated += 1
                else:
                    inserted += 1
        else:
            errors += len(batch)
            print(f"[ERROR] {r.status_code}: {r.text[:300]}")
    print(f"  inserted: {inserted}  updated: {updated}  errors: {errors}")


if __name__ == "__main__":
    main()
