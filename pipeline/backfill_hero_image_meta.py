"""
Backfill heroImage metadata in locations/[slug]/data.ts for cities whose
.jpg already exists on disk but whose data.ts block is missing the
heroImage field.

Use case: a previous fetch_city_images.py run downloaded images but skipped
the data.ts patch (or was run before heroImage was on the type). Now we
just need the Pexels attribution metadata to make data.ts consistent.

Run:
    python pipeline/backfill_hero_image_meta.py
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
DATA_TS = ROOT / "web" / "src" / "app" / "locations" / "[slug]" / "data.ts"
IMG_DIR = ROOT / "web" / "public" / "locations"

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
except ImportError:
    pass

PEXELS_KEY = os.getenv("PEXELS_API_KEY")

QUERY_OVERRIDES = {
    "reading": "reading berkshire town",
    "york": "york england minster",
    "newcastle": "newcastle upon tyne quayside",
    "cambridge": "cambridge england university",
    "oxford": "oxford england spires",
    "hull": "hull east yorkshire marina",
    "brighton": "brighton seafront pier",
    "bournemouth": "bournemouth beach",
    "plymouth": "plymouth devon harbour",
    "portsmouth": "portsmouth spinnaker tower",
    "stoke-on-trent": "stoke on trent staffordshire",
    "milton-keynes": "milton keynes uk centre",
}


def pexels_search(query: str, per_page: int = 5) -> list[dict]:
    if not PEXELS_KEY:
        raise RuntimeError("PEXELS_API_KEY not set")
    r = httpx.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={
            "query": query,
            "per_page": per_page,
            "orientation": "landscape",
            "size": "large",
        },
        timeout=20.0,
    )
    r.raise_for_status()
    return r.json().get("photos", [])


def load_cities_missing_hero() -> list[tuple[str, str]]:
    """Return (slug, name) for every city whose data.ts block has no heroImage."""
    text = DATA_TS.read_text(encoding="utf-8")
    matches = list(re.finditer(r'^  "([a-z-]+)":\s*\{', text, re.M))
    matches_with_ends = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        matches_with_ends.append((m.group(1), m.start(), end))

    missing = []
    for slug, start, end in matches_with_ends:
        chunk = text[start:end]
        if "heroImage" in chunk:
            continue
        # Pull the `name: "..."` from the chunk
        nm = re.search(r'name:\s*"([^"]+)"', chunk)
        if nm:
            missing.append((slug, nm.group(1)))
    return missing


def patch_data_ts(hero_map: dict[str, dict]) -> int:
    text = DATA_TS.read_text(encoding="utf-8")
    updated = 0
    for slug, hero in hero_map.items():
        if not hero:
            continue
        city_pattern = re.compile(
            r'(  "' + re.escape(slug) + r'":\s*\{[\s\S]*?adjacentTown:\s*\{[^}]*\},\n)', re.M
        )

        def replace_in_city(m: re.Match) -> str:
            block = m.group(1)
            hero_lines = (
                "    heroImage: {\n"
                f"      url: {json.dumps(hero['public_url'])},\n"
                f"      alt: {json.dumps(hero['alt'])},\n"
                f"      photographer: {json.dumps(hero['photographer'])},\n"
                f"      photographer_url: {json.dumps(hero['photographer_url'])},\n"
                f"      pexels_url: {json.dumps(hero['pexels_url'])},\n"
                "    },\n"
            )
            return block + hero_lines

        new_text, n = city_pattern.subn(replace_in_city, text, count=1)
        if n > 0:
            text = new_text
            updated += 1
        else:
            print(f"  WARN: could not patch '{slug}' (no adjacentTown anchor)")

    DATA_TS.write_text(text, encoding="utf-8")
    return updated


def main():
    if not PEXELS_KEY:
        sys.exit("PEXELS_API_KEY not set in .env")

    missing = load_cities_missing_hero()
    print(f"{len(missing)} cities missing heroImage in data.ts")
    if not missing:
        return

    hero_map: dict[str, dict] = {}
    for slug, name in missing:
        img_path = IMG_DIR / f"{slug}.jpg"
        if not img_path.exists():
            print(f"  [{slug:>20}]  SKIP no image on disk")
            continue
        query = QUERY_OVERRIDES.get(slug, f"{name} city uk")
        try:
            photos = pexels_search(query, per_page=3)
            if not photos:
                photos = pexels_search(name, per_page=3)
            if not photos:
                print(f"  [{slug:>20}]  no photos returned, using generic credit")
                hero_map[slug] = {
                    "public_url": f"/locations/{slug}.jpg",
                    "alt": f"{name} city scene",
                    "photographer": "Pexels",
                    "photographer_url": "https://www.pexels.com",
                    "pexels_url": "https://www.pexels.com",
                }
                continue
            pick = photos[0]
            hero_map[slug] = {
                "public_url": f"/locations/{slug}.jpg",
                "alt": pick.get("alt") or f"{name} city scene",
                "photographer": pick.get("photographer", ""),
                "photographer_url": pick.get("photographer_url", ""),
                "pexels_url": pick.get("url", ""),
            }
            print(f"  [{slug:>20}]  ok  ({pick.get('photographer', '?')})")
            time.sleep(0.25)
        except Exception as e:
            print(f"  [{slug:>20}]  ERROR {type(e).__name__}: {e}")

    if hero_map:
        print(f"\nPatching {len(hero_map)} entries into {DATA_TS.name}...")
        n = patch_data_ts(hero_map)
        print(f"  {n} entries patched")


if __name__ == "__main__":
    main()
