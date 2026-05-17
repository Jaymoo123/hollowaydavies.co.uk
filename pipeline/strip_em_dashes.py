#!/usr/bin/env python3
"""
Remove em-dashes (U+2014) from content + source files.

Em-dashes are a well-known AI-generated-content tell. This sweep replaces
them with natural punctuation:

  ' — '   (space em-dash space, the common form)        → ', '
  ' —\n'  (em-dash at line end)                          → '\n'
  '— '    (em-dash leading a sentence/clause)            → ''
  '—'     (em-dash with no spaces, e.g. compound noun)   → '-'

En-dashes (U+2013) are preserved — they're correct for numeric ranges
like '2025/26' and '£2,000–£6,000'.

Targets:
  web/content/blog/*.md
  web/content/fundamentals/*.md
  web/src/**/*.tsx
  web/src/**/*.ts

Usage:
  python pipeline/strip_em_dashes.py            # do it
  python pipeline/strip_em_dashes.py --dry-run  # preview counts
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Order matters: longer patterns first
REPLACEMENTS: list[tuple[str, str]] = [
    (" — ", ", "),       # parenthetical aside → comma
    ("— ", ""),          # leading em-dash → drop
    (" —", ""),          # trailing em-dash → drop
    ("—", "-"),          # bare em-dash → hyphen (rare)
]


def transform(text: str) -> tuple[str, int]:
    """Return (new_text, occurrences_replaced)."""
    count = 0
    for old, new in REPLACEMENTS:
        count += text.count(old)
        text = text.replace(old, new)
    return text, count


def gather_files() -> list[Path]:
    paths: list[Path] = []
    for sub in ("web/content/blog", "web/content/fundamentals"):
        d = ROOT / sub
        if d.exists():
            paths.extend(sorted(d.glob("*.md")))
    src = ROOT / "web" / "src"
    if src.exists():
        for ext in ("tsx", "ts"):
            paths.extend(sorted(src.rglob(f"*.{ext}")))
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = gather_files()
    total_files = 0
    total_replacements = 0

    for p in files:
        try:
            raw = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "—" not in raw:
            continue
        new, n = transform(raw)
        if n == 0 or new == raw:
            continue
        total_files += 1
        total_replacements += n
        rel = p.relative_to(ROOT)
        if args.dry_run:
            print(f"[dry-run] {rel}: {n} replacements")
        else:
            p.write_text(new, encoding="utf-8")
            print(f"{rel}: {n} replacements")

    print()
    print(f"Files changed: {total_files}")
    print(f"Total em-dashes replaced: {total_replacements}")


if __name__ == "__main__":
    main()
