"""
Fetch a hero image for a blog post via the Pexels API.

Pexels licence allows free commercial use without attribution, but we attach
photographer credit anyway as good practice.

Usage:
    from fetch_image import fetch_image_for_post
    result = fetch_image_for_post(slug="my-post", query="marketing agency office", category="Agency Finance Essentials")
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

import httpx

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BLOG_DIR = ROOT / "web" / "public" / "blog"


def _api_key():
    return os.getenv("PEXELS_API_KEY")


CATEGORY_FALLBACK_QUERIES = {
    "Limited Company Tax": "uk business office laptop documents",
    "Sole Trader and Self Employment": "freelancer laptop home office uk",
    "VAT and Making Tax Digital": "digital tax computer laptop",
    "Payroll and PAYE": "office payroll laptop calculator",
    "Corporation Tax": "uk paperwork desk accountant",
    "R&D Tax Credits": "modern tech office team working",
    "Incorporation and Structure": "office handshake business meeting",
    "Exit and Capital Gains": "business meeting handshake office",
    "Bookkeeping and Compliance": "modern office desk laptop spreadsheet",
    "Director Pay and Dividends": "office finance meeting laptop",
}


GENERIC_QUERY = "uk small business office laptop"


def build_query(topic_text, category=None):
    """Build a Pexels search query from a topic title plus category hint.

    Strips stop words and HMRC-specific jargon that Pexels won't match.
    """
    if not topic_text:
        topic_text = ""
    text = topic_text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    stop = {"how", "what", "why", "when", "where", "is", "a", "an", "the",
            "to", "of", "for", "with", "and", "or", "but", "in", "on", "at",
            "by", "from", "as", "into", "you", "your", "this", "that",
            "should", "can", "do", "does", "actually", "really"}
    jargon = {"hmrc", "vat", "ir35", "paye", "p11d", "p60", "p45", "badr",
              "mtd", "sa100", "ct600", "p32", "cis"}
    words = [w for w in text.split() if w not in stop and w not in jargon]
    if not words:
        return CATEGORY_FALLBACK_QUERIES.get(category, GENERIC_QUERY)
    return " ".join(words[:5])


def search_pexels(query, per_page=5):
    key = _api_key()
    if not key:
        raise RuntimeError("PEXELS_API_KEY not set in environment")
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": key}
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}
    r = httpx.get(url, headers=headers, params=params, timeout=20.0)
    if r.status_code != 200:
        raise RuntimeError(f"Pexels search failed {r.status_code}: {r.text[:200]}")
    return r.json().get("photos", [])


def download_image(image_url, dest_path):
    r = httpx.get(image_url, timeout=60.0, follow_redirects=True)
    if r.status_code != 200:
        raise RuntimeError(f"Image download failed {r.status_code}: {image_url}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(r.content)


def fetch_image_for_post(slug, topic_text=None, category=None, alt_text=None):
    """Search Pexels, download first usable result to /public/blog/<slug>.jpg.

    Returns dict: {local_path, public_url, photographer, photographer_url, pexels_url}
    Falls back through query → category-fallback → generic if no hits.
    """
    queries = []
    primary = build_query(topic_text or alt_text or "", category)
    queries.append(primary)
    if category and CATEGORY_FALLBACK_QUERIES.get(category) not in queries:
        queries.append(CATEGORY_FALLBACK_QUERIES.get(category, GENERIC_QUERY))
    if GENERIC_QUERY not in queries:
        queries.append(GENERIC_QUERY)

    photos = []
    used_query = None
    for q in queries:
        photos = search_pexels(q)
        if photos:
            used_query = q
            break

    if not photos:
        raise RuntimeError(f"No Pexels results for any query: {queries}")

    photo = photos[0]
    image_url = photo["src"].get("large2x") or photo["src"].get("large") or photo["src"]["original"]
    dest = PUBLIC_BLOG_DIR / f"{slug}.jpg"
    download_image(image_url, dest)

    return {
        "local_path": str(dest),
        "public_url": f"/blog/{slug}.jpg",
        "photographer": photo.get("photographer", ""),
        "photographer_url": photo.get("photographer_url", ""),
        "pexels_url": photo.get("url", ""),
        "alt": photo.get("alt") or alt_text or topic_text or "",
        "query_used": used_query,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_image.py <slug> [topic text] [category]")
        sys.exit(1)
    slug = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else slug.replace("-", " ")
    category = sys.argv[3] if len(sys.argv) > 3 else None
    result = fetch_image_for_post(slug, topic, category)
    print(f"[OK] Downloaded: {result['local_path']}")
    print(f"     Public URL:   {result['public_url']}")
    print(f"     Photographer: {result['photographer']} ({result['photographer_url']})")
    print(f"     Pexels page:  {result['pexels_url']}")
    print(f"     Query used:   {result['query_used']}")


if __name__ == "__main__":
    main()
