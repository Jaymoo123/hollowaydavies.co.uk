"""
Seed the LLM-generated topic ideas (seo-research/topic-ideas-llm.csv) into
blog_topics_agency.

Each idea gets publish_priority=2 so they sit behind any remaining P3 (=3)
originals in the queue. Marked with keyword_source='llm-ideation-v1' for
later filtering.
"""
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


CSV_PATH = Path(__file__).resolve().parents[1] / "seo-research" / "topic-ideas-llm.csv"


def upsert(rows):
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
            print(f"[ERROR] batch {i}-{i + len(batch)}: {r.status_code} {r.text[:300]}")
    return inserted, updated, errors


def main():
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Run pipeline/ideate_topics.py first.")
        sys.exit(1)

    rows = []
    with CSV_PATH.open(encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            title = (raw.get("title") or "").strip()
            cat = (raw.get("category") or "").strip()
            kw = (raw.get("primary_keyword") or "").strip() or None
            note = (raw.get("rationale") or "").strip() or None
            if not title or not cat:
                continue
            rows.append({
                "topic": title,
                "category": cat,
                "primary_keyword": kw,
                "publish_priority": 2,
                "content_tier": "cluster",
                "keyword_source": "llm-ideation-v1",
                "notes": note,
                "used": False,
            })

    print(f"Loaded {len(rows)} ideas from {CSV_PATH}")
    inserted, updated, errors = upsert(rows)
    print(f"  inserted: {inserted}  updated: {updated}  errors: {errors}")


if __name__ == "__main__":
    main()
