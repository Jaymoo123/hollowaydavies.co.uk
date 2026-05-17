"""
Generate brand-consistent SVG illustrations for each blog category.

Each illustration is a simple geometric composition: an off-white surface,
orange accent shapes, and an ink-coloured silhouette evoking the category
(stack of pages, calculator, chart, building, etc). Designed to live on
category landing pages and as blog-card fallbacks where no Pexels image
fits.

Output: web/public/illustrations/<category-slug>.svg
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "web" / "public" / "illustrations"

ORANGE = "#f97316"
ORANGE_LIGHT = "#fed7aa"
INK = "#0a0a0a"
INK_SOFT = "#525252"
SURFACE = "#fafaf7"
HAIRLINE = "#e5e5e5"


def svg(width: int = 600, height: int = 400, body: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="{SURFACE}"/>
{body}
</svg>
"""


ILLUSTRATIONS = {
    "limited-company-tax": svg(body=f"""
  <!-- Document stack representing CT600 + accounts -->
  <rect x="180" y="120" width="200" height="240" fill="white" stroke="{INK}" stroke-width="2"/>
  <rect x="200" y="100" width="200" height="240" fill="white" stroke="{INK}" stroke-width="2"/>
  <rect x="220" y="80" width="200" height="240" fill="white" stroke="{INK}" stroke-width="2"/>
  <line x1="240" y1="120" x2="400" y2="120" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="140" x2="400" y2="140" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="160" x2="380" y2="160" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="180" x2="400" y2="180" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="200" x2="380" y2="200" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="220" x2="400" y2="220" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <rect x="240" y="240" width="80" height="24" fill="{ORANGE}"/>
  <text x="280" y="258" text-anchor="middle" font-family="monospace" font-size="14" font-weight="700" fill="white">CT600</text>
"""),
    "sole-trader-and-self-employment": svg(body=f"""
  <!-- Single-figure desk silhouette -->
  <rect x="120" y="260" width="360" height="20" fill="{INK}"/>
  <rect x="220" y="160" width="160" height="100" fill="white" stroke="{INK}" stroke-width="2"/>
  <line x1="240" y1="180" x2="360" y2="180" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="200" x2="360" y2="200" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="220" x2="340" y2="220" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="240" y1="240" x2="360" y2="240" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <circle cx="160" cy="200" r="40" fill="{ORANGE}"/>
  <rect x="140" y="240" width="40" height="60" fill="{INK}"/>
"""),
    "vat-and-making-tax-digital": svg(body=f"""
  <!-- Digital tablet / cloud sync -->
  <rect x="180" y="100" width="240" height="180" rx="8" fill="white" stroke="{INK}" stroke-width="3"/>
  <rect x="200" y="120" width="200" height="140" fill="{SURFACE}"/>
  <text x="300" y="170" text-anchor="middle" font-family="sans-serif" font-size="48" font-weight="700" fill="{INK}">VAT</text>
  <text x="300" y="210" text-anchor="middle" font-family="monospace" font-size="14" fill="{INK_SOFT}">MTD</text>
  <rect x="290" y="290" width="20" height="14" fill="{INK}"/>
  <ellipse cx="300" cy="320" rx="60" ry="6" fill="{INK_SOFT}"/>
  <!-- Cloud arrows -->
  <path d="M 450 80 Q 470 60 490 80 Q 510 60 530 80 L 520 90 L 540 90 L 530 100 Z" fill="{ORANGE}"/>
"""),
    "payroll-and-paye": svg(body=f"""
  <!-- Stack of payslips -->
  <rect x="220" y="130" width="160" height="100" fill="white" stroke="{INK}" stroke-width="2"/>
  <rect x="210" y="150" width="160" height="100" fill="white" stroke="{INK}" stroke-width="2"/>
  <rect x="200" y="170" width="160" height="100" fill="white" stroke="{INK}" stroke-width="2"/>
  <line x1="210" y1="190" x2="350" y2="190" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="210" y1="210" x2="350" y2="210" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="210" y1="230" x2="330" y2="230" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <rect x="210" y="245" width="50" height="20" fill="{ORANGE}"/>
  <text x="235" y="259" text-anchor="middle" font-family="monospace" font-size="11" font-weight="700" fill="white">PAYE</text>
  <!-- Coins -->
  <circle cx="420" cy="280" r="20" fill="{ORANGE}" stroke="{INK}" stroke-width="2"/>
  <circle cx="450" cy="290" r="20" fill="{ORANGE_LIGHT}" stroke="{INK}" stroke-width="2"/>
  <circle cx="480" cy="280" r="20" fill="{ORANGE}" stroke="{INK}" stroke-width="2"/>
"""),
    "corporation-tax": svg(body=f"""
  <!-- Bar chart marginal relief -->
  <line x1="150" y1="320" x2="450" y2="320" stroke="{INK}" stroke-width="2"/>
  <line x1="150" y1="80" x2="150" y2="320" stroke="{INK}" stroke-width="2"/>
  <rect x="180" y="220" width="50" height="100" fill="{ORANGE_LIGHT}"/>
  <rect x="240" y="180" width="50" height="140" fill="{ORANGE}"/>
  <rect x="300" y="140" width="50" height="180" fill="{ORANGE}"/>
  <rect x="360" y="100" width="50" height="220" fill="{INK}"/>
  <text x="205" y="340" text-anchor="middle" font-family="monospace" font-size="11" fill="{INK_SOFT}">19%</text>
  <text x="265" y="340" text-anchor="middle" font-family="monospace" font-size="11" fill="{INK_SOFT}">22%</text>
  <text x="325" y="340" text-anchor="middle" font-family="monospace" font-size="11" fill="{INK_SOFT}">25%</text>
  <text x="385" y="340" text-anchor="middle" font-family="monospace" font-size="11" fill="{INK_SOFT}">25%</text>
"""),
    "r-and-d-tax-credits": svg(body=f"""
  <!-- Lightbulb + flask -->
  <circle cx="220" cy="180" r="60" fill="{ORANGE_LIGHT}" stroke="{INK}" stroke-width="2"/>
  <rect x="200" y="230" width="40" height="20" fill="{INK}"/>
  <rect x="208" y="250" width="24" height="10" fill="{INK_SOFT}"/>
  <line x1="220" y1="100" x2="220" y2="110" stroke="{INK}" stroke-width="3"/>
  <line x1="160" y1="180" x2="150" y2="180" stroke="{INK}" stroke-width="3"/>
  <line x1="280" y1="180" x2="290" y2="180" stroke="{INK}" stroke-width="3"/>
  <line x1="175" y1="135" x2="167" y2="127" stroke="{INK}" stroke-width="3"/>
  <line x1="265" y1="135" x2="273" y2="127" stroke="{INK}" stroke-width="3"/>
  <!-- Flask -->
  <path d="M 380 140 L 380 200 L 360 290 L 460 290 L 440 200 L 440 140 Z" fill="white" stroke="{INK}" stroke-width="2"/>
  <path d="M 366 260 L 454 260 L 460 290 L 360 290 Z" fill="{ORANGE}"/>
  <line x1="380" y1="140" x2="440" y2="140" stroke="{INK}" stroke-width="3"/>
"""),
    "incorporation-and-structure": svg(body=f"""
  <!-- Building blocks -->
  <rect x="180" y="220" width="120" height="100" fill="{INK}"/>
  <rect x="300" y="180" width="100" height="140" fill="{ORANGE}"/>
  <rect x="400" y="140" width="80" height="180" fill="{INK_SOFT}"/>
  <rect x="200" y="240" width="20" height="30" fill="{ORANGE_LIGHT}"/>
  <rect x="240" y="240" width="20" height="30" fill="{ORANGE_LIGHT}"/>
  <rect x="320" y="210" width="20" height="30" fill="white"/>
  <rect x="360" y="210" width="20" height="30" fill="white"/>
  <rect x="420" y="170" width="20" height="30" fill="white"/>
  <rect x="450" y="170" width="20" height="30" fill="white"/>
  <text x="240" y="350" text-anchor="middle" font-family="monospace" font-size="10" fill="{INK_SOFT}">SOLE TRADER</text>
  <text x="350" y="350" text-anchor="middle" font-family="monospace" font-size="10" fill="{INK_SOFT}">LTD</text>
  <text x="440" y="350" text-anchor="middle" font-family="monospace" font-size="10" fill="{INK_SOFT}">GROUP</text>
"""),
    "exit-and-capital-gains": svg(body=f"""
  <!-- Door with arrow + gains chart -->
  <rect x="160" y="120" width="120" height="200" fill="white" stroke="{INK}" stroke-width="3"/>
  <circle cx="265" cy="220" r="4" fill="{INK}"/>
  <line x1="200" y1="150" x2="240" y2="150" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="200" y1="180" x2="240" y2="180" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <path d="M 310 220 L 480 220 L 460 200 L 480 220 L 460 240" stroke="{ORANGE}" stroke-width="3" fill="none"/>
  <text x="395" y="190" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="700" fill="{INK}">BADR 14%</text>
  <text x="395" y="260" text-anchor="middle" font-family="monospace" font-size="11" fill="{INK_SOFT}">£1m lifetime</text>
"""),
    "bookkeeping-and-compliance": svg(body=f"""
  <!-- Open ledger -->
  <path d="M 150 140 L 300 130 L 300 310 L 150 320 Z" fill="white" stroke="{INK}" stroke-width="2.5"/>
  <path d="M 300 130 L 450 140 L 450 320 L 300 310 Z" fill="white" stroke="{INK}" stroke-width="2.5"/>
  <line x1="170" y1="170" x2="280" y2="165" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="170" y1="195" x2="280" y2="190" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="170" y1="220" x2="280" y2="215" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="170" y1="245" x2="280" y2="240" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="320" y1="170" x2="430" y2="175" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="320" y1="195" x2="430" y2="200" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="320" y1="220" x2="430" y2="225" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <line x1="320" y1="245" x2="430" y2="250" stroke="{INK_SOFT}" stroke-width="1.5"/>
  <rect x="380" y="265" width="50" height="20" fill="{ORANGE}"/>
  <text x="405" y="279" text-anchor="middle" font-family="monospace" font-size="12" font-weight="700" fill="white">£</text>
"""),
    "director-pay-and-dividends": svg(body=f"""
  <!-- Salary vs dividends split -->
  <circle cx="300" cy="200" r="100" fill="{INK}"/>
  <path d="M 300 100 A 100 100 0 0 1 386 250 L 300 200 Z" fill="{ORANGE}"/>
  <path d="M 386 250 A 100 100 0 0 1 300 300 L 300 200 Z" fill="{ORANGE_LIGHT}"/>
  <text x="220" y="195" font-family="monospace" font-size="14" font-weight="700" fill="white">Salary</text>
  <text x="220" y="215" font-family="monospace" font-size="11" fill="white">£12,570</text>
  <text x="360" y="200" font-family="monospace" font-size="11" font-weight="700" fill="{INK}">Div</text>
  <text x="360" y="215" font-family="monospace" font-size="10" fill="{INK}">8.75%</text>
"""),
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for slug, content in ILLUSTRATIONS.items():
        path = OUT_DIR / f"{slug}.svg"
        path.write_text(content, encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT.parent)}")
    print(f"\n{len(ILLUSTRATIONS)} illustrations generated")


if __name__ == "__main__":
    main()
