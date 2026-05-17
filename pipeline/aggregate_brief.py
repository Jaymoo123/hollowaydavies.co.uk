"""
Aggregate all keyword-intelligence outputs into a calibrated content brief
plus a candidate CSV ready for seeding into blog_topics_generalist.

Inputs (all in seo-research/):
  - serper-competitor-titles.csv          (777 rows — top-10 SERPs per seed)
  - serper-competitor-content-map.csv     (683 rows — competitor site pages)
  - serper-gap-ideas.csv                  (45 DeepSeek angle gaps)
  - topic-ideas-llm.csv                   (64 DeepSeek long-tail ideas)
  - autocomplete-candidates.csv           (1,384 Google Autocomplete suggestions)
  - gsc-cross-niche-queries.csv           (103 cross-applicable GSC queries)

Outputs:
  - generalist-content-brief.md           (human-readable brief)
  - generalist-recommended-topics.csv     (deduped candidates ready to seed)
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import httpx

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

from config_supabase import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE, POST_CATEGORIES


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "seo-research"
OUT_MD = RESEARCH / "generalist-content-brief.md"
OUT_CSV = RESEARCH / "generalist-recommended-topics.csv"


def normalise(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def title_case(s: str) -> str:
    acronyms = {"uk", "vat", "mtd", "ir35", "r&d", "paye", "cis", "cgt", "badr",
                "hmrc", "p11d", "p60", "p45", "ai", "ltd", "uae", "itsa", "mvl",
                "s455", "aia", "rdec", "sa100", "sa105", "ct600"}
    words = []
    for w in s.split():
        if w.lower() in acronyms:
            words.append(w.upper())
        elif w.lower() in ("vs", "v"):
            words.append(w.lower())
        else:
            words.append(w[:1].upper() + w[1:].lower() if w else w)
    return " ".join(words).strip()


def fetch_existing():
    """Pull existing seeds for dedupe."""
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = httpx.get(url, headers=headers,
                  params={"select": "topic,primary_keyword,category,content_tier,publish_priority"},
                  timeout=15.0)
    r.raise_for_status()
    return r.json()


def load_csv(path: Path):
    if not path.exists():
        print(f"  WARN: missing {path.name}")
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify_autocomplete(suggestion: str, source_category: str) -> str:
    """Re-classify each autocomplete suggestion into one of POST_CATEGORIES.
    Source_category is the seed's category; usually correct, occasionally not."""
    s = suggestion.lower()
    rules = [
        ("R&D Tax Credits", ["r&d", "research and development", "rdec"]),
        ("VAT and Making Tax Digital", ["vat", "mtd", "making tax digital", "flat rate", "reverse charge"]),
        ("Payroll and PAYE", ["payroll", "paye", "p11d", "p60", "p45", "cis "]),
        ("Director Pay and Dividends", ["dividend", "directors loan", "director's loan", "pay yourself", "trivial benefit", "salary dividend"]),
        ("Incorporation and Structure", ["incorporat", "company formation", "holding company", "family investment company", "sole trader vs", "limited company vs sole trader"]),
        ("Exit and Capital Gains", ["badr", "capital gains", "cgt", "exit", "selling", "members voluntary", "mvl", "business asset disposal"]),
        ("Corporation Tax", ["corporation tax", "ct600", "marginal relief", "annual investment allowance"]),
        ("Sole Trader and Self Employment", ["sole trader", "self employ", "self-employ", "self assessment", "self-assessment"]),
        ("Bookkeeping and Compliance", ["bookkeep", "xero", "quickbooks", "freeagent", "sage", "dext", "confirmation statement", "companies house", "annual accounts"]),
        ("Limited Company Tax", ["limited company", "ltd company", "contractor", "ir35", "off-payroll", "off payroll"]),
    ]
    for cat, kws in rules:
        if any(k in s for k in kws):
            return cat
    return source_category or "Bookkeeping and Compliance"


def cluster_autocomplete(rows):
    """Group near-duplicate suggestions. Same normalised suggestion is one
    cluster. Return list of (canonical_suggestion, frequency, sources)."""
    clusters = defaultdict(lambda: {"sources": set(), "variants": set(), "category": None})
    for r in rows:
        ns = normalise(r["suggestion"])
        c = clusters[ns]
        c["sources"].add(r["source_keyword"])
        c["variants"].add(r["suggestion"])
        # Prefer the most-readable variant (Title Case-ish, longest)
        c["category"] = classify_autocomplete(r["suggestion"], r.get("source_category", ""))
    out = []
    for ns, c in clusters.items():
        canonical = max(c["variants"], key=lambda v: (len(v), v))
        out.append({
            "suggestion": canonical,
            "frequency": len(c["sources"]),
            "source_count": len(c["sources"]),
            "category": c["category"],
        })
    return sorted(out, key=lambda x: (-x["frequency"], x["suggestion"]))


def build_candidate_topics(gap_rows, llm_rows, autocomplete_clusters, gsc_rows, existing_norm):
    """Combine all sources into a single deduped candidate list."""
    candidates = {}  # normalised_topic -> candidate dict

    def add(topic, category, primary_keyword, tier, intent, priority, source, notes=""):
        nt = normalise(topic)
        if nt in existing_norm:
            return  # already seeded
        if nt in candidates:
            candidates[nt]["sources"].add(source)
            candidates[nt]["publish_priority"] = max(candidates[nt]["publish_priority"], priority)
            return
        if category not in POST_CATEGORIES:
            return  # category mismatch, skip
        candidates[nt] = {
            "topic": title_case(topic),
            "category": category,
            "primary_keyword": primary_keyword,
            "content_tier": tier,
            "user_intent": intent,
            "publish_priority": priority,
            "sources": {source},
            "notes": notes,
        }

    # Gap ideas (priority 7, cluster tier, informational)
    for r in gap_rows:
        add(r["title"], r["category"], r.get("primary_keyword", "").strip().lower() or None,
            "cluster", "informational", 7, "gap-ideate-v1", r.get("rationale", ""))

    # Long-tail LLM ideas (priority 6, supporting tier, informational)
    for r in llm_rows:
        add(r["title"], r["category"], r.get("primary_keyword", "").strip().lower() or None,
            "supporting", "informational", 6, "long-tail-v1", r.get("rationale", ""))

    # GSC opportunities — priority 7 if impressions > 5, else 5. Topic = query phrased as a how-to/question.
    for r in gsc_rows:
        try:
            impr = int(r.get("impressions") or 0)
        except ValueError:
            impr = 0
        priority = 7 if impr >= 5 else 5
        q = r["query"].strip()
        # Phrase into a topic title (rough)
        topic = q
        if not q.endswith("?"):
            # Common GSC queries are bare keywords; the title is the question they imply
            topic = title_case(q)
        # Best-effort category guess
        cat = classify_autocomplete(q, "")
        add(topic, cat, q.lower(), "cluster", "informational", priority,
            "gsc-cross-niche-v1", f"GSC {r.get('source_niche')} impr={impr} pos={r.get('position')}")

    # Autocomplete suggestions — supporting tier, priority 5. The autocomplete
    # script already deduped per source_keyword, so each cluster has freq 1
    # here. We rely on the question-quality filter below to pick the top
    # candidates rather than a frequency signal.
    #
    # Keep only suggestions that look like question-format (start with how/what
    # /can/when/why/which/is/do) OR are 4+ word commercial/info phrases. Drop
    # very short (<= 2 words = too generic) and very long (> 12 words =
    # autocomplete junk).
    Q_STARTERS = ("how ", "what ", "when ", "why ", "which ", "can i ", "do i ",
                  "is ", "are ", "should i ", "does ", "where ")
    kept = 0
    for c in autocomplete_clusters:
        s = c["suggestion"].lower().strip()
        word_count = len(s.split())
        is_question = any(s.startswith(q) for q in Q_STARTERS)
        if word_count < 3 or word_count > 12:
            continue
        # Prefer questions; also keep specific informational phrases with explainer suffixes
        if not is_question and not any(suffix in s for suffix in ("explained", "vs", "calculator", " uk", "2026", "deadline", "guide")):
            continue
        topic = title_case(c["suggestion"])
        add(topic, c["category"], c["suggestion"].lower(),
            "supporting", "informational", 5,
            "autocomplete-v1", "from Google Autocomplete")
        kept += 1
    print(f"  autocomplete kept: {kept} of {len(autocomplete_clusters)} (after question/length filter)")

    return list(candidates.values())


def main():
    print("Loading raw research data...")
    gap = load_csv(RESEARCH / "serper-gap-ideas.csv")
    llm = load_csv(RESEARCH / "topic-ideas-llm.csv")
    autocomplete = load_csv(RESEARCH / "autocomplete-candidates.csv")
    gsc = load_csv(RESEARCH / "gsc-cross-niche-queries.csv")
    competitor_titles = load_csv(RESEARCH / "serper-competitor-titles.csv")
    competitor_map = load_csv(RESEARCH / "serper-competitor-content-map.csv")
    print(f"  gap={len(gap)} llm={len(llm)} autocomplete={len(autocomplete)} gsc={len(gsc)} competitor_titles={len(competitor_titles)} competitor_map={len(competitor_map)}")

    print("\nFetching existing seeds from Supabase...")
    existing = fetch_existing()
    existing_norm = set(normalise(e.get("topic") or "") for e in existing) | \
                    set(normalise(e.get("primary_keyword") or "") for e in existing)
    print(f"  {len(existing)} existing seeds")

    print("\nClustering autocomplete suggestions...")
    clusters = cluster_autocomplete(autocomplete)
    print(f"  {len(clusters)} unique clusters")
    multi = [c for c in clusters if c["frequency"] >= 2]
    print(f"  {len(multi)} clusters with frequency >= 2 (cross-seed suggestions)")

    print("\nBuilding candidate topic list...")
    candidates = build_candidate_topics(gap, llm, clusters, gsc, existing_norm)
    print(f"  {len(candidates)} unique new candidates (excluding existing seeds)")

    # By category
    by_cat = Counter(c["category"] for c in candidates)
    by_tier = Counter(c["content_tier"] for c in candidates)
    by_source = Counter(s for c in candidates for s in c["sources"])

    # Write recommended-topics CSV
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "topic", "category", "primary_keyword", "content_tier",
            "user_intent", "publish_priority", "sources", "notes",
        ])
        w.writeheader()
        for c in sorted(candidates, key=lambda x: (-x["publish_priority"], x["category"], x["topic"])):
            row = dict(c)
            row["sources"] = "|".join(sorted(c["sources"]))
            w.writerow(row)
    print(f"\nWrote {OUT_CSV}  ({len(candidates)} candidates)")

    # ===== Build the content brief markdown =====
    lines = []
    lines.append("# Holloway Davies — Calibrated Content Brief")
    lines.append("")
    lines.append("_Generated by `pipeline/aggregate_brief.py` from 79 seeds + Serper + Autocomplete + DeepSeek + GSC cross-niche signals._")
    lines.append("")
    lines.append("## Headline numbers")
    lines.append("")
    lines.append(f"- Seeds already in `blog_topics_generalist`: **{len(existing)}** (17 pillars, 41 clusters, 21 supporting)")
    lines.append(f"- Net-new candidates surfaced this pass: **{len(candidates)}** (after dedupe)")
    lines.append(f"- Raw inputs: {len(gap)} gap angles, {len(llm)} DeepSeek long-tails, {len(autocomplete)} autocomplete suggestions → {len(clusters)} clusters, {len(gsc)} GSC cross-niche queries, {len(competitor_titles)} SERP results, {len(competitor_map)} competitor pages crawled")
    lines.append("")
    lines.append("### Candidate distribution by category")
    lines.append("")
    lines.append("| Category | New candidates |")
    lines.append("|---|---:|")
    for cat in POST_CATEGORIES:
        lines.append(f"| {cat} | {by_cat.get(cat, 0)} |")
    lines.append("")
    lines.append("### Candidate distribution by source")
    lines.append("")
    for src, n in by_source.most_common():
        lines.append(f"- {src}: {n}")
    lines.append("")

    # Top 15 cornerstone — pillars from existing + highest-priority new gap+gsc
    lines.append("## Top 15 cornerstone topics (next-publish priority)")
    lines.append("")
    lines.append("Pillars are already seeded. The 15 below are the highest-leverage cornerstone topics combining the strongest existing pillars with the most strategic new gap ideas.")
    lines.append("")
    existing_pillars = sorted(
        [e for e in existing if e.get("content_tier") == "pillar"],
        key=lambda x: (-(x.get("publish_priority") or 0), x.get("category") or "")
    )
    cornerstones_emitted = 0
    for p in existing_pillars[:10]:
        lines.append(f"1. **[{p.get('category')}]** {p.get('topic')}  _(existing pillar, P{p.get('publish_priority')})_")
        cornerstones_emitted += 1
    # Top 5 new gap/gsc as new cornerstones
    new_cornerstones = sorted(
        [c for c in candidates if c["publish_priority"] >= 7],
        key=lambda x: (-x["publish_priority"], x["category"])
    )[:15 - cornerstones_emitted]
    for c in new_cornerstones:
        lines.append(f"1. **[{c['category']}]** {c['topic']}  _(new, P{c['publish_priority']}, source: {','.join(c['sources'])})_")
    lines.append("")

    # Per-category candidate breakdown
    lines.append("## New candidates by category")
    lines.append("")
    for cat in POST_CATEGORIES:
        cat_candidates = sorted([c for c in candidates if c["category"] == cat],
                                key=lambda x: -x["publish_priority"])
        if not cat_candidates:
            continue
        lines.append(f"### {cat}  ({len(cat_candidates)} candidates)")
        lines.append("")
        for c in cat_candidates[:20]:
            srcs = "|".join(sorted(c["sources"]))
            kw = f"  _kw: {c['primary_keyword']}_" if c["primary_keyword"] else ""
            note = f"  · {c['notes']}" if c.get("notes") else ""
            lines.append(f"- **P{c['publish_priority']}** [{c['content_tier']}] {c['topic']}{kw}{note}")
        if len(cat_candidates) > 20:
            lines.append(f"- _… and {len(cat_candidates) - 20} more in the CSV_")
        lines.append("")

    # GSC opportunity highlights
    lines.append("## GSC cross-niche opportunities (already showing impressions on Property/Dentists)")
    lines.append("")
    lines.append("These queries are already getting impressions on the Property or Dentists GSC. Position 4-6 means the topic already has organic traction — the generalist site is the proper home for them.")
    lines.append("")
    lines.append("| Query | Niche | Impr | Position |")
    lines.append("|---|---|---:|---:|")
    gsc_sorted = sorted(gsc, key=lambda x: (-int(x.get("impressions") or 0), float(x.get("position") or 99)))
    for r in gsc_sorted[:15]:
        lines.append(f"| {r['query']} | {r['source_niche']} | {r.get('impressions')} | {float(r.get('position') or 0):.1f} |")
    lines.append("")

    # Town × service matrix for Phase C programmatic SEO
    lines.append("## Town × service matrix (Phase C programmatic SEO)")
    lines.append("")
    lines.append("Configurable in `niche.config.json` (`seo.service_areas`). Below is the matrix to generate as `/[service]/[town]` pages once the foundational content is in place.")
    lines.append("")
    towns = ["london", "manchester", "birmingham", "leeds", "bristol",
             "glasgow", "edinburgh", "liverpool", "sheffield", "newcastle"]
    services = ["small-business-accountant", "limited-company-accountant",
                "contractor-accountant", "sole-trader-accountant",
                "vat-accountant", "r-and-d-tax-credits", "self-assessment-accountant"]
    lines.append(f"- Towns: {len(towns)} ({', '.join(towns)})")
    lines.append(f"- Services: {len(services)} ({', '.join(services)})")
    lines.append(f"- Total location pages: **{len(towns) * len(services)}** (e.g. `/limited-company-accountant/manchester/`)")
    lines.append("")
    lines.append("Template: each page should include local angle (commute, sector mix, postcode area), a service description, pricing FAQ, and 3-5 local testimonials/case studies.")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")

    # Console summary
    print()
    print("=" * 60)
    print("CANDIDATE DISTRIBUTION BY CATEGORY")
    print("=" * 60)
    for cat in POST_CATEGORIES:
        print(f"  {by_cat.get(cat, 0):>4}  {cat}")
    print(f"\n  TOTAL: {len(candidates)} new candidates ready for seeding")
    print(f"\nReview the brief at: {OUT_MD}")
    print(f"Seed candidates from:  {OUT_CSV}")


if __name__ == "__main__":
    main()
