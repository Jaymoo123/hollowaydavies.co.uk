"""
Apply the 65 manually-vetted title rewrite suggestions to the .md files.

Suggestions I REJECTED:
- Any that embedded "(N chars)" literally in the title
- Any that exceeded 60 chars after rewrite
- Any that replaced "agency" with a worse word ("firms")
- Any that dropped the niche signal where it mattered ("for Recruitment Agencies")
- Any that misrepresented the topic ("rates" -> "costs" for dividend tax)
- Any with no change
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "web" / "content" / "blog"
FUND = ROOT / "web" / "content" / "fundamentals"

# (kind, slug, new_metaTitle)
APPLY = [
    ("blog", "13-week-cash-flow-forecast-agency-insolvency", "13-Week Cash Flow Forecast: Stop Agency Insolvency"),
    ("blog", "accounting-software-marketing-agencies", "Best Accounting Software for UK Marketing Agencies 2026"),
    ("blog", "agency-financial-kpis", "8 Financial KPIs Every Agency Founder Must Track"),
    ("blog", "agency-gross-profit-margin-uk-fix", "Agency gross profit margin: why yours is lower & fix"),
    ("blog", "agency-profit-margins-benchmarks", "Agency Profit Margins: UK Benchmarks for 2025"),
    ("blog", "alphabet-share-structure-agency-founder", "Alphabet shares for agency founders: how they work"),
    ("blog", "annual-investment-allowance-agency-equipment-2025-26", "AIA for Agency Equipment: 2025/26 Guide"),
    ("blog", "automate-mtd-itsa-updates-agency", "Automate MTD ITSA quarterly updates for your agency"),
    ("blog", "average-agency-overhead-rate-uk", "Agency Overhead Rate UK: Calculate & Benchmark Yours"),
    ("blog", "average-agency-revenue-per-employee-uk", "Agency revenue per employee: UK benchmark & tips"),
    ("blog", "business-asset-disposal-relief-agency", "BADR for Agency Founders: Keep More of Your Exit Cash"),
    ("blog", "capital-allowances-office-fit-out-agency", "Claim capital allowances on agency office fit-out costs"),
    ("blog", "cash-flow-forecast-creative-agency-uk", "Cash flow forecast creative agency: 7 survival steps"),
    ("blog", "cgt-rates-2025-agency-founder-shares", "CGT 2025: what agency founders must know for share sales"),
    ("blog", "chart-of-accounts-digital-agency-retainer-project-work", "Chart of accounts for digital agencies: retainer setup"),
    ("blog", "cost-incorporate-agency-2025-26", "Agency incorporation costs 2025/26: fees & taxes"),
    ("blog", "digital-records-dividends-mtd-agency-founders", "MTD Digital Records for Dividends: Agency Founder Guide"),
    ("blog", "dividend-allowance-2025-26-agency-directors", "Dividend Allowance 2025/26: Agency Directors' Guide"),
    ("blog", "dividend-vouchers-board-minutes-agency-guide", "Dividend Vouchers & Board Minutes for Your Agency"),
    ("blog", "earn-out-agency-acquisitions-tax", "Earn Out Tax in Agency Deals: Key Reliefs & Traps"),
    ("blog", "employee-ownership-trust-agency-exit", "Sell Your Agency Tax-Free via Employee Ownership Trust"),
    ("blog", "flat-rate-vat-agencies", "Flat Rate VAT for Agencies: Worth It in 2025/26?"),
    ("blog", "hmrc-deadlines-agency-founders", "2025/26 HMRC Deadlines Every Agency Founder Needs"),
    ("blog", "holding-company-agency-group", "Holding Company for Agency: Pros, Cons & Setup Tips"),
    ("blog", "holding-company-vs-trading-company-agency", "Holding Company vs Trading Company: Agency Choice"),
    ("blog", "how-to-choose-accountant-agency", "Choose an Accountant for Your Agency | Expert Guide"),
    ("blog", "how-to-pay-yourself-agency-founder", "Salary vs Dividends: How Agency Founders Pay Themselves"),
    ("blog", "how-to-read-agency-pl", "How to Read Your Agency P&L: Finance 101 for Founders"),
    ("blog", "how-to-value-agency-for-sale", "Agency Valuation UK: Sell Your Agency at Top Price"),
    ("blog", "incorporation-cost-agency-founders", "Incorporation Cost for Agency Founders: Real Numbers"),
    ("blog", "inside-outside-ir35-agency-contractors", "Inside vs Outside IR35: Agency Contractor Rules"),
    ("blog", "invoicing-international-clients-uk-agency-vat", "UK Agency VAT: Invoicing International Clients Guide"),
    ("blog", "late-corporation-tax-penalty-agency-uk", "Agency Late Corp Tax Penalty: Avoid HMRC Fines"),
    ("blog", "mtd-itsa-penalty-agency-founder", "MTD ITSA Penalty: What Agency Founders Must Pay"),
    ("blog", "mtd-mixed-vat-non-vat-agency", "MTD for Mixed VAT & Non-VAT Agencies: UK Guide"),
    ("blog", "mtd-software-xero-agency-reporting", "MTD Xero agency reporting: 6 top software picks"),
    ("blog", "mtd-vat-agencies", "MTD for VAT: Agency Compliance Guide 2025/26"),
    ("blog", "mtd-vat-vs-mtd-itsa-agency-founder-difference", "MTD VAT vs MTD ITSA: Key Differences for Agency Owners"),
    ("blog", "non-uk-resident-director-agency-tax-implications", "Non-UK Director Tax: Agency Implications Explained"),
    ("blog", "optimal-debt-equity-ratio-small-agency-uk", "Optimal Debt-to-Equity Ratio for UK Small Agencies"),
    ("blog", "optimal-salary-dividend-split-agency-directors", "Optimal Salary Dividend Split for Directors 2025/26"),
    ("blog", "p11d-benefits-kind-agency-directors", "P11D Agency Director: What to Report as Benefits in Kind"),
    ("blog", "pay-dividends-retained-profits-directors-loan", "Pay Dividends from Retained Profits: No Director's Loan"),
    ("blog", "paye-dividends-multiple-directors-agency", "PAYE & Dividends for Multiple Agency Directors: How-To"),
    ("blog", "prepare-digital-records-mtd-itsa-agency", "MTD ITSA 2026: Prepare your agency's digital records"),
    ("blog", "questions-to-ask-agency-accountant", "Agency accountant questions to ask before choosing"),
    ("blog", "restructure-agency-group-structure", "Agency Group Restructure: Single to Multi-Company Guide"),
    ("blog", "revenue-vs-billings-recruitment-agency", "Revenue vs Billings for Recruiters: Key Difference"),
    ("blog", "salary-sacrifice-pension-agency-director", "Salary sacrifice pension for agency directors: how-to"),
    ("blog", "section-455-tax-charge-directors-loans-agency", "Section 455 tax charge on director's loans explained"),
    ("blog", "selling-agency-tax-implications", "Selling Your Agency Tax UK: BADR, CGT & Exit Strategy"),
    ("blog", "specialist-vs-general-accountant-agency", "Agency Accountant vs General: Which Do You Need?"),
    ("blog", "spouse-shares-agency-income-splitting", "Spouse Share Income Splitting: Agency Tax Guide"),
    ("blog", "status-determination-statements-agencies", "IR35 SDS agency: what to include in a status statement"),
    ("blog", "tax-efficient-salary-agency-director-2025-26", "Agency Director Tax-Efficient Salary 2025/26: Best Rate"),
    ("blog", "transfer-sole-trader-to-limited-company-mid-year-agency", "Transfer Sole Trader to Ltd Co Mid-Year: Agency Tax Tips"),
    ("blog", "uk-agency-founder-dubai-tax-obligations", "Dubai-Based UK Agency Founder: Your Tax Duties"),
    ("blog", "value-creative-agency-revenue-retainers", "Value Creative Agency Retainer Revenue: Exit Guide"),
    ("blog", "vat-client-entertainment-agency-uk", "VAT on Client Meals & Agency Entertainment: UK Rules"),
    ("blog", "vat-cross-border-digital-advertising-agency", "UK agency VAT on cross-border digital ads: guide"),
    ("blog", "vat-digital-products-agency-website-uk", "VAT rules for digital products: UK agency guide"),
    ("blog", "what-does-agency-accountant-do", "Agency Accountant Role: What They Do for UK Founders"),
    ("fundamental", "agency-tax-compliance-complete-guide", "Agency Tax Compliance UK: Key Steps for Founders"),
    ("fundamental", "choosing-agency-accountant-pillar", "Agency Accountant Guide: How to Choose the Right One"),
    ("fundamental", "mtd-agency-founder-pillar", "MTD for Agency Founders: ITSA, VAT & Deadlines 2025/26"),
    ("fundamental", "selling-your-agency-pillar", "Selling Your Agency Tax Guide: BADR & Earn-Outs"),
]


def main():
    applied = skipped = errors = 0
    for kind, slug, new_title in APPLY:
        if len(new_title) > 60:
            print(f"SKIP {slug}: suggested {len(new_title)} chars > 60")
            skipped += 1
            continue
        d = BLOG if kind == "blog" else FUND
        path = d / f"{slug}.md"
        if not path.exists():
            print(f"MISS {kind}/{slug}: file not found")
            errors += 1
            continue
        text = path.read_text(encoding="utf-8")
        new_title_escaped = new_title.replace('"', '\\"')
        new_text, n = re.subn(
            r'^(metaTitle:\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{new_title_escaped}"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
        if n == 0:
            print(f"FAIL {slug}: metaTitle field not matched")
            errors += 1
            continue
        path.write_text(new_text, encoding="utf-8")
        print(f"OK   {slug:<55} ({len(new_title)}) {new_title}")
        applied += 1
    print(f"\nApplied: {applied}  Skipped: {skipped}  Errors: {errors}")


if __name__ == "__main__":
    main()
