"""
Submit URLs to IndexNow (Bing, Yandex, Seznam, Naver, Yep, others).

Usage:
  # Submit a single URL or several inline:
  python pipeline/submit_indexnow.py https://www.hollowaydavies.co.uk/blog/some-post

  # Submit everything in the live sitemap (use sparingly, e.g. after big content drops):
  python pipeline/submit_indexnow.py --from-sitemap

  # Submit URLs listed in a text file (one per line):
  python pipeline/submit_indexnow.py --from-file urls.txt

  # Drain the pending-publish queue (URLs added by generators after each post):
  python pipeline/submit_indexnow.py --from-queue

  # Add a URL to the queue without submitting (used by generators):
  python pipeline/submit_indexnow.py --enqueue https://www.hollowaydavies.co.uk/blog/foo

Notes:
  - IndexNow limit: 10,000 URLs per request. Script chunks automatically.
  - Etiquette: only submit URLs that are *new or recently changed*. Don't
    re-submit the same content repeatedly — search engines may rate-limit.
  - A 200 or 202 response means accepted. 422 usually means a URL doesn't
    match the host, or the key file isn't reachable at keyLocation.
  - Queue file lives at pipeline/.indexnow_queue.txt (gitignored). Drained
    on a successful --from-queue run.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
import urllib.error
import json
import xml.etree.ElementTree as ET

HOST = "www.hollowaydavies.co.uk"
KEY = "432fba0acf043d10bee408eb4a80932e"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
SITEMAP_URL = f"https://{HOST}/sitemap.xml"
ENDPOINT = "https://api.indexnow.org/IndexNow"
CHUNK_SIZE = 10_000
QUEUE_FILE = os.path.join(os.path.dirname(__file__), ".indexnow_queue.txt")


def enqueue(url: str) -> None:
    """Append a URL to the pending-publish queue for later submission.

    Called by content generators after a successful publish. The URL is only
    pinged when someone later runs `python pipeline/submit_indexnow.py
    --from-queue` (typically after a `git push` so the content is actually
    live on Vercel).
    """
    if not url.startswith(f"https://{HOST}"):
        return
    existing: set[str] = set()
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, encoding="utf-8") as f:
            existing = {line.strip() for line in f if line.strip()}
    if url in existing:
        return
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def load_queue() -> list[str]:
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def clear_queue() -> None:
    if os.path.exists(QUEUE_FILE):
        os.remove(QUEUE_FILE)


def submit_chunk(urls: list[str]) -> tuple[int, str]:
    body = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def load_sitemap_urls() -> list[str]:
    with urllib.request.urlopen(SITEMAP_URL, timeout=30) as resp:
        xml = resp.read()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(xml)
    return [loc.text.strip() for loc in root.findall("sm:url/sm:loc", ns) if loc.text]


def load_urls_from_file(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="*", help="URLs to submit")
    parser.add_argument("--from-sitemap", action="store_true", help="Submit every URL in the live sitemap")
    parser.add_argument("--from-file", help="Read URLs (one per line) from a file")
    parser.add_argument("--from-queue", action="store_true", help="Drain pipeline/.indexnow_queue.txt (clears on success)")
    parser.add_argument("--enqueue", help="Append URL to the queue WITHOUT submitting (for generator scripts)")
    parser.add_argument("--dry-run", action="store_true", help="Print URLs but don't submit")
    args = parser.parse_args()

    if args.enqueue:
        enqueue(args.enqueue)
        print(f"Queued for next --from-queue run: {args.enqueue}")
        return 0

    urls: list[str] = []
    if args.from_sitemap:
        urls.extend(load_sitemap_urls())
    if args.from_file:
        urls.extend(load_urls_from_file(args.from_file))
    if args.from_queue:
        urls.extend(load_queue())
    urls.extend(args.urls)

    urls = [u for u in dict.fromkeys(urls) if u.startswith(f"https://{HOST}")]

    if not urls:
        print("No valid URLs to submit (must start with https://" + HOST + ")", file=sys.stderr)
        return 1

    print(f"Prepared {len(urls)} URL(s) for IndexNow submission")
    if args.dry_run:
        for u in urls:
            print(" ", u)
        return 0

    for i in range(0, len(urls), CHUNK_SIZE):
        chunk = urls[i:i + CHUNK_SIZE]
        status, body = submit_chunk(chunk)
        print(f"Chunk {i // CHUNK_SIZE + 1}: {len(chunk)} URLs -> HTTP {status}")
        if status not in (200, 202):
            print(f"  Response: {body[:500]}", file=sys.stderr)
            return 2

    if args.from_queue:
        clear_queue()
        print("Queue cleared.")
    print("Submission complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
