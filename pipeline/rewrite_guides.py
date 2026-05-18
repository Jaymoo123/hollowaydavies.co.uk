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
import urllib.request
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


SYSTEM_PROMPT = """You are a senior ICAEW-qualified UK accountant writing long-form guides for Holloway Davies, a generalist UK accountancy firm.

Audience: UK business owners across every sector. Limited company directors, contractors, sole traders, partnership owners, small business owners.

CRITICAL CONTEXT, READ CAREFULLY: the user prompt will include TWO existing versions of this guide, one from this site and one from a sister site (Agency Founder Finance). Both are too similar and Google will treat them as cross-domain duplicate content. Your job is to write a NEW Holloway Davies version that is substantively different from BOTH. Keep the facts identical (rates, thresholds, dates, HMRC form names, deadlines, percentages, allowances) but change everything else.

DIVERGENCE REQUIREMENTS (mandatory):
1. DIFFERENT TITLE. Avoid mirroring either existing title's phrasing or structure. Use a different framing (a question, a number, a deadline-anchored statement, a contrarian framing, etc.).
2. DIFFERENT TEASER. New angle, new hook.
3. DIFFERENT OPENING PARAGRAPH. Do not open with the same scene-setting that either version uses.
4. DIFFERENT WORKED EXAMPLES. Different industries, different £ figures (all plausible and accurate), different scenarios.
5. DIFFERENT INDUSTRY ANCHORS. Rotate through: independent retailers, professional services firms, manufacturing SMEs, hospitality, software companies, construction subcontractors, healthcare practices, e-commerce sellers, consultancies, sole-trader trades.
6. DIFFERENT SECTION HEADINGS where natural. Reorder where it serves the reader. The checklist / procedural feel should stay, but the order of sections may shift.
7. DIFFERENT SUPPORTING DETAIL. Where the existing versions cite one HMRC form, deadline trap, or worked penalty, cite a different (still real) one.

PRESERVE EXACTLY:
- Every numeric fact: rates, thresholds, allowances, deadlines, tax years, HMRC form names, monetary limits.
- HTML structure tags used: <h2>, <h3>, <p>, <ul>, <li>, <strong>, <table>. Use roughly the same types of elements.
- Roughly the same total length (within +/- 25%).
- The procedural / checklist DNA. Readers should still finish with a clear set of actions.

VOICE: Financial Times editorial. Precise, confident, plain English, occasional sharp opinion. UK English (specialise, organise, recognise, behaviour, modelling).

ABSOLUTE BANS:
- NO em-dashes or en-dashes anywhere. Use commas, full stops, parentheses, middle dots, or restructure.
- NO "agency founder" / "agency founders" / "for agency founders" / "your agency" framing.
- "Agency" as a noun in a sector list (a marketing agency, an advertising agency) is acceptable. The ban is on the AUDIENCE framing.
- NO copy-pasted phrases from either of the existing versions longer than 6 consecutive words.

OUTPUT FORMAT: a single JSON object with exactly these three keys:
{
  "title": "<new title>",
  "teaser": "<new teaser, ~50-80 words>",
  "body": "<new HTML body>"
}
No markdown fences, no commentary, just the JSON.
"""


AFF_BASE = "https://www.agencyfounderfinance.co.uk"


def fetch_aff_guide(slug: str, timeout: int = 20) -> str | None:
    """Fetch the parallel guide from Agency Founder Finance and return its
    raw HTML body. Returns None on any error."""
    url = f"{AFF_BASE}/guides/{slug}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hd-rewrite-bot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    h1_end = html.lower().find("</h1>")
    if h1_end == -1:
        return None
    tail = html[h1_end:]
    # Pull every relevant content tag in order, up to first <footer>
    foot = tail.lower().find("<footer")
    if foot != -1:
        tail = tail[:foot]
    blocks = re.findall(
        r"<(?:h2|h3|p|ul|ol)[^>]*>.*?</(?:h2|h3|p|ul|ol)>",
        tail,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not blocks:
        return None
    return "\n".join(blocks)


_WORD_RE = re.compile(r"[a-z]{4,}")
_STOP = {
    "your", "this", "that", "from", "with", "have", "will", "they", "their",
    "than", "when", "what", "which", "into", "more", "less", "most", "much",
    "such", "also", "been", "were", "where", "while", "would", "could",
    "should", "about", "after", "before", "between", "because", "through",
}


def _vocab(text: str) -> set[str]:
    cleaned = re.sub(r"<[^>]+>", " ", text).lower()
    return {w for w in _WORD_RE.findall(cleaned) if w not in _STOP}


def call_deepseek(client: DeepSeekClient, entry: dict, aff_body: str | None) -> dict | None:
    aff_block = (
        f"\nAgency Founder Finance version (do NOT replicate its structure, examples or wording):\n{aff_body}\n"
        if aff_body
        else ""
    )
    user_prompt = f"""Current title: {entry['title']}
Current teaser: {entry['teaser']}
Current category: {entry['category']}

Holloway Davies current body (also too similar to the AFF version, do not replicate):
{entry['body']}
{aff_block}
Write a NEW Holloway Davies version following every divergence rule. Return the JSON object now."""
    raw = client.generate_creative(
        prompt=user_prompt,
        system=SYSTEM_PROMPT,
        temperature=0.75,
        max_tokens=6000,
    )
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    # Strip any stray em/en-dashes from the JSON string content too.
    raw = raw.replace(" — ", ", ").replace(" – ", ", ")
    raw = raw.replace("—", ", ").replace("–", ", ")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"    JSON parse failed: {e}")
        print(f"    raw start: {raw[:200]}")
        return None


OUTPUT_BANNED = (
    "—",
    "–",
    "agency founder",
    "agency founders",
    "for agency founders",
    "your agency",
)


AFF_OVERLAP_MAX = 0.55


def validate(
    slug: str,
    original: dict,
    new: dict,
    aff_body: str | None,
) -> tuple[bool, str]:
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
    if aff_body:
        new_v = _vocab(new["body"])
        aff_v = _vocab(aff_body)
        if not new_v:
            return False, "no distinctive words in output body"
        overlap = len(new_v & aff_v) / len(new_v)
        if overlap > AFF_OVERLAP_MAX:
            return False, f"AFF word overlap {overlap:.0%} > {AFF_OVERLAP_MAX:.0%}"
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


def rewrite_one(entry: dict, use_aff_guard: bool = True) -> dict | None:
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
    slug = entry["slug"]
    aff_body = fetch_aff_guide(slug) if use_aff_guard else None
    if use_aff_guard and aff_body is None:
        print(f"  [{slug:>32}]  no AFF reference fetched, proceeding without overlap guard")
    t0 = time.time()
    for attempt in range(1, 4):
        try:
            new = call_deepseek(client, entry, aff_body)
        except Exception as e:
            print(f"  [{slug:>32}]  DeepSeek error: {e}")
            continue
        if new is None:
            continue
        ok, msg = validate(slug, entry, new, aff_body)
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
    parser.add_argument(
        "--no-aff-guard",
        action="store_true",
        help="skip AFF fetch + word-overlap rejection",
    )
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

    use_aff_guard = not args.no_aff_guard
    rewritten: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(rewrite_one, e, use_aff_guard): e for e in targets}
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
