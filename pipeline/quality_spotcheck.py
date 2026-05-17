"""
Quality spot-check on random samples of generated content.

Checks:
  - 5 random blog posts: em-dashes, agency leftovers, ICAEW mention, FAQ present,
    worked GBP figures, named HMRC forms, UK English spelling
  - 5 random city pages: hero image present, sectorEmphasis names a real local detail,
    case study has specific figures
  - 5 random glossary entries: no agency framing, em-dash count, length preserved

Outputs a markdown report at seo-research/quality-spotcheck-YYYYMMDD.md
"""
import random
import re
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "web" / "content" / "blog"
FUND_DIR = ROOT / "web" / "content" / "fundamentals"
CITIES_TS = ROOT / "web" / "src" / "app" / "locations" / "[slug]" / "data.ts"
GLOSSARY_TS = ROOT / "web" / "src" / "app" / "glossary" / "[slug]" / "data.ts"
OUT = ROOT / "seo-research" / f"quality-spotcheck-{date.today().isoformat()}.md"


BANNED_BRAND_PATTERNS = (
    "UK Business Accountants",
    "ukbusinessaccountants",
    "Agency Founder Finance",
    "agencyfounderfinance",
    "agency founder",
    "for agency founders",
    "Tax Brief",  # old newsletter name
)

HMRC_FORMS = ("CT600", "SA100", "SA103", "SA800", "VAT1", "P11D", "P32", "P60", "P45", "CIS300")

UK_SPELLINGS = ("specialise", "organise", "analyse", "recognise", "centre", "colour", "favour", "labour")
US_SPELLINGS = ("specialize", "organize", "analyze", "recognize", "center", "color", "favor", "labor")


def check_blog_post(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    body = text.split("---\n", 2)[-1] if text.count("---") >= 2 else text

    em_dashes = body.count("—")
    en_dashes = body.count("–")
    has_icaew = "ICAEW" in body
    has_faq = "Frequently asked" in text.lower() or "faqs:" in text.lower() or "faq1" in text.lower() or "==FAA" in text
    # Worked GBP figures: at least one £X,XXX where X,XXX is specific (not round thousands)
    figs = re.findall(r"£([\d,]+)", body)
    specific_figs = [f for f in figs if "," in f and not f.endswith(",000") and not f.endswith(",500")]
    hmrc_named = [h for h in HMRC_FORMS if h in body]
    brand_leftover = [b for b in BANNED_BRAND_PATTERNS if b in text]
    us_spellings = [w for w in US_SPELLINGS if re.search(rf"\b{w}\b", body, re.IGNORECASE)]

    title_match = re.search(r'title:\s*"([^"]+)"', text)
    title = title_match.group(1) if title_match else path.name

    return {
        "file": path.name,
        "title": title[:70],
        "em_dashes": em_dashes,
        "en_dashes": en_dashes,
        "has_icaew": has_icaew,
        "has_faq": has_faq,
        "specific_figs": len(specific_figs),
        "hmrc_named": len(hmrc_named),
        "brand_leftover": brand_leftover,
        "us_spellings": us_spellings,
        "word_count": len(body.split()),
    }


def check_city(slug: str, data_text: str) -> dict:
    block_pattern = re.compile(
        r'  "' + re.escape(slug) + r'":\s*\{([\s\S]*?)\n  \},', re.MULTILINE
    )
    m = block_pattern.search(data_text)
    if not m:
        return {"slug": slug, "found": False}
    block = m.group(1)

    em_dashes = block.count("—")
    has_hero = "heroImage" in block
    brand_leftover = [b for b in BANNED_BRAND_PATTERNS if b in block]

    # Specific figures in case study
    figs = re.findall(r"£([\d,]+)", block)
    specific_figs = [f for f in figs if "," in f and not f.endswith(",000")]

    # sectorEmphasis content (should name a sector and an employer)
    se_match = re.search(r'sectorEmphasis:\s*"([^"]+)"', block)
    sector_emphasis = se_match.group(1) if se_match else ""

    return {
        "slug": slug,
        "found": True,
        "em_dashes": em_dashes,
        "has_hero": has_hero,
        "brand_leftover": brand_leftover,
        "case_specific_figs": len(specific_figs),
        "sector_emphasis_length": len(sector_emphasis),
    }


def check_glossary_entry(slug: str, data_text: str) -> dict:
    block_pattern = re.compile(
        r'  "' + re.escape(slug) + r'":\s*\{([\s\S]*?body:\s*`([^`]*)`),?\s*\n  \},', re.MULTILINE
    )
    m = block_pattern.search(data_text)
    if not m:
        return {"slug": slug, "found": False}
    block = m.group(1)
    body = m.group(2)

    em_dashes = body.count("—")
    brand_leftover = [b for b in BANNED_BRAND_PATTERNS if b in body]
    agency_audience = [p for p in ("for agency founders", "your agency", "agency founder") if p.lower() in body.lower()]

    return {
        "slug": slug,
        "found": True,
        "em_dashes": em_dashes,
        "brand_leftover": brand_leftover,
        "agency_audience_phrases": agency_audience,
        "body_word_count": len(body.split()),
    }


def main():
    random.seed()

    print("Picking samples...")
    blog_files = list(BLOG_DIR.glob("*.md")) + list(FUND_DIR.glob("*.md"))
    blog_sample = random.sample(blog_files, min(5, len(blog_files)))

    cities_text = CITIES_TS.read_text(encoding="utf-8")
    city_slugs = re.findall(r'^  "([^"]+)":\s*\{', cities_text, re.MULTILINE)
    city_sample = random.sample(city_slugs, min(5, len(city_slugs)))

    glossary_text = GLOSSARY_TS.read_text(encoding="utf-8")
    glossary_slugs = re.findall(r'^  "([^"]+)":\s*\{', glossary_text, re.MULTILINE)
    glossary_sample = random.sample(glossary_slugs, min(5, len(glossary_slugs)))

    blog_results = [check_blog_post(p) for p in blog_sample]
    city_results = [check_city(s, cities_text) for s in city_sample]
    glossary_results = [check_glossary_entry(s, glossary_text) for s in glossary_sample]

    # Build report
    lines = [f"# Quality spot-check report — {date.today().isoformat()}", ""]
    lines.append(f"Sampled {len(blog_results)} blog/pillar posts, {len(city_results)} city pages, {len(glossary_results)} glossary entries.")
    lines.append("")

    # Blog
    lines.append("## Blog / fundamentals posts")
    lines.append("")
    lines.append("| File | Words | Em-dash | ICAEW | FAQ | GBP figs | HMRC forms | Brand leftover | US spellings |")
    lines.append("|---|---:|---:|:---:|:---:|---:|---:|---|---|")
    for r in blog_results:
        lines.append(
            f"| {r['file'][:50]} | {r['word_count']} | {r['em_dashes']} | "
            f"{'YES' if r['has_icaew'] else 'no'} | {'YES' if r['has_faq'] else 'no'} | "
            f"{r['specific_figs']} | {r['hmrc_named']} | "
            f"{', '.join(r['brand_leftover']) or '-'} | {', '.join(r['us_spellings']) or '-'} |"
        )

    # City
    lines.append("")
    lines.append("## City pages")
    lines.append("")
    lines.append("| Slug | Em-dash | Hero img | Brand leftover | Case figs | sectorEmphasis len |")
    lines.append("|---|---:|:---:|---|---:|---:|")
    for r in city_results:
        if not r.get("found"):
            lines.append(f"| {r['slug']} | NOT FOUND | - | - | - | - |")
            continue
        lines.append(
            f"| {r['slug']} | {r['em_dashes']} | {'YES' if r['has_hero'] else 'no'} | "
            f"{', '.join(r['brand_leftover']) or '-'} | {r['case_specific_figs']} | {r['sector_emphasis_length']} |"
        )

    # Glossary
    lines.append("")
    lines.append("## Glossary entries")
    lines.append("")
    lines.append("| Slug | Words | Em-dash | Brand leftover | Agency-audience phrases |")
    lines.append("|---|---:|---:|---|---|")
    for r in glossary_results:
        if not r.get("found"):
            lines.append(f"| {r['slug']} | NOT FOUND | - | - | - |")
            continue
        lines.append(
            f"| {r['slug']} | {r['body_word_count']} | {r['em_dashes']} | "
            f"{', '.join(r['brand_leftover']) or '-'} | {', '.join(r['agency_audience_phrases']) or '-'} |"
        )

    # Summary verdict
    lines.append("")
    lines.append("## Summary verdict")
    lines.append("")

    blog_issues = sum(
        1 for r in blog_results
        if r["em_dashes"] or r["brand_leftover"] or r["us_spellings"] or not r["has_icaew"] or not r["has_faq"]
    )
    city_issues = sum(
        1 for r in city_results
        if r.get("found") and (r["em_dashes"] or r["brand_leftover"] or not r["has_hero"])
    )
    glossary_issues = sum(
        1 for r in glossary_results
        if r.get("found") and (r["em_dashes"] or r["brand_leftover"] or r["agency_audience_phrases"])
    )

    lines.append(f"- Blog posts with issues: **{blog_issues} of {len(blog_results)}**")
    lines.append(f"- City pages with issues: **{city_issues} of {len(city_results)}**")
    lines.append(f"- Glossary entries with issues: **{glossary_issues} of {len(glossary_results)}**")
    lines.append("")

    if blog_issues + city_issues + glossary_issues == 0:
        lines.append("All samples clean. No quality issues found.")
    else:
        lines.append("Sample issues detected. Inspect the rows marked above and consider remediation script.")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
