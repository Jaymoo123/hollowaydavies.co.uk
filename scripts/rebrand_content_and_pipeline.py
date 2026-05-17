"""
Sweep brand references in generated content + pipeline prompts.

Targets ONLY these paths:
  web/content/blog/*.md         (310 generated blog posts)
  web/content/fundamentals/*.md (17 pillar guides)
  pipeline/*.py                 (DeepSeek prompts for future generations)

Swap pairs (in order):
  "UK Business Accountants Ltd" -> "Holloway Davies Ltd"
  "UK Business Accountants"     -> "Holloway Davies"
  "ukbusinessaccountants.co.uk" -> "hollowaydavies.co.uk"
  "ukbusinessaccountants"       -> "hollowaydavies"

Idempotent. Re-runs are no-ops.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SWAPS = [
    ("UK Business Accountants Ltd", "Holloway Davies Ltd"),
    ("UK Business Accountants", "Holloway Davies"),
    ("ukbusinessaccountants.co.uk", "hollowaydavies.co.uk"),
    ("ukbusinessaccountants", "hollowaydavies"),
]

TARGETS = [
    (ROOT / "web" / "content" / "blog", "*.md"),
    (ROOT / "web" / "content" / "fundamentals", "*.md"),
    (ROOT / "pipeline", "*.py"),
]


def swap_file(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return 0
    new_text = text
    n = 0
    for old, new in SWAPS:
        if old in new_text:
            n += new_text.count(old)
            new_text = new_text.replace(old, new)
    if n and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return n


def main():
    files = []
    for base, pattern in TARGETS:
        if base.exists():
            files.extend(base.glob(pattern))
    print(f"Scanning {len(files)} files...")
    n_files = 0
    n_swaps = 0
    for f in files:
        n = swap_file(f)
        if n:
            n_files += 1
            n_swaps += n
    print(f"Swapped {n_swaps} occurrences across {n_files} files")


if __name__ == "__main__":
    main()
