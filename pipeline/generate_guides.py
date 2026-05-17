"""Generate 4 long-form gated guides (lead magnets) using DeepSeek."""
import json, os, sys
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
OUT = ROOT / "web" / "src" / "app" / "guides" / "[slug]" / "data.ts"

GUIDES = [
    {"slug": "tax-year-end-checklist",
     "title": "The UK Agency Founder's Tax Year-End Checklist 2025/26",
     "teaser": "23 actions to take before 5 April 2026 to optimise your agency's tax position. Covers salary/dividend timing, pension contributions, BADR planning, dividend declarations, and R&D claim preparation.",
     "topic_brief": "A comprehensive year-end tax planning checklist for UK agency founders. 23 specific actions ordered by deadline. Cover salary/dividend timing decisions, pension contributions (£60k AA), dividend declarations before year-end, AIA capital purchases, R&D claim preparation, director's loan repayments before 9-month deadline (S455), BADR planning if exit is on the horizon, ISAs (£20k), CGT annual exemption (£3k) usage. Include specific dates and what to do by when. End with 'how to make this happen' action plan.",
     "category": "Year-end planning"},
    {"slug": "switching-accountants-playbook",
     "title": "How to Switch Accountants: The Agency Founder's 30-Day Playbook",
     "teaser": "A practical 30-day playbook for switching from a generalist accountant to a specialist. Includes the 12-point professional clearance template, the data migration checklist, and the questions to ask before signing with a new firm.",
     "topic_brief": "A practical 30-day playbook for switching accountants. Cover: signs you've outgrown your current accountant, how to evaluate a specialist vs generalist, the professional clearance letter (12 specific items to request), the authorisation codes you need (64-8, HMRC online services), data migration (Xero/QB/FreeAgent backup process), parallel running period, when to switch the year-end filing, what NOT to do mid-year. Include a 30-day timeline with weekly milestones. Include questions to ask before signing with a new accountant.",
     "category": "Switching accountants"},
    {"slug": "dubai-pre-move-checklist",
     "title": "The Pre-Dubai Move Financial Checklist for UK Agency Founders",
     "teaser": "Everything to do in the 12-18 months before you move to Dubai. UK statutory residence test planning, what to do with your UK Ltd, asset disposal timing, UAE entity setup options, banking, and the practical checklist most relocators get wrong.",
     "topic_brief": "A comprehensive 12-18 month pre-Dubai relocation checklist for UK agency founders. Cover: statutory residence test planning (counting days, ties test), what to do with the UK Ltd (keep with UK-resident director, run from Dubai, or close), asset disposal timing (CGT efficient sequencing), pension contributions before leaving (60k AA), ISA contributions before becoming non-resident, UK property decisions, UAE entity options (mainland vs free zone, IFZA/JAFZA/DMCC comparison), UAE golden visa eligibility, banking setup (UK accounts to keep, UAE accounts to open), tax registration in UAE, the 90-day window after moving for various UK filings, NRL scheme if you keep UK rental property. Include a 12-month countdown timeline.",
     "category": "Dubai relocation"},
    {"slug": "first-90-days-post-incorporation",
     "title": "The Agency Founder's First 90 Days Post-Incorporation Guide",
     "teaser": "What to set up in your first 90 days as a UK limited company. Bank account, Xero or FreeAgent, VAT registration timing, payroll if hiring, optimal salary setup, dividend declaration mechanics, and the things most founders forget to do.",
     "topic_brief": "A comprehensive first 90 days guide for newly incorporated UK agency founders. Cover (in order of urgency): business bank account setup, accounting software selection (Xero vs FreeAgent vs QuickBooks for agencies), Companies House registration confirmations, HMRC corporation tax registration (within 3 months), PAYE registration if hiring, payroll setup, VAT registration decision (compulsory at £90k, voluntary below), first dividend mechanics (board minutes, dividend voucher template), director's salary setup (£12,570 at PT to avoid employee NI), employment allowance eligibility, R&D credit eligibility check, professional clearance from any previous accountant. Include a 90-day timeline with week-by-week actions. End with the 5 things agency founders most commonly miss in the first 90 days.",
     "category": "New founders"},
]

SYSTEM = """You write practical long-form guides for UK agency founders.

REQUIREMENTS:
- 2,200 to 2,800 words of body HTML
- Open with a single-paragraph intro stating exactly what the guide covers and who it's for
- Use clear H2 sections (6-10 of them)
- Use H3 subsections where helpful
- Use ordered <ol> or unordered <ul> lists liberally — this is a checklist-style guide
- Use <table> for comparison content where it helps
- Include specific 2025/26 UK figures (BADR 14%, CGT higher 24%, corp tax 19/25, dividend 8.75/33.75/39.35, dividend allowance £500, AIA £1M, VAT £90k, PA £12,570)
- Reference specific HMRC forms (CT600, P11D, SA100, VAT1, P32, 64-8) where relevant
- Reference real software names (Xero, FreeAgent, QuickBooks, Klaviyo, BrightPay) where natural
- UK English (organise, specialise, recognise)
- No AI cliches (unlock, navigate the complex, in today's, leverage, harness, robust, seamless)
- End with a clear "Your action plan" or "Next steps" H2 section with 3-5 numbered actions

OUTPUT: body HTML only. Use <p>, <h2>, <h3>, <ul>, <ol>, <li>, <strong>, <em>, <table>, <thead>, <tbody>, <tr>, <th>, <td>. No <h1>. No frontmatter."""


def generate_guide(client, g):
    prompt = f"""Write the body HTML for: {g['title']}

Brief: {g['topic_brief']}

2,200-2,800 words. Output body HTML only."""
    return client.generate_creative(prompt=prompt, system=SYSTEM, temperature=0.55, max_tokens=4096).strip()


def escape_for_ts(s):
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def main():
    client = DeepSeekClient(api_key=DEEPSEEK_API_KEY)
    entries = []
    for i, g in enumerate(GUIDES, 1):
        try:
            body = generate_guide(client, g)
        except Exception as e:
            print(f"  [{i}/{len(GUIDES)}] {g['slug']}: ERROR {e}")
            continue
        entries.append({**g, "body": body})
        print(f"  [{i}/{len(GUIDES)}] {g['slug']:<40} {len(body)} chars")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// AUTO-GENERATED by pipeline/generate_guides.py",
        "",
        "export type Guide = {",
        "  slug: string;",
        "  title: string;",
        "  teaser: string;",
        "  category: string;",
        "  body: string;",
        "};",
        "",
        "export const GUIDES: Record<string, Guide> = {",
    ]
    for e in entries:
        lines.append(f'  "{e["slug"]}": {{')
        lines.append(f'    slug: "{e["slug"]}",')
        lines.append(f'    title: {json.dumps(e["title"])},')
        lines.append(f'    teaser: {json.dumps(e["teaser"])},')
        lines.append(f'    category: {json.dumps(e["category"])},')
        lines.append(f'    body: `{escape_for_ts(e["body"])}`,')
        lines.append('  },')
    lines.append("};")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {len(entries)} guides to {OUT}")


if __name__ == "__main__":
    main()
