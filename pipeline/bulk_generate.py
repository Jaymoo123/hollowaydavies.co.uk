"""
Bulk generate ALL queued (unused) topics from blog_topics_generalist with
N-way parallelism via a thread pool.

Pre-fetches the topic list once, then assigns each topic to exactly one
worker thread. No claim races, no wasted LLM calls.

Each topic goes through the same pipeline as `generate_blog_supabase.py`:
1. DeepSeek content generation (pillar or cluster prompt)
2. Parse + validate + strip dashes
3. Pexels image fetch
4. Write markdown to web/content/blog/ or web/content/fundamentals/
5. Mark topic used in Supabase
6. Enqueue URL for IndexNow

Run:
    python pipeline/bulk_generate.py                  # all unused, default 5 workers
    python pipeline/bulk_generate.py --workers 3
    python pipeline/bulk_generate.py --limit 20       # cap to first 20
    python pipeline/bulk_generate.py --tier pillar    # only pillar topics
    python pipeline/bulk_generate.py --dry-run        # generate but don't mark used / IndexNow
    python pipeline/bulk_generate.py --skip-image     # skip Pexels fetch (faster, no image)
"""
import argparse
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Force UTF-8 stdout on Windows
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "utils"))

import httpx

import generate_blog_supabase as gen


def fetch_all_unused(tier=None, limit=None):
    url = f"{gen.SUPABASE_URL}/rest/v1/{gen.SUPABASE_TABLE}"
    headers = {"apikey": gen.SUPABASE_KEY, "Authorization": f"Bearer {gen.SUPABASE_KEY}"}
    params = {
        "used": "eq.false",
        # Pillars first within each priority level, then by created_at to keep
        # results stable across calls.
        "order": "publish_priority.desc.nullslast,content_tier.desc,created_at.asc",
    }
    if tier:
        params["content_tier"] = f"eq.{tier}"
    r = httpx.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    topics = r.json()
    if limit:
        topics = topics[:limit]
    return topics


def process_one(topic, dry_run=False, skip_image=False):
    """Generate, write, mark used. Returns (slug, error_str)."""
    topic_id = topic["id"]
    title = topic["topic"]
    tier = topic.get("content_tier", "cluster")
    t0 = time.time()
    try:
        # Temporarily silence fetch_image if requested
        if skip_image:
            gen.fetch_image_for_post = None

        raw = gen.generate_content(topic)
        fields = gen.parse_llm_output(raw)
        slug = gen.export_to_markdown(fields, content_tier=tier)
        if not dry_run:
            gen.mark_topic_used(topic_id, slug)
            try:
                from submit_indexnow import enqueue
                enqueue(f"{gen.SITE_BASE_URL}/blog/{slug}")
            except Exception:
                pass  # IndexNow enqueue failure is non-fatal
        elapsed = time.time() - t0
        return (slug, None, elapsed, tier)
    except Exception as e:
        elapsed = time.time() - t0
        return (None, f"{title[:60]}: {type(e).__name__}: {e}", elapsed, tier)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5, help="parallel worker threads (default 5)")
    parser.add_argument("--limit", type=int, default=None, help="cap to first N unused topics")
    parser.add_argument("--tier", choices=["pillar", "cluster", "supporting"], help="restrict to one tier")
    parser.add_argument("--dry-run", action="store_true", help="skip mark_topic_used + IndexNow")
    parser.add_argument("--skip-image", action="store_true", help="skip Pexels image fetch")
    args = parser.parse_args()

    print("=" * 70)
    print(f"BULK CONTENT GENERATION  (workers={args.workers})")
    print(f"Site: {gen.SITE_BASE_URL}")
    print(f"Table: {gen.SUPABASE_TABLE}")
    if args.dry_run:
        print("DRY RUN: markdown will be written; topics NOT marked used.")
    print("=" * 70)

    topics = fetch_all_unused(tier=args.tier, limit=args.limit)
    print(f"\nQueued: {len(topics)} unused topics")
    if not topics:
        print("Nothing to do.")
        return

    # Show what's about to run
    from collections import Counter
    tiers = Counter(t.get("content_tier", "cluster") for t in topics)
    pris = Counter(t.get("publish_priority") for t in topics)
    print(f"  by tier: {dict(tiers)}")
    print(f"  by priority: {dict(sorted(pris.items(), key=lambda x: -(x[0] or 0)))}")
    print()

    start = time.time()
    succeeded, failed = [], []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(process_one, t, args.dry_run, args.skip_image): t for t in topics}
        for i, future in enumerate(as_completed(futures), 1):
            topic = futures[future]
            slug, err, elapsed, tier = future.result()
            prefix = f"[{i:>3}/{len(topics)}] {elapsed:>5.1f}s [{tier[:7]:<7}]"
            if err:
                failed.append((topic["topic"], err))
                print(f"{prefix} FAIL: {err}")
            else:
                succeeded.append(slug)
                print(f"{prefix} OK   {slug}")

    total = time.time() - start
    print()
    print("=" * 70)
    print(f"DONE in {total/60:.1f} min  ({total:.0f}s)")
    print(f"  Succeeded: {len(succeeded)}")
    print(f"  Failed:    {len(failed)}")
    if failed:
        print("\nFailures (re-run targeted with --topic flag if needed):")
        for title, err in failed:
            print(f"  - {title}")
            print(f"      {err}")
    print("=" * 70)


if __name__ == "__main__":
    main()
