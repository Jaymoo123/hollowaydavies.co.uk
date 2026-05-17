"""
Fix outdated BADR (10% -> 14%) and standard CGT (20% -> 24%) rates in
generated content.

Strategy: safe text patches only. Identifies posts with worked-example
numeric calculations (e.g. "£100,000 at 10% BADR") and flags them for
manual review rather than risking incorrect numeric edits.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "web" / "content" / "blog"
FUND = ROOT / "web" / "content" / "fundamentals"

# Safe text-only patches — replacements where the rate is stated in context
# unambiguously. We do NOT touch numeric worked examples (those need manual
# review because the calculated tax amount changes too).
BADR_PATTERNS = [
    # "BADR at 10%" -> "BADR at 14% (for disposals from 6 April 2025)"
    (r"\bBADR at 10\s*%(?!\s*[,;])", "BADR at 14% (for disposals from 6 April 2025)"),
    (r"\bat 10\s*% BADR\b", "at 14% BADR"),
    (r"\b10\s*% BADR rate\b", "14% BADR rate"),
    (r"\b10\s*% with BADR\b", "14% with BADR"),
    # "BADR ... 10% CGT"
    (r"\bBADR\b([^.!?\n]{1,40})\b10\s*% CGT\b", r"BADR\g<1>14% CGT"),
    (r"\bBADR\b([^.!?\n]{1,40})\b10\s*% capital gains tax\b", r"BADR\g<1>14% capital gains tax"),
    (r"\bBADR\b([^.!?\n]{1,40})\b10\s*% capital gains\b", r"BADR\g<1>14% capital gains"),
    (r"\bBADR\b([^.!?\n]{1,40})\b10\s*% rate\b", r"BADR\g<1>14% rate"),
    # Inverse: rate first, then BADR
    (r"\b10\s*% CGT\b([^.!?\n]{1,40})\bBADR\b", r"14% CGT\g<1>BADR"),
    (r"\b10\s*% capital gains tax\b([^.!?\n]{1,40})\bBADR\b", r"14% capital gains tax\g<1>BADR"),
    # "BADR ... reduces CGT to 10%"
    (r"\bBADR\b([^.!?\n]{1,80})\breduces?\b([^.!?\n]{0,40})\bto 10\s*%", r"BADR\g<1>reduces\g<2>to 14%"),
    (r"\bBADR\b([^.!?\n]{1,80})\bcuts? your CGT to 10\s*%", r"BADR\g<1>cuts your CGT to 14%"),
    (r"\bBADR\b([^.!?\n]{1,80})\bcuts? your Capital Gains Tax to 10\s*%", r"BADR\g<1>cuts your Capital Gains Tax to 14%"),
    # "10% under BADR" / "10% (BADR)"
    (r"\b10\s*% under BADR\b", "14% under BADR"),
    (r"\b10\s*%\s*\(\s*BADR\s*\)", "14% (BADR)"),
    (r"\bunder BADR\b([^.!?\n]{1,40})\b10\s*%", r"under BADR\g<1>14%"),
    # Standalone "BADR remains at 10%" — this is a factual claim that needs full rewrite
    (r"\bBADR remains at 10\s*%", "BADR is 14% from 6 April 2025 (was 10% before then)"),
    (r"\bBADR itself remains at 10\s*%", "BADR is 14% from 6 April 2025"),
    # "10% on the first £1m of gains" near BADR (loose)
    (r"\b10\s*% (?:capital gains tax )?(?:CGT )?(?:rate )?(?:on )?(?:the )?first £?1\s*[Mm](?:illion)?\b", "14% on the first £1m"),
]

# Standard CGT higher rate from 20% to 24% — only where unambiguous
CGT_PATTERNS = [
    # "without BADR ... 20%" / "20% without BADR"
    (r"\bwithout BADR\b([^.!?\n]{1,40})\b20\s*%", r"without BADR\g<1>24%"),
    (r"\b20\s*% without BADR\b", "24% without BADR"),
    (r"\b20\s*% standard CGT\b", "24% standard CGT"),
    # "above £1m at 20%" near BADR
    (r"\babove £1\s*[Mm]\b([^.!?\n]{1,40})\b20\s*%", r"above £1m\g<1>24%"),
    (r"\babove the £1\s*[Mm](?:illion)?(?:\s+(?:lifetime\s+)?limit)?\b([^.!?\n]{1,40})\b20\s*%", r"above the £1m limit\g<1>24%"),
]

# Patterns that indicate WORKED EXAMPLES with numeric calculations — flag for manual review
NUMERIC_FLAG_PATTERNS = [
    r"£\d[\d,]*\s+(?:at|@)\s+10\s*%\s+(?:BADR|with BADR)",
    r"10\s*%\s+(?:of|on)\s+£\d[\d,]*",
    r"BADR\b[^.!?\n]{1,60}=\s*£\d[\d,]+",
]


def main():
    text_patches = 0
    files_patched = set()
    needs_manual = []

    for d in [BLOG, FUND]:
        for path in sorted(d.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            new = text

            # Apply BADR patches
            for pat, repl in BADR_PATTERNS:
                new2, n = re.subn(pat, repl, new, flags=re.IGNORECASE)
                if n > 0:
                    text_patches += n
                    new = new2

            # Apply CGT patches
            for pat, repl in CGT_PATTERNS:
                new2, n = re.subn(pat, repl, new, flags=re.IGNORECASE)
                if n > 0:
                    text_patches += n
                    new = new2

            if new != text:
                path.write_text(new, encoding="utf-8")
                files_patched.add(path.name)

            # Check for worked examples needing manual review
            for pat in NUMERIC_FLAG_PATTERNS:
                if re.search(pat, new, re.IGNORECASE):
                    needs_manual.append((path.name, re.search(pat, new, re.IGNORECASE).group()))
                    break

    print(f"Text-level patches: {text_patches} across {len(files_patched)} files")
    print(f"\nPosts with numeric worked examples needing manual review ({len(needs_manual)}):")
    for name, match in needs_manual[:30]:
        print(f"  {name}: ...{match[:80]}...")

    if len(needs_manual) > 30:
        print(f"  ... and {len(needs_manual) - 30} more")


if __name__ == "__main__":
    main()
