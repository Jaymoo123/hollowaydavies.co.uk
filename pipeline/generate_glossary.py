"""Generate 25 glossary entries for UK agency founders using DeepSeek.

Output: web/src/app/glossary/[slug]/data.ts as a structured TypeScript module.
Entries are hand-curated for accuracy and use 2025/26 figures.
"""
import json
import os
import re
import sys
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
OUT = ROOT / "web" / "src" / "app" / "glossary" / "[slug]" / "data.ts"

# 25 terms with metadata. Each will get a definition via DeepSeek.
TERMS = [
    {"slug": "badr", "term": "BADR (Business Asset Disposal Relief)", "category": "Tax", "primary_kw": "what is BADR"},
    {"slug": "ir35", "term": "IR35 (Off-Payroll Working Rules)", "category": "Contractors", "primary_kw": "what is IR35"},
    {"slug": "mtd-itsa", "term": "MTD ITSA (Making Tax Digital for Income Tax)", "category": "Compliance", "primary_kw": "what is MTD ITSA"},
    {"slug": "mtd", "term": "MTD (Making Tax Digital)", "category": "Compliance", "primary_kw": "what is MTD"},
    {"slug": "section-455", "term": "Section 455 (Director's Loan Tax Charge)", "category": "Tax", "primary_kw": "what is Section 455"},
    {"slug": "aia", "term": "AIA (Annual Investment Allowance)", "category": "Tax", "primary_kw": "what is AIA"},
    {"slug": "r-and-d-tax-credits", "term": "R&D Tax Credits", "category": "Tax", "primary_kw": "what are R&D tax credits"},
    {"slug": "corporation-tax", "term": "Corporation Tax", "category": "Tax", "primary_kw": "UK corporation tax explained"},
    {"slug": "personal-allowance", "term": "Personal Allowance", "category": "Tax", "primary_kw": "UK personal allowance"},
    {"slug": "dividend-allowance", "term": "Dividend Allowance", "category": "Tax", "primary_kw": "UK dividend allowance"},
    {"slug": "flat-rate-vat", "term": "Flat Rate VAT Scheme", "category": "VAT", "primary_kw": "what is flat rate VAT"},
    {"slug": "vat-threshold", "term": "VAT Registration Threshold", "category": "VAT", "primary_kw": "UK VAT threshold"},
    {"slug": "national-insurance", "term": "National Insurance Contributions (NI)", "category": "Tax", "primary_kw": "UK national insurance explained"},
    {"slug": "paye", "term": "PAYE (Pay As You Earn)", "category": "Tax", "primary_kw": "what is PAYE"},
    {"slug": "p11d", "term": "P11D (Benefits in Kind Form)", "category": "Compliance", "primary_kw": "what is a P11D"},
    {"slug": "sa100", "term": "SA100 (Self Assessment Tax Return)", "category": "Compliance", "primary_kw": "what is SA100"},
    {"slug": "ct600", "term": "CT600 (Corporation Tax Return)", "category": "Compliance", "primary_kw": "what is CT600"},
    {"slug": "cis", "term": "CIS (Construction Industry Scheme)", "category": "Compliance", "primary_kw": "what is CIS"},
    {"slug": "eis-seis", "term": "EIS and SEIS (Investment Tax Reliefs)", "category": "Tax", "primary_kw": "EIS SEIS explained"},
    {"slug": "capital-gains-tax", "term": "Capital Gains Tax (CGT)", "category": "Tax", "primary_kw": "UK capital gains tax"},
    {"slug": "holding-company", "term": "Holding Company", "category": "Structure", "primary_kw": "what is a holding company"},
    {"slug": "spv", "term": "SPV (Special Purpose Vehicle)", "category": "Structure", "primary_kw": "what is an SPV"},
    {"slug": "ebitda", "term": "EBITDA", "category": "Finance", "primary_kw": "what is EBITDA"},
    {"slug": "gross-margin", "term": "Gross Margin", "category": "Finance", "primary_kw": "what is gross margin"},
    {"slug": "utilisation-rate", "term": "Utilisation Rate", "category": "Finance", "primary_kw": "what is agency utilisation rate"},
]

SYSTEM = """You write concise, accurate UK accountancy glossary entries for agency founders.

REQUIREMENTS:
- 250-350 words per entry
- Open with a single-sentence plain-English definition
- Then explain how it works for UK agency founders specifically
- Include current 2025/26 figures where relevant
- Reference correct UK rates (BADR 14% for 2025/26, rising to 18% from 6 April 2026; corporation tax 19% small / 25% main; CGT 18%/24%; dividend tax 8.75%/33.75%/39.35%; dividend allowance £500; AIA £1M; VAT threshold £90k from April 2024; PA £12,570)
- Plain English, no jargon without explanation
- UK English (specialise, organise, recognise)
- No AI cliches (unlock, navigate the complex, in today's, leverage, harness)
- No em-dashes
- End with a single short paragraph: "When this matters for agency founders"
- Output ONLY the body HTML — no <html>, no frontmatter, no title heading (the page renders the term name separately)
- Use <p>, <ul>/<li>, <strong>. No <h1> or <h2>.
"""


def generate_entry(client, term):
    prompt = f"""Write the definition body for: {term['term']}

Category: {term['category']}
Primary keyword to target naturally: {term['primary_kw']}

Output the body HTML only. Start with a <p> opening definition. 250-350 words."""
    out = client.generate_creative(prompt=prompt, system=SYSTEM, temperature=0.5, max_tokens=900)
    # Strip any leading/trailing markdown or non-HTML
    out = out.strip()
    # Remove any markdown headings that slipped in
    out = re.sub(r"^#+ .*\n", "", out, flags=re.MULTILINE)
    return out


def escape_for_ts(s):
    """Escape backticks and ${ for safe interpolation in TS template literals."""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def main():
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
    print(f"Generating {len(TERMS)} glossary entries...")

    entries = []
    for i, t in enumerate(TERMS, 1):
        try:
            body = generate_entry(client, t)
        except Exception as e:
            print(f"  [{i}/{len(TERMS)}] {t['slug']}: ERROR {e}")
            continue
        entries.append({**t, "body": body})
        print(f"  [{i:>2}/{len(TERMS)}] {t['slug']:<30} {len(body)} chars")

    # Write to TypeScript module
    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// AUTO-GENERATED by pipeline/generate_glossary.py",
        "// Edit definitions in this file; do not regenerate without backing up changes.",
        "",
        "export type GlossaryEntry = {",
        "  slug: string;",
        "  term: string;",
        "  category: string;",
        "  primary_kw: string;",
        "  body: string;",
        "};",
        "",
        "export const GLOSSARY: Record<string, GlossaryEntry> = {",
    ]
    for e in entries:
        lines.append(f'  "{e["slug"]}": {{')
        lines.append(f'    slug: "{e["slug"]}",')
        lines.append(f'    term: {json.dumps(e["term"])},')
        lines.append(f'    category: {json.dumps(e["category"])},')
        lines.append(f'    primary_kw: {json.dumps(e["primary_kw"])},')
        lines.append(f'    body: `{escape_for_ts(e["body"])}`,')
        lines.append('  },')
    lines.append("};")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {len(entries)} entries to {OUT}")


if __name__ == "__main__":
    main()
