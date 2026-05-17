"""
Seed comparison blog topics into blog_topics_generalist.

Comparison content catches commercial-intent SERPs that landing pages and
industry verticals miss: "X vs Y", "online vs high street", "accountant vs
bookkeeper", etc.

Run:
    python pipeline/seed_comparison_pages.py
    python pipeline/seed_comparison_pages.py --dry-run
"""
import argparse
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


COMPARISONS = [
    ("Crunch Vs TaxAssist Vs Mazuma: Online Accountant Comparison 2025", "crunch vs taxassist vs mazuma", "Bookkeeping and Compliance"),
    ("TaxAssist Vs Crunch: Which UK Online Accountant Should You Choose?", "taxassist vs crunch", "Bookkeeping and Compliance"),
    ("Mazuma Vs Crunch: Online Accountant Comparison For Small Businesses", "mazuma vs crunch", "Bookkeeping and Compliance"),
    ("Online Accountant Vs High Street Accountant: Which Is Right For Your Business?", "online accountant vs high street", "Bookkeeping and Compliance"),
    ("Fixed Fee Accountant Vs Hourly Billing: Which Is Better Value?", "fixed fee vs hourly accountant", "Bookkeeping and Compliance"),
    ("Xero Vs FreeAgent: Which Cloud Accounting Software Is Better For UK Limited Companies?", "xero vs freeagent", "Bookkeeping and Compliance"),
    ("QuickBooks Vs Xero: Cloud Accounting Comparison For UK Small Business", "quickbooks vs xero", "Bookkeeping and Compliance"),
    ("FreeAgent Vs QuickBooks: Best UK Software For Contractors And Sole Traders", "freeagent vs quickbooks", "Bookkeeping and Compliance"),
    ("Accountant Vs Bookkeeper: What's The Difference And Which Do You Need?", "accountant vs bookkeeper", "Bookkeeping and Compliance"),
    ("ICAEW Vs ACCA Vs AAT: What Each UK Accountancy Qualification Means For You", "icaew vs acca vs aat accountant", "Bookkeeping and Compliance"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = []
    for topic, kw, category in COMPARISONS:
        rows.append({
            "topic": topic,
            "category": category,
            "primary_keyword": kw,
            "user_intent": "transactional",
            "content_tier": "cluster",
            "publish_priority": 8,
            "keyword_source": "comparison-v1",
            "notes": "Comparison page: commercial-intent SERP target",
            "used": False,
        })

    print(f"{len(rows)} comparison topics to seed")
    if args.dry_run:
        for r in rows:
            print(f"  - {r['topic']}")
        return

    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    params = {"on_conflict": "topic"}
    r = httpx.post(url, headers=headers, params=params, json=rows, timeout=30)
    if r.status_code in (200, 201):
        body = r.json()
        ins = sum(1 for x in body if not x.get("used_at"))
        upd = len(body) - ins
        print(f"inserted: {ins}  updated: {upd}")
    else:
        print(f"[ERROR] {r.status_code}: {r.text[:200]}")


if __name__ == "__main__":
    main()
