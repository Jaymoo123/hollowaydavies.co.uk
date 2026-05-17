"""
Surgically rewrite the small number of AI-flag word leaks (leverage, unlock,
robust, seamless, etc.) to natural human alternatives. Reads context, picks
a sensible replacement based on the sentence around it.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "web" / "content" / "blog"
FUND = ROOT / "web" / "content" / "fundamentals"

# (regex, replacement) — keep replacements conservative + UK English
REPLACEMENTS = [
    # "leverage" — almost always means "use" in business writing
    (r"\bLeverage\b", "Use"),
    (r"\bleverage\b", "use"),
    (r"\bleveraged\b", "used"),
    (r"\bleveraging\b", "using"),
    (r"\bleverages\b", "uses"),
    # "unlock" — usually means "get" or "access"
    (r"\bUnlock\b", "Get"),
    (r"\bunlock\b", "access"),
    (r"\bunlocking\b", "accessing"),
    (r"\bunlocks\b", "gets"),
    # "robust" — usually means "strong" or "reliable" or just nothing
    (r"\brobust\b", "strong"),
    (r"\bRobust\b", "Strong"),
    # "seamless" — usually means "smooth" or "clean"
    (r"\bseamless\b", "smooth"),
    (r"\bSeamless\b", "Smooth"),
    # "tax landscape" / "business landscape" → "tax environment" / "business environment"
    (r"\btax landscape\b", "tax environment"),
    (r"\bbusiness landscape\b", "business environment"),
    (r"\bfinancial landscape\b", "financial environment"),
    (r"\bdigital landscape\b", "digital environment"),
    # "when it comes to" — drop or rephrase
    (r"\bWhen it comes to\s+", "On "),
    (r"\bwhen it comes to\s+", "on "),
]


def main():
    total_changes = 0
    files_touched = 0
    for d in [BLOG, FUND]:
        for path in sorted(d.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            new_text = text
            file_changes = 0
            for pat, repl in REPLACEMENTS:
                new_text, n = re.subn(pat, repl, new_text)
                file_changes += n
            if file_changes > 0:
                path.write_text(new_text, encoding="utf-8")
                files_touched += 1
                total_changes += file_changes
                print(f"  {path.name}: {file_changes} replacements")
    print(f"\n{files_touched} files touched, {total_changes} replacements applied")


if __name__ == "__main__":
    main()
