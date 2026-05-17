"""
Fix cluster-on-cluster cannibalisation by re-pointing duplicate
primary_keywords to narrower long-tail variants.

Logic:
  1. Group used posts by (category, normalised primary_keyword)
  2. Where >1 cluster post shares a keyword, keep the one with shortest
     title (most generic = the canonical landing for that query) AND keep
     any pillar untouched. Re-point all other clusters.
  3. For each post needing re-pointing, ask DeepSeek to derive a narrower
     long-tail keyword (3-6 words) from the post's actual title.
  4. Update .md frontmatter + Supabase row.
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
BLOG = ROOT / "web" / "content" / "blog"
FUND = ROOT / "web" / "content" / "fundamentals"


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def fetch_posts():
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        params={
            "select": "id,topic,slug,category,primary_keyword,content_tier",
            "used": "eq.true",
        },
    )
    r.raise_for_status()
    return r.json()


def identify_repointing_candidates(posts):
    """Returns list of posts that need a new keyword.

    A cluster post needs re-pointing if:
      - Its primary_keyword (normalised) is shared with another cluster post
        OR with a pillar in the same category
      - AND it's NOT the keeper for that group
    """
    by_group = defaultdict(list)
    for p in posts:
        if not p.get("primary_keyword"):
            continue
        key = (p["category"], norm(p["primary_keyword"]))
        by_group[key].append(p)

    needs_repointing = []
    for (cat, kw), group in by_group.items():
        if len(group) <= 1:
            continue
        # Sort: pillars stay (lowest sort), then shortest-title cluster keeps
        pillars = [p for p in group if p.get("content_tier") == "pillar"]
        clusters = [p for p in group if p.get("content_tier") != "pillar"]
        clusters.sort(key=lambda x: len(x["topic"]))

        # Keepers: ALL pillars + the shortest-title cluster
        keep = set(p["id"] for p in pillars)
        if clusters:
            keep.add(clusters[0]["id"])

        for p in group:
            if p["id"] not in keep:
                needs_repointing.append(p)
    return needs_repointing


def generate_narrow_keyword(client, post):
    prompt = f"""Generate a NARROW long-tail primary keyword (3-6 words, no punctuation) for this UK business accountancy blog post.

Title: {post['topic']}
Current keyword (too broad, conflicts with another post): {post['primary_keyword']}
Category: {post['category']}

Rules:
- Must be 3-6 words
- Must be more specific than the current keyword
- Must be a phrase a real UK business owner (limited company director, contractor, sole trader, partnership owner, small business owner) might type into Google
- Must reflect the SPECIFIC angle of this post's title (not the generic category)
- No punctuation, no quotes
- UK English

Return ONLY the keyword phrase on one line, nothing else."""
    out = client.generate_creative(prompt=prompt, system="You are an SEO keyword strategist for a UK generalist accountancy firm. You return concise long-tail keywords only.", temperature=0.4, max_tokens=60)
    # Take first non-empty line, strip
    for line in out.splitlines():
        line = line.strip().strip('"').strip("'").strip()
        if line and 8 <= len(line) <= 80:
            # Sanity: must not be the same as current
            if norm(line) != norm(post["primary_keyword"]):
                return line
    return None


def find_md(slug):
    for d in [BLOG, FUND]:
        p = d / f"{slug}.md"
        if p.exists():
            return p
    return None


def update_md(path, new_kw):
    """Currently we don't store primary_keyword in MD frontmatter, so this is a no-op.
    Slug + canonical + content all stay the same. Only the Supabase row tracks the
    keyword going forward (for analytics / future regeneration)."""
    return


def update_supabase(post_id, new_kw):
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        params={"id": f"eq.{post_id}"},
        json={"primary_keyword": new_kw},
        timeout=15,
    )
    r.raise_for_status()


def main():
    print("Fetching used posts...")
    posts = fetch_posts()
    print(f"  {len(posts)} posts loaded")

    candidates = identify_repointing_candidates(posts)
    print(f"\n  {len(candidates)} posts need re-pointing (cluster-on-cluster overlap)")
    if not candidates:
        print("No cannibalisation found.")
        return

    print("\n  Sample of what needs fixing:")
    for c in candidates[:5]:
        print(f"    [{c['category']}] {c['topic'][:75]}")
        print(f"      current kw: '{c['primary_keyword']}'")

    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)

    log_rows = []
    updated = 0
    for i, post in enumerate(candidates, 1):
        try:
            new_kw = generate_narrow_keyword(client, post)
        except Exception as e:
            print(f"  [{i}/{len(candidates)}] {post['slug']}: ERROR {e}")
            continue
        if not new_kw:
            print(f"  [{i}/{len(candidates)}] {post['slug']}: no suggestion returned")
            continue
        try:
            update_supabase(post["id"], new_kw)
        except Exception as e:
            print(f"  [{i}/{len(candidates)}] {post['slug']}: Supabase ERROR {e}")
            continue
        log_rows.append({
            "slug": post["slug"],
            "category": post["category"],
            "old_keyword": post["primary_keyword"],
            "new_keyword": new_kw,
        })
        updated += 1
        print(f"  [{i:>2}/{len(candidates)}] {post['slug'][:60]:<60}")
        print(f"         '{post['primary_keyword']}' -> '{new_kw}'")

    # Write change log
    log_path = ROOT / "seo-research" / "cannibalisation-fix-log.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["slug", "category", "old_keyword", "new_keyword"])
        w.writeheader()
        for row in log_rows:
            w.writerow(row)
    print(f"\nUpdated {updated} posts. Change log: {log_path}")


if __name__ == "__main__":
    main()
