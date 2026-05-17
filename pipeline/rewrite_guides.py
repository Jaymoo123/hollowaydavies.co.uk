"""
Rewrite guides body content from agency-founder framing to generalist
UK business owner framing.

Reads web/src/app/guides/[slug]/data.ts, rewrites title + teaser + body
for each entry. Preserves slug + category.

Run:
    python pipeline/rewrite_guides.py                 # all entries
    python pipeline/rewrite_guides.py --only tax-year-end-checklist
    python pipeline/rewrite_guides.py --workers 4
"""
import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "utils"))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from config_supabase import DEEPSEEK_API_KEY
from deepseek_client import DeepSeekClient


ROOT = Path(__file__).resolve().parents[1]
DATA_TS = ROOT / "web" / "src" / "app" / "guides" / "[slug]" / "data.ts"


SYSTEM_PROMPT = """You are a senior ICAEW-qualified UK accountant rewriting long-form guides for Holloway Davies, a generalist UK accountancy firm.

Audience: UK business owners. Limited company directors, contractors, sole traders, partnership owners, and small business owners across every sector. NOT agency founders specifically.

Your job: take an existing HTML guide and rewrite the TITLE, TEASER, and BODY to remove all "agency founder" / "your agency" framing while preserving:
  - Every factual detail (rates, thresholds, dates, HMRC form names, deadlines)
  - The HTML structure (<h2>, <h3>, <p>, <ul>, <li>, <strong>, <table>, etc.)
  - Roughly the same length (do NOT shorten by more than 15%)
  - The same conceptual coverage, action-orientation, and depth
  - The checklist / procedural feel

VOICE: Financial Times editorial. Precise, confident, plain English, occasional sharp opinion. UK English (specialise, organise, recognise).

BANS:
- NO em-dashes anywhere. Use commas, full stops, parentheses, middle dots.
- NO "agency founder" / "agency founders" / "for agency founders" / "your agency" framing.
- "Agency" as a noun in a sector list (a marketing agency, an advertising agency) is fine. The ban is on the AUDIENCE framing.
- Replace agency-specific examples with generalist UK business examples (limited company directors, contractors, sole traders, food manufacturers, software companies, consultancies, retailers, partnerships, etc.)

TITLE: should be of the form "The UK [Owner Type or Business] [Topic] Checklist/Guide" without "Agency Founder's".
TEASER: similar reframing.
BODY: rewrite all instances of agency-targeted framing.

OUTPUT FORMAT: a single JSON object with exactly these three keys:
{
  "title": "<new title>",
  "teaser": "<new teaser, ~50-80 words>",
  "body": "<new HTML body, starts with <p>, same structure as original>"
}
No markdown fences, no commentary, just the JSON.
"""


def call_deepseek(client: DeepSeekClient, entry: dict) -> dict | None:
    user_prompt = f"""Current title: {entry['title']}
Current teaser: {entry['teaser']}
Current category: {entry['category']}

Current body (HTML):
{entry['body']}

Return the rewritten JSON object now."""
    raw = client.generate_creative(
        prompt=user_prompt,
        system=SYSTEM_PROMPT,
        temperature=0.55,
        max_tokens=6000,
    )
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"    JSON parse failed: {e}")
        print(f"    raw start: {raw[:200]}")
        return None


OUTPUT_BANNED = (
    "—",
    "agency founder",
    "agency founders",
    "for agency founders",
    "your agency",
)


def validate(slug: str, original: dict, new: dict) -> tuple[bool, str]:
    for k in ("title", "teaser", "body"):
        if k not in new:
            return False, f"missing key: {k}"
    if not new["body"].lstrip().startswith("<p>") and not new["body"].lstrip().startswith("<h"):
        return False, "body doesn't start with <p> or <h>"
    low_blob = (new["title"] + " " + new["teaser"] + " " + new["body"]).lower()
    for b in OUTPUT_BANNED:
        if b.lower() in low_blob:
            return False, f"banned string: {b!r}"
    if len(new["body"]) < 0.6 * len(original["body"]):
        return False, f"body too short: {len(new['body'])} vs original {len(original['body'])}"
    return True, ""


# Regex to extract each guide entry. Format is auto-generated and stable.
ENTRY_PATTERN = re.compile(
    r'  "([^"]+)":\s*\{\s*\n'
    r'\s*slug:\s*"([^"]+)",\s*\n'
    r'\s*title:\s*"([^"]+)",\s*\n'
    r'\s*teaser:\s*"([^"]+)",\s*\n'
    r'\s*category:\s*"([^"]+)",\s*\n'
    r'\s*body:\s*`([^`]*)`,\s*\n'
    r'\s*\},',
    re.MULTILINE,
)


def load_entries() -> list[dict]:
    text = DATA_TS.read_text(encoding="utf-8")
    out = []
    for m in ENTRY_PATTERN.finditer(text):
        outer, slug, title, teaser, category, body = m.groups()
        if outer != slug:
            continue
        out.append({
            "slug": slug,
            "title": title,
            "teaser": teaser,
            "category": category,
            "body": body,
        })
    return out


def rewrite_one(entry: dict) -> dict | None:
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
    slug = entry["slug"]
    t0 = time.time()
    for attempt in range(1, 4):
        try:
            new = call_deepseek(client, entry)
        except Exception as e:
            print(f"  [{slug:>32}]  DeepSeek error: {e}")
            continue
        if new is None:
            continue
        ok, msg = validate(slug, entry, new)
        if ok:
            elapsed = time.time() - t0
            print(f"  [{slug:>32}]  {elapsed:>5.1f}s  OK  (body {len(entry['body'])} -> {len(new['body'])} chars)")
            return new
        print(f"  [{slug:>32}]  attempt {attempt}: {msg}")
    print(f"  [{slug:>32}]  GAVE UP")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    entries = load_entries()
    print(f"Parsed {len(entries)} guide entries")
    targets = entries
    if args.only:
        targets = [e for e in entries if e["slug"] == args.only]
        if not targets:
            sys.exit(f"slug not found: {args.only}")

    print(f"Rewriting {len(targets)} guides (workers={args.workers})...")
    print()

    rewritten: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(rewrite_one, e): e for e in targets}
        for fut in as_completed(futures):
            e = futures[fut]
            r = fut.result()
            if r is not None:
                rewritten[e["slug"]] = r

    print()
    print(f"Successful: {len(rewritten)} / {len(targets)}")
    if not rewritten:
        sys.exit("nothing to write")

    text = DATA_TS.read_text(encoding="utf-8")
    patched = 0
    for slug, new in rewritten.items():
        safe_title = new["title"].replace('"', '\\"')
        safe_teaser = new["teaser"].replace('"', '\\"')
        safe_body = new["body"].replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        entry_pattern = re.compile(
            r'(  "' + re.escape(slug) + r'":\s*\{\s*\n'
            r'\s*slug:\s*"' + re.escape(slug) + r'",\s*\n)'
            r'\s*title:\s*"[^"]*",\s*\n'
            r'\s*teaser:\s*"[^"]*",\s*\n'
            r'(\s*category:\s*"[^"]*",\s*\n)'
            r'\s*body:\s*`[^`]*`(,\s*\n\s*\},)',
            re.MULTILINE,
        )
        def replace_entry(m: re.Match) -> str:
            return (
                m.group(1)
                + f'    title: "{safe_title}",\n'
                + f'    teaser: "{safe_teaser}",\n'
                + m.group(2)
                + f"    body: `{safe_body}`"
                + m.group(3)
            )
        new_text, n = entry_pattern.subn(replace_entry, text, count=1)
        if n == 1:
            text = new_text
            patched += 1
        else:
            print(f"  WARN: couldn't patch {slug}")

    DATA_TS.write_text(text, encoding="utf-8")
    print(f"\nPatched {patched} entries in {DATA_TS.name}")


if __name__ == "__main__":
    main()
