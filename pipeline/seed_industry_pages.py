"""
Seed industry-vertical blog topics into blog_topics_generalist.

Each topic targets a "accountant for [industry]" search query. We seed them
as cluster posts (priority 8) tied to a relevant POST_CATEGORY. After seeding,
the existing bulk_generate.py picks them up.

Run:
    python pipeline/seed_industry_pages.py
    python pipeline/seed_industry_pages.py --dry-run
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


# (topic, primary_keyword, category, intent_hint)
INDUSTRY_VERTICALS = [
    # Trades
    ("Accountant For Tradespeople UK", "accountant for tradespeople", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Builders UK", "accountant for builders", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Plumbers UK", "accountant for plumbers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Electricians UK", "accountant for electricians", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Construction Subcontractors (CIS)", "accountant for construction subcontractors", "Payroll and PAYE", "transactional"),
    # Hospitality / retail
    ("Accountant For Restaurants And Cafes", "accountant for restaurants", "Bookkeeping and Compliance", "transactional"),
    ("Accountant For Pubs And Bars UK", "accountant for pubs", "Bookkeeping and Compliance", "transactional"),
    ("Accountant For Hotels UK", "accountant for hotels", "Bookkeeping and Compliance", "transactional"),
    ("Accountant For Retail Shops UK", "accountant for retail shops", "VAT and Making Tax Digital", "transactional"),
    ("Accountant For Hairdressers UK", "accountant for hairdressers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Beauty Therapists UK", "accountant for beauty therapists", "Sole Trader and Self Employment", "transactional"),
    # Ecommerce
    ("Accountant For Ecommerce Sellers UK", "accountant for ecommerce sellers", "VAT and Making Tax Digital", "transactional"),
    ("Accountant For Amazon FBA Sellers UK", "accountant for amazon fba sellers", "VAT and Making Tax Digital", "transactional"),
    ("Accountant For Dropshippers UK", "accountant for dropshippers", "VAT and Making Tax Digital", "transactional"),
    ("Accountant For Etsy Sellers UK", "accountant for etsy sellers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Shopify Stores UK", "accountant for shopify stores", "VAT and Making Tax Digital", "transactional"),
    # Tech / creative
    ("Accountant For Software Companies UK", "accountant for software companies", "R&D Tax Credits", "transactional"),
    ("Accountant For SaaS Startups UK", "accountant for saas startups", "R&D Tax Credits", "transactional"),
    ("Accountant For AI Startups UK", "accountant for ai startups", "R&D Tax Credits", "transactional"),
    ("Accountant For Tech Startups UK", "accountant for tech startups", "Incorporation and Structure", "transactional"),
    ("Accountant For IT Contractors UK", "accountant for it contractors", "Limited Company Tax", "transactional"),
    ("Accountant For Software Engineers UK", "accountant for software engineers", "Limited Company Tax", "transactional"),
    ("Accountant For Designers UK", "accountant for designers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Photographers UK", "accountant for photographers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Marketing Agencies UK", "accountant for marketing agencies", "Limited Company Tax", "transactional"),
    # Creator / online
    ("Accountant For Content Creators And YouTubers UK", "accountant for content creators", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For OnlyFans Creators UK", "accountant for onlyfans creators", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Influencers UK", "accountant for influencers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Musicians UK", "accountant for musicians", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Actors And Performers UK", "accountant for actors", "Sole Trader and Self Employment", "transactional"),
    # Professional services
    ("Accountant For Solicitors And Law Firms UK", "accountant for solicitors", "Limited Company Tax", "transactional"),
    ("Accountant For Architects UK", "accountant for architects", "Limited Company Tax", "transactional"),
    ("Accountant For Consultants UK", "accountant for consultants", "Limited Company Tax", "transactional"),
    ("Accountant For Personal Trainers UK", "accountant for personal trainers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Tutors UK", "accountant for tutors", "Sole Trader and Self Employment", "transactional"),
    # Healthcare
    ("Accountant For GPs And Doctors UK", "accountant for gps and doctors", "Limited Company Tax", "transactional"),
    ("Accountant For Locum Doctors UK", "accountant for locum doctors", "Limited Company Tax", "transactional"),
    ("Accountant For Vets UK", "accountant for vets", "Limited Company Tax", "transactional"),
    ("Accountant For Dentists UK", "accountant for dentists", "Limited Company Tax", "transactional"),
    ("Accountant For Medical Professionals UK", "accountant for medical professionals", "Limited Company Tax", "transactional"),
    # Property / driving / delivery
    ("Accountant For Landlords And BTL Portfolios UK", "accountant for landlords", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Airbnb Hosts UK", "accountant for airbnb hosts", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Property Developers UK", "accountant for property developers", "Limited Company Tax", "transactional"),
    ("Accountant For Uber And Taxi Drivers UK", "accountant for uber drivers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Delivery Drivers UK", "accountant for delivery drivers", "Sole Trader and Self Employment", "transactional"),
    # Niche but real
    ("Accountant For Farmers UK", "accountant for farmers", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Charities UK", "accountant for charities", "Bookkeeping and Compliance", "transactional"),
    ("Accountant For Churches UK", "accountant for churches", "Bookkeeping and Compliance", "transactional"),
    ("Accountant For Schools UK", "accountant for schools", "Bookkeeping and Compliance", "transactional"),
    ("Accountant For Crypto Traders UK", "accountant for crypto traders", "Sole Trader and Self Employment", "transactional"),
    ("Accountant For Forex Traders UK", "accountant for forex traders", "Sole Trader and Self Employment", "transactional"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = []
    for topic, kw, category, intent in INDUSTRY_VERTICALS:
        rows.append({
            "topic": topic,
            "category": category,
            "primary_keyword": kw,
            "user_intent": intent,
            "content_tier": "cluster",
            "publish_priority": 8,
            "keyword_source": "industry-vertical-v1",
            "notes": f"Industry vertical landing. Target: 'accountant for [industry]' SERPs.",
            "used": False,
        })

    print(f"{len(rows)} industry-vertical topics to seed")
    from collections import Counter
    by_cat = Counter(r["category"] for r in rows)
    for c, n in by_cat.most_common():
        print(f"  {n:>3}  {c}")

    if args.dry_run:
        print("\n[dry-run] first 5:")
        for r in rows[:5]:
            print(f"  - {r['topic']}  ({r['primary_keyword']})")
        return

    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    params = {"on_conflict": "topic"}
    ins = upd = err = 0
    for i in range(0, len(rows), 25):
        batch = rows[i:i+25]
        r = httpx.post(url, headers=headers, params=params, json=batch, timeout=30)
        if r.status_code in (200, 201):
            for item in r.json():
                if item.get("used_at"):
                    upd += 1
                else:
                    ins += 1
        else:
            err += len(batch)
            print(f"[ERROR] {r.status_code}: {r.text[:200]}")
    print(f"\ninserted: {ins}  updated: {upd}  errors: {err}")


if __name__ == "__main__":
    main()
