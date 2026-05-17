"""
Rescore the blog_topics_generalist queue against SE Ranking volume +
difficulty data.

Expects the SE Ranking CSV export at seo-research/seranking-results.csv.
SE Ranking column names vary between exports; this script handles common
variants (Keyword / keyword / Phrase, Search Volume / Volume / volume,
Difficulty / KD / Keyword Difficulty, etc.).

Two outputs:

  seo-research/rescore-suggestions.csv
    Per-topic rescore suggestion:
      topic, primary_keyword, current_priority, current_tier,
      sv (search volume), kd (difficulty), competition,
      new_priority, action (keep / bump / drop / pillar-promote / drop-zero-vol)

  seo-research/rescore-additions.csv
    High-value keywords NOT in the queue that we should consider adding
    (autocomplete or GSC sources with strong SE Ranking metrics).

The script DOES NOT write to Supabase by default. Use --apply to push the
new publish_priority values back to blog_topics_generalist.

Scoring formula (transparent, easy to tune):
  effective_score = sqrt(sv) * intent_weight / max(kd, 5)
  intent_weight: transactional=1.6, navigational=1.2, informational=1.0
  new_priority bands:
    score >= 4   -> 9 (cornerstone)
    score >= 2   -> 8
    score >= 1   -> 7
    score >= 0.4 -> 6
    score >= 0.1 -> 5
    else         -> 4 (drop-candidate)

Run:
    python pipeline/rescore_with_seranking.py                    # dry run
    python pipeline/rescore_with_seranking.py --apply            # push priorities to Supabase
    python pipeline/rescore_with_seranking.py --min-volume 100   # filter additions
"""
import argparse
import csv
import math
import os
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from config_supabase import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "seo-research"
INPUT_CSV = RESEARCH / "seranking-results.csv"
OUT_RESCORE = RESEARCH / "rescore-suggestions.csv"
OUT_ADDITIONS = RESEARCH / "rescore-additions.csv"

INTENT_WEIGHT = {
    "transactional": 1.6,
    "commercial": 1.4,
    "navigational": 1.2,
    "informational": 1.0,
}


def normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _pick(row: dict, *candidates) -> str:
    """Pick the first non-empty value from candidate column names."""
    for c in candidates:
        for k in row.keys():
            if k.strip().lower() == c.lower():
                v = (row[k] or "").strip()
                if v:
                    return v
    return ""


def _to_int(s: str):
    s = (s or "").replace(",", "").replace(" ", "").strip()
    if not s or s.lower() in ("n/a", "na", "-", "none"):
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _to_float(s: str):
    s = (s or "").replace(",", "").replace(" ", "").strip()
    if not s or s.lower() in ("n/a", "na", "-", "none"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_seranking():
    """Return {normalised_keyword: {kw, sv, kd, comp, cpc}}."""
    if not INPUT_CSV.exists():
        sys.exit(f"ERROR: missing {INPUT_CSV}. Drop the SE Ranking CSV there first.")
    out = {}
    with INPUT_CSV.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = _pick(row, "Keyword", "keyword", "Phrase", "phrase", "Search Term", "Query")
            if not kw:
                continue
            sv = _to_int(_pick(row, "Search Volume", "Search vol.", "Search vol", "Volume", "SV", "Avg. Monthly Searches", "search_volume"))
            kd = _to_int(_pick(row, "Difficulty", "Keyword Difficulty", "KD", "difficulty"))
            comp = _to_float(_pick(row, "Competition", "competition", "Comp"))
            cpc = _to_float(_pick(row, "CPC", "cpc", "Cost Per Click"))
            intent = _pick(row, "Search Intent", "Search intent", "Intent", "intent")
            out[normalise(kw)] = {
                "kw": kw, "sv": sv, "kd": kd, "comp": comp, "cpc": cpc, "intent": intent,
            }
    return out


def fetch_queue():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = httpx.get(url, headers=headers,
                  params={"select": "id,topic,primary_keyword,user_intent,content_tier,publish_priority,used,category"},
                  timeout=15)
    r.raise_for_status()
    return r.json()


def score(sv, kd, intent):
    if sv is None or kd is None:
        return None
    if sv <= 0:
        return 0.0
    iw = INTENT_WEIGHT.get((intent or "informational").lower(), 1.0)
    return math.sqrt(sv) * iw / max(kd, 5)


def score_to_priority(s):
    if s is None:
        return None  # keep current priority if no data
    if s >= 4:    return 9
    if s >= 2:    return 8
    if s >= 1:    return 7
    if s >= 0.4:  return 6
    if s >= 0.1:  return 5
    return 4


def decide_action(current_pri, new_pri, sv, used):
    """Human-readable action label."""
    if used:
        return "already-published"
    if new_pri is None:
        return "no-data"
    if sv is not None and sv == 0:
        return "drop-zero-vol"
    if new_pri > (current_pri or 0):
        diff = new_pri - (current_pri or 0)
        return f"bump-up (+{diff})"
    if new_pri < (current_pri or 0):
        diff = (current_pri or 0) - new_pri
        return f"bump-down (-{diff})"
    return "keep"


def patch_priority(topic_id, new_pri):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
               "Content-Type": "application/json", "Prefer": "return=minimal"}
    r = httpx.patch(url, headers=headers, params={"id": f"eq.{topic_id}"},
                    json={"publish_priority": new_pri}, timeout=15)
    r.raise_for_status()


def load_extras():
    """Load autocomplete + GSC keywords not in the queue (legacy source)."""
    extras = {}
    for src, path in [("autocomplete", RESEARCH / "autocomplete-candidates.csv"),
                      ("gsc", RESEARCH / "gsc-cross-niche-queries.csv")]:
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                kw = (r.get("suggestion") or r.get("query") or "").strip()
                if not kw:
                    continue
                extras.setdefault(normalise(kw), {"kw": kw, "source": src})
    return extras


# Relevance filter for UK business accountancy queries
RELEVANT_TOKENS = (
    "accountant", "accounting", "bookkeep",
    "tax", "vat", "mtd", "ir35", "r&d", "rdec",
    "corporation", "dividend", "self assessment", "self-assessment", "self employ",
    "sole trader", "limited company", "ltd company", "ltd ",
    "contractor", "freelance", "freelancer",
    "director", "payroll", "paye", "cis",
    "badr", "capital gain", "cgt", "hmrc",
    "company formation", "incorporat",
    "xero", "quickbooks", "freeagent", "sage", "dext", "brightpay",
    "expense", "allowance", "deduction",
    "partnership", "llp",
    "startup ", "start-up", "small business",
    "salary", "national insurance", " ni ",
    "companies house", "p11d", "p60", "p45",
    "ct600", "sa100", "sa103", "sa800",
    "annual accounts", "confirmation statement",
    "director's loan", "directors loan", "directors' loan",
)
EXCLUDED_TOKENS = (
    # HMRC portals / login pages (informational-navigational, not service queries)
    "personal tax account", "tax account login", "my tax account",
    "council tax account", "council tax", "business tax account",
    "hmrc account", "hmrc tax account",
    "gov.uk personal", "gov uk personal",
    # Banking accounts / consumer accounts (not accountancy)
    "bank account", "checking account", "savings account",
    "current account", "current accounts",
    "social media", "email account", "games account",
    "minecraft", "steam", "playstation", "paypal", "snapchat",
    "tiktok", "instagram", "facebook", "youtube", "spotify",
    "netflix", "amazon prime", "disney", "crypto wallet",
    "bitcoin account", "childcare",
    # Films / culture
    "the accountant", "accountant film", "accountant 2", "accountant movie",
    # Career / salary as employment, not service fee
    "accountant salary", "accountancy salary", "tax accountant salary",
    "accountant jobs", "accountant cv", "accounting apprenticeships",
    "accounting jobs", "accounting career", "master in", "masters in",
    "degree in accounting", "accounting degree",
    "trainee accountant", "graduate accountant",
    # Training / courses / qualifications (not B2B service queries)
    "accountant course", "accountant courses", "accounting course",
    "accounting courses", "accountancy course", "accounting training",
    "aat course", "acca course", "cima course", "icaew course",
    "past papers", "a levels", "level 3 accounting", "level 4 accounting",
    # Misc noise
    "dartford crossing", "congestion charge",
    "british accountancy awards",
    "accountants seo", "seo for accountants",  # services FOR accountants, not BY us
    "accounts assistant", "accounts payable", "accounts receivable",  # bookkeeping roles
    # Known UK accountancy firm brand names that appear in suggestion expansions
    "rowleys", "moore scarrott", "jp accountancy", "rr accounting",
    "abacus accounting", "larking gowen", "haines watts", "azets",
    "saffery", "bdo", "kpmg", "pwc", "ey ", "deloitte", "grant thornton",
    "mazars", "rsm", "crowe", "smith and williamson", "evelyn partners",
    "anderson anderson", "milsted langdon",
    # Generic short brand-y patterns
    "& co accountants", "& co accountant",
    "associates accountants", "associates accounting",
)


# A token looks like a brand name if it's a 2-3 word phrase ending in
# "accountants" / "accounting" / "& co" / "ltd" preceded by a non-keyword
# proper-noun-style token (e.g. "Rowleys", "Moore Scarrott").
_BRAND_TAIL = re.compile(r"\b(accountants?|accountancy|accounting|& co|ltd|llp)\s*$", re.IGNORECASE)
_GENERIC_HEAD = {"online", "small", "business", "uk", "fixed", "fee", "best",
                 "cheap", "local", "specialist", "limited", "ltd", "personal",
                 "tax", "vat", "contractor", "freelance", "freelancer",
                 "sole", "trader", "self", "employed", "company", "chartered",
                 "qualified", "icaew", "acca", "aat", "management", "payroll",
                 "hr", "hospitality", "agriculture", "construction", "retail",
                 "ecommerce", "tech", "creative", "medical", "dental", "legal"}


def looks_like_brand(kw: str) -> bool:
    """Heuristic: if first token isn't a generic descriptor and the phrase
    ends with 'accountants/accounting/& co/ltd', it's probably a firm name."""
    if not _BRAND_TAIL.search(kw):
        return False
    first = kw.strip().split()[0].lower()
    return first not in _GENERIC_HEAD


def is_relevant(kw: str) -> bool:
    k = kw.lower()
    if any(e in k for e in EXCLUDED_TOKENS):
        return False
    if looks_like_brand(kw):
        return False
    return any(r in k for r in RELEVANT_TOKENS)


def intent_boost(intent_str: str) -> float:
    """Map SE Ranking intent codes (single or comma-separated) to weight.
    Codes: C = commercial, T = transactional, L = local (commercial),
    N = navigational, I = informational."""
    if not intent_str:
        return 1.0
    parts = [p.strip().upper() for p in re.split(r"[,/]", intent_str)]
    weight = 1.0
    if "T" in parts: weight = max(weight, 1.6)
    if "C" in parts: weight = max(weight, 1.5)
    if "L" in parts: weight = max(weight, 1.4)
    if "N" in parts: weight = max(weight, 1.1)
    return weight


def discover_additions_from_seranking(se_data, queue_norms, min_sv, max_kd, top_n):
    """Source new topic candidates DIRECTLY from the SE Ranking export.

    The SE Ranking export is a 'suggestion expansion' from a seed keyword
    (here, 'accountant'). It contains thousands of real UK-search-volume
    keywords. The relevance filter strips out portal/login/film/career noise.

    Returns list of dicts ranked by (commercial-weighted) score, deduped
    against the current queue."""
    rows = []
    for n, d in se_data.items():
        kw = d["kw"]
        sv, kd = d["sv"], d["kd"]
        if sv is None or kd is None or sv < min_sv or kd > max_kd:
            continue
        if not is_relevant(kw):
            continue
        if n in queue_norms:
            continue  # already in queue
        intent = d.get("intent", "")
        s = math.sqrt(sv) * intent_boost(intent) / max(kd, 5)
        rows.append({
            "keyword": kw, "source": "seranking",
            "sv": sv, "kd": kd, "intent": intent,
            "competition": d.get("comp"), "cpc": d.get("cpc"),
            "score": round(s, 3),
            "suggested_priority": score_to_priority(s),
        })
    rows.sort(key=lambda r: -r["score"])
    return rows[:top_n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="push new priorities to Supabase (default is dry-run)")
    parser.add_argument("--min-volume", type=int, default=50,
                        help="for the additions list, require SV >= this (default 50)")
    parser.add_argument("--max-difficulty", type=int, default=60,
                        help="for the additions list, require KD <= this (default 60)")
    args = parser.parse_args()

    print(f"Loading SE Ranking results from {INPUT_CSV.name}...")
    se = load_seranking()
    print(f"  {len(se)} keywords with metrics")

    print("Fetching queue from Supabase...")
    queue = fetch_queue()
    print(f"  {len(queue)} topics")

    rescore_rows = []
    matched_norms = set()
    bump_up = bump_down = keep = no_data = drop = 0
    for t in queue:
        pk_norm = normalise(t.get("primary_keyword") or "")
        if not pk_norm:
            continue
        data = se.get(pk_norm)
        sv = data["sv"] if data else None
        kd = data["kd"] if data else None
        comp = data["comp"] if data else None
        s = score(sv, kd, t.get("user_intent"))
        new_pri = score_to_priority(s) if s is not None else None
        action = decide_action(t.get("publish_priority"), new_pri, sv, t.get("used"))
        if data:
            matched_norms.add(pk_norm)
        if "bump-up" in action: bump_up += 1
        elif "bump-down" in action: bump_down += 1
        elif action == "keep": keep += 1
        elif action == "no-data": no_data += 1
        elif action == "drop-zero-vol": drop += 1
        rescore_rows.append({
            "topic": t["topic"],
            "category": t.get("category"),
            "primary_keyword": t.get("primary_keyword"),
            "current_priority": t.get("publish_priority"),
            "current_tier": t.get("content_tier"),
            "user_intent": t.get("user_intent"),
            "sv": sv, "kd": kd, "competition": comp,
            "score": round(s, 3) if s is not None else None,
            "new_priority": new_pri,
            "action": action,
            "used": t.get("used"),
            "id": t["id"],
        })

    OUT_RESCORE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_RESCORE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rescore_rows[0].keys()))
        w.writeheader()
        for r in sorted(rescore_rows, key=lambda x: -(x.get("new_priority") or 0)):
            w.writerow(r)
    print(f"\nWrote {OUT_RESCORE}")
    print(f"  bump-up:     {bump_up}")
    print(f"  bump-down:   {bump_down}")
    print(f"  keep:        {keep}")
    print(f"  no-data:     {no_data}  (keyword not in SE Ranking export)")
    print(f"  drop-vol=0:  {drop}")

    # Additions: source DIRECTLY from SE Ranking (relevance + intent filtered)
    # This is where the real gaps surface, since the SE Ranking export contains
    # thousands of UK-search-volume keywords we never saw in autocomplete/GSC.
    queue_norms = {normalise(t.get("primary_keyword") or "") for t in queue if t.get("primary_keyword")}
    queue_norms |= {normalise(t.get("topic") or "") for t in queue if t.get("topic")}
    add_rows = discover_additions_from_seranking(
        se, queue_norms,
        min_sv=args.min_volume,
        max_kd=args.max_difficulty,
        top_n=200,
    )
    with OUT_ADDITIONS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["keyword","source","sv","kd","intent","competition","cpc","score","suggested_priority"])
        w.writeheader()
        for r in add_rows:
            w.writerow(r)
    print(f"\nWrote {OUT_ADDITIONS}  (top {len(add_rows)} relevant additions)")
    if add_rows:
        print("\nTop 20 additions by score:")
        for r in add_rows[:20]:
            print(f"  P{r['suggested_priority']}  score={r['score']:5.2f}  sv={r['sv']:>5}  kd={r['kd']:>3}  intent={r['intent']:<8}  {r['keyword']!r}")

    if args.apply:
        print("\n--apply: pushing new priorities to Supabase...")
        applied = 0
        for r in rescore_rows:
            if r["action"].startswith("bump") and not r["used"]:
                try:
                    patch_priority(r["id"], r["new_priority"])
                    applied += 1
                except Exception as e:
                    print(f"  FAIL: {r['topic'][:50]}: {e}")
        print(f"  applied: {applied} priority updates")
    else:
        print("\nDry run only. Re-run with --apply to push priorities to Supabase.")


if __name__ == "__main__":
    main()
