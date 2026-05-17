"""
Export keyword lists for the SE Ranking bulk keyword research tool.

Produces three plain-text files (one keyword per line) in seo-research/:

  seranking-keywords-current.txt    — distinct primary_keywords from the 199
                                       topics currently queued in
                                       blog_topics_generalist. Use this to
                                       validate volume + difficulty for what
                                       we're already planning to publish.

  seranking-keywords-autocomplete.txt — Google Autocomplete candidates from
                                         the earlier pass that didn't make
                                         it into the seeded queue (P5,
                                         filtered to question-format or
                                         info-style phrases, deduped).

  seranking-keywords-gsc-niche.txt    — cross-niche queries surfaced from
                                         the Property + Dentists GSC dumps
                                         that aren't yet in our queue.

  seranking-keywords-all.txt          — union of all three above, deduped.
                                         Single paste for SE Ranking bulk
                                         input.

After you run SE Ranking on the lists, drop the CSV outputs back into
seo-research/ as seranking-results-*.csv and we can re-prioritise the queue
against real volume / difficulty data.

Run:
    python pipeline/export_for_seranking.py
"""
import csv
import os
import re
import sys
from collections import OrderedDict
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


def normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def fetch_queued_keywords():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = httpx.get(url, headers=headers,
                  params={"select": "topic,primary_keyword", "limit": "500"},
                  timeout=15)
    r.raise_for_status()
    out = OrderedDict()
    for row in r.json():
        pk = (row.get("primary_keyword") or "").strip()
        if pk and pk.lower() not in out:
            out[pk.lower()] = pk
    return list(out.values())


def load_autocomplete_extras(existing_norm):
    p = RESEARCH / "autocomplete-candidates.csv"
    if not p.exists():
        return []
    Q_STARTERS = ("how ", "what ", "when ", "why ", "which ", "can i ", "do i ",
                  "is ", "are ", "should i ", "does ", "where ")
    keep = []
    seen = set()
    with p.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            s = (r.get("suggestion") or "").strip()
            sn = normalise(s)
            if not s or sn in existing_norm or sn in seen:
                continue
            wc = len(s.split())
            if wc < 3 or wc > 12:
                continue
            is_q = any(s.lower().startswith(q) for q in Q_STARTERS)
            has_modifier = any(m in s.lower() for m in
                               ("explained", "vs", "calculator", " uk", "2026",
                                "deadline", "guide", "cost", "near me"))
            if not is_q and not has_modifier:
                continue
            keep.append(s)
            seen.add(sn)
    return keep


def load_gsc_extras(existing_norm):
    p = RESEARCH / "gsc-cross-niche-queries.csv"
    if not p.exists():
        return []
    keep = []
    seen = set()
    with p.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            q = (r.get("query") or "").strip()
            qn = normalise(q)
            if not q or qn in existing_norm or qn in seen:
                continue
            keep.append(q)
            seen.add(qn)
    return keep


def write_list(path: Path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(items) + "\n", encoding="utf-8")
    print(f"  wrote {path.name}: {len(items)} keywords")


def main():
    print("Fetching primary_keywords from blog_topics_generalist...")
    current = fetch_queued_keywords()
    current_norm = {normalise(k) for k in current}
    print(f"  {len(current)} distinct primary keywords in queue")

    print("Loading autocomplete extras (not already queued)...")
    ac_extras = load_autocomplete_extras(current_norm)
    print(f"  {len(ac_extras)} autocomplete candidates")

    print("Loading GSC cross-niche extras (not already queued)...")
    gsc_extras = load_gsc_extras(current_norm)
    print(f"  {len(gsc_extras)} GSC candidates")

    # Combined deduped
    combined_norm = set()
    combined = []
    for kw in current + ac_extras + gsc_extras:
        n = normalise(kw)
        if n in combined_norm:
            continue
        combined_norm.add(n)
        combined.append(kw)

    print()
    write_list(RESEARCH / "seranking-keywords-current.txt", current)
    write_list(RESEARCH / "seranking-keywords-autocomplete.txt", ac_extras)
    write_list(RESEARCH / "seranking-keywords-gsc-niche.txt", gsc_extras)
    write_list(RESEARCH / "seranking-keywords-all.txt", combined)

    print()
    print(f"TOTAL unique keywords for SE Ranking: {len(combined)}")
    print()
    print("Paste seranking-keywords-all.txt into the SE Ranking bulk research")
    print("input. When you have the CSV back, drop it as")
    print("seo-research/seranking-results.csv and we will rescore + re-prioritise.")


if __name__ == "__main__":
    main()
