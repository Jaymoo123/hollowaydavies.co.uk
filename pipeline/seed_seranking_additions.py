"""
Seed the highest-value SE Ranking additions into blog_topics_generalist.

Reads seo-research/rescore-additions.csv (produced by rescore_with_seranking.py),
filters to the buckets the user picked (pricing / service-specific / industry-
vertical / local-near-me by default), dedupes near-duplicate keywords into
single topics (with the duplicates rolled up as secondary_keywords), and
upserts to Supabase.

Run:
    python pipeline/seed_seranking_additions.py            # all 4 buckets
    python pipeline/seed_seranking_additions.py --dry-run
    python pipeline/seed_seranking_additions.py --buckets pricing service-specific
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict
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


CSV_PATH = Path(__file__).resolve().parents[1] / "seo-research" / "rescore-additions.csv"

STOPWORDS = {"a", "an", "the", "for", "of", "in", "on", "at", "to", "with",
             "and", "or", "by", "as", "is", "are", "uk"}


def normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def canonical_tokens(kw: str) -> frozenset:
    """Bag-of-words canonicalisation. Two keywords with the same content
    tokens (ignoring stopwords + plurals + order) collapse into one group."""
    toks = [t for t in normalise(kw).split() if t not in STOPWORDS]
    # Conservative synonyms
    syn = {"ltd": "limited"}
    toks = [syn.get(t, t) for t in toks]
    # Treat "accountant"/"accountants"/"accountancy"/"accounting" as the same root
    toks = ["accountant" if t in {"accountants", "accountancy", "accounting"} else t for t in toks]
    # Treat cost/costs/fee/fees/price/prices/pricing/charge/charges as the same root
    toks = ["cost" if t in {"costs", "fee", "fees", "price", "prices", "pricing", "charge", "charges"} else t for t in toks]
    # Treat "service"/"services" / "bookkeeper"/"bookkeepers"/"bookkeeping" as same roots
    toks = ["service" if t in {"services"} else t for t in toks]
    toks = ["bookkeeping" if t in {"bookkeeper", "bookkeepers"} else t for t in toks]
    # Treat "small business"/"small businesses" as same root
    toks = ["business" if t in {"businesses"} else t for t in toks]
    return frozenset(toks)


def bucket(kw: str) -> str:
    k = kw.lower()
    if any(c in k for c in ["near me", "my area"]):
        return "local-near-me"
    if any(c in k for c in ["hospitality", "agriculture", "hr ", "restaurant", "cafe", "retail",
                            "ecommerce", "dental", "medical", "legal", "construction",
                            "manufacturing", "tech ", "startup", "engineering", "consulting",
                            "creative", "marketing", "farm", "charity", "church", "school"]):
        return "industry-vertical"
    if any(c in k for c in ["cost", "fee", "fees", "price", "quote", "how much",
                            "pricing", "charge", "cheap"]):
        return "pricing"
    if any(c in k for c in ["payroll", "management accounting", "vat ", "cgt",
                            "self assessment", "self-assessment", "r&d", "company formation",
                            "incorporat", "annual accounts", "confirmation statement",
                            "bookkeep"]):
        return "service-specific"
    return "other"


def infer_category(kw: str) -> str:
    """Map a keyword to one of the 10 POST_CATEGORIES. More-specific rules first."""
    k = kw.lower()
    if any(t in k for t in ("r&d", "research and development", "rdec")):
        return "R&D Tax Credits"
    if any(t in k for t in ("vat", "mtd", "making tax digital", "flat rate")):
        return "VAT and Making Tax Digital"
    if any(t in k for t in ("payroll", "paye", "p11d", "p60", "p45", "cis ",
                            "accounts and payroll", "accounts & payroll")):
        return "Payroll and PAYE"
    if any(t in k for t in ("dividend", "directors loan", "director's loan",
                            "pay yourself", "trivial benefit")):
        return "Director Pay and Dividends"
    if any(t in k for t in ("badr", "capital gains", "cgt", "exit", "selling business",
                            "members voluntary", "mvl", "business asset disposal")):
        return "Exit and Capital Gains"
    if any(t in k for t in ("corporation tax", "ct600", "marginal relief",
                            "annual investment allowance")):
        return "Corporation Tax"
    if any(t in k for t in ("sole trader", "self employ", "self-employ",
                            "self assessment", "self-assessment", "freelancer", "freelance")):
        return "Sole Trader and Self Employment"
    if any(t in k for t in ("incorporat", "company formation", "holding company",
                            "family investment", "limited company vs", "sole trader vs")):
        return "Incorporation and Structure"
    if any(t in k for t in ("contractor", "ir35", "off-payroll", "off payroll",
                            "limited company", "ltd company", "ltd accountant")):
        return "Limited Company Tax"
    return "Bookkeeping and Compliance"  # default catch-all


def derive_topic_title(canonical_kw: str, bk: str) -> str:
    """Turn the canonical SE Ranking keyword into a clean Title Case topic."""
    acronyms = {"uk", "vat", "mtd", "ir35", "r&d", "paye", "cis", "cgt", "badr",
                "hmrc", "p11d", "p60", "p45", "ai", "ltd", "uae", "itsa", "mvl",
                "s455", "aia", "rdec", "sa100", "sa105", "ct600", "hr"}
    words = []
    for w in canonical_kw.split():
        if w.lower() in acronyms:
            words.append(w.upper())
        elif w.lower() in ("vs", "v"):
            words.append(w.lower())
        else:
            words.append(w[:1].upper() + w[1:].lower() if w else w)
    title = " ".join(words).strip()
    # Append a 2025/26 marker for pricing topics so titles are unique year-on-year
    if bk == "pricing" and "2025" not in title and "2026" not in title:
        title = f"{title} (2025/26)"
    return title


def load_and_group(buckets_wanted):
    """Load additions CSV, filter by bucket, group near-duplicates."""
    if not CSV_PATH.exists():
        sys.exit(f"missing {CSV_PATH}")
    rows = []
    with CSV_PATH.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            kw = (r.get("keyword") or "").strip()
            if not kw:
                continue
            # Drop SE Ranking-formatted negative-keyword queries and other noise
            if any(c in kw for c in ("-", "+", "[", "]", "(", ")", '"')):
                continue
            bk = bucket(kw)
            if bk not in buckets_wanted:
                continue
            try:
                sv = int(r.get("sv") or 0)
                kd = int(r.get("kd") or 50)
            except (ValueError, TypeError):
                sv, kd = 0, 50
            rows.append({"kw": kw, "sv": sv, "kd": kd,
                         "intent": r.get("intent", ""), "bucket": bk})
    # Group by canonical token set
    groups = defaultdict(list)
    for r in rows:
        groups[canonical_tokens(r["kw"])].append(r)
    # Pick representative per group: highest sv, then lowest kd
    topics = []
    for tokens, members in groups.items():
        members.sort(key=lambda r: (-r["sv"], r["kd"]))
        rep = members[0]
        secondary = [m["kw"] for m in members[1:]]
        topics.append({
            "primary_keyword": rep["kw"].lower(),
            "secondary_keywords": secondary,
            "sv": rep["sv"],
            "kd": rep["kd"],
            "intent": rep["intent"],
            "bucket": rep["bucket"],
            "members": [m["kw"] for m in members],
        })
    # Sort by SV desc then KD asc
    topics.sort(key=lambda t: (-t["sv"], t["kd"]))
    return topics


def topic_to_row(t):
    cat = infer_category(t["primary_keyword"])
    title = derive_topic_title(t["primary_keyword"], t["bucket"])
    # Map intent code(s) to our schema's enum
    intent_code = (t["intent"] or "").upper()
    if "T" in intent_code: intent = "transactional"
    elif "L" in intent_code or "C" in intent_code: intent = "transactional"  # commercial maps to transactional in our enum
    elif "N" in intent_code: intent = "navigational"
    else: intent = "informational"
    return {
        "topic": title,
        "category": cat,
        "primary_keyword": t["primary_keyword"],
        "secondary_keywords": t["secondary_keywords"][:5],  # cap to 5
        "user_intent": intent,
        "content_tier": "cluster",
        "publish_priority": 8,  # all SE-Ranking-sourced additions get P8
        "target_search_volume": t["sv"],
        "keyword_difficulty": t["kd"],
        "keyword_source": f"seranking-{t['bucket']}-v1",
        "notes": f"SE Ranking: sv={t['sv']} kd={t['kd']} bucket={t['bucket']} variants={len(t['members'])}",
        "used": False,
    }


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
        r = httpx.post(url, headers=headers, params=params, json=batch, timeout=30)
        if r.status_code in (200, 201):
            for item in r.json():
                if item.get("used_at"):
                    updated += 1
                else:
                    inserted += 1
        else:
            errors += len(batch)
            print(f"[ERROR] batch {i}: {r.status_code} {r.text[:300]}")
    return inserted, updated, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--buckets", nargs="+",
                        default=["pricing", "service-specific", "industry-vertical", "local-near-me"],
                        help="which buckets to add (default: all four picked)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Loading rescore-additions.csv, filtering to buckets: {args.buckets}")
    topics = load_and_group(set(args.buckets))
    print(f"  {len(topics)} unique topics after grouping near-duplicates")

    from collections import Counter
    by_bucket = Counter(t["bucket"] for t in topics)
    print("\nBy bucket (after dedupe):")
    for k, v in by_bucket.most_common():
        print(f"  {v:>3}  {k}")

    rows = [topic_to_row(t) for t in topics]

    from collections import Counter
    by_cat = Counter(r["category"] for r in rows)
    print("\nBy inferred category:")
    for c in POST_CATEGORIES:
        if by_cat.get(c):
            print(f"  {by_cat.get(c, 0):>3}  {c}")

    if args.dry_run:
        print("\n[dry-run] First 25 rows:")
        for r in rows[:25]:
            sk = f"  +{len(r['secondary_keywords'])} secondary" if r['secondary_keywords'] else ""
            print(f"  P{r['publish_priority']}  sv={r['target_search_volume']:>4}  kd={r['keyword_difficulty']:>3}  [{r['category'][:25]:<25}]  {r['topic']}{sk}")
        return

    print(f"\nUpserting {len(rows)} topics to {SUPABASE_TABLE}...")
    ins, upd, err = upsert(rows)
    print(f"  inserted: {ins}  updated: {upd}  errors: {err}")


if __name__ == "__main__":
    main()
