"""
Rewrite glossary body content for Holloway Davies, deliberately diverging
from the parallel Agency Founder Finance entries (cross-domain duplicate
content risk).

Reads web/src/app/glossary/[slug]/data.ts, fetches the AFF equivalent at
/glossary/{slug}, then sends BOTH to DeepSeek with instructions to write
a substantively different entry: different opening sentence, different
worked examples, different paragraph order where natural, while keeping
the facts (rates, thresholds, dates, HMRC form names) identical.

A word-overlap check against the AFF body rejects rewrites that share
more than 55% of distinctive vocabulary, and the entry retries up to 3
times.

Run:
    python pipeline/rewrite_glossary.py                # all entries
    python pipeline/rewrite_glossary.py --only badr
    python pipeline/rewrite_glossary.py --limit 3      # smoke test
    python pipeline/rewrite_glossary.py --workers 4
    python pipeline/rewrite_glossary.py --no-aff-guard # skip AFF fetch
"""
import argparse
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
DATA_TS = ROOT / "web" / "src" / "app" / "glossary" / "[slug]" / "data.ts"


SYSTEM_PROMPT = """You are a senior ICAEW-qualified UK accountant writing glossary entries for Holloway Davies, a generalist UK accountancy firm.

Audience: UK business owners across every sector. Limited company directors, contractors working through their own Ltd, sole traders, freelancers, partnership owners, small business owners.

CRITICAL CONTEXT, READ CAREFULLY: the user prompt will include TWO existing versions of this entry, one from this site and one from a sister site (Agency Founder Finance). Both are too similar to each other and Google will treat them as duplicate content. Your job is to write a NEW Holloway Davies version that is substantively different from BOTH. Keep the facts identical (rates, thresholds, dates, HMRC form names, deadlines, percentages, allowances) but change everything else.

DIVERGENCE REQUIREMENTS (mandatory):
1. DIFFERENT OPENING SENTENCE. Do not start with "X is a UK tax relief that..." or "X is the tax that..." or any phrasing that mirrors the existing versions. Open with a question, an example, a recent change, a common misconception, or a practical scenario.
2. DIFFERENT WORKED EXAMPLES. If the existing versions use £100,000 profit and a consultancy, you might use £180,000 profit and a software company, or £75,000 and a sole-trader plumbing business. Numbers must be plausible and the maths must check out.
3. DIFFERENT INDUSTRY ANCHORS. Rotate through: independent retailers, professional services firms, manufacturing SMEs, hospitality operators, software companies, construction subcontractors, healthcare practices, e-commerce sellers, consultancies, sole-trader trades. Pick ones that fit the topic, not the same ones the existing versions use.
4. DIFFERENT PARAGRAPH ORDER where natural. If the existing versions go definition → mechanics → example → caveats → "when this matters", consider definition → common pitfall → mechanics → worked example → action, or any other order that serves the reader.
5. DIFFERENT SUPPORTING DETAIL. Where the existing versions cite one HMRC form or one trap, cite a different (still real) one.

PRESERVE EXACTLY:
- Every numeric fact: rates, thresholds, allowances, deadlines, tax years, HMRC form names, monetary limits.
- HTML structure tags used: <p>, <ul>, <li>, <strong>. Use roughly the same TYPES of elements but not necessarily the same count or order.
- Roughly the same total length (within +/- 25%).

VOICE: Financial Times editorial. Precise, confident, plain English, occasional sharp opinion. UK English (specialise, organise, recognise, behaviour, modelling).

ABSOLUTE BANS:
- NO em-dashes or en-dashes anywhere. Use commas, full stops, parentheses, middle dots, or restructure the sentence.
- NO "agency founder" / "agency founders" / "for agency founders" / "your agency" framing.
- "Agency" as a noun in a sector list ("a marketing agency", "an advertising agency", "the agency in the chain" for IR35) is acceptable. The ban is on the AUDIENCE framing.
- NO copy-pasted phrases from either of the existing versions longer than 6 consecutive words.

OUTPUT: only the new HTML body. No JSON wrapper, no markdown fences, no commentary. The body must start with <p> and end with </p>.
"""


AFF_BASE = "https://www.agencyfounderfinance.co.uk"


def fetch_aff_body(slug: str, timeout: int = 15) -> str | None:
    """Fetch the parallel glossary entry from Agency Founder Finance and
    return its raw HTML body (the paragraphs after the H1). Returns None on
    any error so the caller can fall back to single-source rewriting."""
    url = f"{AFF_BASE}/glossary/{slug}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hd-rewrite-bot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    # Crude extraction: pull every <p>...</p> after the first H1.
    h1_end = html.lower().find("</h1>")
    if h1_end == -1:
        return None
    tail = html[h1_end:]
    paragraphs = re.findall(r"<p[^>]*>.*?</p>", tail, flags=re.DOTALL | re.IGNORECASE)
    if not paragraphs:
        return None
    # Cap at first 12 paragraphs to stay roughly in line with body length.
    return "\n".join(paragraphs[:12])


_WORD_RE = re.compile(r"[a-z]{4,}")
_STOP = {
    "your", "this", "that", "from", "with", "have", "will", "they", "their",
    "than", "when", "what", "which", "into", "more", "less", "most", "much",
    "such", "also", "been", "were", "where", "while", "would", "could",
    "should", "about", "after", "before", "between", "because", "through",
}


def _vocab(text: str) -> set[str]:
    """Distinctive lowercase words length >= 4, minus common stop words."""
    cleaned = re.sub(r"<[^>]+>", " ", text).lower()
    return {w for w in _WORD_RE.findall(cleaned) if w not in _STOP}


def call_deepseek(client: DeepSeekClient, entry: dict, aff_body: str | None) -> str:
    aff_block = (
        f"\nAgency Founder Finance version (avoid replicating its structure, examples or wording):\n{aff_body}\n"
        if aff_body
        else ""
    )
    user_prompt = f"""Term: {entry['term']}
Category: {entry['category']}
Primary keyword: {entry['primary_kw']}

Holloway Davies current body (also too similar to the AFF version, do not replicate):
{entry['body']}
{aff_block}
Write a NEW Holloway Davies version following every divergence rule in your instructions. Return ONLY the new HTML body, starting with <p> and ending with </p>."""
    raw = client.generate_creative(
        prompt=user_prompt,
        system=SYSTEM_PROMPT,
        temperature=0.75,
        max_tokens=2400,
    )
    # Strip any accidental code fences
    raw = re.sub(r"^```(?:html)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    # Post-process: replace stray em/en-dashes the model emitted despite the
    # ban. Cheaper than failing a validate-retry loop for a single character.
    raw = raw.replace(" — ", ", ").replace(" – ", ", ")
    raw = raw.replace("—", ", ").replace("–", ", ")
    return raw.strip()


# Banned strings in OUTPUT
OUTPUT_BANNED = (
    "—",  # em-dash
    "–",  # en-dash
    "agency founder",
    "agency founders",
    "for agency founders",
    "your agency",
)

# Max share of distinctive words that may overlap with the AFF body.
AFF_OVERLAP_MAX = 0.55


def validate_body(
    slug: str,
    original: str,
    new: str,
    aff_body: str | None,
) -> tuple[bool, str]:
    if not new.lstrip().startswith("<p>"):
        return False, "doesn't start with <p>"
    low = new.lower()
    for b in OUTPUT_BANNED:
        if b.lower() in low:
            return False, f"banned string: {b!r}"
    # Length floor: at least 60% of original
    if len(new) < 0.6 * len(original):
        return False, f"too short: {len(new)} vs original {len(original)}"
    if aff_body:
        new_v = _vocab(new)
        aff_v = _vocab(aff_body)
        if not new_v:
            return False, "no distinctive words in output"
        overlap = len(new_v & aff_v) / len(new_v)
        if overlap > AFF_OVERLAP_MAX:
            return False, f"AFF word overlap {overlap:.0%} > {AFF_OVERLAP_MAX:.0%}"
    return True, ""


# Regex to extract each glossary entry from data.ts. The file format is
# stable (auto-generated by generate_glossary.py originally).
ENTRY_PATTERN = re.compile(
    r'  "([^"]+)":\s*\{\s*\n'
    r'\s*slug:\s*"([^"]+)",\s*\n'
    r'\s*term:\s*"([^"]+)",\s*\n'
    r'\s*category:\s*"([^"]+)",\s*\n'
    r'\s*primary_kw:\s*"([^"]+)",\s*\n'
    r'\s*body:\s*`([^`]*)`,\s*\n'
    r'\s*\},',
    re.MULTILINE,
)


def load_entries() -> list[dict]:
    text = DATA_TS.read_text(encoding="utf-8")
    out = []
    for m in ENTRY_PATTERN.finditer(text):
        outer, slug, term, category, primary_kw, body = m.groups()
        if outer != slug:
            continue
        out.append({
            "slug": slug,
            "term": term,
            "category": category,
            "primary_kw": primary_kw,
            "body": body,
            "span": (m.start(), m.end()),
        })
    return out


def emit_entry(slug: str, term: str, category: str, primary_kw: str, body: str) -> str:
    """Re-emit a single glossary entry block. body is raw HTML; we wrap in
    backticks (template literal). Escape any backticks in the body."""
    safe_body = body.replace("`", "\\`").replace("${", "\\${")
    # Escape double quotes in the term/category strings if present
    return (
        f'  "{slug}": {{\n'
        f'    slug: "{slug}",\n'
        f'    term: "{term.replace(chr(34), chr(92)+chr(34))}",\n'
        f'    category: "{category}",\n'
        f'    primary_kw: "{primary_kw.replace(chr(34), chr(92)+chr(34))}",\n'
        f'    body: `{safe_body}`,\n'
        f'  }},'
    )


def rewrite_one(entry: dict, use_aff_guard: bool = True) -> str | None:
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
    slug = entry["slug"]
    aff_body = fetch_aff_body(slug) if use_aff_guard else None
    if use_aff_guard and aff_body is None:
        print(f"  [{slug:>32}]  no AFF reference fetched, proceeding without overlap guard")
    t0 = time.time()
    for attempt in range(1, 4):
        try:
            new_body = call_deepseek(client, entry, aff_body)
        except Exception as e:
            print(f"  [{slug:>32}]  DeepSeek error: {e}")
            continue
        ok, msg = validate_body(slug, entry["body"], new_body, aff_body)
        if ok:
            elapsed = time.time() - t0
            print(f"  [{slug:>32}]  {elapsed:>5.1f}s  OK  ({len(entry['body'])} -> {len(new_body)} chars)")
            return new_body
        print(f"  [{slug:>32}]  attempt {attempt}: {msg}")
    print(f"  [{slug:>32}]  GAVE UP after 3 attempts")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="rewrite one slug only")
    parser.add_argument("--limit", type=int, help="rewrite first N entries")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--no-aff-guard",
        action="store_true",
        help="skip AFF fetch + word-overlap rejection (single-source rewrite)",
    )
    args = parser.parse_args()

    entries = load_entries()
    print(f"Parsed {len(entries)} glossary entries from {DATA_TS.name}")

    targets = entries
    if args.only:
        targets = [e for e in entries if e["slug"] == args.only]
        if not targets:
            sys.exit(f"slug not found: {args.only}")
    elif args.limit:
        targets = entries[: args.limit]

    print(f"Rewriting {len(targets)} entries (workers={args.workers})...")
    print()

    use_aff_guard = not args.no_aff_guard
    new_bodies: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(rewrite_one, e, use_aff_guard): e for e in targets
        }
        for fut in as_completed(futures):
            e = futures[fut]
            nb = fut.result()
            if nb is not None:
                new_bodies[e["slug"]] = nb

    print()
    print(f"Successful rewrites: {len(new_bodies)} / {len(targets)}")
    if not new_bodies:
        sys.exit("no rewrites; nothing to write")

    if args.dry_run:
        print("\n[dry-run] First entry rewritten body preview:")
        first = list(new_bodies.keys())[0]
        print(f"--- {first} ---")
        print(new_bodies[first][:600])
        return

    # Reassemble the file. We replace each entry's body in-place by reading
    # the file fresh and patching each entry's body block.
    text = DATA_TS.read_text(encoding="utf-8")
    patched = 0
    for slug, new_body in new_bodies.items():
        safe = new_body.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        # Find this entry's body assignment and replace just the body content
        entry_pattern = re.compile(
            r'(  "' + re.escape(slug) + r'":\s*\{\s*\n'
            r'\s*slug:\s*"' + re.escape(slug) + r'",\s*\n'
            r'\s*term:\s*"[^"]*",\s*\n'
            r'\s*category:\s*"[^"]*",\s*\n'
            r'\s*primary_kw:\s*"[^"]*",\s*\n'
            r'\s*body:\s*)`[^`]*`(,\s*\n\s*\},)',
            re.MULTILINE,
        )
        new_text, n = entry_pattern.subn(
            lambda m: m.group(1) + "`" + safe + "`" + m.group(2),
            text,
            count=1,
        )
        if n == 1:
            text = new_text
            patched += 1
        else:
            print(f"  WARN: couldn't patch {slug}")

    DATA_TS.write_text(text, encoding="utf-8")
    print(f"\nPatched {patched} entries in {DATA_TS.name}")


if __name__ == "__main__":
    main()
