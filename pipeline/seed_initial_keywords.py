"""
Seed the initial generalist seed keywords into blog_topics_generalist.

Reads pipeline/seed_keywords.csv (the curated seed set drafted at the start of
the keyword-intelligence pass) and upserts each row as a topic row. These
rows become the input for serper_mine.py — Serper queries each
`primary_keyword` to harvest PAA, related searches, and top-10 competitor
titles.

The CSV is treated as the source of truth for the seed set. Re-running this
script is idempotent (upsert on `topic`).

Run:
    python pipeline/seed_initial_keywords.py             # upsert all rows
    python pipeline/seed_initial_keywords.py --dry-run   # show mapping only
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


CSV_PATH = Path(__file__).resolve().parent / "seed_keywords.csv"


def _topic_from_keyword(keyword: str) -> str:
    """Turn a keyword phrase into a clean topic title for the unique-on-topic
    constraint. Title-cases each word, preserves obvious acronyms."""
    acronyms = {"uk", "vat", "mtd", "ir35", "r&d", "paye", "cis", "cgt", "badr",
                "hmrc", "p11d", "p60", "p45", "ai", "ltd", "uae", "itsa", "mvl"}
    words = []
    for w in keyword.split():
        if w.lower() in acronyms:
            words.append(w.upper().replace("R&D", "R&D"))
        else:
            words.append(w.capitalize())
    return " ".join(words).strip()


def load_rows():
    if not CSV_PATH.exists():
        print(f"ERROR: missing {CSV_PATH}")
        sys.exit(1)
    rows = []
    skipped = []
    with CSV_PATH.open(encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            keyword = (raw.get("keyword") or "").strip()
            if not keyword:
                continue
            category = (raw.get("category") or "").strip()
            if category not in POST_CATEGORIES:
                skipped.append((keyword, f"unmapped category '{category}'"))
                continue
            intent_raw = (raw.get("intent") or "informational").strip().lower()
            intent = intent_raw if intent_raw in {
                "informational", "transactional", "navigational"
            } else "informational"
            tier_raw = (raw.get("content_tier") or "cluster").strip().lower()
            tier = tier_raw if tier_raw in {"pillar", "cluster", "supporting"} else "cluster"
            try:
                priority = int((raw.get("priority") or "5").strip())
            except ValueError:
                priority = 5
            priority = max(1, min(10, priority))

            rows.append({
                "topic": _topic_from_keyword(keyword),
                "category": category,
                "primary_keyword": keyword,
                "user_intent": intent,
                "content_tier": tier,
                "publish_priority": priority,
                "keyword_source": "generalist-seed-v1",
                "notes": (raw.get("notes") or "").strip() or None,
                "used": False,
            })
    return rows, skipped


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
        batch = rows[i : i + 25]
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
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows, skipped = load_rows()
    print(f"Loaded {len(rows)} seed keywords from {CSV_PATH.name}  (skipped {len(skipped)})")
    for kw, why in skipped:
        print(f"  SKIP: {kw}  ({why})")

    from collections import Counter
    cats = Counter(r["category"] for r in rows)
    tiers = Counter(r["content_tier"] for r in rows)
    intents = Counter(r["user_intent"] for r in rows)
    print("\nBy category:")
    for c in POST_CATEGORIES:
        print(f"  {cats.get(c, 0):>3}  {c}")
    print("\nBy tier:", dict(tiers))
    print("By intent:", dict(intents))

    if args.dry_run:
        print("\n[dry-run] First 5 rows:")
        for r in rows[:5]:
            print(f"  - [{r['publish_priority']}] {r['topic']!r}  kw={r['primary_keyword']!r}  ({r['category']})")
        return

    print(f"\nUpserting to {SUPABASE_TABLE}...")
    inserted, updated, errors = upsert(rows)
    print(f"  inserted: {inserted}  updated: {updated}  errors: {errors}")


if __name__ == "__main__":
    main()
