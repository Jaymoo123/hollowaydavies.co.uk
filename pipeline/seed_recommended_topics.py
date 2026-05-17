"""
Push the top recommended topics into blog_topics_generalist.

Reads seo-research/generalist-recommended-topics.csv (produced by
aggregate_brief.py) and upserts the top N rows by publish_priority.

By default skips autocomplete-only rows (priority 5) — those are the
noisiest layer and benefit from manual cherry-picking.

Run:
    python pipeline/seed_recommended_topics.py                # top 100, P>=6
    python pipeline/seed_recommended_topics.py --max 80
    python pipeline/seed_recommended_topics.py --min-priority 7  # gap+GSC only
    python pipeline/seed_recommended_topics.py --include-autocomplete  # all P5+
    python pipeline/seed_recommended_topics.py --dry-run
"""
import argparse
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

from config_supabase import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE, POST_CATEGORIES


CSV_PATH = Path(__file__).resolve().parents[1] / "seo-research" / "generalist-recommended-topics.csv"


def load_candidates(min_priority: int, max_n: int | None, include_autocomplete: bool):
    rows = []
    skipped_cat = 0
    skipped_autocomplete = 0
    with CSV_PATH.open(encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            try:
                pri = int(raw["publish_priority"])
            except (ValueError, TypeError):
                pri = 5
            if pri < min_priority:
                continue
            sources = (raw.get("sources") or "").lower()
            if not include_autocomplete and "autocomplete" in sources and pri == 5:
                skipped_autocomplete += 1
                continue
            cat = raw.get("category", "").strip()
            if cat not in POST_CATEGORIES:
                skipped_cat += 1
                continue
            rows.append({
                "topic": raw["topic"].strip(),
                "category": cat,
                "primary_keyword": (raw.get("primary_keyword") or "").strip() or None,
                "user_intent": (raw.get("user_intent") or "informational").strip().lower(),
                "content_tier": (raw.get("content_tier") or "supporting").strip().lower(),
                "publish_priority": pri,
                "keyword_source": (raw.get("sources") or "aggregate-v1").strip(),
                "notes": (raw.get("notes") or "").strip() or None,
                "used": False,
            })
    rows.sort(key=lambda r: (-r["publish_priority"], r["category"], r["topic"]))
    print(f"  skipped: {skipped_cat} (bad category), {skipped_autocomplete} (autocomplete P5)")
    if max_n and len(rows) > max_n:
        print(f"  capping to top {max_n} (of {len(rows)} eligible)")
        rows = rows[:max_n]
    return rows


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
            print(f"[ERROR] batch {i}-{i+len(batch)}: {r.status_code} {r.text[:300]}")
    return inserted, updated, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=120, help="cap number of rows seeded")
    parser.add_argument("--min-priority", type=int, default=6, help="minimum publish_priority to include")
    parser.add_argument("--include-autocomplete", action="store_true",
                        help="include autocomplete-sourced P5 candidates")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = load_candidates(args.min_priority, args.max, args.include_autocomplete)
    print(f"\nLoaded {len(rows)} candidates from {CSV_PATH.name}  (min_priority={args.min_priority})")

    from collections import Counter
    cats = Counter(r["category"] for r in rows)
    tiers = Counter(r["content_tier"] for r in rows)
    pris = Counter(r["publish_priority"] for r in rows)
    print("\nBy category:")
    for c in POST_CATEGORIES:
        print(f"  {cats.get(c, 0):>3}  {c}")
    print("\nBy tier:", dict(tiers))
    print("By priority:", dict(sorted(pris.items(), reverse=True)))

    if args.dry_run:
        print("\n[dry-run] First 10 rows:")
        for r in rows[:10]:
            print(f"  - [P{r['publish_priority']}] {r['category']:<35} {r['topic']}")
        return

    print(f"\nUpserting to {SUPABASE_TABLE}...")
    inserted, updated, errors = upsert(rows)
    print(f"  inserted: {inserted}  updated: {updated}  errors: {errors}")


if __name__ == "__main__":
    main()
