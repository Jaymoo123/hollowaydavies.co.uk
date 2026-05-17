"""
Scan existing posts. Where internal-link count < 3, append a Related Articles
block. Where > 7, log a warning.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from generate_blog_supabase import normalise_internal_links

BLOG_DIR = Path(__file__).resolve().parents[1] / "web" / "content" / "blog"


def get_field(fm, name):
    m = re.search(rf'^{name}:\s*"([^"]*)"', fm, re.MULTILINE)
    return m.group(1) if m else ""


def main():
    files = sorted(BLOG_DIR.glob("*.md"))
    print(f"Scanning {len(files)} posts...")
    for path in files:
        text = path.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        if not fm_match:
            continue
        fm, body = fm_match.group(1), fm_match.group(2)
        slug = get_field(fm, "slug") or path.stem
        category = get_field(fm, "category")
        if not category:
            continue
        before = body.count('href="/')
        if before >= 3 and before <= 7:
            print(f"OK     {path.name:<48}  {before} links")
            continue
        new_body = normalise_internal_links(body, slug, category)
        after = new_body.count('href="/')
        if new_body != body:
            new_text = f"---\n{fm}\n---\n{new_body}"
            path.write_text(new_text, encoding="utf-8")
            print(f"FIXED  {path.name:<48}  {before} -> {after} links")
        else:
            print(f"WARN   {path.name:<48}  {before} links (no related-post candidates or over-linked)")


if __name__ == "__main__":
    main()
