"""
LLM-driven blog topic ideation for Agency Founder Finance.

Asks DeepSeek to generate N new informational long-tail blog topics,
specifically excluding any that duplicate or paraphrase the existing 54.

Outputs seo-research/topic-ideas-llm.csv for human review before seeding.

Run:
    python pipeline/ideate_topics.py            # default 60 ideas
    python pipeline/ideate_topics.py --count 80
    python pipeline/ideate_topics.py --dry-run  # print ideas, no CSV write
"""
import argparse
import csv
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "utils"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from config_supabase import (
    DEEPSEEK_API_KEY,
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_TABLE,
    POST_CATEGORIES,
)
from deepseek_client import DeepSeekClient
import httpx


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "seo-research" / "topic-ideas-llm.csv"


SYSTEM_PROMPT = """You are a senior content strategist for Holloway Davies, a generalist
UK accountancy firm serving limited company directors, contractors, sole traders,
partnerships and small businesses across every sector.

You are an expert at identifying genuine search-demand gaps for SEO blog content.

You only generate topic ideas that:
- Target a specific, long-tail informational search query a real UK business owner, director or contractor would type
- Cover tax, finance, accounting, payroll, VAT, R&D, incorporation, exit, or compliance topics
- Avoid generic explainers a strong cornerstone already covers ("what is corporation tax", "what is VAT") unless angle is genuinely fresh
- Avoid pure commercial-intent landing-page queries ("accountant for X")
- Are distinct topics, not paraphrases of each other
- Reflect specific UK 2025/26 tax law (BADR 14% to 18% from April 2026, MTD ITSA April 2026 for £50k+, IR35 SDS, S455 33.75%, £500 dividend allowance, VAT threshold £90k)

You write tight, specific titles in question-format, how-to format, or scenario-format.
You do not use em-dashes. You do not use AI cliches ("unlocking", "navigating the complex", "in today's", "delve").
"""


def fetch_existing_topic_titles():
    """Pull all topic titles from Supabase (used + unused)."""
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = httpx.get(url, headers=headers, params={"select": "topic,category,primary_keyword"})
    r.raise_for_status()
    return r.json()


def build_user_prompt(count, existing):
    existing_titles = "\n".join(f"- {t['topic']}" for t in existing)
    categories_list = " | ".join(POST_CATEGORIES)
    n_cats = len(POST_CATEGORIES)
    per_cat = max(4, count // n_cats)
    return f"""Generate {count} NEW blog topic ideas for Holloway Davies (generalist UK accountancy firm).

REQUIREMENTS:
- Spread across all {n_cats} categories (at least {per_cat} per category, ideally more)
- Each idea must NOT duplicate or paraphrase any topic in the EXISTING TOPICS list below
- Each idea must be specific enough to target a single long-tail search query
- Mix of question-format, how-to, scenario-based, and comparison titles
- Include UK-specific angles where relevant (locations, tax years, HMRC forms, ICAEW)
- Include business-type specificity where relevant (limited company, contractor, sole trader, partnership, startup)
- Cover edge cases and timely questions (MTD ITSA April 2026 rollout, BADR rate change April 2026, Budget changes, S455 director loan rules)

CATEGORIES (use exact spelling):
{categories_list}

EXISTING TOPICS (DO NOT duplicate or paraphrase):
{existing_titles}

OUTPUT FORMAT (one idea per line, no numbering, no markdown):
CATEGORY | TITLE | PRIMARY_KEYWORD | ONE-LINE_RATIONALE

Example lines:
VAT and Making Tax Digital | When Should a Growing Sole Trader Voluntarily Register for VAT Before the Threshold? | voluntary vat registration sole trader | Pre-threshold planning gap, mid difficulty
Director Pay and Dividends | What Counts as a Trivial Benefit When You're the Only Director? | trivial benefits sole director | Compliance edge case, low difficulty

Generate exactly {count} ideas. Spread evenly across categories."""


def parse_ideas(raw_text):
    ideas = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" not in line:
            continue
        # Strip leading numbering / bullets
        line = re.sub(r"^[\-\*\d]+[\.\)]?\s*", "", line)
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        category = parts[0]
        title = parts[1]
        keyword = parts[2] if len(parts) > 2 else ""
        rationale = parts[3] if len(parts) > 3 else ""
        if not title or not category:
            continue
        ideas.append({
            "category": category,
            "title": title,
            "primary_keyword": keyword,
            "rationale": rationale,
        })
    return ideas


def normalise(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def dedupe(ideas, existing):
    existing_norm = {normalise(t["topic"]): t["topic"] for t in existing}
    existing_kw = {normalise(t.get("primary_keyword") or ""): t["topic"] for t in existing}
    unique = []
    dropped = []
    for idea in ideas:
        nt = normalise(idea["title"])
        nk = normalise(idea["primary_keyword"])
        if nt in existing_norm:
            dropped.append((idea, f"duplicate title of: {existing_norm[nt]}"))
            continue
        if nk and nk in existing_kw and nk != "":
            dropped.append((idea, f"duplicate keyword of: {existing_kw[nk]}"))
            continue
        if idea["category"] not in POST_CATEGORIES:
            dropped.append((idea, f"unknown category: {idea['category']}"))
            continue
        unique.append(idea)
    return unique, dropped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=60, help="number of ideas to request")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Fetching existing topics from Supabase...")
    existing = fetch_existing_topic_titles()
    print(f"  {len(existing)} existing topics loaded")

    print(f"\nAsking DeepSeek for {args.count} new topic ideas...")
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
    raw = client.generate_creative(
        prompt=build_user_prompt(args.count, existing),
        system=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=4096,
    )
    print(f"[OK] {len(raw)} chars returned")

    ideas = parse_ideas(raw)
    print(f"[OK] {len(ideas)} ideas parsed from response")

    unique, dropped = dedupe(ideas, existing)
    print(f"[OK] {len(unique)} unique (dropped {len(dropped)} duplicates / invalid)")

    from collections import Counter
    dist = Counter(i["category"] for i in unique)
    print("\nDistribution:")
    for cat in POST_CATEGORIES:
        print(f"  {dist.get(cat, 0):>3}  {cat}")

    if dropped:
        print("\nDropped (first 10):")
        for d, reason in dropped[:10]:
            print(f"  - {d['title'][:60]}  ({reason})")

    if args.dry_run:
        print("\n[dry-run] First 5 unique ideas:")
        for i in unique[:5]:
            print(f"  [{i['category']}] {i['title']}")
            print(f"      kw: {i['primary_keyword']} | {i['rationale']}")
        return

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "title", "primary_keyword", "rationale"])
        for idea in unique:
            w.writerow([idea["category"], idea["title"], idea["primary_keyword"], idea["rationale"]])
    print(f"\nWritten {len(unique)} ideas to {OUT_CSV}")


if __name__ == "__main__":
    main()
