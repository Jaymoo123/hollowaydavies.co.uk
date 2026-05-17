"""
Cross-niche GSC query analysis.

Reads the cached GSC query dumps for Property and Dentists, filters out
niche-specific queries (landlord, dental, btl, etc.), and surfaces queries
that a generalist UK business accountancy site could win.

Two outputs:
  1. seo-research/gsc-cross-niche-queries.csv — every query that survives
     the niche-specific filter, with impressions/clicks/CTR/position +
     source niche + flag for overlap with our existing 79 seeds.
  2. seo-research/gsc-cross-niche-summary.md — short markdown with
     headline counts and the top-30 unclaimed queries by impressions.

Run:
    python pipeline/gsc_cross_niche_analysis.py
"""
import csv
import json
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


REPO = Path(__file__).resolve().parents[2]
PROPERTY_DUMP = REPO / "scripts" / "gsc_property_data.json"
DENTISTS_DUMP = REPO / "scripts" / "gsc_dentists_data.json"
OUT_CSV = Path(__file__).resolve().parents[1] / "seo-research" / "gsc-cross-niche-queries.csv"
OUT_MD = Path(__file__).resolve().parents[1] / "seo-research" / "gsc-cross-niche-summary.md"


# Tokens that mark a query as niche-specific. Only exclude queries that are
# clearly about being a landlord OR working in dental practice. KEEP queries
# that merely mention "property" in a generic CGT/PPR/tax context — those are
# precisely the cross-applicable signals the generalist site should pick up
# (the property site ranks position 80+ for general CGT terms because it
# only partially covers them; the generalist site is the proper home).
PROPERTY_TOKENS = {
    # Landlord-business indicators (hard exclude)
    "landlord", "landlords",
    "buy to let", "btl", "buy-to-let", " btl ", " btl", "btl ",
    "rental income", "rental property", "rental yield",
    "let property", "letting agent", "letting agents",
    "section 24", "s24", "section24",
    "hmo ", " hmo", "fhl", "holiday let", "airbnb",
    "stamp duty", "sdlt",
    "rent a room",
    "sa105",  # HMRC self assessment property pages
    # Property-niche service / structure / advice indicators
    "property investor", "property investors",
    "property portfolio", "portfolio incorporation",
    "property company structure", "property group structure",
    "property accountant", "property specialist", "property specialists",
    "property accounting", "property management",
    "property tax accountant", "property tax specialist",
    "property tax specialists", "property tax advice",
    "tax accountant property", "tax-efficient property", "smart property",
    "incorporating a property", "incorporate property",
    "buy to let mortgage", "btl mortgage",
    "property investment",
    # Section 24 paraphrases that the property GSC dominates
    "mortgage interest tax relief", "tax relief on mortgage interest",
    "tax relief on mortgage", "20 tax credit on mortgage",
    "mortgage tax relief", "mortgage interest relief",
}
DENTIST_TOKENS = {
    # Practice-business indicators
    "dental practice", "dental practices",
    "dental accountant", "dental accountants",
    "dental accounting",
    "dentist", "dentists",
    "orthodontist", "orthodontic",
    "associate dentist", "principal dentist",
    "nhs pension",
    "dental nurse", "dental hygienist",
    "associate contract", "associate agreement",
    "lab costs",  # dental lab costs
}

NICHE_TOKENS = PROPERTY_TOKENS | DENTIST_TOKENS


def normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def is_niche_specific(query: str) -> str | None:
    q = " " + query.lower() + " "
    for tok in PROPERTY_TOKENS:
        if tok in q:
            return "property-specific"
    for tok in DENTIST_TOKENS:
        if tok in q:
            return "dentist-specific"
    return None


def load_queries(dump_path: Path, niche_label: str):
    with dump_path.open(encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for q in data.get("queries", []):
        keys = q.get("keys") or []
        query = keys[0] if keys else None
        if not query:
            continue
        rows.append({
            "query": query.strip(),
            "impressions": int(q.get("impressions") or 0),
            "clicks": int(q.get("clicks") or 0),
            "ctr": float(q.get("ctr") or 0),
            "position": float(q.get("position") or 0),
            "source_niche": niche_label,
            "fetched_at": data.get("fetched_at"),
        })
    return rows


def fetch_existing_seed_keywords():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = httpx.get(url, headers=headers, params={"select": "primary_keyword,topic"}, timeout=15.0)
    r.raise_for_status()
    items = r.json()
    return {normalise(i.get("primary_keyword") or ""): i for i in items if i.get("primary_keyword")} | \
           {normalise(i.get("topic") or ""): i for i in items if i.get("topic")}


def main():
    if not PROPERTY_DUMP.exists() or not DENTISTS_DUMP.exists():
        print("ERROR: missing cached GSC dumps in scripts/")
        sys.exit(1)

    print(f"Loading Property GSC queries from {PROPERTY_DUMP.name}")
    prop = load_queries(PROPERTY_DUMP, "property")
    print(f"  {len(prop)} queries")
    print(f"Loading Dentists GSC queries from {DENTISTS_DUMP.name}")
    dent = load_queries(DENTISTS_DUMP, "dentists")
    print(f"  {len(dent)} queries")

    all_q = prop + dent
    print(f"\nTotal raw queries: {len(all_q)}")

    # Bucket: niche-specific vs cross-applicable
    cross = []
    niche_specific_count = {"property-specific": 0, "dentist-specific": 0}
    for r in all_q:
        verdict = is_niche_specific(r["query"])
        if verdict:
            niche_specific_count[verdict] += 1
            continue
        cross.append(r)
    print(f"  niche-specific (filtered out): property={niche_specific_count['property-specific']}, dentist={niche_specific_count['dentist-specific']}")
    print(f"  cross-applicable: {len(cross)}")

    # Tag each cross-applicable query with whether it's already in our seed set.
    print("\nLoading existing generalist seeds for overlap check...")
    seeds_lookup = fetch_existing_seed_keywords()
    print(f"  {len(seeds_lookup)} seed entries")
    for r in cross:
        r["overlaps_existing_seed"] = normalise(r["query"]) in seeds_lookup

    cross_sorted = sorted(cross, key=lambda x: (-x["impressions"], -x["clicks"], x["position"]))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "query", "impressions", "clicks", "ctr", "position",
            "source_niche", "overlaps_existing_seed", "fetched_at",
        ])
        w.writeheader()
        for r in cross_sorted:
            w.writerow(r)
    print(f"Wrote {OUT_CSV}")

    # Summary markdown
    overlap = sum(1 for r in cross if r["overlaps_existing_seed"])
    unclaimed = [r for r in cross_sorted if not r["overlaps_existing_seed"]]
    impr_sum = sum(r["impressions"] for r in cross)
    impr_unclaimed = sum(r["impressions"] for r in unclaimed)

    lines = []
    lines.append("# Cross-niche GSC opportunity (Property + Dentists)")
    lines.append("")
    lines.append(f"_Source dumps: Property ({prop[0]['fetched_at'] if prop else 'n/a'}), Dentists ({dent[0]['fetched_at'] if dent else 'n/a'})_")
    lines.append("")
    lines.append("## Headline")
    lines.append(f"- Total raw queries scraped: **{len(all_q)}**")
    lines.append(f"- Niche-specific (filtered): **{sum(niche_specific_count.values())}** ({niche_specific_count})")
    lines.append(f"- Cross-applicable for generalist site: **{len(cross)}** queries, **{impr_sum:,}** total impressions")
    lines.append(f"- Already covered by an existing seed: **{overlap}**")
    lines.append(f"- Unclaimed by current seed set: **{len(unclaimed)}**, **{impr_unclaimed:,}** impressions")
    lines.append("")
    lines.append("## Top 30 unclaimed cross-applicable queries (by impressions)")
    lines.append("")
    lines.append("| Query | Niche | Impr | Clicks | CTR | Position |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for r in unclaimed[:30]:
        lines.append(f"| {r['query']} | {r['source_niche']} | {r['impressions']} | {r['clicks']} | {r['ctr']:.2%} | {r['position']:.1f} |")
    lines.append("")
    lines.append("_Generated by `pipeline/gsc_cross_niche_analysis.py` — refresh source dumps with `agents/utils/gsc_fetcher.py` for the latest signal._")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
