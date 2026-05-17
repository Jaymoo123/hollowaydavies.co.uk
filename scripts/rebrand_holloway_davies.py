"""
Sweep all 'UK Business Accountants' → 'Holloway Davies' and
'ukbusinessaccountants.co.uk' → 'hollowaydavies.co.uk' across the codebase.

Idempotent. Re-running is a no-op once swept.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files to scan: web/src + emails + scripts (skip node_modules + .next + content/)
ROOTS = [
    ROOT / "web" / "src",
    ROOT / "pipeline",
    ROOT / "niche.config.json",
]
EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".mdx", ".py", ".txt"}

SWAPS = [
    ("UK Business Accountants Ltd", "Holloway Davies Ltd"),
    ("UK Business Accountants", "Holloway Davies"),
    ("ukbusinessaccountants.co.uk", "hollowaydavies.co.uk"),
    ("ukbusinessaccountants", "hollowaydavies"),
]


def collect_files() -> list[Path]:
    out = []
    for r in ROOTS:
        if r.is_file():
            if r.suffix in EXTS or r.suffix == ".json":
                out.append(r)
            continue
        if not r.exists():
            continue
        for p in r.rglob("*"):
            if p.is_file() and p.suffix in EXTS and "node_modules" not in str(p) and ".next" not in str(p):
                out.append(p)
    return out


def swap_file(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return 0
    new_text = text
    n_total = 0
    for old, new in SWAPS:
        if old in new_text:
            count = new_text.count(old)
            new_text = new_text.replace(old, new)
            n_total += count
    if n_total and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return n_total


def main():
    files = collect_files()
    print(f"Scanning {len(files)} files...")
    total_files = 0
    total_swaps = 0
    for f in files:
        n = swap_file(f)
        if n:
            total_files += 1
            total_swaps += n
            print(f"  {n:>3} swap{'s' if n != 1 else ''}  {f.relative_to(ROOT)}")
    print(f"\nTotal: {total_swaps} swaps across {total_files} files")


if __name__ == "__main__":
    main()
