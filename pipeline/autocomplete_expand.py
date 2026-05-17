"""
Google Autocomplete expansion for the generalist seed set.

Why this exists: Serper's UK SERP responses on this account return only the
`organic` block (no peopleAlsoAsk, no relatedSearches). Google Autocomplete is
a free public endpoint that surfaces real query completions, so we use it as
a fallback for seed expansion.

For every primary_keyword in blog_topics_generalist, we query the autocomplete
endpoint with:
  - the keyword itself
  - the keyword prefixed by each WH-word / common question opener
  - the keyword suffixed with location / pricing / comparison modifiers

Suggestions are deduped against existing topics + each other.

Output: seo-research/autocomplete-candidates.csv

Run:
    python pipeline/autocomplete_expand.py
    python pipeline/autocomplete_expand.py --limit 20      # cap seeds
    python pipeline/autocomplete_expand.py --pillars-only  # only pillar keywords
"""
import argparse
import csv
import os
import re
import sys
import time
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


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "seo-research" / "autocomplete-candidates.csv"

# Prefix variants: WH-questions and high-intent openers.
PREFIXES = ["", "how", "what", "when", "can i", "how much", "how to"]

# Suffix variants: pricing, comparison, location, freshness modifiers.
SUFFIXES = ["", "uk", "cost", "vs", "2026"]


def fetch_seeds(pillars_only=False):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    params = {
        "select": "topic,primary_keyword,category,content_tier",
        "order": "publish_priority.desc.nullslast",
    }
    if pillars_only:
        params["content_tier"] = "eq.pillar"
    r = httpx.get(url, headers=headers, params=params, timeout=15.0)
    r.raise_for_status()
    return [t for t in r.json() if t.get("primary_keyword")]


def autocomplete(query: str, client: httpx.Client):
    """Hit Google's unofficial autocomplete endpoint. Returns a list of suggestions."""
    try:
        r = client.get(
            "http://suggestqueries.google.com/complete/search",
            params={"client": "firefox", "q": query, "hl": "en-GB", "gl": "uk"},
            timeout=8.0,
        )
        if r.status_code != 200:
            return []
        data = r.json()
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            return [s for s in data[1] if isinstance(s, str)]
    except Exception:
        return []
    return []


def normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def build_query_variants(keyword: str):
    """Build the set of query strings we'll send to autocomplete for one seed."""
    variants = set()
    for prefix in PREFIXES:
        for suffix in SUFFIXES:
            parts = []
            if prefix:
                parts.append(prefix)
            parts.append(keyword)
            if suffix:
                parts.append(suffix)
            q = " ".join(parts).strip()
            variants.add(q)
    return sorted(variants)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--pillars-only", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.05,
                        help="seconds between autocomplete requests")
    args = parser.parse_args()

    seeds = fetch_seeds(pillars_only=args.pillars_only)
    if args.limit:
        seeds = seeds[: args.limit]
    print(f"Expanding autocomplete for {len(seeds)} seeds...")

    existing_titles = set(normalise(s["topic"]) for s in seeds)
    existing_kw = set(normalise(s["primary_keyword"]) for s in seeds)

    # Pre-compute query plan size so we can show a progress estimate.
    sample_variants = len(build_query_variants("x"))
    total_queries = len(seeds) * sample_variants
    print(f"  ~{sample_variants} variants per seed = ~{total_queries} autocomplete calls")
    print(f"  Estimated runtime: ~{total_queries * args.sleep / 60:.1f} min")

    candidates = {}  # normalised -> dict
    queries_made = 0

    with httpx.Client() as client:
        for i, seed in enumerate(seeds, 1):
            kw = seed["primary_keyword"]
            variants = build_query_variants(kw)
            seed_suggestions = set()
            for q in variants:
                suggs = autocomplete(q, client)
                queries_made += 1
                for s in suggs:
                    s_clean = s.strip()
                    if not s_clean or len(s_clean) < 5:
                        continue
                    seed_suggestions.add(s_clean)
                time.sleep(args.sleep)

            # Dedupe + filter
            new_for_seed = 0
            for s in seed_suggestions:
                ns = normalise(s)
                if ns in existing_titles or ns in existing_kw:
                    continue
                # Skip suggestions identical to the seed
                if ns == normalise(kw):
                    continue
                if ns not in candidates:
                    candidates[ns] = {
                        "suggestion": s,
                        "source_keyword": kw,
                        "source_topic": seed["topic"],
                        "source_category": seed["category"],
                        "source_tier": seed.get("content_tier") or "",
                    }
                    new_for_seed += 1

            print(f"  [{i:>3}/{len(seeds)}] {kw[:50]:<50} variants={len(variants)} suggestions={len(seed_suggestions)} new={new_for_seed}")

    print()
    print(f"Total autocomplete calls: {queries_made}")
    print(f"Unique new candidates: {len(candidates)}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["suggestion", "source_keyword", "source_topic", "source_category", "source_tier"])
        for c in candidates.values():
            w.writerow([c["suggestion"], c["source_keyword"], c["source_topic"], c["source_category"], c["source_tier"]])
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
