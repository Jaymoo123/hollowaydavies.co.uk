"""
Blog generation for Holloway Davies (generalist) using DeepSeek + Supabase.
Same pattern as Property/Dentists/Medical pipelines, adapted for the generalist niche.
"""
import os
import sys
import re
from datetime import datetime, timezone
import httpx

# Force UTF-8 stdout/stderr on Windows so Unicode chars in prints don't crash.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

# Add agents/ to path for DeepSeekClient
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "utils"))

from config_supabase import (
    DEEPSEEK_API_KEY,
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_TABLE,
    OUTPUT_MD_DIR,
    OUTPUT_MD_DIR_FUNDAMENTALS,
    SITE_BASE_URL,
    AUTHOR_NAME,
    BLOG_SYSTEM_PROMPT,
    PILLAR_SYSTEM_PROMPT,
    POST_CATEGORIES,
    INTERNAL_LINK_SLUGS,
    get_relevant_audience_link,
)

try:
    from deepseek_client import DeepSeekClient
except ImportError:
    print("ERROR: Could not import DeepSeekClient. Check agents/utils/deepseek_client.py exists.")
    sys.exit(1)

try:
    from fetch_image import fetch_image_for_post
except ImportError:
    fetch_image_for_post = None
    print("[INFO] fetch_image module not available - images will be skipped")


def fetch_unused_topic():
    """Fetch highest priority unused topic from the configured blog topics table."""
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    params = {
        "used": "eq.false",
        "order": "publish_priority.desc.nullslast,keyword_difficulty.asc.nullslast,created_at.asc",
        "limit": "1",
    }
    response = httpx.get(url, headers=headers, params=params)
    response.raise_for_status()
    topics = response.json()
    if not topics:
        print("No unused topics found in blog_topics_agency.")
        return None
    topic = topics[0]
    print(f"Selected topic (priority {topic.get('publish_priority', 'N/A')}, difficulty {topic.get('keyword_difficulty', 'N/A')}): {topic['topic']}")
    return topic


def fetch_topic_by_slug_or_topic(needle):
    """Fetch a specific topic by primary_keyword or topic match (for --topic flag)."""
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    # Try exact topic match first, then exact primary_keyword match
    for col in ("topic", "primary_keyword"):
        r = httpx.get(url, headers=headers, params={col: f"eq.{needle}", "limit": "1"}, timeout=15.0)
        r.raise_for_status()
        rows = r.json()
        if rows:
            return rows[0]
    return None


def mark_topic_used(topic_id, slug):
    """Mark topic as used in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    params = {"id": f"eq.{topic_id}"}
    payload = {
        "used": True,
        "used_at": datetime.now(timezone.utc).isoformat(),
        "slug": slug,
    }
    response = httpx.patch(url, headers=headers, params=params, json=payload)
    response.raise_for_status()
    print(f"[OK] Marked topic {topic_id} as used (slug: {slug})")


def generate_content(topic_data):
    """Generate blog or pillar content using DeepSeek.

    Branches on content_tier: 'pillar' uses PILLAR_SYSTEM_PROMPT + larger
    max_tokens; anything else uses BLOG_SYSTEM_PROMPT.
    """
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)

    topic = topic_data["topic"]
    primary_keyword = topic_data.get("primary_keyword") or topic
    secondary_keywords = topic_data.get("secondary_keywords") or []
    user_intent = topic_data.get("user_intent", "informational")
    search_volume = topic_data.get("target_search_volume", "unknown")
    content_tier = topic_data.get("content_tier", "cluster")
    suggested_slug = topic_data.get("suggested_slug", "")
    notes = topic_data.get("notes", "")
    is_pillar = content_tier == "pillar"

    if isinstance(secondary_keywords, list):
        keywords_text = ", ".join([k for k in secondary_keywords if k]) or "none"
    else:
        keywords_text = str(secondary_keywords) if secondary_keywords else "none"

    seo_guidance = f"""
SEO REQUIREMENTS:
- Primary keyword: "{primary_keyword}" (search volume: {search_volume}/month)
- Secondary keywords: {keywords_text}
- Search intent: {user_intent}
- Content type: {content_tier}
- Optimise for {user_intent} intent

KEYWORD USAGE:
- Use primary keyword in H1, first paragraph, and 2-3 times naturally throughout
- Include secondary keywords naturally in subheadings and body content
- Do not keyword-stuff — natural language only
"""

    slug_hint = f"\nSuggested slug: {suggested_slug}" if suggested_slug else ""
    notes_hint = f"\nEditorial notes: {notes}" if notes else ""

    pillar_extra = ""
    if is_pillar:
        pillar_extra = "\n\nThis is a PILLAR GUIDE. Target 3,500 to 5,000 words. Include 8-12 H2 sections, multiple H3 subsections, at least one HTML <table>, an Action Checklist section near the end, and 4-6 FAQs."

    user_prompt = f"""Generate a comprehensive {'pillar guide' if is_pillar else 'blog post'} for UK business owners (limited companies, contractors, sole traders, partnerships, small businesses).

Primary topic: {topic}
{seo_guidance}{slug_hint}{notes_hint}{pillar_extra}

Available internal links (use naturally where relevant):
{chr(10).join(f"- {link}" for link in INTERNAL_LINK_SLUGS)}

Categories to choose from: {", ".join(POST_CATEGORIES)}

Generate the content following the exact format in your system prompt."""

    print(f"Generating: {topic}")
    print(f"  Keyword: {primary_keyword} | Intent: {user_intent} | Volume: {search_volume} | Tier: {content_tier}")

    return client.generate_creative(
        prompt=user_prompt,
        system=PILLAR_SYSTEM_PROMPT if is_pillar else BLOG_SYSTEM_PROMPT,
        temperature=0.7 if is_pillar else 0.75,
        max_tokens=8192 if is_pillar else 4096,
    )


def parse_llm_output(raw_text):
    """Parse LLM output into structured fields."""
    fields = {}
    pattern = r'==([^=]+)==\s*(.*?)(?=\n==|$)'
    matches = re.findall(pattern, raw_text, re.DOTALL)
    for key, value in matches:
        key_clean = key.strip().lower().replace("-", "_").replace(" ", "_")
        fields[key_clean] = value.strip()
    return fields


def slugify_category(category):
    """Convert category name to URL slug matching the frontend's slugifyCategory()."""
    slug = category.lower()
    slug = slug.replace("&", "and")
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug).strip('-')
    return slug


def validate_post(fields, slug):
    """Validate generated content before writing."""
    issues = []
    meta_title = fields.get('meta_title', '')
    meta_desc = fields.get('meta_description', '')
    content = fields.get('content', '')

    if not slug or slug == 'untitled':
        issues.append("Missing or default slug")
    if not fields.get('name'):
        issues.append("Missing title")
    if not fields.get('category'):
        issues.append("Missing category")
    if len(meta_title) > 60:
        issues.append(f"metaTitle too long ({len(meta_title)} chars, max 60)")
    if len(meta_desc) > 155:
        issues.append(f"metaDescription too long ({len(meta_desc)} chars, max 155)")
    if not meta_desc:
        issues.append("Missing metaDescription")
    if re.search(r'\[.*?\]\(.*?\)', content):
        issues.append("Content contains markdown links (use HTML <a> tags)")
    if not fields.get('faq1'):
        issues.append("No FAQs generated")
    if len(content) < 500:
        issues.append(f"Content too short ({len(content)} chars)")
    if '—' in content:
        issues.append("Em dashes found in content (should not be used)")

    if issues:
        print(f"[WARN] Validation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"[OK] Validation passed")

    return issues


def strip_em_dashes(text):
    """Strip em-dashes and en-dashes from body content. Both read as
    AI-generated.

    Em-dashes typically appear with surrounding spaces (' — '). Replace the
    whole pattern with a single ', ' so we don't leave a stray leading space
    before the comma. Bare or trailing em-dashes also collapse cleanly. The
    fallback also turns end-of-sentence em-dashes (no trailing space) into a
    full stop where context suggests it.

    En-dashes are usually a numeric range marker (e.g. '£50,000 - £250,000')
    so they map to a hyphen."""
    if not text:
        return text
    # Collapse surrounding whitespace around an em-dash into a single ", "
    text = re.sub(r"\s*—\s*", ", ", text)
    # Tidy up any double-comma artefacts that this can create
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s+,", ",", text)
    # En-dashes to hyphens for numeric ranges
    text = text.replace("–", "-")
    return text


def truncate_meta(text, max_len):
    """Truncate at last whole word under max_len. Drop trailing prepositions/conjunctions
    and stray punctuation so the result reads as a complete-ish phrase."""
    if not text or len(text) <= max_len:
        return text
    DANGLERS = {"to", "of", "for", "with", "and", "or", "but", "the", "a", "an",
                "in", "on", "at", "by", "from", "as", "into", "upon", "is", "are",
                "vs", "vs.", "&"}
    cut = text[:max_len].rsplit(" ", 1)[0]
    cut = cut.rstrip(",;:.- ")
    parts = cut.split()
    while parts and parts[-1].lower().rstrip(",;:.") in DANGLERS:
        parts.pop()
    return " ".join(parts).rstrip(",;:.- ")


def fetch_related_posts(category, current_slug, limit=2):
    """Return up to `limit` other used topics in the same category.

    Returns list of {'topic', 'slug'} dicts."""
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    params = {
        "select": "topic,slug",
        "category": f"eq.{category}",
        "used": "eq.true",
        "slug": f"neq.{current_slug}",
        "order": "used_at.desc",
        "limit": str(limit),
    }
    try:
        r = httpx.get(url, headers=headers, params=params, timeout=15.0)
        if r.status_code == 200:
            return [row for row in r.json() if row.get("slug")]
    except Exception as e:
        print(f"[WARN] fetch_related_posts failed: {e}")
    return []


def normalise_internal_links(content_html, slug, category):
    """Count internal links. Warn if over 7. If under 3, append a Related
    Articles block referencing 2 other posts in the same category."""
    hrefs = re.findall(r'href="(/[^"]*)"', content_html)
    count = len(hrefs)
    category_slug_for_links = slugify_category(category)

    if count > 7:
        print(f"[WARN] Over-linked: {count} internal links (target 3-7). Manual review suggested.")

    if count < 3:
        related = fetch_related_posts(category, slug, limit=2)
        if related:
            items = "\n".join(
                f'    <li><a href="/blog/{category_slug_for_links}/{r["slug"]}">{r["topic"]}</a></li>'
                for r in related
            )
            block = (
                f'\n\n<h2>Related articles in {category}</h2>\n'
                f'<ul>\n{items}\n</ul>\n'
            )
            content_html = content_html.rstrip() + block
            print(f"[FIX] Under-linked ({count} links) - appended {len(related)} related-post links")
        else:
            print(f"[WARN] Under-linked ({count} links) but no published siblings found in {category}")

    return content_html


def export_to_markdown(fields, content_tier="cluster"):
    """Export parsed fields to Markdown file.

    Pillars go to web/content/fundamentals/ with canonical /fundamentals/<slug>.
    Everything else goes to web/content/blog/ with canonical /blog/<cat>/<slug>.
    """
    slug = fields.get("slug", "untitled")
    today = datetime.now().strftime("%Y-%m-%d")
    category = fields.get('category', 'Bookkeeping and Compliance')
    category_slug = slugify_category(category)
    is_pillar = content_tier == "pillar"
    if is_pillar:
        canonical = f"{SITE_BASE_URL}/fundamentals/{slug}"
    else:
        canonical = f"{SITE_BASE_URL}/blog/{category_slug}/{slug}"

    # Drop unescaped inner double-quotes (they break YAML frontmatter).
    # We strip rather than escape because DeepSeek often quotes a word for
    # emphasis (e.g. "good") and the result reads fine without the quotes.
    def clean(s):
        return strip_em_dashes((s or "")).replace('"', '')

    name = clean(fields.get('name', 'Untitled'))
    h1 = clean(fields.get('h1', name))
    meta_title_raw = clean(fields.get('meta_title', name))
    meta_desc_raw = clean(fields.get('meta_description', ''))
    summary = clean(fields.get('3_liner', ''))
    alt_tag = clean(fields.get('alt_tag', ''))
    content = strip_em_dashes(fields.get('content', ''))
    content = normalise_internal_links(content, slug, category)

    meta_title = truncate_meta(meta_title_raw, 60)
    meta_desc = truncate_meta(meta_desc_raw, 155)
    if meta_title != meta_title_raw:
        print(f"[FIX] metaTitle truncated {len(meta_title_raw)} -> {len(meta_title)} chars")
    if meta_desc != meta_desc_raw:
        print(f"[FIX] metaDescription truncated {len(meta_desc_raw)} -> {len(meta_desc)} chars")

    faqs = []
    for i in range(1, 5):
        question = strip_em_dashes(fields.get(f'faq{i}', '').strip())
        answer = strip_em_dashes(fields.get(f'faa{i}', '').strip())
        if question and answer:
            q_escaped = question.replace('"', '\\"')
            a_escaped = answer.replace('"', '\\"')
            faqs.append(f'  - question: "{q_escaped}"\n    answer: "{a_escaped}"')

    faqs_yaml = "\n".join(faqs) if faqs else ""
    faqs_section = f"faqs:\n{faqs_yaml}" if faqs_yaml else "faqs: []"

    cleaned_fields = {
        **fields,
        'name': name,
        'h1': h1,
        'meta_title': meta_title,
        'meta_description': meta_desc,
        '3_liner': summary,
        'alt_tag': alt_tag,
        'content': content,
    }
    validate_post(cleaned_fields, slug)

    image_url = ""
    image_credit_yaml = ""
    if fetch_image_for_post is not None:
        try:
            img = fetch_image_for_post(slug=slug, topic_text=name, category=category, alt_text=alt_tag)
            image_url = img["public_url"]
            credit_parts = [
                f'  photographer: "{img["photographer"]}"',
                f'  photographerUrl: "{img["photographer_url"]}"',
                f'  sourceUrl: "{img["pexels_url"]}"',
                f'  source: "Pexels"',
            ]
            image_credit_yaml = "imageCredit:\n" + "\n".join(credit_parts)
            print(f"[OK] Image: {img['public_url']} (Pexels, by {img['photographer']})")
        except Exception as e:
            print(f"[WARN] Image fetch failed: {e}")

    image_credit_section = image_credit_yaml if image_credit_yaml else "imageCredit: {}"

    front_matter = f"""---
title: "{name}"
slug: "{slug}"
canonical: "{canonical}"
date: "{today}"
author: "{AUTHOR_NAME}"
category: "{category}"
metaTitle: "{meta_title}"
metaDescription: "{meta_desc}"
altText: "{alt_tag}"
image: "{image_url}"
{image_credit_section}
h1: "{h1}"
summary: "{summary}"
schema: ""
{faqs_section}
---

{content}
"""

    output_dir = OUTPUT_MD_DIR_FUNDAMENTALS if is_pillar else OUTPUT_MD_DIR
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{slug}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(front_matter)

    print(f"[OK] Written: {output_path}")
    return slug


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="Generate a specific topic by exact topic or primary_keyword match (overrides priority order). Use for validation runs.")
    parser.add_argument("--dry-run", action="store_true", help="Generate, validate, write markdown locally, but skip mark_topic_used and IndexNow enqueue.")
    args = parser.parse_args()

    print("=" * 60)
    print("Holloway Davies. Blog Generation (DeepSeek)")
    print("=" * 60)

    if args.topic:
        print(f"\n[1/5] Fetching specific topic: {args.topic!r}")
        topic_row = fetch_topic_by_slug_or_topic(args.topic)
        if not topic_row:
            print(f"No topic found matching {args.topic!r}.")
            return
        print(f"Selected: {topic_row['topic']}  (priority {topic_row.get('publish_priority', 'N/A')}, tier {topic_row.get('content_tier', 'N/A')})")
    else:
        print("\n[1/5] Fetching highest priority unused topic from Supabase...")
        topic_row = fetch_unused_topic()
        if not topic_row:
            print(f"No topics to process. Seed candidates into {SUPABASE_TABLE} first.")
            return

    topic_id = topic_row["id"]

    print("\n[2/5] Generating content with DeepSeek...")
    raw_content = generate_content(topic_row)
    print(f"[OK] {len(raw_content)} characters generated")

    print("\n[3/5] Parsing output...")
    fields = parse_llm_output(raw_content)
    print(f"[OK] {len(fields)} fields parsed")

    print("\n[4/5] Writing Markdown...")
    slug = export_to_markdown(fields, content_tier=topic_row.get("content_tier", "cluster"))

    if args.dry_run:
        print("\n[5/5] --dry-run: skipping mark_topic_used and IndexNow enqueue.")
        print("\n" + "=" * 60)
        print(f"[DRY RUN COMPLETE] {slug}.md  (topic still marked unused)")
        print("=" * 60)
        return

    print("\n[5/5] Marking topic as used...")
    mark_topic_used(topic_id, slug)

    try:
        from submit_indexnow import enqueue
        enqueue(f"{SITE_BASE_URL}/blog/{slug}")
    except Exception as e:
        print(f"[WARN] IndexNow enqueue skipped: {e}")

    print("\n" + "=" * 60)
    print(f"[COMPLETE] {slug}.md")
    print(f"Preview: {SITE_BASE_URL}/blog/{slug}")
    print("Queued for IndexNow. After `git push`, run:")
    print("  python pipeline/submit_indexnow.py --from-queue")
    print("=" * 60)


if __name__ == "__main__":
    main()
