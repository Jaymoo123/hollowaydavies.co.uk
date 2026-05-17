#!/usr/bin/env python3
"""
Enhance existing blog posts and pillar guides for AI extraction and
E-E-A-T signals.

For each .md in web/content/blog and web/content/fundamentals:
  - Adds `authorSlug: james-whitfield` if not present (canonical /team/[slug] byline)
  - Adds `updatedDate: <today>` if not present
  - Adds a 4–5 bullet `keyTakeaways:` array if not present
    (generated from title + summary + opening ~600 words via DeepSeek)

The frontend renders `keyTakeaways` as a visible "Key takeaways" box at the
top of the article with .tldr class for Google's speakable schema. Posts
without `keyTakeaways` fall back to rendering `summary` as a TL;DR box.

Idempotent: re-running skips posts that already have all three fields.
Use --force to re-generate keyTakeaways even if present.

Usage:
    python pipeline/enhance_posts_for_ai.py                  # all posts, blog + fundamentals
    python pipeline/enhance_posts_for_ai.py --dry-run        # preview, write nothing
    python pipeline/enhance_posts_for_ai.py --limit 10       # only first 10 unprocessed
    python pipeline/enhance_posts_for_ai.py --only blog      # only blog posts
    python pipeline/enhance_posts_for_ai.py --only fundamentals
    python pipeline/enhance_posts_for_ai.py --slug some-post # only that single slug
    python pipeline/enhance_posts_for_ai.py --force          # re-generate keyTakeaways

Requires:
    DEEPSEEK_API_KEY in environment or .env at repo root
    pip install pyyaml requests python-dotenv
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    print("Missing dependency: pyyaml. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import requests  # type: ignore
except ImportError:
    print("Missing dependency: requests. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv  # type: ignore

    # Try Digital Agency/.env first (per-project), then the monorepo root .env
    # one level up where the shared DEEPSEEK_API_KEY usually lives.
    _root = Path(__file__).resolve().parents[1]
    load_dotenv(_root / ".env")
    load_dotenv(_root.parent / ".env", override=False)
except ImportError:
    pass

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "web" / "content" / "blog"
FUND_DIR = ROOT / "web" / "content" / "fundamentals"

DEFAULT_AUTHOR_SLUG = "james-whitfield"
TODAY = date.today().isoformat()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

SYSTEM_PROMPT = """You are an editor at Agency Founder Finance, a specialist UK accountancy firm for agency founders.

Given the title, summary, and opening of an article, produce 4–5 short declarative bullets that capture the article's most useful takeaways. These bullets will render as a "Key takeaways" box at the top of the article and feed AI search engines that extract concise answers.

Rules for each bullet:
- Complete declarative sentence, 12–28 words.
- Lead with the actionable insight, not a generic phrase like "This article covers".
- Use 2025/26 UK tax figures (corporation tax 19%/25%, dividend 8.75%/33.75%/39.35%, BADR 14% rising to 18% on 6 April 2026, VAT threshold £90,000, MTD ITSA dates 2026/2027).
- No marketing fluff. No "we recommend" / "you should consider". State the fact or rule.
- British English spelling.

Return ONLY a JSON array of strings. No prose, no markdown, no code fence. Example: ["First takeaway.", "Second takeaway.", "Third takeaway.", "Fourth takeaway."]
"""


def parse_frontmatter(raw: str) -> tuple[dict, str] | None:
    m = FRONTMATTER_RE.match(raw)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"  YAML parse error: {e}", file=sys.stderr)
        return None
    if not isinstance(data, dict):
        return None
    return data, m.group(2)


def serialise_frontmatter(data: dict, body: str) -> str:
    yaml_text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=10000,
        default_flow_style=False,
    )
    return f"---\n{yaml_text}---\n{body}"


def first_words(html_or_md: str, n: int = 600) -> str:
    text = re.sub(r"```.*?```", "", html_or_md, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split(" ")
    return " ".join(words[:n])


def call_deepseek(messages: list[dict[str, str]], max_tokens: int = 600) -> str:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")
    res = requests.post(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    res.raise_for_status()
    payload = res.json()
    return payload["choices"][0]["message"]["content"]


def generate_takeaways(title: str, summary: str, body_snippet: str) -> list[str] | None:
    user = (
        f"Title: {title}\n\n"
        f"Existing summary: {summary}\n\n"
        f"Article opening:\n{body_snippet}\n\n"
        "Produce the JSON array now."
    )
    try:
        raw = call_deepseek(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ]
        )
    except Exception as e:
        print(f"  DeepSeek error: {e}", file=sys.stderr)
        return None

    # DeepSeek with response_format=json_object returns a JSON object. Accept either
    # a top-level array (some models do this) or an object with a sole array value.
    try:
        parsed: Any = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            print(f"  Could not parse JSON: {raw[:200]}", file=sys.stderr)
            return None
        try:
            parsed = json.loads(m.group(0))
        except json.JSONDecodeError as e:
            print(f"  Could not parse extracted JSON: {e}", file=sys.stderr)
            return None

    if isinstance(parsed, dict):
        # find first list value
        for v in parsed.values():
            if isinstance(v, list):
                parsed = v
                break
    if not isinstance(parsed, list):
        print(f"  Unexpected JSON shape: {type(parsed).__name__}", file=sys.stderr)
        return None

    bullets = [str(x).strip() for x in parsed if isinstance(x, (str, int, float))]
    bullets = [b for b in bullets if 20 <= len(b) <= 300]
    if not (3 <= len(bullets) <= 6):
        print(f"  Bullet count outside 3–6 ({len(bullets)})", file=sys.stderr)
        return None
    return bullets


def process_file(path: Path, force: bool, dry_run: bool) -> str:
    raw = path.read_text(encoding="utf-8")
    parsed = parse_frontmatter(raw)
    if not parsed:
        return "skip-no-frontmatter"
    fm, body = parsed

    changed = False

    if not fm.get("authorSlug"):
        fm["authorSlug"] = DEFAULT_AUTHOR_SLUG
        changed = True

    if not fm.get("updatedDate"):
        fm["updatedDate"] = TODAY
        changed = True

    needs_takeaways = force or not fm.get("keyTakeaways")
    if needs_takeaways:
        title = fm.get("title") or fm.get("h1") or path.stem
        summary = fm.get("summary") or fm.get("metaDescription") or ""
        snippet = first_words(body, 600)
        bullets = generate_takeaways(title, summary, snippet)
        if bullets:
            fm["keyTakeaways"] = bullets
            changed = True
        else:
            return "fail-takeaways"

    if not changed:
        return "skip-already-done"

    if dry_run:
        return "would-update"

    path.write_text(serialise_frontmatter(fm, body), encoding="utf-8")
    return "updated"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="Re-generate keyTakeaways even if present")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--only", choices=["blog", "fundamentals"])
    ap.add_argument("--slug", help="Process only the post with this slug (matches filename)")
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds between API calls")
    args = ap.parse_args()

    dirs = []
    if args.only == "blog":
        dirs = [BLOG_DIR]
    elif args.only == "fundamentals":
        dirs = [FUND_DIR]
    else:
        dirs = [BLOG_DIR, FUND_DIR]

    files: list[Path] = []
    for d in dirs:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            if args.slug and p.stem != args.slug:
                continue
            files.append(p)

    if args.limit:
        files = files[: args.limit]

    if not DEEPSEEK_API_KEY and not args.dry_run:
        print("DEEPSEEK_API_KEY not set. Set it in .env or environment.", file=sys.stderr)
        sys.exit(1)

    counts = {
        "updated": 0,
        "would-update": 0,
        "skip-already-done": 0,
        "skip-no-frontmatter": 0,
        "fail-takeaways": 0,
    }

    for i, path in enumerate(files, 1):
        rel = path.relative_to(ROOT)
        print(f"[{i}/{len(files)}] {rel}", end=" ... ", flush=True)
        try:
            result = process_file(path, force=args.force, dry_run=args.dry_run)
        except Exception as e:
            print(f"ERROR: {e}")
            counts["fail-takeaways"] = counts.get("fail-takeaways", 0) + 1
            continue
        counts[result] = counts.get(result, 0) + 1
        print(result)
        # Only sleep when we made a network call
        if result in ("updated", "would-update") and not fm_was_pure_metadata_only(path):
            time.sleep(args.sleep)

    print("\n— Summary —")
    for k, v in counts.items():
        print(f"  {k}: {v}")


def fm_was_pure_metadata_only(_path: Path) -> bool:
    # Cheap helper: we just always sleep — keeps rate-limit friendly even on
    # mixed runs. If you want to optimise this, track which paths were
    # network-bound. For now, the cost is negligible.
    return False


if __name__ == "__main__":
    main()
