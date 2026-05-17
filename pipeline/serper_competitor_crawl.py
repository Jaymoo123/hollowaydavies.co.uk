"""
Crawl direct competitors' indexed pages via Serper `site:` queries.

For each competitor domain, query Serper for `site:domain.com` and capture
every URL + title Google returns. Aggregate into a content matrix.

Outputs:
  - serper-competitor-content-map.csv  (every URL per competitor)
  - serper-competitor-summary.csv      (per-competitor topic counts)

Run:
    python pipeline/serper_competitor_crawl.py
"""
import csv
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

import httpx

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass


ROOT = Path(__file__).resolve().parents[1]
OUT_MAP = ROOT / "seo-research" / "serper-competitor-content-map.csv"
OUT_SUMMARY = ROOT / "seo-research" / "serper-competitor-summary.csv"

SERPER_KEY = os.getenv("SERPER_API_KEY")

# Direct UK generalist accountancy competitors.
# - Online accountants: Crunch, Mazuma, TaxAssist, Boox, Gorilla, The Accountancy,
#   Accounting-Wise (a-wise.co.uk), FastAccountant
# - Traditional generalist firms: Haines Watts (hwca.com)
# - Software/learn hubs that rank for cornerstone UK Ltd / sole-trader queries:
#   FreeAgent, GoSimpleTax
# - Company formation + filing hub: 1stFormations
# The four added (gorillaaccounting, theaccountancy, a-wise, 1stformations) each
# appeared 10-14 times in the seed SERPs we already captured.
COMPETITORS = [
    "crunch.co.uk",
    "mazumamoney.co.uk",
    "taxassist.co.uk",
    "boox.co.uk",
    "freeagent.com",
    "hwca.com",
    "gosimpletax.com",
    "fastaccountant.co.uk",
    "gorillaaccounting.com",
    "theaccountancy.co.uk",
    "a-wise.co.uk",
    "1stformations.co.uk",
]

# How many pages of results to pull per competitor (each page = ~10 results).
PAGES_PER_COMPETITOR = 6
SLEEP = 0.4


def serper(q, page=1):
    body = {"q": q, "gl": "gb", "num": 10, "page": page}
    r = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
        json=body,
        timeout=20.0,
    )
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    return r.json()


def classify_topic(title, url):
    """Crude topic classification — useful for the per-competitor summary."""
    t = (title + " " + url).lower()
    # Order matters: more specific rules first so a CIS/R&D page doesn't get
    # caught by the broad "Tax/Compliance" rule.
    rules = [
        ("R&D", ["r&d", "r and d", "research and development", "rdec"]),
        ("MTD", ["mtd", "making tax digital"]),
        ("VAT", ["vat ", "/vat", "flat rate", "reverse charge"]),
        ("IR35", ["ir35", "off-payroll", "off payroll"]),
        ("Payroll/PAYE", ["payroll", " paye", "p11d", "p60", "p45", "cis "]),
        ("Director Pay/Dividends", ["dividend", "pay yourself", "directors loan", "directors' loan", "trivial benefit"]),
        ("Incorporation/Structure", ["incorporat", "limited compan", "sole trader", "company formation", "holding company", "family investment company"]),
        ("Exit/CGT", ["exit ", "selling", "badr", "business asset disposal", "capital gains", "cgt", "mvl", "members voluntary"]),
        ("Corporation Tax", ["corporation tax", "ct600", "marginal relief", "annual investment allowance"]),
        ("Self Assessment", ["self assessment", "self-assessment", "tax return"]),
        ("Bookkeeping/Software", ["bookkeep", "xero", "quickbooks", "freeagent", "sage ", "software", "dext"]),
        ("Compliance/HMRC", ["hmrc", "companies house", "confirmation statement", "annual accounts"]),
        ("Pricing/Services", ["pricing", "fees", "cost of", "how much"]),
    ]
    matched = [name for name, kws in rules if any(k in t for k in kws)]
    return matched[0] if matched else "Other"


def main():
    if not SERPER_KEY:
        print("ERROR: SERPER_API_KEY not set")
        sys.exit(1)

    print(f"Crawling {len(COMPETITORS)} competitors, up to {PAGES_PER_COMPETITOR} pages each...")
    rows = []
    credits = 0
    for domain in COMPETITORS:
        urls_seen = set()
        page_results = 0
        for page in range(1, PAGES_PER_COMPETITOR + 1):
            try:
                data = serper(f"site:{domain}", page=page)
            except Exception as e:
                print(f"  {domain} p{page}: ERROR {e}")
                break
            credits += int(data.get("credits") or 1)
            organic = data.get("organic", [])
            if not organic:
                break
            new = 0
            for hit in organic:
                url = (hit.get("link") or "").strip()
                if not url or url in urls_seen:
                    continue
                urls_seen.add(url)
                title = (hit.get("title") or "").strip()
                topic = classify_topic(title, url)
                rows.append({
                    "competitor": domain,
                    "topic_cluster": topic,
                    "title": title,
                    "url": url,
                    "snippet": (hit.get("snippet") or "")[:200],
                })
                new += 1
                page_results += 1
            if new == 0:
                break
            time.sleep(SLEEP)
        print(f"  {domain}: captured {page_results} pages")

    print(f"\nCredits used: {credits}")
    print(f"Total competitor pages captured: {len(rows)}")

    OUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    with OUT_MAP.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["competitor", "topic_cluster", "title", "url", "snippet"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {OUT_MAP}")

    # Per-competitor topic cluster summary
    by_comp = defaultdict(lambda: Counter())
    for r in rows:
        by_comp[r["competitor"]][r["topic_cluster"]] += 1

    all_clusters = sorted({r["topic_cluster"] for r in rows})
    with OUT_SUMMARY.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["competitor", "total_pages", *all_clusters])
        for comp in COMPETITORS:
            c = by_comp.get(comp, Counter())
            w.writerow([comp, sum(c.values()), *[c.get(cl, 0) for cl in all_clusters]])
    print(f"Wrote {OUT_SUMMARY}")

    # Print a quick on-screen comparison
    print("\nPer-competitor topic coverage:")
    print(f"{'competitor':<30} {'total':>5}  {'  '.join(f'{cl[:6]:>6}' for cl in all_clusters)}")
    for comp in COMPETITORS:
        c = by_comp.get(comp, Counter())
        cells = "  ".join(f"{c.get(cl, 0):>6}" for cl in all_clusters)
        print(f"{comp:<30} {sum(c.values()):>5}  {cells}")


if __name__ == "__main__":
    main()
