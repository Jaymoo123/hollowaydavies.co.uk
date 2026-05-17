"""
Generate competitor-informed topic ideas.

Reads serper-competitor-titles.csv. For each source_keyword, takes the top
competitor titles and asks DeepSeek to generate angle ideas we are NOT
covering. Dedupes against existing topics. Output to
seo-research/serper-gap-ideas.csv.
"""
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

from config_supabase import (
    DEEPSEEK_API_KEY,
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_TABLE,
    POST_CATEGORIES,
)

try:
    from deepseek_client import DeepSeekClient
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "utils"))
    from deepseek_client import DeepSeekClient


ROOT = Path(__file__).resolve().parents[1]
COMPETITOR_CSV = ROOT / "seo-research" / "serper-competitor-titles.csv"
OUT_CSV = ROOT / "seo-research" / "serper-gap-ideas.csv"


SYSTEM_PROMPT = """You are a senior SEO content strategist for Holloway Davies,
a generalist UK accountancy firm serving limited company directors, contractors,
sole traders, partnerships and small businesses across every sector.

You generate topic angles we are NOT covering, that fill gaps in our existing
content based on what competitors are ranking for.

Each idea must:
- Be a specific long-tail topic a UK business owner, director or contractor would search for
- Cover an angle that the competitors below haven't covered well (or that we can do better)
- Avoid duplicating any of our existing topics listed
- Be relevant to UK business tax, accounting, compliance, payroll, VAT, R&D, incorporation or exit
- Use a specific framing (question, how-to, scenario, comparison, numbered guide)
- Reflect current UK 2025/26 tax law where relevant (MTD ITSA April 2026, BADR rate change April 2026, dividend allowance £500, etc.)

You do not use em-dashes. You do not use AI cliches ("unlock", "navigate the complex", "in today's", "delve").
"""


def normalise(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def fetch_existing():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = httpx.get(url, headers=headers, params={"select": "topic,category,primary_keyword"})
    r.raise_for_status()
    return r.json()


def load_competitor_groups():
    groups = defaultdict(list)
    with COMPETITOR_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rank = int(row["rank"])
            except ValueError:
                continue
            if rank > 6:
                continue
            groups[(row["source_keyword"], row["source_topic"], row["category"])].append({
                "rank": rank,
                "title": row["competitor_title"],
                "url": row["competitor_url"],
                "snippet": row["snippet"],
            })
    return groups


def parse_ideas(raw):
    ideas = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        line = re.sub(r"^[\-\*\d]+[\.\)]?\s*", "", line)
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        cat = parts[0]
        title = parts[1]
        keyword = parts[2] if len(parts) > 2 else ""
        rationale = parts[3] if len(parts) > 3 else ""
        if not title or cat not in POST_CATEGORIES:
            continue
        ideas.append({
            "category": cat,
            "title": title,
            "primary_keyword": keyword,
            "rationale": rationale,
        })
    return ideas


def main():
    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not set")
        sys.exit(1)

    print(f"Loading competitor data from {COMPETITOR_CSV.name}...")
    groups = load_competitor_groups()
    print(f"  {len(groups)} keyword groups with top-6 competitor results")

    print("Loading existing topics from Supabase...")
    existing = fetch_existing()
    existing_titles = set(normalise(e["topic"]) for e in existing)
    existing_kw = set(normalise(e.get("primary_keyword") or "") for e in existing)
    print(f"  {len(existing)} existing topics")

    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)

    # Build single prompt with all keyword groups
    categories_list = " | ".join(POST_CATEGORIES)
    group_blocks = []
    for (kw, topic, cat), hits in groups.items():
        comp = "\n".join(f"    {h['rank']}. {h['title']}" for h in hits[:5])
        group_blocks.append(f"  Keyword: {kw}  (our topic: {topic}, category: {cat})\n  Top competitors:\n{comp}")
    # Limit to first 25 groups to keep prompt within token budget
    if len(group_blocks) > 25:
        group_blocks = group_blocks[:25]
        print(f"  (limited to first 25 groups for prompt budget)")
    groups_text = "\n\n".join(group_blocks)

    existing_titles_text = "\n".join(f"- {e['topic']}" for e in existing[:120])

    user_prompt = f"""Below is our existing content map plus competitor SERP intelligence for our target keywords.

For each keyword group, generate 2 NEW topic ideas that:
- Target the same keyword cluster from an angle the competitors don't cover well
- Are not paraphrases of our existing topics
- Use specific UK generalist business-tax framing (Ltd directors, contractors, sole traders, small businesses)

CATEGORIES (use exact spelling):
{categories_list}

EXISTING TOPICS (do not duplicate):
{existing_titles_text}

KEYWORD GROUPS + TOP COMPETITORS:
{groups_text}

OUTPUT FORMAT (one idea per line, no markdown, no numbering):
CATEGORY | TITLE | PRIMARY_KEYWORD | RATIONALE (one short sentence: which competitor gap, or why we can win)

Generate around 50 ideas total, spread across the keyword groups."""

    print("Asking DeepSeek for gap topic ideas...")
    raw = client.generate_creative(
        prompt=user_prompt,
        system=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=4096,
    )
    print(f"[OK] {len(raw)} chars returned")

    ideas = parse_ideas(raw)
    print(f"[OK] {len(ideas)} parsed")

    unique = []
    dropped = []
    for i in ideas:
        nt = normalise(i["title"])
        # Dedupe ONLY on title - two different angle posts can share a primary keyword
        if nt in existing_titles:
            dropped.append((i, "exact title duplicate"))
            continue
        unique.append(i)
    print(f"[OK] {len(unique)} unique (dropped {len(dropped)} duplicates)")
    if dropped and len(dropped) >= len(ideas) - 5:
        print(f"  Sample of dropped (debug):")
        for d, reason in dropped[:5]:
            print(f"    - {d['title']!r}  ({reason})")

    from collections import Counter
    dist = Counter(i["category"] for i in unique)
    print("\nDistribution:")
    for cat in POST_CATEGORIES:
        print(f"  {dist.get(cat, 0):>3}  {cat}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "title", "primary_keyword", "rationale"])
        for i in unique:
            w.writerow([i["category"], i["title"], i["primary_keyword"], i["rationale"]])
    print(f"\nWrote {OUT_CSV}")


if __name__ == "__main__":
    main()
