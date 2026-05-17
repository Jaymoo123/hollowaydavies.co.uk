"""
Generate downloadable PDF templates for /templates.

Each template is a single-page, brand-consistent A4 PDF that a UK business
owner can fill in. Layout: off-white background, orange accent header,
ink-coloured body type, Helvetica throughout (Geist is not licensed for PDF
embedding without further work; Helvetica reads close enough).

Templates produced:
  invoice-template.pdf            UK VAT-aware invoice template
  expense-tracker.pdf             Monthly expenses log
  year-end-checklist.pdf          Limited company year-end tax checklist
  mtd-itsa-checklist.pdf          MTD ITSA quarterly preparation checklist
  mileage-log.pdf                 Business mileage log
  dividend-voucher.pdf            UK dividend voucher template
  board-minutes.pdf               Single-director board minutes template

Outputs to: web/public/templates/
"""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "web" / "public" / "templates"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette
ORANGE = colors.HexColor("#f97316")
ORANGE_LIGHT = colors.HexColor("#fed7aa")
INK = colors.HexColor("#0a0a0a")
INK_SOFT = colors.HexColor("#525252")
SURFACE = colors.HexColor("#fafaf7")
HAIRLINE = colors.HexColor("#e5e5e5")


def header_footer(canvas, doc, title):
    """Draw the orange accent bar + Holloway Davies wordmark on every page."""
    canvas.saveState()
    # Top orange band
    canvas.setFillColor(ORANGE)
    canvas.rect(0, A4[1] - 8, A4[0], 8, fill=1, stroke=0)
    # Brand
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(15 * mm, A4[1] - 22, "HOLLOWAY DAVIES")
    canvas.setFillColor(INK_SOFT)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(15 * mm, A4[1] - 32, title)
    # Footer
    canvas.setFillColor(INK_SOFT)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(15 * mm, 15 * mm, "Holloway Davies, ICAEW chartered accountants. hollowaydavies.co.uk")
    canvas.drawRightString(A4[0] - 15 * mm, 15 * mm, "Free template, share freely. Not personal tax advice.")
    # Bottom orange line
    canvas.setStrokeColor(ORANGE)
    canvas.setLineWidth(1.5)
    canvas.line(15 * mm, 22 * mm, A4[0] - 15 * mm, 22 * mm)
    canvas.restoreState()


def styles():
    s = getSampleStyleSheet()
    base = ParagraphStyle("BodyBase", parent=s["BodyText"], fontName="Helvetica",
                          fontSize=9.5, leading=13, textColor=INK)
    h1 = ParagraphStyle("H1", parent=s["Heading1"], fontName="Helvetica-Bold",
                        fontSize=22, leading=26, textColor=INK, spaceAfter=4)
    h2 = ParagraphStyle("H2", parent=s["Heading2"], fontName="Helvetica-Bold",
                        fontSize=12, leading=16, textColor=INK, spaceBefore=8, spaceAfter=4)
    intro = ParagraphStyle("Intro", parent=base, fontSize=10, leading=14,
                           textColor=INK_SOFT)
    small = ParagraphStyle("Small", parent=base, fontSize=8, leading=11,
                           textColor=INK_SOFT)
    return base, h1, h2, intro, small


def build_invoice():
    base, h1, h2, intro, small = styles()
    story = [
        Paragraph("Invoice template", h1),
        Paragraph("UK VAT-aware invoice. Replace the [bracketed] placeholders.", intro),
        Spacer(1, 8),
    ]
    # Header table: From / To
    header_data = [
        [Paragraph("<b>From</b>", base), Paragraph("<b>To</b>", base)],
        [Paragraph("[Your business name]<br/>[Address line 1]<br/>[Postcode]<br/>VAT no. [if registered]<br/>Co. reg. [if Ltd]", base),
         Paragraph("[Client business name]<br/>[Address line 1]<br/>[Postcode]", base)],
    ]
    t = Table(header_data, colWidths=[85 * mm, 85 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, HAIRLINE),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Invoice metadata
    meta = [
        ["Invoice number", "[001]", "Date issued", "[DD MMM YYYY]"],
        ["Due date", "[DD MMM YYYY]", "Payment terms", "[Net 30]"],
    ]
    t = Table(meta, colWidths=[35 * mm, 50 * mm, 35 * mm, 50 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (0, -1), SURFACE),
        ("BACKGROUND", (2, 0), (2, -1), SURFACE),
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, HAIRLINE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, HAIRLINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # Line items table
    items = [
        ["Description", "Qty", "Unit price", "Net amount"],
        ["[Description of work or product]", "1", "£0.00", "£0.00"],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "Subtotal", "£0.00"],
        ["", "", "VAT @ 20%", "£0.00"],
        ["", "", "Total due", "£0.00"],
    ]
    t = Table(items, colWidths=[85 * mm, 20 * mm, 35 * mm, 30 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LINEBELOW", (0, 0), (-1, 4), 0.4, HAIRLINE),
        ("FONTNAME", (2, 7), (3, 7), "Helvetica-Bold"),
        ("BACKGROUND", (2, 7), (3, 7), ORANGE_LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Payment details</b>", base))
    story.append(Paragraph("Account name: [Your business name]<br/>Sort code: [00-00-00] · Account number: [12345678]<br/>Reference: invoice number above", base))
    story.append(Spacer(1, 12))
    story.append(Paragraph("If you are not VAT-registered, delete the VAT row above and rename Subtotal to Total. Sole traders should add: \"This invoice is issued by [name] trading as [business name].\"", small))
    return story


def build_expense_tracker():
    base, h1, h2, intro, small = styles()
    story = [
        Paragraph("Monthly expense tracker", h1),
        Paragraph("Use one sheet per month. Reconcile against bank statements at month-end and then carry totals into your bookkeeping software.", intro),
        Spacer(1, 8),
    ]
    rows = [["Date", "Description", "Category", "Net", "VAT", "Total", "Method"]]
    for _ in range(22):
        rows.append([""] * 7)
    rows.append(["", "", "Totals", "£0.00", "£0.00", "£0.00", ""])
    t = Table(rows, colWidths=[22*mm, 60*mm, 28*mm, 20*mm, 18*mm, 20*mm, 18*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (3, 0), (5, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.3, HAIRLINE),
        ("BACKGROUND", (0, -1), (-1, -1), ORANGE_LIGHT),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Common categories (HMRC-aligned):</b> Office costs · Travel · Subsistence · Equipment (under £200) · Software & subscriptions · Professional services · Marketing · Phone & internet · Bank charges · Use of home as office (£6/wk simplified)", small))
    return story


def build_year_end_checklist():
    base, h1, h2, intro, small = styles()
    story = [
        Paragraph("Limited company year-end tax checklist", h1),
        Paragraph("Use this checklist in the 4-6 weeks before your company year-end. Tick each item once it is done. Specific deadlines and rates are 2025/26 figures.", intro),
        Spacer(1, 10),
    ]
    sections = [
        ("Before year-end (4-6 weeks out)", [
            "Calculate projected taxable profit for the year",
            "Review director salary: are you at £12,570 (PA + primary NI threshold)?",
            "Review dividend extraction against personal allowance and basic-rate band",
            "Consider employer pension contribution before year-end (corporation tax deductible, no NI)",
            "Check Annual Investment Allowance position (£1M annual limit)",
            "Identify any R&D-qualifying expenditure for claim preparation",
            "Confirm Employment Allowance entitlement (multi-employee Ltds only)",
        ]),
        ("Before year-end (final week)", [
            "Pay or accrue staff bonuses and pension contributions",
            "Pay any director loan account balances over £10,000 to avoid BIK and S455",
            "Issue dividend vouchers and pass board resolutions (date BEFORE year-end)",
            "Make any capital purchases planned for the year (laptops, equipment)",
            "Review work-in-progress and accrued income for the cut-off",
        ]),
        ("After year-end (within 9 months)", [
            "File annual accounts at Companies House",
            "File CT600 corporation tax return with HMRC",
            "Pay corporation tax liability (9 months and 1 day after year-end)",
            "Complete and file confirmation statement (within 14 days of due date)",
            "File P11D for any directors' benefits in kind (by 6 July)",
        ]),
    ]
    for title, items in sections:
        story.append(Paragraph(title, h2))
        for it in items:
            story.append(Paragraph(f"&#9744; &nbsp;&nbsp;{it}", base))
    story.append(Spacer(1, 12))
    story.append(Paragraph("This is editorial guidance, not personal tax advice. For a year-end review specific to your company, book a free 30-minute call at hollowaydavies.co.uk/contact.", small))
    return story


def build_mtd_itsa_checklist():
    base, h1, h2, intro, small = styles()
    story = [
        Paragraph("MTD for Income Tax (ITSA): quarterly preparation checklist", h1),
        Paragraph("Mandatory from 6 April 2026 for sole traders and landlords with qualifying income over £50,000. From April 2027 for £30,000+. From April 2028 for £20,000+. Use this checklist each quarter.", intro),
        Spacer(1, 10),
    ]
    sections = [
        ("Pre-MTD setup (one-off)", [
            "Confirm your qualifying income for the prior tax year",
            "Choose HMRC-recognised software (Xero, FreeAgent, QuickBooks, GoSimpleTax)",
            "Sign up via gov.uk for MTD for Income Tax",
            "Connect your software to HMRC",
            "Set up digital records of all income and expenses (no paper-only records)",
            "If you use a spreadsheet, install MTD-compatible bridging software",
        ]),
        ("Each quarter (within one month of the quarter end)", [
            "Reconcile bank account against software for the quarter",
            "Categorise all income transactions",
            "Categorise all expense transactions",
            "Resolve any uncategorised entries",
            "Run the quarterly summary report",
            "Submit the quarterly update to HMRC via your software",
            "Save a PDF copy of the submission confirmation",
        ]),
        ("End-of-period statement (after tax year)", [
            "Make any accounting adjustments (accruals, prepayments, depreciation)",
            "Confirm allowable vs disallowable expenses",
            "Submit end-of-period statement (EOPS) for each income source",
            "Submit final declaration",
            "Pay any tax due by 31 January",
        ]),
    ]
    for title, items in sections:
        story.append(Paragraph(title, h2))
        for it in items:
            story.append(Paragraph(f"&#9744; &nbsp;&nbsp;{it}", base))
    story.append(Spacer(1, 12))
    story.append(Paragraph("MTD ITSA penalties use a points-based system. Late submissions accrue points; once a threshold is reached, a £200 penalty applies plus £200 for each subsequent late submission.", small))
    return story


def build_mileage_log():
    base, h1, h2, intro, small = styles()
    story = [
        Paragraph("Business mileage log", h1),
        Paragraph("Use HMRC's Approved Mileage Allowance Payment rates: 45p per mile for the first 10,000 business miles in the tax year, 25p thereafter for cars and vans. Motorcycles: 24p. Bicycles: 20p.", intro),
        Spacer(1, 10),
    ]
    rows = [["Date", "From", "To", "Purpose", "Miles", "Rate", "Claim"]]
    for _ in range(22):
        rows.append([""] * 7)
    rows.append(["", "", "", "Totals", "0", "", "£0.00"])
    t = Table(rows, colWidths=[20*mm, 35*mm, 35*mm, 45*mm, 15*mm, 15*mm, 20*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (4, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.3, HAIRLINE),
        ("BACKGROUND", (0, -1), (-1, -1), ORANGE_LIGHT),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Eligible business mileage:</b> visits to clients or suppliers, travel between work sites, training and conferences. NOT commuting between home and a permanent workplace.", small))
    return story


def build_dividend_voucher():
    base, h1, h2, intro, small = styles()
    story = [
        Paragraph("Dividend voucher template", h1),
        Paragraph("UK Companies Act 2006 requires a written dividend voucher for every dividend paid. Issue one per shareholder per dividend payment. Keep with company records for at least 6 years.", intro),
        Spacer(1, 12),
    ]
    rows = [
        ["Company name", "[Your Company Ltd]"],
        ["Company number", "[12345678]"],
        ["Registered office", "[Address line 1, Postcode]"],
        ["Date of dividend declaration", "[DD MMM YYYY]"],
        ["Date of payment", "[DD MMM YYYY]"],
        ["", ""],
        ["Shareholder name", "[Full legal name]"],
        ["Shareholder address", "[Address line 1, Postcode]"],
        ["Class of shares held", "[e.g. Ordinary £1 shares]"],
        ["Number of shares held", "[e.g. 100]"],
        ["Dividend per share", "[£0.00]"],
        ["Total dividend amount", "[£0.00]"],
    ]
    t = Table(rows, colWidths=[70 * mm, 100 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (0, -1), SURFACE),
        ("GRID", (0, 0), (-1, -1), 0.3, HAIRLINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Declaration</b>", base))
    story.append(Paragraph("The directors of [Your Company Ltd] confirm that this dividend has been declared from distributable reserves available at the date of declaration above. The dividend is paid in proportion to the shareholdings shown.", base))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Signed (director): _________________________________  Date: _____________", base))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Dividends must be paid from distributable reserves (accumulated realised profits less losses and previous distributions). A dividend paid without sufficient reserves is unlawful and recoverable from the shareholders.", small))
    return story


def build_board_minutes():
    base, h1, h2, intro, small = styles()
    story = [
        Paragraph("Board minutes (interim dividend declaration)", h1),
        Paragraph("Template for a single-director or multi-director limited company minuting a dividend declaration. Adapt for other resolutions (salary changes, bonus payments, capital purchases).", intro),
        Spacer(1, 12),
        Paragraph("<b>[Your Company Ltd] · Company number [12345678]</b>", base),
        Paragraph("Minutes of a meeting of the directors held at [registered office] on [DD MMM YYYY] at [time].", base),
        Spacer(1, 10),
        Paragraph("<b>Present</b>", h2),
        Paragraph("[Director name 1] (chair)<br/>[Director name 2, if applicable]", base),
        Spacer(1, 4),
        Paragraph("<b>Quorum</b>", h2),
        Paragraph("It was noted that a quorum was present and the meeting was duly constituted.", base),
        Spacer(1, 4),
        Paragraph("<b>Distributable reserves</b>", h2),
        Paragraph("The directors reviewed the management accounts as at [date] which show distributable reserves of £[amount]. The directors are satisfied that sufficient distributable profits are available to support the proposed interim dividend.", base),
        Spacer(1, 4),
        Paragraph("<b>Resolution</b>", h2),
        Paragraph("IT WAS RESOLVED that an interim dividend of £[per-share amount] per [class] share be declared and paid on [payment date] to shareholders on the register on [record date]. Total dividend: £[total amount].", base),
        Spacer(1, 4),
        Paragraph("<b>Dividend vouchers</b>", h2),
        Paragraph("Dividend vouchers will be issued to each shareholder and copies retained with the company records.", base),
        Spacer(1, 20),
        Paragraph("There being no further business, the meeting closed.", base),
        Spacer(1, 18),
        Paragraph("Signed: _________________________________  Date: _____________", base),
        Paragraph("[Director name 1], Chair", small),
        Spacer(1, 12),
        Paragraph("These minutes evidence the board resolution and must be retained with the company's statutory books. Dividends paid without a board resolution can be challenged as unlawful distributions.", small),
    ]
    return story


TEMPLATES = [
    ("invoice-template", "Invoice template", build_invoice),
    ("expense-tracker", "Monthly expense tracker", build_expense_tracker),
    ("year-end-checklist", "Year-end tax checklist", build_year_end_checklist),
    ("mtd-itsa-checklist", "MTD for Income Tax checklist", build_mtd_itsa_checklist),
    ("mileage-log", "Business mileage log", build_mileage_log),
    ("dividend-voucher", "Dividend voucher template", build_dividend_voucher),
    ("board-minutes", "Board minutes template", build_board_minutes),
]


def make_pdf(slug: str, title: str, story_builder):
    out_path = OUT_DIR / f"{slug}.pdf"
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=35 * mm,
        bottomMargin=30 * mm,
        title=f"Holloway Davies · {title}",
        author="Holloway Davies",
    )
    story = story_builder()

    def on_page(canvas, doc):
        header_footer(canvas, doc, title)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return out_path


def main():
    print(f"Generating {len(TEMPLATES)} PDF templates...")
    for slug, title, builder in TEMPLATES:
        p = make_pdf(slug, title, builder)
        size_kb = p.stat().st_size / 1024
        print(f"  wrote {p.name}  ({size_kb:.1f} KB)")
    print(f"\nDone. Files in {OUT_DIR}")


if __name__ == "__main__":
    main()
