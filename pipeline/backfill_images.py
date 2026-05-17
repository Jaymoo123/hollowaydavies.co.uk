"""
Backfill Pexels images for blog posts that don't have one yet.

Reads each markdown file under web/content/blog/, parses frontmatter, and if
`image:` is empty, fetches one via fetch_image_for_post() and rewrites the
frontmatter in place.
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

from fetch_image import fetch_image_for_post

BLOG_DIR = Path(__file__).resolve().parents[1] / "web" / "content" / "blog"


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return None, None
    return m.group(1), m.group(2)


def get_field(fm, name):
    m = re.search(rf'^{name}:\s*"([^"]*)"', fm, re.MULTILINE)
    return m.group(1) if m else ""


def set_image_and_credit(fm, image_url, credit):
    fm = re.sub(r'^image:\s*"[^"]*"', f'image: "{image_url}"', fm, count=1, flags=re.MULTILINE)
    credit_block = (
        "imageCredit:\n"
        f'  photographer: "{credit["photographer"]}"\n'
        f'  photographerUrl: "{credit["photographer_url"]}"\n'
        f'  sourceUrl: "{credit["pexels_url"]}"\n'
        f'  source: "Pexels"'
    )
    if re.search(r"^imageCredit:", fm, re.MULTILINE):
        fm = re.sub(
            r"^imageCredit:.*?(?=\n[a-zA-Z][a-zA-Z0-9]*:|\Z)",
            credit_block,
            fm,
            count=1,
            flags=re.MULTILINE | re.DOTALL,
        )
    else:
        fm = re.sub(
            r'(^image:\s*"[^"]*"\n)',
            r"\1" + credit_block + "\n",
            fm,
            count=1,
            flags=re.MULTILINE,
        )
    return fm


def main():
    files = sorted(BLOG_DIR.glob("*.md"))
    print(f"Found {len(files)} blog post(s)")
    for path in files:
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if fm is None:
            print(f"SKIP {path.name}: no frontmatter")
            continue
        existing_image = get_field(fm, "image")
        if existing_image:
            print(f"SKIP {path.name}: already has image {existing_image}")
            continue
        slug = get_field(fm, "slug") or path.stem
        title = get_field(fm, "title")
        category = get_field(fm, "category")
        alt = get_field(fm, "altText")
        try:
            img = fetch_image_for_post(slug=slug, topic_text=title, category=category, alt_text=alt)
        except Exception as e:
            print(f"FAIL {path.name}: {e}")
            continue
        new_fm = set_image_and_credit(fm, img["public_url"], img)
        new_text = f"---\n{new_fm}\n---\n{body}"
        path.write_text(new_text, encoding="utf-8")
        print(f"OK   {path.name}  ->  {img['public_url']}  (by {img['photographer']})")


if __name__ == "__main__":
    main()
