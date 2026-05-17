"""Second pass at BADR/CGT rate fixes — broader patterns to catch what pass 1 missed."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "web" / "content" / "blog"
FUND = ROOT / "web" / "content" / "fundamentals"

# Sentence-level patterns — match a whole sentence then rewrite inside it
def patch_sentence(text):
    """Apply numerous patches to text. Return new text + count of changes."""
    new = text
    n_changes = 0

    # Direct phrase swaps (BADR context implied by adjacent words)
    direct = [
        (r"\b10\s*%\s*\(\s*with BADR\s*\)", "14% (with BADR)"),
        (r"\b10\s*% with BADR\b", "14% with BADR"),
        (r"\b10\s*% rather than 20\s*%", "14% rather than 24%"),
        (r"\b10\s*% instead of 20\s*%", "14% instead of 24%"),
        (r"\b10\s*% \(BADR\) or 20\s*%", "14% (BADR) or 24%"),
        (r"\btax at 10\s*%", "tax at 14%"),
        (r"\btaxed at 10\s*%", "taxed at 14%"),
        (r"\b10\s*% if BADR applies\b", "14% if BADR applies"),
        (r"\b10\s*% if BADR\b", "14% if BADR"),
        (r"\bif BADR applies\b([^.!?\n]{0,60})\b10\s*%", r"if BADR applies\g<1>14%"),
        (r"\b(BADR\)?,?\s+(?:so\s+)?the rate is) 10\s*%", r"\g<1> 14%"),
        (r"\b(BADR\)?,?\s+the tax rate is) 10\s*%", r"\g<1> 14%"),
        (r"\bis 10\s*% rather than 20\s*%", "is 14% rather than 24%"),
        (r"\bfirst £1\s*[Mm](?:illion)?\s+at 10\s*%", "first £1 million at 14%"),
        (r"\bfirst £1\s*[Mm](?:illion)?\s+is\s+at 10\s*%", "first £1 million is at 14%"),
        (r"\bfirst £1\s*[Mm](?:illion)?\s+is\s+covered at 10\s*%", "first £1 million is covered at 14%"),
        (r"\bfirst £1\s*[Mm](?:illion)?\s+of\s+(?:your\s+)?(?:lifetime\s+)?gain[s]?\s+is taxed at 10\s*%", "first £1 million of gains is taxed at 14%"),
        (r"\bsecond £1\s*[Mm](?:illion)?\s+is\s+at 20\s*%", "second £1 million is at 24%"),
        (r"\bBADR\b([^.!?\n]{0,40})\bgives you a 10\s*%", r"BADR\g<1>gives you a 14%"),
        (r"\bBADR\b([^.!?\n]{0,40})\bis taxed at 10\s*%", r"BADR\g<1>is taxed at 14%"),
        (r"\bBADR\b([^.!?\n]{0,80})\b10\s*% capital gains tax rate\b", r"BADR\g<1>14% capital gains tax rate"),
        (r"\b10\s*% tax on their exit\b", "14% tax on their exit"),
        (r"\b10\s*% tax on qualifying disposals\b", "14% tax on qualifying disposals"),
        (r"\b10\s*% on gains up to £1\s*[Mm]\b", "14% on gains up to £1m"),
        (r"\bBADR\b([^.!?\n]{0,40})\bmay apply at 10\s*%", r"BADR\g<1>may apply at 14%"),
        (r"\bBADR\b([^.!?\n]{0,40})\bapplies at 10\s*%", r"BADR\g<1>applies at 14%"),
        (r"\bBADR claim \(10\s*% tax rate\b", "BADR claim (14% tax rate"),
        (r"\b10\s*% BADR\b(?! rate)", "14% BADR"),
        (r"\bBADR\b([^.!?\n]{0,80})\b10\s*% on £1\s*[Mm](?:illion)?\b", r"BADR\g<1>14% on £1 million"),
        (r"\bBADR\b([^.!?\n]{0,80})\byou pay 10\s*%", r"BADR\g<1>you pay 14%"),
        (r"\bremaining BADR allowance, you pay 10\s*%", "remaining BADR allowance, you pay 14%"),
        (r"\brate is 10\s*% on the first\b", "rate is 14% on the first"),
        (r"\brate is 10\s*% on qualifying\b", "rate is 14% on qualifying"),
        (r"\brate is 10\s*% on gains\b", "rate is 14% on gains"),
        # 20% CGT after BADR limit
        (r"\babove the £1\s*[Mm](?:illion)?\b([^.!?\n]{0,40})\bat 20\s*%", r"above the £1 million\g<1>at 24%"),
        (r"\bat 20\s*%([^.!?\n]{0,40})\babove the £1\s*[Mm]", r"at 24%\g<1>above the £1 million"),
        (r"\bsecond £1\s*[Mm](?:illion)?\s+(?:is\s+)?at 20\s*%", "second £1 million at 24%"),
    ]

    for pat, repl in direct:
        if callable(repl):
            new, n = re.subn(pat, repl, new, flags=re.IGNORECASE)
        else:
            new, n = re.subn(pat, repl, new, flags=re.IGNORECASE)
        n_changes += n

    return new, n_changes


def main():
    total = 0
    files = 0
    for d in [BLOG, FUND]:
        for path in sorted(d.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            new, n = patch_sentence(text)
            if n > 0:
                path.write_text(new, encoding="utf-8")
                files += 1
                total += n

    print(f"Pass 2: {total} patches across {files} files")


if __name__ == "__main__":
    main()
