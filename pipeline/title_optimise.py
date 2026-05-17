"""
Compare our published post metaTitles against top competitor titles for the
same target keyword. Ask DeepSeek to suggest a tighter, more click-worthy
metaTitle that conforms to winning patterns while keeping our angle.

Output: seo-research/title-rewrite-suggestions.csv with current vs suggested,
plus a one-line rationale. You review and apply manually.
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "utils"))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from config_supabase import DEEPSEEK_API_KEY, SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE
from deepseek_client import DeepSeekClient


ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "web" / "content" / "blog"
FUNDAMENTALS_DIR = ROOT / "web" / "content" / "fundamentals"
COMPETITOR_CSV = ROOT / "seo-research" / "serper-competitor-titles.csv"
OUT_CSV = ROOT / "seo-research" / "title-rewrite-suggestions.csv"


SYSTEM_PROMPT = """You are an expert UK SEO copywriter. You write metaTitles that:
- Are 50 to 60 characters
- Front-load the primary keyword
- Are click-worthy without being clickbait
- Conform to winning patterns from top-ranking competitors when they're justified
- Are specific (numbers, dates, scenarios) rather than generic
- Avoid AI cliches (unlock, navigate, complete guide unless genuinely a guide, etc.)
"""


def load_posts():
    """Load all published posts (blog + fundamentals)."""
    posts = []
    for d, kind in [(BLOG_DIR, "blog"), (FUNDAMENTALS_DIR, "fundamental")]:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            text = p.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
            if not m:
                continue
            fm = m.group(1)
            title = re.search(r'^title:\s*"([^"]*)"', fm, re.MULTILINE)
            slug = re.search(r'^slug:\s*"([^"]*)"', fm, re.MULTILINE)
            category = re.search(r'^category:\s*"([^"]*)"', fm, re.MULTILINE)
            meta_title = re.search(r'^metaTitle:\s*"([^"]*)"', fm, re.MULTILINE)
            if not (title and slug):
                continue
            posts.append({
                "kind": kind,
                "slug": slug.group(1),
                "title": title.group(1),
                "category": category.group(1) if category else "",
                "metaTitle": meta_title.group(1) if meta_title else "",
                "path": str(p),
            })
    return posts


def load_competitor_titles_by_keyword():
    if not COMPETITOR_CSV.exists():
        return {}
    by_kw = defaultdict(list)
    with COMPETITOR_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rank = int(row["rank"])
            except ValueError:
                continue
            if rank > 5:
                continue
            by_kw[row["source_topic"].lower()].append({
                "rank": rank,
                "title": row["competitor_title"],
            })
    return by_kw


def find_competitor_titles(post_title, competitor_data):
    """Match post title to competitor data via substring on the topic field."""
    nt = post_title.lower()
    for source_topic, hits in competitor_data.items():
        if source_topic in nt or nt.split(":")[0].strip() in source_topic:
            return hits
    return []


def suggest_title(client, post, competitor_titles):
    competitors_text = "\n".join(f"  {h['rank']}. {h['title']}" for h in competitor_titles[:5])
    user_prompt = f"""Our post:
  Title:     {post['title']}
  metaTitle: {post['metaTitle']} ({len(post['metaTitle'])} chars)
  Category:  {post['category']}

Top competitor titles for this topic:
{competitors_text if competitors_text else '  (no competitor data)'}

Suggest ONE replacement metaTitle that:
- Is 50 to 60 characters total (count them)
- Front-loads the primary keyword
- Is more compelling than the current one
- Borrows winning patterns from competitors where justified
- Is not clickbait

Format your response as exactly two lines, no preamble:
SUGGESTED: <new metaTitle here>
WHY: <one short sentence explaining the change>"""

    raw = client.generate_creative(
        prompt=user_prompt,
        system=SYSTEM_PROMPT,
        temperature=0.5,
        max_tokens=200,
    )
    suggested = ""
    why = ""
    for line in raw.splitlines():
        if line.upper().startswith("SUGGESTED:"):
            suggested = line.split(":", 1)[1].strip().strip('"').strip()
        elif line.upper().startswith("WHY:"):
            why = line.split(":", 1)[1].strip()
    return suggested, why


def main():
    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not set")
        sys.exit(1)

    posts = load_posts()
    competitor_data = load_competitor_titles_by_keyword()
    print(f"Loaded {len(posts)} posts ({sum(1 for p in posts if p['kind']=='blog')} blog, {sum(1 for p in posts if p['kind']=='fundamental')} pillar)")
    print(f"Competitor data: {len(competitor_data)} source topics")

    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)

    rows = []
    for i, post in enumerate(posts, 1):
        competitor_titles = find_competitor_titles(post["title"], competitor_data)
        try:
            suggested, why = suggest_title(client, post, competitor_titles)
        except Exception as e:
            print(f"  [{i}/{len(posts)}] {post['slug']}: ERROR {e}")
            continue
        if not suggested:
            continue
        rows.append({
            "kind": post["kind"],
            "slug": post["slug"],
            "current_metaTitle": post["metaTitle"],
            "current_len": len(post["metaTitle"]),
            "suggested_metaTitle": suggested,
            "suggested_len": len(suggested),
            "why": why,
            "competitor_count": len(competitor_titles),
        })
        print(f"  [{i}/{len(posts)}] {post['slug'][:45]:<45}  {len(post['metaTitle'])} -> {len(suggested)}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "kind", "slug", "current_metaTitle", "current_len",
            "suggested_metaTitle", "suggested_len", "why", "competitor_count"
        ])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {len(rows)} suggestions to {OUT_CSV}")
    print("Review the CSV, then apply changes manually (or I can apply selected ones for you).")


if __name__ == "__main__":
    main()
