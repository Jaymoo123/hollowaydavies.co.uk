"""
Serper.dev SERP mining for Agency Founder Finance.

For each primary_keyword in blog_topics_agency (used + unused), query Serper
UK and capture:
  - peopleAlsoAsk (when Google returns them)
  - relatedSearches (when Google returns them)
  - top 10 organic competitor titles + URLs

Outputs two CSVs to seo-research/:
  - serper-paa-candidates.csv  (deduped new topic ideas from PAA + related)
  - serper-competitor-titles.csv  (competitor SERP intelligence for gap analysis)

Run:
    python pipeline/serper_mine.py                  # all unique primary keywords
    python pipeline/serper_mine.py --limit 20       # cap to first 20 queries
    python pipeline/serper_mine.py --pillars-only   # only the 9 pillar keywords
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


SERPER_KEY = os.getenv("SERPER_API_KEY")
ROOT = Path(__file__).resolve().parents[1]
PAA_CSV = ROOT / "seo-research" / "serper-paa-candidates.csv"
COMPETITOR_CSV = ROOT / "seo-research" / "serper-competitor-titles.csv"


def fetch_topics(pillars_only=False):
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


def serper_query(q, gl="gb"):
    r = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
        json={"q": q, "gl": gl, "num": 10},
        timeout=20.0,
    )
    r.raise_for_status()
    return r.json()


def normalise(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="cap number of queries")
    parser.add_argument("--pillars-only", action="store_true", help="only query pillar keywords")
    parser.add_argument("--sleep", type=float, default=0.5, help="seconds between requests")
    args = parser.parse_args()

    if not SERPER_KEY:
        print("ERROR: SERPER_API_KEY not set in .env")
        sys.exit(1)

    topics = fetch_topics(pillars_only=args.pillars_only)
    if args.limit:
        topics = topics[: args.limit]
    print(f"Querying Serper for {len(topics)} keywords (UK)...")

    existing_titles_normalised = set(normalise(t["topic"]) for t in topics)
    existing_kw_normalised = set(normalise(t["primary_keyword"]) for t in topics)

    paa_candidates = {}  # normalised -> {question, source_topic, source_kw}
    related_candidates = {}
    competitor_rows = []

    credits_used = 0
    no_paa_count = 0
    for i, t in enumerate(topics, 1):
        kw = t["primary_keyword"]
        try:
            data = serper_query(kw)
        except Exception as e:
            print(f"  [{i}/{len(topics)}] {kw}: ERROR {e}")
            continue
        credits_used += int(data.get("credits") or 1)

        # Organic top 10 → competitor intelligence
        for pos, hit in enumerate(data.get("organic", [])[:10], 1):
            competitor_rows.append({
                "source_keyword": kw,
                "source_topic": t["topic"],
                "category": t["category"],
                "rank": pos,
                "competitor_title": hit.get("title", ""),
                "competitor_url": hit.get("link", ""),
                "snippet": (hit.get("snippet", "") or "")[:200],
            })

        paa = data.get("peopleAlsoAsk", [])
        rel = data.get("relatedSearches", [])

        if not paa:
            no_paa_count += 1

        # PAA → new topic candidates (skip if duplicates existing)
        for q in paa:
            question = q.get("question", "").strip()
            if not question:
                continue
            nq = normalise(question)
            if nq in existing_titles_normalised:
                continue
            if nq not in paa_candidates:
                paa_candidates[nq] = {
                    "question": question,
                    "source_keyword": kw,
                    "source_topic": t["topic"],
                    "source_category": t["category"],
                }

        # Related searches
        for r in rel:
            query = r.get("query", "").strip()
            if not query:
                continue
            nq = normalise(query)
            if nq in existing_kw_normalised or nq in existing_titles_normalised:
                continue
            if nq not in related_candidates:
                related_candidates[nq] = {
                    "query": query,
                    "source_keyword": kw,
                    "source_topic": t["topic"],
                    "source_category": t["category"],
                }

        print(f"  [{i:>3}/{len(topics)}] {kw[:55]:<55} paa={len(paa)} rel={len(rel)} organic={len(data.get('organic',[]))}")
        time.sleep(args.sleep)

    print()
    print(f"Credits used: {credits_used}")
    print(f"Queries with no PAA: {no_paa_count}/{len(topics)}")
    print(f"Unique PAA candidates: {len(paa_candidates)}")
    print(f"Unique related-search candidates: {len(related_candidates)}")
    print(f"Competitor rows captured: {len(competitor_rows)}")

    PAA_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PAA_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source", "candidate_question_or_query", "source_keyword", "source_topic", "source_category"])
        for c in paa_candidates.values():
            w.writerow(["PAA", c["question"], c["source_keyword"], c["source_topic"], c["source_category"]])
        for c in related_candidates.values():
            w.writerow(["RELATED", c["query"], c["source_keyword"], c["source_topic"], c["source_category"]])
    print(f"Wrote {PAA_CSV}")

    with COMPETITOR_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "source_keyword", "source_topic", "category", "rank",
            "competitor_title", "competitor_url", "snippet"
        ])
        w.writeheader()
        for row in competitor_rows:
            w.writerow(row)
    print(f"Wrote {COMPETITOR_CSV}")


if __name__ == "__main__":
    main()
