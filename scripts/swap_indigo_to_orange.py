"""
Sweep all `indigo-N` Tailwind classes to `orange-N` across web/src.

Per the locked design system memory, the brand uses orange (#f97316 = orange-500)
not indigo. Indigo references are stale agency-template leftovers.

Idempotent: re-running on already-swept code is a no-op.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "web" / "src"

# Match Tailwind colour classes only:
#   indigo-50, indigo-600, indigo-700/20, bg-indigo-50, focus:bg-indigo-600, hover:text-indigo-700, etc.
PAT = re.compile(r"\bindigo-(\d{2,3})\b")


def swap_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = PAT.subn(lambda m: f"orange-{m.group(1)}", text)
    if n:
        path.write_text(new_text, encoding="utf-8")
    return n


def main():
    files = list(SRC.rglob("*.tsx")) + list(SRC.rglob("*.ts")) + list(SRC.rglob("*.css"))
    total_files = 0
    total_swaps = 0
    for f in files:
        if "node_modules" in str(f):
            continue
        n = swap_file(f)
        if n:
            total_files += 1
            total_swaps += n
            print(f"  {n:>3} swap{'s' if n != 1 else ''}  {f.relative_to(ROOT)}")
    print(f"\nTotal: {total_swaps} swaps across {total_files} files")


if __name__ == "__main__":
    main()
